"""
Configuration classes for LLM load testing.
"""

import os
from typing import Any

from pydantic import BaseModel, Field, ValidationInfo, field_validator


def _build_vllm_url() -> str:
    """Build vLLM URL from environment variables, compatible with GPU setup."""
    # Check for full URL first (load generator style)
    if url := os.getenv("VLLM_URL"):
        return url

    # Build from components (compatible with ansible env.j2)
    host = os.getenv("VLLM_HOST", "localhost")
    port = os.getenv("VLLM_PORT", "8000")
    return f"http://{host}:{port}/v1/chat/completions"


class LoadTestConfig(BaseModel):
    """Configuration for LLM load testing."""

    # Connection settings (from GPU VM)
    url: str = Field(
        default_factory=lambda: _build_vllm_url(),
        description="API endpoint URL (from VLLM_HOST/VLLM_PORT or VLLM_URL)",
    )
    api_key: str | None = Field(
        default_factory=lambda: os.getenv("VLLM_API_KEY"),
        description="API authentication key (from GPU VM)",
    )
    timeout: float = Field(
        default=60.0, description="Request timeout in seconds", gt=0, le=300.0
    )

    # Model settings (from GPU VM)
    model_name: str = Field(
        default_factory=lambda: os.getenv(
            "MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.3"
        ),
        description="LLM model name (from GPU VM)",
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("MAX_TOKENS", "128")),
        description="Max tokens to generate per request",
        ge=1,
        le=4096,  # Reasonable upper limit
    )
    temperature: float = Field(
        default=0.0, description="Sampling temperature", ge=0.0, le=2.0
    )

    # Load test settings (load generator specific)
    total_requests: int = Field(
        default_factory=lambda: int(os.getenv("LOAD_REQUESTS", "50")),
        description="Total requests to send",
        ge=1,
    )
    concurrency: int = Field(
        default_factory=lambda: int(os.getenv("LOAD_CONCURRENCY", "1")),
        description="Concurrent requests",
        ge=1,
    )
    warmup_count: int = Field(default=5, description="Warmup requests count", ge=0)
    stream: bool = Field(
        default_factory=lambda: os.getenv("LOAD_STREAM", "false").lower() == "true",
        description="Enable streaming mode for TTFT measurement",
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """Validate model name format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Model name cannot be empty")
        return v.strip()

    @field_validator("concurrency")
    @classmethod
    def validate_concurrency(cls, v: int, info: ValidationInfo) -> int:
        """Ensure concurrency doesn't exceed total requests."""
        if info.data:
            total_requests = info.data.get("total_requests", 50)
            if v > total_requests:
                return total_requests
        return v

    @field_validator("stream")
    @classmethod
    def validate_stream(cls, v: bool, info: ValidationInfo) -> bool:
        """Validate streaming configuration."""
        # Streaming requires reasonable timeout and token limits
        if v and info.data:
            timeout = info.data.get("timeout", 60.0)
            max_tokens = info.data.get("max_tokens", 128)

            if timeout < 30.0:
                raise ValueError("Streaming mode requires timeout >= 30 seconds")
            if max_tokens > 1000:
                raise ValueError(
                    "Streaming mode with high max_tokens may cause timeouts"
                )
        return v

    def get_request_payload_template(self) -> dict[str, Any]:
        """Get template payload for API requests."""
        payload = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        if self.stream:
            payload["stream"] = True

        return payload

    def get_summary(self) -> dict[str, Any]:
        """Get configuration summary for logging."""
        return {
            "url": self.url,
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "total_requests": self.total_requests,
            "concurrency": self.concurrency,
            "warmup_count": self.warmup_count,
            "stream_enabled": self.stream,
            "timeout": self.timeout,
        }
