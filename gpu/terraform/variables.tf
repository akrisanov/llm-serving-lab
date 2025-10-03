variable "yc_token" { type = string }
variable "yc_cloud_id" { type = string }
variable "yc_folder_id" { type = string }
variable "yc_zone" {
  type    = string
  default = "ru-central1-b"
}

# Security & networking

variable "my_ip" {
  type        = string
  description = "x.x.x.x/32"
}

# OBS network integration
variable "obs_network_id" {
  type        = string
  description = "ID of existing OBS VPC network"
}

variable "obs_subnet_id" {
  type        = string
  description = "ID of existing OBS subnet"
}

variable "obs_subnet_cidr" {
  type        = string
  description = "CIDR block of OBS subnet for security group rules"
}

variable "vm_user" {
  type    = string
  default = "ubuntu"
}

variable "ssh_public_key" { type = string }

# GPU settings
variable "gpu_type" {
  type    = string
  default = "t4i"
  validation {
    condition     = contains(["t4i", "a100"], var.gpu_type)
    error_message = "gpu_type should be 't4i' or 'a100'."
  }
}

# vCPU / RAM / Диск
variable "cores" {
  type    = number
  default = 8
}
variable "memory_gb" {
  type    = number
  default = 32
}
variable "disk_gb" {
  type    = number
  default = 200
}

# VM image
variable "image_family" {
  type    = string
  default = "ubuntu-2204-lts-cuda-12-2"
}

# endpoint OTLP gRPC to Obs VM
variable "obs_otlp_endpoint" {
  type        = string
  description = "OTLP gRPC endpoint (host:port) for sending metrics to the Obs VM"
}

# Service ports
# Which port to use for vLLM OpenAI API on GPU VM
variable "vllm_port" {
  type    = number
  default = 8000
}
