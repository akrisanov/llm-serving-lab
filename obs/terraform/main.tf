data "yandex_compute_image" "ubuntu" {
  family = "ubuntu-2204-lts"
}

resource "yandex_vpc_network" "obs_net" {
  name = "obs-net"
}

resource "yandex_vpc_subnet" "obs_subnet" {
  name           = "obs-subnet"
  zone           = var.yc_zone
  network_id     = yandex_vpc_network.obs_net.id
  v4_cidr_blocks = [var.obs_cidr]
}

# Security group
resource "yandex_vpc_security_group" "obs_sg" {
  name        = "obs-sg"
  network_id  = yandex_vpc_network.obs_net.id
  description = "Allow SSH from admin, Grafana/CH from admin, OTLP from GPU VM"

  ingress {
    protocol       = "TCP"
    description    = "SSH from admin"
    port           = 22
    v4_cidr_blocks = [var.admin_cidr]
  }

  # Grafana 3000 -> from admin only
  ingress {
    protocol       = "TCP"
    description    = "Grafana from admin"
    port           = 3000
    v4_cidr_blocks = [var.admin_cidr]
  }

  # Jupyter 8888 -> from admin only
  ingress {
    protocol       = "TCP"
    description    = "Jupyter from admin"
    port           = 8888
    v4_cidr_blocks = [var.admin_cidr]
  }

  # ClickHouse HTTP 8123 -> from admin only
  ingress {
    protocol       = "TCP"
    description    = "CH HTTP from admin"
    port           = 8123
    v4_cidr_blocks = [var.admin_cidr]
  }

  # ClickHouse native 9000 -> from admin only (optional)
  ingress {
    protocol       = "TCP"
    description    = "CH native from admin"
    port           = 9000
    v4_cidr_blocks = [var.admin_cidr]
  }

  # OTLP gRPC 4317 + HTTP 4318 -> from GPU VM/CIDR
  ingress {
    protocol       = "TCP"
    description    = "OTLP gRPC from GPU VM"
    port           = 4317
    v4_cidr_blocks = [var.gpu_vm_cidr]
  }
  ingress {
    protocol       = "TCP"
    description    = "OTLP HTTP from GPU VM"
    port           = 4318
    v4_cidr_blocks = [var.gpu_vm_cidr]
  }

  # ICMP (ping) from internal subnet
  ingress {
    protocol       = "ICMP"
    description    = "ICMP from internal subnet"
    v4_cidr_blocks = [var.obs_cidr]
  }

  egress {
    protocol       = "ANY"
    description    = "all egress"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

# Cloud-init: prepare for Ansible (python, apt updates)
locals {
  cloud_init = <<-EOF
  #cloud-config
  package_update: true
  packages:
    - python3
    - python3-apt
    - curl
    - ca-certificates
  users:
    - name: ${var.ssh_user}
      sudo: ALL=(ALL) NOPASSWD:ALL
      groups: sudo
      shell: /bin/bash
      ssh_authorized_keys:
        - ${var.ssh_pubkey}
  EOF
}

resource "yandex_compute_instance" "obs_vm" {
  name        = var.obs_vm_name
  platform_id = "standard-v3"
  zone        = var.yc_zone

  resources {
    cores         = var.obs_cores
    memory        = var.obs_memory_gb
    core_fraction = 100
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = var.disk_size_gb
      type     = "network-ssd"
    }
  }

  network_interface {
    subnet_id          = yandex_vpc_subnet.obs_subnet.id
    nat                = true
    security_group_ids = [yandex_vpc_security_group.obs_sg.id]
  }

  metadata = {
    user-data = local.cloud_init
    ssh-keys  = "${var.ssh_user}:${var.ssh_pubkey}"
  }
}
