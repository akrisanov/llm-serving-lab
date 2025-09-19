# llm-serving-lab

A long-term lab for **LLM serving experiments**: from single-node baselines to multi-GPU scaling,
with metrics logged into ClickHouse and visualized in Grafana.

## Purpose

This repository is a structured sandbox for exploring **AI infrastructure engineering** problems around model serving:

- Establish reproducible baselines for different model sizes and context lengths
- Experiment with batching, scheduling, quantization, and throughput optimization
- Capture performance metrics in ClickHouse and visualize trends in Grafana
- Build a library of **Perf Notes** and microbenchmarks (ring buffers, queues, etc.)
- Grow from single-node serving to distributed inference infrastructure

## Repository layout

```bash
llm-serving-lab/
  benchmarks/      # microbenches (e.g. ring buffer, queues)
  dashboards/      # Grafana dashboards + provisioning
  scripts/         # loadgen, logging, helpers
  src/             # future custom code / extensions
  notes/           # Perf Notes, weekly milestones, CS spine notes
  Makefile         # shortcuts (docker compose, bench, log)
  docker-compose.yml
```

## Usage

TBD

## Observability stack

All metrics/logs are collected off the GPU VM into a dedicated **Observability VM**.
This VM runs ClickHouse, Grafana, and an OpenTelemetry Collector (gateway).

See [obs/README.md](obs/README.md) for Terraform + Ansible setup instructions.

## Notes

- Week-specific deliverables (e.g. “Week 1: Repo, Baseline, Metrics plumbing”) live under `notes/`.
- Performance notes are tracked in markdown alongside raw JSON run logs.

---

*This is an experimental research repo. Expect rapid iteration.*
