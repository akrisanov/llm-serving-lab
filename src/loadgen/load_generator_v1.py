"""
Load Generator V1
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx

from .config import LoadTestConfig

logger = logging.getLogger(__name__)


@dataclass
class RequestResult:
    """Result of a single API request."""

    latency_ms: float
    ttft_ms: float | None  # Time-to-First-Token for streaming
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    success: bool
    error: str | None = None
    tokens_per_second: float | None = None  # Generation speed


@dataclass
class LoadTestResults:
    """Aggregated results of load test."""

    total_requests: int
    successful_requests: int
    failed_requests: int
    total_tokens: int
    elapsed_time: float
    latencies: list[float]
    ttft_latencies: list[float]  # Time-to-First-Token measurements
    generation_speeds: list[float]  # Tokens per second per request

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests > 0:
            return self.successful_requests / self.total_requests
        return 0.0

    @property
    def tokens_per_second(self) -> float:
        """Calculate tokens per second throughput."""
        if self.elapsed_time > 0:
            return self.total_tokens / self.elapsed_time
        return 0.0

    @property
    def requests_per_second(self) -> float:
        """Calculate requests per second."""
        if self.elapsed_time > 0:
            return self.successful_requests / self.elapsed_time
        return 0.0

    def get_percentile(self, percentile: float) -> float:
        """Calculate latency percentile using nearest-rank method."""
        if not self.latencies:
            return 0.0

        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)

        # Use nearest-rank method: P = (percentile/100) * n
        rank = percentile / 100 * n

        # Convert to 0-based index
        if rank == int(rank) and rank > 0:
            # Exact rank - average with next value for better accuracy
            index = int(rank) - 1
            if index + 1 < n:
                value = (sorted_latencies[index] + sorted_latencies[index + 1]) / 2
            else:
                value = sorted_latencies[index]
        else:
            # Round up to next index
            index = min(int(rank), n - 1)
            value = sorted_latencies[index]

        return round(value, 1)

    def get_ttft_percentile(self, percentile: float) -> float:
        """Calculate TTFT percentile using nearest-rank method."""
        if not self.ttft_latencies:
            return 0.0

        sorted_ttft = sorted(self.ttft_latencies)
        n = len(sorted_ttft)

        # Use nearest-rank method: P = (percentile/100) * n
        rank = percentile / 100 * n

        # Convert to 0-based index
        if rank == int(rank) and rank > 0:
            # Exact rank - average with next value for better accuracy
            index = int(rank) - 1
            if index + 1 < n:
                value = (sorted_ttft[index] + sorted_ttft[index + 1]) / 2
            else:
                value = sorted_ttft[index]
        else:
            # Round up to next index
            index = min(int(rank), n - 1)
            value = sorted_ttft[index]

        return round(value, 1)

    @property
    def avg_generation_speed(self) -> float:
        """Calculate average generation speed (tokens/sec per request)."""
        if not self.generation_speeds:
            return 0.0
        return sum(self.generation_speeds) / len(self.generation_speeds)

    @property
    def avg_ttft_ms(self) -> float:
        """Calculate average Time-to-First-Token."""
        if not self.ttft_latencies:
            return 0.0
        return sum(self.ttft_latencies) / len(self.ttft_latencies)


class LoadGeneratorV1:
    """Load Generator V1 - Simple async implementation for LLM APIs."""

    def __init__(self, config: LoadTestConfig):
        self.config = config
        self._setup_client()

    def _setup_client(self) -> None:
        """Setup HTTP client with headers and concurrency settings."""
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        else:
            headers["Authorization"] = "Bearer dummy"  # Fallback for testing

        # Ensure sufficient connections for concurrency
        max_connections = max(self.config.concurrency * 2, 20)
        max_keepalive = max(self.config.concurrency, 10)

        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(self.config.timeout),
            limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive,
            ),
        )

    def _create_payload(self) -> dict[str, Any]:
        """Create request payload using config template."""
        return self.config.get_request_payload_template()

    async def _make_request(self) -> RequestResult:
        """Make a single API request and measure performance."""
        payload = self._create_payload()
        start_time = time.time()
        ttft_time = None

        try:
            if self.config.stream:
                # Streaming request for TTFT measurement
                async with self.client.stream(
                    "POST", self.config.url, json=payload
                ) as response:
                    response.raise_for_status()

                    first_token_time = None
                    generation_start_time = None
                    prompt_tokens = 0
                    completion_tokens = 0

                    # Process streaming response
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue

                        if line == "data: [DONE]":
                            break

                        try:
                            # Parse SSE data
                            data = json.loads(line[6:])  # Remove "data: " prefix

                            # Check for first token (TTFT measurement)
                            if "choices" in data and data["choices"]:
                                choice = data["choices"][0]
                                if "delta" in choice and choice["delta"].get("content"):
                                    if first_token_time is None:
                                        first_token_time = time.time()
                                        ttft_time = (
                                            first_token_time - start_time
                                        ) * 1000
                                        generation_start_time = first_token_time

                                    # Count tokens (approximation: 4 chars = 1 token)
                                    content = choice["delta"]["content"]
                                    completion_tokens += max(1, len(content) // 4)

                            # Extract token usage if available in final message
                            if "usage" in data:
                                prompt_tokens = data["usage"].get("prompt_tokens", 0)
                                completion_tokens = data["usage"].get(
                                    "completion_tokens", completion_tokens
                                )

                        except (json.JSONDecodeError, KeyError):
                            # Skip malformed SSE events
                            continue

                    end_time = time.time()

                    # Calculate generation speed (tokens/sec after first token)
                    if generation_start_time and completion_tokens > 0:
                        generation_time = end_time - generation_start_time
                        tokens_per_second = (
                            completion_tokens / generation_time
                            if generation_time > 0
                            else 0
                        )
                    else:
                        tokens_per_second = 0.0

                    return RequestResult(
                        latency_ms=(end_time - start_time) * 1000,
                        ttft_ms=ttft_time,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=prompt_tokens + completion_tokens,
                        success=True,
                        tokens_per_second=tokens_per_second,
                    )
            else:
                # Non-streaming request (existing logic)
                response = await self.client.post(self.config.url, json=payload)
                response.raise_for_status()
                end_time = time.time()

                data = response.json()
                usage = data.get("usage", {})
                completion_tokens = usage.get("completion_tokens", 0)

                # For non-streaming, estimate generation speed (no TTFT available)
                generation_time = end_time - start_time
                tokens_per_second = (
                    completion_tokens / generation_time if generation_time > 0 else 0
                )

                return RequestResult(
                    latency_ms=(end_time - start_time) * 1000,
                    ttft_ms=None,  # Not measurable in non-streaming mode
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=completion_tokens,
                    total_tokens=usage.get("total_tokens", 0),
                    success=True,
                    tokens_per_second=tokens_per_second,
                )

        except httpx.TimeoutException as e:
            end_time = time.time()
            return RequestResult(
                latency_ms=(end_time - start_time) * 1000,
                ttft_ms=ttft_time,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                success=False,
                error=f"Timeout: {str(e)}",
            )
        except httpx.HTTPStatusError as e:
            end_time = time.time()
            return RequestResult(
                latency_ms=(end_time - start_time) * 1000,
                ttft_ms=ttft_time,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                success=False,
                error=f"HTTP {e.response.status_code}: {str(e)}",
            )
        except Exception as e:
            end_time = time.time()
            return RequestResult(
                latency_ms=(end_time - start_time) * 1000,
                ttft_ms=ttft_time,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                success=False,
                error=str(e),
            )

    async def _warmup(self) -> None:
        """Perform warmup requests."""
        if self.config.warmup_count <= 0:
            return

        logger.info(
            "Starting warmup",
            extra={"warmup_requests": self.config.warmup_count, "phase": "warmup"},
        )
        warmup_tasks = [self._make_request() for _ in range(self.config.warmup_count)]
        await asyncio.gather(*warmup_tasks, return_exceptions=True)
        logger.info("Warmup completed", extra={"phase": "warmup"})

    async def _run_load_test(self) -> list[RequestResult]:
        """Run the main load test with concurrency control."""
        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.config.concurrency)

        # Thread-safe counters for progress tracking
        completed_requests = 0
        failed_requests = 0

        async def bounded_request() -> RequestResult:
            nonlocal completed_requests, failed_requests
            async with semaphore:
                result = await self._make_request()
                # These operations are atomic in asyncio
                completed_requests += 1
                if not result.success:
                    failed_requests += 1
                return result

        # Create all tasks
        tasks = [bounded_request() for _ in range(self.config.total_requests)]

        # Execute with concurrency control and exception handling
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(
                "Critical error during load test execution",
                extra={"error": str(e), "phase": "load_test"},
            )
            raise

        # Process results safely
        valid_results = []
        for result in results:
            if isinstance(result, RequestResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                # Create failed result for unexpected exceptions
                logger.warning(
                    "Unexpected exception in task",
                    extra={"error": str(result), "phase": "load_test"},
                )
                valid_results.append(
                    RequestResult(
                        latency_ms=0.0,
                        ttft_ms=None,
                        prompt_tokens=0,
                        completion_tokens=0,
                        total_tokens=0,
                        success=False,
                        error=f"Task exception: {str(result)}",
                    )
                )

        logger.info(
            "Load test batch completed",
            extra={
                "completed_requests": completed_requests,
                "failed_requests": failed_requests,
                "phase": "load_test",
            },
        )

        return valid_results

    def _aggregate_results(
        self, results: list[RequestResult], elapsed_time: float
    ) -> LoadTestResults:
        """Aggregate individual results into summary statistics."""
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]

        total_tokens = sum(r.total_tokens for r in successful_results)
        latencies = [r.latency_ms for r in successful_results]

        # Collect TTFT measurements (only available for streaming requests)
        ttft_latencies = [
            r.ttft_ms for r in successful_results if r.ttft_ms is not None
        ]

        # Collect generation speeds
        generation_speeds = [
            r.tokens_per_second
            for r in successful_results
            if r.tokens_per_second is not None
        ]

        return LoadTestResults(
            total_requests=len(results),
            successful_requests=len(successful_results),
            failed_requests=len(failed_results),
            total_tokens=total_tokens,
            elapsed_time=elapsed_time,
            latencies=latencies,
            ttft_latencies=ttft_latencies,
            generation_speeds=generation_speeds,
        )

    async def run(self) -> LoadTestResults:
        """Run complete load test with warmup and cleanup."""
        try:
            # Warmup phase
            await self._warmup()

            # Main load test
            logger.info(
                "Starting load test",
                extra={
                    "total_requests": self.config.total_requests,
                    "concurrency": self.config.concurrency,
                    "model": self.config.model_name,
                    "phase": "load_test",
                },
            )

            start_time = time.time()
            results = await self._run_load_test()
            elapsed_time = time.time() - start_time

            return self._aggregate_results(results, elapsed_time)

        except asyncio.CancelledError:
            logger.warning("Load test was cancelled", extra={"phase": "cleanup"})
            raise
        except Exception as e:
            logger.error(
                "Load test failed", extra={"error": str(e), "phase": "load_test"}
            )
            raise
        finally:
            # Ensure client is always closed cleanly
            try:
                await self.client.aclose()
                logger.debug("HTTP client closed", extra={"phase": "cleanup"})
            except Exception as e:
                logger.warning(
                    "Error closing HTTP client",
                    extra={"error": str(e), "phase": "cleanup"},
                )

    def log_results(self, results: LoadTestResults) -> None:
        """Log structured results."""
        # Log configuration summary first
        logger.info("Load test configuration", extra=self.config.get_summary())

        log_data = {
            "phase": "results",
            "tokens_per_second": round(results.tokens_per_second, 2),
            "requests_per_second": round(results.requests_per_second, 2),
            "latency_p50": results.get_percentile(50),
            "latency_p95": results.get_percentile(95),
            "latency_p99": results.get_percentile(99),
            "total_requests": results.total_requests,
            "successful_requests": results.successful_requests,
            "failed_requests": results.failed_requests,
            "success_rate": round(results.success_rate, 4),
            "concurrency": self.config.concurrency,
            "total_tokens": results.total_tokens,
            "elapsed_time": round(results.elapsed_time, 2),
        }

        # Add TTFT metrics if available (streaming mode)
        if results.ttft_latencies:
            log_data.update(
                {
                    "ttft_avg_ms": round(results.avg_ttft_ms, 2),
                    "ttft_p50": results.get_ttft_percentile(50),
                    "ttft_p95": results.get_ttft_percentile(95),
                    "ttft_p99": results.get_ttft_percentile(99),
                    "streaming_enabled": True,
                }
            )
        else:
            log_data["streaming_enabled"] = False

        # Add generation speed metrics if available
        if results.generation_speeds:
            log_data["avg_generation_speed_tps"] = round(
                results.avg_generation_speed, 2
            )

        logger.info("Load test completed", extra=log_data)


async def main() -> None:
    """Main entry point."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    config = LoadTestConfig()
    generator = LoadGeneratorV1(config)

    results = await generator.run()
    generator.log_results(results)


if __name__ == "__main__":
    asyncio.run(main())
