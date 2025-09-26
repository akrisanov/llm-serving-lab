# GPU VM Infrastructure

Infrastructure and automation for GPU-enabled virtual machines in Yandex Cloud for LLM inference workloads.
All operations are managed through a comprehensive Makefile.

## Overview

The infrastructure includes:

- **VPC Network** and Subnet for isolated networking
- **Security Group** with restricted access (SSH and vLLM API only from your IP)
- **GPU Compute Instance** with CUDA-enabled Ubuntu image
- **Cloud-init** configuration for basic system setup

## Architecture

```text
┌─────────────────────────────────────┐
│            Your IP                  │
│         (Admin Access)              │
└─────────────┬───────────────────────┘
              │ SSH (22) + vLLM API (8000)
              ▼
┌─────────────────────────────────────┐
│         GPU VM Network              │
│     (10.128.0.0/24 subnet)          │
│                                     │
│  ┌─────────────────────────────┐    │
│  │       GPU Instance          │    │
│  │   - CUDA Ubuntu 22.04       │    │
│  │   - GPU (T4i/A100)          │    │
│  │   - vLLM Service            │    │
│  │   - OTLP Metrics Export     │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
              │ OTLP gRPC (4317)
              ▼
        Observability Stack
```

## GPU Types Supported

| GPU Type | Platform ID       | Memory | Use Case                    |
|----------|-------------------|--------|-----------------------------|
| `t4i`    | `standard-v3-t4i` | 16GB   | Small-medium models (7B-13B)|
| `a100`   | `gpu-standard-v3` | 40GB   | Large models (30B+)         |

## Prerequisites

1. **Yandex Cloud CLI** configured with sufficient permissions
2. **Terraform** >= 1.6.0 installed
3. **Ansible** >= 2.9 for configuration management
4. **Make** utility (standard on macOS/Linux)
5. **SSH key pair** for VM access
6. **Observability stack** deployed (optional, for metrics collection)

> **💡 Tip**: All operations are managed through `make` commands - no need to remember complex terraform or ansible commands!

## Quick Start

The GPU infrastructure is managed through make commands for easy deployment and operations:

```bash
# Setup configuration (creates terraform.tfvars from example)
make setup

# Edit configuration with your values
make edit-config

# Deploy entire GPU infrastructure
make deploy-all

# Check deployment status
make status

# Connect to GPU VM via SSH
make ssh

# Monitor GPU usage and services
make gpu-info
make status-services
```

### Manual Configuration

If you prefer to edit configuration files directly:

```bash
# Copy example configuration
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

Edit `terraform/terraform.tfvars` with your values:

```hcl
# Yandex Cloud credentials
yc_token     = "ya29.your_token"
yc_cloud_id  = "b1gxxxxxxxxxxxxx"
yc_folder_id = "b1gxxxxxxxxxxxxx"

# Security
my_ip          = "203.0.113.1/32"  # Your public IP
ssh_public_key = "ssh-ed25519 AAAAC3Nz... your_key"

# GPU configuration
gpu_type  = "t4i"    # or "a100" for larger models
cores     = 8        # vCPUs (adjust based on GPU type)
memory_gb = 32       # RAM in GB
disk_gb   = 200      # Storage in GB

# Observability
obs_otlp_endpoint = "obs-vm-ip:4317"  # Your OBS stack endpoint
```

## Configuration Reference

### Required Variables

| Variable             | Description                | Example                |
|----------------------|----------------------------|------------------------|
| `yc_token`           | Yandex Cloud OAuth token   | `ya29.xxxxx`           |
| `yc_cloud_id`        | Cloud ID                   | `b1gxxxxx`             |
| `yc_folder_id`       | Folder ID                  | `b1gxxxxx`             |
| `my_ip`              | Your public IP (CIDR)      | `203.0.113.1/32`       |
| `ssh_public_key`     | SSH public key content     | `ssh-ed25519 AAA...`   |
| `obs_otlp_endpoint`  | OBS OTLP endpoint          | `obs-vm-ip:4317`       |

### Optional Variables

| Variable       | Default                 | Description                      |
|----------------|-------------------------|----------------------------------|
| `yc_zone`      | `ru-central1-a`         | Availability zone                |
| `vm_user`      | `ubuntu`                | VM username                      |
| `gpu_type`     | `t4i`                   | GPU type (`t4i` or `a100`)       |
| `cores`        | `8`                     | Number of vCPUs                  |
| `memory_gb`    | `32`                    | RAM in GB                        |
| `disk_gb`      | `200`                   | Disk size in GB                  |
| `image_family` | `ubuntu-2204-lts-cuda`  | VM image family                  |
| `vllm_port`    | `8000`                  | vLLM API port                    |

## Outputs

| Output             | Description                        |
|--------------------|------------------------------------|
| `gpu_public_ip`    | Public IP address of the GPU VM    |
| `gpu_internal_ip`  | Internal IP address within VPC     |

## Management Commands

### Infrastructure Management

```bash
make setup              # Setup configuration files
make edit-config        # Edit terraform configuration
make plan              # Show terraform plan
make deploy            # Deploy infrastructure
make deploy-all        # Full deployment (init + deploy)
make destroy           # Destroy infrastructure (with confirmation)
make output            # Show terraform outputs
make status            # Show infrastructure status
```

### VM Operations

```bash
make ssh               # SSH to GPU VM
make gpu-info          # Show GPU status and utilization
make status-services   # Check systemd services status
make logs              # Show vLLM service logs on remote host
```

### Security & Secrets Management

```bash
make vault-create      # Create new encrypted vault file
make vault-edit        # Edit encrypted vault file
make vault-view        # View encrypted vault file
make vault-password    # Create vault password file for automatic authentication
```

**Note**: Ansible vault operations require a password file at `ansible/vault/.vault_pass`. Use `make vault-password` to create this file securely, or create it manually:

```bash
echo "your_vault_password" > ansible/vault/.vault_pass
chmod 600 ansible/vault/.vault_pass
```

### Observability Integration

```bash
make set-obs-endpoint  # Configure OBS endpoint interactively
make test-obs         # Test OBS connectivity
```

## Post-Deployment Setup

After deploying with `make deploy-all`, the VM comes with vLLM pre-installed and configured:

1. **Check deployment status**: `make status-services`
2. **Check GPU status**: `make gpu-info`
3. **Configure OTLP metrics export**: `make set-obs-endpoint`
4. **Start vLLM service**: `make ssh` then `sudo systemctl start vllm`
5. **Monitor logs**: `make logs`

The vLLM service is pre-configured to:

- Load Mistral-7B-Instruct-v0.3 model by default
- Listen on port 8000 with OpenAI-compatible API
- Export GPU metrics to your observability stack
- Run as systemd service with automatic restart

To customize the model or configuration:

```bash
# Connect to VM
make ssh

