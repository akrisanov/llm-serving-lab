# Grafana Dashboards

This directory contains Grafana dashboard definitions in JSON format for the LLM serving lab observability stack.

## Available Dashboards

### `experiment_overview.json`

High-level overview dashboard for experiment monitoring and performance tracking.

### `gpu_node_health.json`

GPU node health monitoring dashboard showing hardware metrics, utilization, and system health.

## Usage

These dashboards are automatically provisioned when deploying the observability stack via Ansible:

```bash
cd ansible
ansible-playbook -i inventory.ini playbooks/site.yml
```

The dashboards will be available in Grafana at `http://<obs-vm-ip>:3000` after deployment.

## Editing Dashboards

1. **Via Grafana UI**: Make changes in the web interface, then export the updated JSON
2. **Direct JSON editing**: Edit the `.json` files directly and redeploy

To update dashboards after editing:

```bash
# Re-run just the dashboard deployment task
ansible-playbook -i inventory.ini playbooks/site.yml --tags deploy
```

## Dashboard Development

When creating new dashboards:

1. Create/edit in Grafana UI
2. Export dashboard JSON via Share → Export → Save to file
3. Save the JSON file in this directory
4. Redeploy to apply changes

## ClickHouse Data Source

All dashboards are configured to use the ClickHouse data source with connection details:

- **Server**: `http://clickhouse:8123`
- **Database**: `otel_metrics` (configurable via `CH_DB` env var)
- **User**: `otel` (configurable via `CH_USER` env var)
