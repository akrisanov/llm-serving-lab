# Week 1: Repo, Baseline, Metrics plumbing

## Deliverables

- Repo scaffolded
- vLLM 7B baseline (short + long context)
- ClickHouse + Grafana wired; first charts live
- **Perf Notes #1** (inference time breakdown)

## Grafana panels

1. Tokens/sec over time
2. p95 / p99 latency
3. GPU util + VRAM (placeholder via nvidia-smi)
4. Queue depth (placeholder)

## CS spine

- OSTEP: processes, threads, memory (skim + 10 bullet notes)
- Implement a **ring buffer** with a microbench → ops/sec vs Python list
