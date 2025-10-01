# llm-serving-lab

A long-term lab for **LLM serving experiments**: from baselines to multi-GPU scaling with comprehensive monitoring.

## Purpose

This repository provides **production-ready infrastructure** for LLM serving experiments with comprehensive monitoring:

- **Automated Infrastructure**: Terraform + Ansible for GPU VMs and observability stack
- **Pre-configured vLLM**: Ready-to-use inference server with Mistral-7B-Instruct model
- **Full Observability**: GPU metrics, system monitoring, and API analytics in Grafana
- **Interactive Experimentation**: Jupyter Notebook environment for load testing and analysis
- **Scalable Foundation**: From single-node baselines to multi-GPU experiments
- **Research-Ready**: Structured environment for AI infrastructure engineering experiments

## Reliability Features

Both infrastructure stacks include reliability features:

**Automated Health Checks:**

- Services are started in dependency order with health checks
- Built-in retry logic and timeout handling
- Automatic validation after deployment

**Robust Deployment:**

```bash
# Reliable deployment commands for both stacks
make deploy            # Deploy with health checks
make validate          # Quick validation of all services
# (obs only: make restart-services)
```

**Troubleshooting Support:**

```bash
# Common debugging commands
make ping             # Test connectivity
make logs             # View service logs
make status-services  # Check service status
make ssh              # Direct server access
```

See individual README files for detailed troubleshooting guides.

## Architecture Overview

The lab consists of two main components:

- **GPU VM**: Runs vLLM inference server with automatic GPU monitoring
- **Observability VM**: Collects metrics via OpenTelemetry, stores in ClickHouse, visualizes in Grafana, and provides Jupyter Notebook environment for interactive experimentation

All metrics are collected off the GPU VM to keep inference performance unaffected by monitoring overhead. The Jupyter environment on the OBS VM enables researchers to perform load testing, analyze results, and iterate on experiments without impacting GPU resources.

## Key Features

### Infrastructure & Deployment

- **Automated Deployment**: Complete infrastructure setup with `make deploy-all`
- **Production Ready**: vLLM service with systemd management and auto-restart
- **Model Ready**: Pre-configured Mistral-7B-Instruct (first startup takes 10-15 minutes for model loading)
- **Comprehensive Monitoring**: GPU utilization, memory usage, API metrics
- **Interactive Dashboards**: Real-time Grafana visualizations
- **Jupyter Environment**: Pre-configured notebook environment with load testing tools
- **Secure by Default**: VPC isolation, restricted access, encrypted secrets, API authentication
- **Cost Optimized**: Easy VM start/stop, resource right-sizing

### Python Development

- **Modular Architecture**: Reusable monitoring modules in `src/`
- **Local Development**: Full IDE support with type hints and autocompletion
- **Testing Tools**: CLI script for local metrics testing and debugging
- **Load Testing Framework**: Async load generator with configurable scenarios
- **Jupyter Integration**: Pre-installed development environment with all project dependencies
- **Code Quality**: Ruff integration for consistent formatting and linting
- **Infrastructure Integration**: Python modules deployed seamlessly via Ansible

## Getting Started

**Important:** Deploy in this order as GPU stack depends on OBS network:

1. **Deploy OBS stack first:** See [obs/README.md](obs/README.md) for observability stack setup
2. **Update GPU network config:** Get network IDs from OBS and update GPU terraform.tfvars
3. **Deploy GPU stack:** See [gpu/README.md](gpu/README.md) for GPU infrastructure setup
4. **Wait for model loading:** First vLLM startup takes 10-15 minutes for model download and loading

## Repository Layout

```text
llm-serving-lab/
├── src/                   # Python modules for development
│   ├── loadgen/           # Load testing framework
│   │   ├── load_generator_v1.py  # Async load generator
│   │   └── config.py             # Configuration management
│   ├── monitoring/        # Metrics collection modules
│   │   ├── metrics_exporter.py   # Main exporter class
│   │   ├── gpu_metrics.py        # GPU metrics via NVIDIA ML
│   │   ├── system_metrics.py     # System metrics via psutil
│   │   └── vllm_metrics.py       # vLLM API metrics
│   ├── deployment/        # Deployment utilities (planned)
│   └── utils/             # Common utilities (planned)
├── gpu/                   # GPU infrastructure (Terraform + Ansible)
│   ├── ansible/           # Ansible automation for VM configuration
│   ├── terraform/         # Infrastructure provisioning
│   ├── Makefile           # GPU management commands
│   └── README.md          # GPU setup instructions
├── obs/                   # Observability stack (ClickHouse, Grafana, Jupyter)
│   ├── dashboards/        # Grafana dashboards (JSON format)
│   ├── sql/               # ClickHouse SQL scripts and schema
│   ├── config/            # Service configurations (Jupyter, Docker Compose)
│   ├── ansible/           # Ansible automation for deployment
│   ├── terraform/         # Infrastructure provisioning
│   ├── Makefile           # OBS management commands
│   └── README.md          # Observability setup instructions
├── notebooks/             # Jupyter notebooks for experiments and analysis
├── benchmarks/            # Performance benchmarks and analysis (planned)
├── notes/                 # Weekly deliverables and research notes
├── metrics-cli.py         # CLI tool for local metrics testing
├── pyproject.toml         # Project dependencies and tool configuration
└── README.md
```

