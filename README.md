# llm-serving-lab

A long-term lab for **LLM serving experiments**: from baselines to multi-GPU scaling with comprehensive monitoring.

## Reliability## Research Notes

- Week-specific deliverables (e.g. "Week 1: Repo, Baseline, Metrics plumbing") live under `notes/`
- Performance notes are tracked in markdown alongside raw JSON run logs
- Experimental findings and weekly deliverables are documented for research purposess

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

## Purpose

This repository provides **production-ready infrastructure** for LLM serving experiments with comprehensive monitoring:

- **Automated Infrastructure**: Terraform + Ansible for GPU VMs and observability stack
- **Pre-configured vLLM**: Ready-to-use inference server with Mistral-7B-Instruct model
- **Full Observability**: GPU metrics, system monitoring, and API analytics in Grafana
- **Scalable Foundation**: From single-node baselines to multi-GPU experiments
- **Research-Ready**: Structured environment for AI infrastructure engineering experiments

## Architecture Overview

The lab consists of two main components:

- **GPU VM**: Runs vLLM inference server with automatic GPU monitoring
- **Observability VM**: Collects metrics via OpenTelemetry, stores in ClickHouse, visualizes in Grafana

All metrics are collected off the GPU VM to keep inference performance unaffected by monitoring overhead.

## Key Features

- **Automated Deployment**: Complete infrastructure setup with `make deploy-all`
- **Production Ready**: vLLM service with systemd management and auto-restart
- **Model Ready**: Pre-configured Mistral-7B-Instruct (first startup takes 10-15 minutes for model loading)
- **Comprehensive Monitoring**: GPU utilization, memory usage, API metrics
- **Interactive Dashboards**: Real-time Grafana visualizations
- **Secure by Default**: VPC isolation, restricted access, encrypted secrets, API authentication
- **Cost Optimized**: Easy VM start/stop, resource right-sizing

## Getting Started

**Important:** Deploy in this order as GPU stack depends on OBS network:

1. **Deploy OBS stack first:** See [obs/README.md](obs/README.md) for observability stack setup
2. **Update GPU network config:** Get network IDs from OBS and update GPU terraform.tfvars
3. **Deploy GPU stack:** See [gpu/README.md](gpu/README.md) for GPU infrastructure setup
4. **Wait for model loading:** First vLLM startup takes 10-15 minutes for model download and loading

## Repository Layout

```text
llm-serving-lab/
├── gpu/                   # GPU infrastructure (Terraform + Ansible)
│   ├── ansible/           # Ansible automation for VM configuration
│   ├── terraform/         # Infrastructure provisioning
│   ├── Makefile           # GPU management commands
│   └── README.md          # GPU setup instructions
├── obs/                   # Observability stack (ClickHouse, Grafana)
│   ├── dashboards/        # Grafana dashboards (JSON format)
│   ├── sql/               # ClickHouse SQL scripts and schema
│   ├── ansible/           # Ansible automation for deployment
│   ├── terraform/         # Infrastructure provisioning
│   ├── Makefile           # OBS management commands
│   └── README.md          # Observability setup instructions
├── benchmarks/            # Performance benchmarks and analysis (planned)
├── notes/                 # Weekly deliverables and research notes
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

Run linting and validation:

```bash
# Lint Ansible playbooks (from individual directories)
cd gpu/ && uv run ansible-lint ansible/
cd obs/ && uv run ansible-lint ansible/

# Lint YAML files
uv run yamllint gpu/ansible/ obs/ansible/

# Validate Terraform configurations
cd gpu/terraform/ && terraform fmt -check && terraform validate
cd obs/terraform/ && terraform fmt -check && terraform validate
```

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

   # View Grafana dashboards
   # Access http://<obs-vm-ip>:3000
   ```

See individual README files for detailed instructions.

## Observability Stack

All metrics/logs are collected off the GPU VM into a dedicated **Observability VM**.
This VM runs ClickHouse, Grafana, and an OpenTelemetry Collector (gateway).

See [obs/README.md](obs/README.md) for Terraform + Ansible setup instructions.

## Research Notes

Experimental findings and weekly deliverables are tracked in the `notes/` directory.

## Notes

- Week-specific deliverables (e.g. “Week 1: Repo, Baseline, Metrics plumbing”) live under `notes/`.
- Performance notes are tracked in markdown alongside raw JSON run logs.

---

*This is an experimental research repo. Expect rapid iteration.*
