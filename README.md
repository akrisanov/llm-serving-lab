# llm-serving-lab

A long-term lab for **LLM serving experiments**: from## Architecture Overview

The lab consists of two main components:

- **GPU VM**: Runs vLLM inference server with automatic GPU monitoring
- **Observability VM**: Collects metrics via OpenTelemetry, stores in ClickHouse, visualizes in Grafana

All metrics are collected off the GPU VM to keep inference performance unaffected by monitoring overhead.

## Key Features

- **Automated Deployment**: Complete infrastructure setup with `make deploy-all`
- **Production Ready**: vLLM service with systemd management and auto-restart
- **Comprehensive Monitoring**: GPU utilization, memory usage, API metrics
- **Interactive Dashboards**: Real-time Grafana visualizations
- **Secure by Default**: VPC isolation, restricted access, encrypted secrets
- **Cost Optimized**: Easy VM start/stop, resource right-sizing

## Getting Started

1. See [obs/README.md](obs/README.md) for observability stack setup
2. See [gpu/README.md](gpu/README.md) for GPU infrastructure setup
3. Both use standardized make commands for easy management

## Research Notes

Experimental findings and weekly deliverables are tracked in `notes/` directory.selines to multi-GPU scaling,
with metrics logged into ClickHouse and visualized in Grafana.

## Purpose

This repository provides **production-ready infrastructure** for LLM serving experiments with comprehensive monitoring:

- **Automated Infrastructure**: Terraform + Ansible for GPU VMs and observability stack
- **Pre-configured vLLM**: Ready-to-use inference server with Mistral-7B-Instruct model
- **Full Observability**: GPU metrics, system monitoring, and API analytics in Grafana
- **Scalable Foundation**: From single-node baselines to multi-GPU experiments
- **Research-Ready**: Structured environment for AI infrastructure engineering experiments

## Repository layout

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

2. **Deploy GPU Infrastructure:**

   ```bash
   cd gpu/
   # Copy and configure example files
   make copy-examples
   # Edit terraform.tfvars and inventory.ini with your values
   make deploy-all
   ```

3. **Monitor and Manage:**

   ```bash
   # Check GPU status
   cd gpu/ && make gpu-info

   # View Grafana dashboards
   # Access http://<obs-vm-ip>:3000
   ```

See individual README files for detailed instructions.

## Observability stack

All metrics/logs are collected off the GPU VM into a dedicated **Observability VM**.
This VM runs ClickHouse, Grafana, and an OpenTelemetry Collector (gateway).

See [obs/README.md](obs/README.md) for Terraform + Ansible setup instructions.

## Notes

- Week-specific deliverables (e.g. “Week 1: Repo, Baseline, Metrics plumbing”) live under `notes/`.
- Performance notes are tracked in markdown alongside raw JSON run logs.

---

*This is an experimental research repo. Expect rapid iteration.*
