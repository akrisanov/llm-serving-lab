variable "yc_token" { type = string }
variable "yc_cloud_id" { type = string }
variable "yc_folder_id" { type = string }
variable "yc_zone" {
  type    = string
  default = "ru-central1-a"
}

variable "obs_vm_name" {
  type    = string
  default = "obs-vm"
}
variable "obs_cidr" {
  type    = string
  default = "10.128.0.0/24"
}

# Allow admin access to Grafana/ClickHouse from this CIDR (e.g., your home/VPN)
variable "admin_cidr" { type = string }

# Allow OTLP from GPU VM (or its CIDR)
variable "gpu_vm_cidr" { type = string }

# VM sizing
variable "obs_cores" {
  type    = number
  default = 8
}
variable "obs_memory_gb" {
  type    = number
  default = 32
}
variable "disk_size_gb" {
  type    = number
  default = 200
}

# SSH
variable "ssh_user" {
  type    = string
  default = "ubuntu"
}
variable "ssh_pubkey" { type = string } # contents of your ~/.ssh/id_rsa.pub

# Grafana/ClickHouse creds
variable "ch_user" {
  type    = string
  default = "otel"
}
variable "ch_password" {
  type      = string
  sensitive = true
}
variable "ch_db" {
  type    = string
  default = "otel_metrics"
}
variable "grafana_admin_user" {
  type    = string
  default = "admin"
}
variable "grafana_admin_password" {
  type      = string
  sensitive = true
}