# Edit vLLM configuration
sudo systemctl edit vllm

# Or modify the startup script
sudo nano /opt/vllm/start_vllm.sh
```

## Security Considerations

- **Limited access**: Only your IP can access SSH and vLLM API
- **No public GPU access**: API is not exposed to the internet
- **VPC isolation**: VM runs in isolated network
- **HTTPS recommended**: Consider adding TLS termination for production

## Cost Optimization

- **Stop when not in use**: GPU instances are expensive
- **Right-size resources**: Match CPU/memory to your model requirements
- **Use preemptible instances**: Consider for development workloads

## Troubleshooting

### Common Issues

1. **GPU not detected**:

   ```bash
   # Connect to VM and check GPU
   make ssh
   nvidia-smi

   # Or check remotely
   make gpu-info
   ```

2. **Configuration issues**:

   ```bash
   # Check terraform configuration
   make plan

   # Verify current status
   make status
   ```

3. **Service problems**:

   ```bash
   # Check all services
   make status-services

   # View system logs
   make logs

   # Check vLLM logs if running
   make logs
   ```

4. **Network issues**:
   - Verify security group rules with `make status`
   - Check your public IP hasn't changed
   - Test OBS connectivity with `make test-obs`

### Monitoring

Monitor your GPU VM through:

```bash
# Real-time GPU utilization
make gpu-info

# Service status
make status-services

# Infrastructure status
make status
```

The VM can export metrics to your observability stack via OTLP:

- GPU utilization and memory
- System metrics
- Model inference latency
- Request throughput

Configure with: `make set-obs-endpoint`

## Cleanup

To destroy the infrastructure:

```bash
make destroy
```

**⚠️ Warning**: This will permanently delete the VM and all data on it.

## All Available Commands

Run `make help` or `make` to see all available commands:

```bash
make                    # Show help with all available commands
make setup              # Setup configuration files
make edit-config        # Edit terraform configuration
make plan              # Show terraform plan
make deploy            # Deploy infrastructure
make deploy-all        # Full deployment (init + deploy)
make destroy           # Destroy infrastructure
make teardown          # Stop services and destroy infrastructure
make output            # Show terraform outputs
make status            # Show infrastructure status
make ssh               # SSH to GPU VM
make gpu-info          # Show GPU status and utilization
make status-services   # Check systemd services status
make stop-services     # Stop services on remote host
make logs              # Show vLLM service logs on remote host
make set-obs-endpoint  # Configure OBS endpoint
make test-obs          # Test OBS connectivity
make clean             # Clean terraform state and cache
make vault-create      # Create new encrypted vault file
make vault-edit        # Edit encrypted vault file
make vault-view        # View encrypted vault file
make vault-password    # Create vault password file
```

## Integration

This GPU VM infrastructure integrates seamlessly with:

- **Observability stack** (`../obs/`) for comprehensive metrics and monitoring
- **Make-based workflow** consistent with the obs stack management
- **Benchmarking tools** (`../benchmarks/`) for performance testing
- **Secure configuration** with example files and .gitignore patterns

## Contributing

When modifying this configuration:

1. Update the Makefile if adding new operations
2. Test with both T4i and A100 GPU types
3. Verify security group rules and example files
4. Update this README with any new make commands
5. Follow the same security patterns as the obs stack
