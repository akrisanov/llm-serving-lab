output "gpu_public_ip" {
  value = yandex_compute_instance.gpu.network_interface[0].nat_ip_address
}

output "gpu_internal_ip" {
  value = yandex_compute_instance.gpu.network_interface[0].ip_address
}
