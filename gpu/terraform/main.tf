locals {
  name_prefix = "gpu-vm"
  labels = {
    project = "llm-serving-lab"
    role    = "gpu"
  }
  platform_id = var.gpu_type == "a100" ? "gpu-standard-v3" : "standard-v3-t4i"
  gpu_count   = 1
}

data "yandex_compute_image" "gpu_ubuntu" {
  family    = var.image_family
  folder_id = "standard-images" # Public images folder
}

# Use existing OBS network and subnet
data "yandex_vpc_network" "obs_net" {
  network_id = var.obs_network_id
}

data "yandex_vpc_subnet" "obs_subnet" {
  subnet_id = var.obs_subnet_id
}

resource "yandex_vpc_security_group" "sg" {
  name       = "${local.name_prefix}-sg"
  network_id = data.yandex_vpc_network.obs_net.id
  labels     = local.labels

  # egress: all outbound traffic
  egress {
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
    description    = "Allow all egress"
  }

  # SSH from your IP
  ingress {
    protocol       = "TCP"
    port           = 22
    v4_cidr_blocks = [var.my_ip]
    description    = "SSH"
  }

  # vLLM OpenAI API only from your IP
  ingress {
    protocol       = "TCP"
    port           = var.vllm_port
    v4_cidr_blocks = [var.my_ip]
    description    = "vLLM OpenAI API"
  }

  # Allow ICMP (ping) from internal subnet
  ingress {
    protocol       = "ICMP"
    v4_cidr_blocks = ["10.128.0.0/24"]
    description    = "ICMP from internal subnet"
  }

  # Allow metrics exporter from internal subnet
  ingress {
    protocol       = "TCP"
    port           = 9090
    v4_cidr_blocks = ["10.128.0.0/24"]
    description    = "Metrics exporter from internal subnet"
  }
}

resource "yandex_compute_instance" "gpu" {
  name        = local.name_prefix
  platform_id = local.platform_id
  zone        = var.yc_zone
  labels      = local.labels

  resources {
    cores         = var.cores
    memory        = var.memory_gb
    core_fraction = 100
    gpus          = local.gpu_count
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.gpu_ubuntu.id
      size     = var.disk_gb
      type     = "network-ssd"
    }
  }

  network_interface {
    subnet_id          = data.yandex_vpc_subnet.obs_subnet.id
    nat                = true
    security_group_ids = [yandex_vpc_security_group.sg.id]
  }

  metadata = {
    ssh-keys  = "${var.vm_user}:${var.ssh_public_key}"
    user-data = <<-CLOUDCFG
      #cloud-config
      package_update: true
      package_upgrade: false
      users:
        - name: ${var.vm_user}
          groups: [sudo, docker]
          shell: /bin/bash
          sudo: ['ALL=(ALL) NOPASSWD:ALL']
      write_files:
        - path: /etc/llm_env
          permissions: "0644"
          owner: root:root
          content: |
            OBS_OTLP_ENDPOINT=${var.obs_otlp_endpoint}
            VLLM_PORT=${var.vllm_port}
      runcmd:
        - [ bash, -lc, "apt-get update -y" ]
        - [ bash, -lc, "apt-get install -y python3-venv python3-pip git curl" ]
        - [ bash, -lc, "mkdir -p /opt/llm && chown ${var.vm_user}:${var.vm_user} /opt/llm" ]
    CLOUDCFG
  }
}
