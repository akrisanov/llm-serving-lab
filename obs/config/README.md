# Configuration Files for OBS VM

This directory contains all configuration files for the Observability VM deployment.

## Files Overview

### Core Services

- **`docker-compose.yml`** - Docker Compose configuration for the observability stack (ClickHouse, Grafana, OpenTelemetry Collector)
- **`jupyter_notebook_config.py.j2`** - Simplified Jupyter Notebook configuration template

### Grafana Configuration

- **`grafana/provisioning-datasource.yaml`** - ClickHouse datasource configuration for Grafana
- **`grafana/provisioning-dashboards.yaml`** - Dashboard provisioning configuration
- **`grafana/install-plugins.sh`** - Script to install Grafana plugins

### OpenTelemetry Configuration

- **`otel/collector-gateway.yaml`** - OpenTelemetry Collector gateway configuration for receiving metrics from GPU VM

## Configuration Philosophy

These configuration files follow these principles:

1. **Simplicity** - Only essential settings are configured, defaults are used where appropriate
2. **Environment Variables** - Sensitive data and environment-specific values use environment variables
3. **Template Variables** - Ansible variables are used for dynamic configuration during deployment
4. **Security** - Secure defaults with proper authentication and access controls

## Usage

These files are deployed by Ansible roles:

- `obs_stack` role deploys Docker Compose and service configurations
- `jupyter_setup` role deploys Jupyter configuration
- Configuration files are copied to `/opt/obs/` on the target VM
