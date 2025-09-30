# Python Modules

This directory contains reusable Python modules for LLM serving lab components.

## Structure

```text
src/
├── monitoring/              # Metrics collection modules
│   ├── metrics_exporter.py  # Main exporter class and entry point
│   ├── gpu_metrics.py       # NVIDIA GPU metrics via nvidia-ml-py
│   ├── system_metrics.py    # System metrics via psutil
│   └── vllm_metrics.py      # vLLM API metrics via HTTP
├── deployment/              # Deployment utilities (future)
└── utils/                   # Common utilities (future)
```

## Development Workflow

### Local Development

1. **Install dependencies**:

   ```bash
   cd /path/to/llm-serving-lab
   uv sync --extra monitoring --extra dev
   ```

2. **Test locally** (without deploying):

   ```bash
   # Dry run - collect metrics once and print
   python metrics-cli.py --dry-run --log-level DEBUG

   # Test individual modules
   uv run python -c "from src.monitoring.system_metrics import get_system_metrics; print(get_system_metrics())"
   ```

3. **Code quality**:

   ```bash
   # Format code
   uv run ruff format src/ metrics-cli.py

   # Check for issues
   uv run ruff check src/ metrics-cli.py

   # Auto-fix issues
   uv run ruff check --fix src/ metrics-cli.py
   ```

### Deployment Integration

The Python modules are automatically deployed via Ansible:

1. **Source code** is copied to `/opt/llm-serving-lab/src/` on target VMs
2. **Ansible templates** (e.g., `metrics_exporter.py.j2`) import and use these modules
3. **Dependencies** are installed via pip on the target system

## Module Documentation

### monitoring.metrics_exporter

**Main metrics exporter class with OpenTelemetry integration.**

```python
from monitoring.metrics_exporter import MetricsExporter, create_exporter_from_env

# Create from environment variables
exporter = create_exporter_from_env()
exporter.run()  # Start continuous collection

# Or create manually
exporter = MetricsExporter(
    obs_otlp_endpoint="obs-vm:4317",
    vllm_port=8000,
    collect_interval=30,
    gpu_type="RTX-4090"
)

# Collect once
metrics = exporter.collect_metrics()
```

**Environment variables:**

- `OBS_OTLP_ENDPOINT`: Required. OBS OTLP endpoint (e.g., "obs-vm:4317")
- `VLLM_PORT`: vLLM server port (default: 8000)
- `METRICS_INTERVAL`: Collection interval in seconds (default: 30)
- `GPU_TYPE`: GPU type identifier (default: "unknown")

### monitoring.gpu_metrics

**NVIDIA GPU metrics collection via nvidia-ml-py.**

```python
from monitoring.gpu_metrics import init_nvidia, get_gpu_metrics

# Initialize NVIDIA ML library
if init_nvidia():
    metrics = get_gpu_metrics()
    # Returns: {'gpu_0_utilization': 85, 'gpu_0_memory_used': 12345, ...}
```

**Collected metrics per GPU:**

- `gpu_{i}_utilization`: GPU utilization percentage
- `gpu_{i}_memory_utilization`: GPU memory utilization percentage
- `gpu_{i}_memory_total`: Total GPU memory in bytes
- `gpu_{i}_memory_used`: Used GPU memory in bytes
- `gpu_{i}_memory_free`: Free GPU memory in bytes
- `gpu_{i}_temperature`: GPU temperature in Celsius
- `gpu_{i}_power_draw`: Power draw in watts (if supported)

### monitoring.system_metrics

**System metrics collection via psutil.**

```python
from monitoring.system_metrics import get_system_metrics

metrics = get_system_metrics()
# Returns: {'cpu_percent': 45.2, 'memory_total': 32768, ...}
```

**Collected metrics:**

- `cpu_percent`: CPU utilization percentage
- `cpu_count`: Number of CPU cores
- `memory_total`: Total system memory in bytes
- `memory_available`: Available memory in bytes
- `memory_percent`: Memory utilization percentage
- `disk_total`: Total disk space in bytes (root filesystem)
- `disk_used`: Used disk space in bytes
- `disk_percent`: Disk utilization percentage
- `load_1min`, `load_5min`, `load_15min`: System load averages

### monitoring.vllm_metrics

**vLLM API metrics collection via HTTP.**

```python
from monitoring.vllm_metrics import get_vllm_metrics

metrics = get_vllm_metrics(port=8000)
# Returns: {'vllm_requests_total': 123, 'vllm_tokens_generated': 5678, ...}
```

**Features:**

- Parses Prometheus-style metrics from `/metrics` endpoint
- Prefixes all metrics with `vllm_`
- Handles connection errors gracefully
- Configurable timeout (5 seconds default)

## Dependencies

### Core Dependencies

- `opentelemetry-api>=1.20.0`: OpenTelemetry metrics API
- `opentelemetry-sdk>=1.20.0`: OpenTelemetry SDK
- `opentelemetry-exporter-otlp>=1.20.0`: OTLP exporter for sending metrics
- `nvidia-ml-py>=12.0.0`: NVIDIA GPU metrics (optional, graceful fallback)
- `psutil>=5.9.0`: System metrics
- `requests>=2.31.0`: HTTP client for vLLM metrics

### Development Dependencies

- `ruff>=0.6.0`: Code formatting and linting

## Code Quality Standards

The project uses **ruff** for code quality:

### Configuration

- **Line length**: 88 characters (Black-compatible)
- **Target Python**: 3.13+
- **Enabled rules**: pycodestyle, Pyflakes, isort, pyupgrade, bugbear, simplify, comprehensions
- **Import sorting**: First-party modules (`monitoring`, `deployment`, `utils`) sorted separately

### Per-file Rules

- **CLI scripts**: Allow print statements and longer lines
- **Templates**: Relaxed style requirements
- **Tests**: Allow asserts and test-specific patterns

## Testing

### Local Testing

```bash
# Test all modules without external dependencies
python metrics-cli.py --dry-run

# Test individual modules
python -c "from src.monitoring.system_metrics import get_system_metrics; print(len(get_system_metrics()))"

# Test with verbose logging
python metrics-cli.py --dry-run --log-level DEBUG
```

### Integration Testing

```bash
# Test on actual infrastructure (requires deployed VMs)
python metrics-cli.py --obs-endpoint "your-obs-vm:4317" --interval 5
```

## Production Deployment

These modules are automatically deployed via Ansible:

1. **Source code** copied to `/opt/llm-serving-lab/src/` on target VMs
2. **Ansible templates** import and configure these modules
3. **Dependencies** installed via pip on target systems

This enables seamless integration between local development and production deployment.

## Benefits

1. **IDE Support**: Full IntelliSense, debugging, refactoring
2. **Testing**: Easy to write unit tests for individual modules
3. **Reusability**: Code can be used outside Ansible (Docker, direct Python, etc.)
4. **Maintainability**: Clean separation of concerns
5. **Development Speed**: No need to deploy to test changes

## Future Enhancements

- **deployment/** module: Configuration generation utilities
- **utils/** module: Common helpers and utilities
- **Unit tests**: pytest-based test suite
- **Type checking**: mypy integration
- **Documentation**: sphinx-based API docs
