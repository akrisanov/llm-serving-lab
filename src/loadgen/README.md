# Load Generator

High-performance load testing tool for LLM APIs.

## Features

- **High throughput**: Async design handles thousands of concurrent requests
- **Real-time metrics**: Latency percentiles, throughput, and success rates
- **Easy configuration**: Environment variables or Python config
- **GPU VM integration**: Works seamlessly with deployed LLM servers
- **Comprehensive reporting**: Structured logs and detailed statistics

## Installation

Install the loadgen dependencies:

```bash
uv sync --extra loadgen
```

## Quick Start

```python
import asyncio
from src.loadgen import LoadGeneratorV1, LoadTestConfig

# Create configuration
config = LoadTestConfig(
    total_requests=100,
    concurrency=10,
    max_tokens=128
)

# Run load test
async def main():
    generator = LoadGeneratorV1(config)
    results = await generator.run()
    generator.log_results(results)

asyncio.run(main())
```

## Configuration

### Environment Variables

Set these variables to configure your load test:

```bash
# GPU Server Settings (read from your GPU VM)
MODEL_NAME="mistralai/Mistral-7B-Instruct-v0.3"
VLLM_HOST="192.168.1.100"
VLLM_PORT="8000"
MAX_MODEL_LEN="2048"
VLLM_API_KEY="your-api-key"

# Load Test Settings
LOAD_REQUESTS="100"
LOAD_CONCURRENCY="10"
```

### Configuration Reference

| Variable           | Default                                     | Description              |
|--------------------|---------------------------------------------|--------------------------|
| `MODEL_NAME`       | `mistralai/Mistral-7B-Instruct-v0.3`        | LLM model to test        |
| `VLLM_HOST`        | `localhost`                                 | GPU server IP            |
| `VLLM_PORT`        | `8000`                                      | vLLM API port            |
| `MAX_MODEL_LEN`    | `128`                                       | Max tokens per response  |
| `VLLM_API_KEY`     | None                                        | API authentication       |
| `LOAD_REQUESTS`    | `50`                                        | Total requests to send   |
| `LOAD_CONCURRENCY` | `1`                                         | Concurrent requests      |

## Results

Get detailed performance metrics:

| Metric                    | Description                           |
|---------------------------|---------------------------------------|
| **Throughput**            | Tokens/second and requests/second     |
| **Latency Percentiles**   | p50, p95, p99 response times          |
| **Success Rate**          | Percentage of successful requests     |
| **Error Analysis**        | Detailed failure breakdown            |
| **Resource Usage**        | Connection pool utilization           |

## Example Usage

```bash
# Set your GPU server details
export MODEL_NAME="mistralai/Mistral-7B-Instruct-v0.3"
export VLLM_HOST="192.168.1.100"
export VLLM_PORT="8000"

# Configure load test
export LOAD_REQUESTS="500"
export LOAD_CONCURRENCY="20"

# Run the test
python -m src.loadgen.load_generator_v1
```

Sample output:

```text
2025-10-01 14:30:15 - Starting warmup - 5 requests
2025-10-01 14:30:16 - Warmup completed
2025-10-01 14:30:16 - Starting load test - 500 requests, concurrency: 20
2025-10-01 14:30:25 - Load test completed
  Throughput: 245.67 tokens/sec, 55.2 requests/sec
  Latency: p50=156ms, p95=298ms, p99=445ms
  Success: 500/500 (100.0%)
```
