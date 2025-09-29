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
6. **Observability stack** deployed first (required for network configuration)

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

**⚠️ Important:** Get network IDs from deployed OBS stack first:

```bash
cd ../obs/terraform && terraform output obs_network_id obs_subnet_id
```

```hcl
# Yandex Cloud credentials
yc_token     = "ya29.your_token"
yc_cloud_id  = "b1gxxxxxxxxxxxxx"
yc_folder_id = "b1gxxxxxxxxxxxxx"

# Security
my_ip          = "203.0.113.1/32"  # Your public IP
ssh_public_key = "ssh-ed25519 AAAAC3Nz... your_key"

# Network settings from OBS (REQUIRED - get from OBS terraform output)
obs_network_id = "enpxxxxxxxxxxxxx"  # From OBS stack output
obs_subnet_id  = "e9bxxxxxxxxxxxxx"  # From OBS stack output

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

**Note**: The vLLM API key is automatically generated and stored in the Ansible vault file. To retrieve it after deployment:

```bash
make vault-view  # View vault contents including API key
# Or check on the VM directly:
make ssh
sudo systemctl status vllm.service  # API key visible in command line
```

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
4. **Wait for model loading**: The first startup takes 10-15 minutes (see below)
5. **Monitor logs**: `make logs`

### ⏳ Model Loading Process

**Important**: The first time vLLM starts, it needs to download and load the model into GPU memory:

- **Download time**: 5-10 minutes (downloading ~13GB Mistral-7B from HuggingFace)
- **Loading time**: 2-5 minutes (loading model weights into GPU memory)
- **Total first startup**: 10-15 minutes typically

**What to expect during first startup:**

```bash
# Check if model is still loading
make logs

# You'll see logs like:
# "Starting to load model mistralai/Mistral-7B-Instruct-v0.3..."
# "Loading weights took 142.89 seconds"
# "Model loading took 13.5084 GiB and 646.147558 seconds"

# API will be ready when you see:
# "Supported_tasks: ['generate']"
```

**Testing API availability:**

```bash
# Check if API is responding (requires auth)
ssh -i ~/.ssh/planfact ubuntu@<GPU_VM_IP> \
  "curl -s -H 'Authorization: Bearer <API_KEY>' http://localhost:8000/v1/models"

# Should return JSON with model info when ready
# Returns {"error":"Unauthorized"} without proper auth
# Times out if model is still loading
```

The vLLM service is pre-configured to:

- Load Mistral-7B-Instruct-v0.3 model by default
- Listen on port 8000 with OpenAI-compatible API
- **Require Bearer token authorization** for API access
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

1. **API timeouts or "Connection refused" errors**:

   **Problem:** `curl` commands timeout or return connection errors when testing vLLM API

   **Cause:** Model is still downloading/loading (especially on first startup)

   **Solution:**

   ```bash
   # Check if vLLM service is running
   make status-services

   # Monitor loading progress
   make logs

   # Look for these key log messages:
   # - "Starting to load model..." (download starting)
   # - "Loading weights took X seconds" (model loaded)
   # - "Supported_tasks: ['generate']" (API ready)

   # Test API only after seeing "Supported_tasks" in logs
   # Use correct port (8000, not 8001) and authorization:
   ssh -i ~/.ssh/planfact ubuntu@<IP> \
     "curl -H 'Authorization: Bearer <API_KEY>' http://localhost:8000/v1/models"
   ```

2. **Network configuration errors** (Missing required argument "network_id"):

   **Problem:** Terraform fails with "Missing required argument" for network_id

   **Solution:** Update network IDs from OBS stack:

   ```bash
   # Get current network IDs from OBS
   cd ../obs/terraform && terraform output obs_network_id obs_subnet_id

   # Update your terraform.tfvars with the output values
   vim terraform/terraform.tfvars
   # Update: obs_network_id = "your_network_id"
   # Update: obs_subnet_id = "your_subnet_id"
   ```

3. **GPU not detected**:

   ```bash
   # Connect to VM and check GPU
   make ssh
   nvidia-smi

   # Or check remotely
   make gpu-info
   ```

4. **Configuration issues**:

   ```bash
   # Check terraform configuration
   make plan

   # Verify current status
   make status
   ```

5. **Service problems**:

   ```bash
   # Check all services
   make status-services

   # View system logs
   make logs

   # Check vLLM logs if running
   make logs
   ```

6. **Network issues**:
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