## Environment Setup

### Prerequisites

- Python 3.13+ (managed with `uv`)
- Terraform
- Ansible
- Docker (for local development)

### Python Environment with uv

Initialize the project environment:

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync

# Activate environment (optional, uv run handles this automatically)
source .venv/bin/activate
```

### Terraform Configuration for Russia

**For users in Russia:** Copy the Terraform configuration template to enable local provider mirrors:

```bash
# Copy template to home directory
cp config/terraformrc ~/.terraformrc

# Create local provider mirror directory
mkdir -p ~/.local/terraform-providers
```

This configuration uses a filesystem mirror for the Yandex Cloud provider, which helps with connectivity issues from Russia.

### Development Tools

```bash
# Install all dependencies
uv sync --extra dev --extra monitoring

# Infrastructure validation
cd gpu/ && uv run ansible-lint ansible/      # Lint GPU Ansible
cd obs/ && uv run ansible-lint ansible/      # Lint OBS Ansible
uv run yamllint gpu/ansible/ obs/ansible/    # Lint YAML files

# Terraform validation
cd gpu/terraform/ && terraform fmt -check && terraform validate
cd obs/terraform/ && terraform fmt -check && terraform validate

# Python development - see src/README.md for details
python metrics-cli.py --dry-run --log-level DEBUG  # Test metrics locally
```

### Python Module Development

For detailed information about Python modules and development workflow, see [src/README.md](src/README.md).

**Note:** Some ansible-lint errors related to vault files are expected when vault passwords are not available.

## Usage

### Quick Start

1. **Deploy Observability Stack:**

   ```bash
   cd obs/
   # Copy and configure example files
   make copy-examples
   # Edit terraform.tfvars and inventory.ini with your values
   make deploy-all
   ```

2. **Get OBS network configuration:**

   ```bash
   cd obs/terraform/
   terraform output obs_network_id obs_subnet_id
   ```

3. **Deploy GPU Infrastructure:**

   ```bash
   cd gpu/
   # Copy and configure example files
   make copy-examples
   # Edit terraform.tfvars with your values AND update obs_network_id/obs_subnet_id from step 2
   make deploy-all
   ```

4. **Monitor Model Loading and Manage:**

   ```bash
   # Wait for model loading (first startup takes 10-15 minutes)
   cd gpu/ && make logs  # Monitor loading progress

   # Check when API is ready (look for "Supported_tasks: ['generate']" in logs)
   # Test API with: make ssh then curl with proper auth (see GPU README)

   # Check GPU status
   make gpu-info

   # Access monitoring interfaces
   # Grafana: http://<obs-vm-ip>:3000
   # Jupyter: http://<obs-vm-ip>:8888 (password in /opt/jupyter/.jupyter_password)
   ```

5. **Interactive Experimentation:**

   ```bash
   # Use Jupyter for load testing and analysis
   # Access http://<obs-vm-ip>:8888
   # Navigate to example notebooks for load testing scenarios
   # Create custom experiments and analyze results
   ```

See individual README files for detailed instructions.

## Observability Stack

All metrics/logs are collected off the GPU VM into a dedicated **Observability VM**.
This VM runs ClickHouse, Grafana, OpenTelemetry Collector (gateway), and Jupyter Notebook.

**Key Services:**

- **ClickHouse**: High-performance time-series database for metrics storage
- **Grafana**: Interactive dashboards and alerting (accessible at `:3000`)
- **OpenTelemetry Collector**: Metrics aggregation gateway
- **Jupyter Notebook**: Interactive experimentation environment (accessible at `:8888`)

See [obs/README.md](obs/README.md) for Terraform + Ansible setup instructions.

## Research Notes

Experimental findings and weekly deliverables are tracked in the `notes/` directory.

## Notes

- Week-specific deliverables (e.g. “Week 1: Repo, Baseline, Metrics plumbing”) live under `notes/`.
- Performance notes are tracked in markdown alongside raw JSON run logs.

---

*This is an experimental research repo. Expect rapid iteration.*
