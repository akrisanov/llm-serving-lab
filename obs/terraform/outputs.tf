output "obs_public_ip" { value = yandex_compute_instance.obs_vm.network_interface[0].nat_ip_address }
output "obs_private_ip" { value = yandex_compute_instance.obs_vm.network_interface[0].ip_address }
output "ssh_user" { value = var.ssh_user }

# Network outputs for GPU VM to use same network
output "obs_network_id" { value = yandex_vpc_network.obs_net.id }
output "obs_subnet_id" { value = yandex_vpc_subnet.obs_subnet.id }
