.PHONY: help init plan apply destroy status clean install deploy config ssh

# Default target
help: ## Show this help message
	@echo "GPU VM Management"
	@echo "Usage: make <target>"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# Terraform commands
init: ## Initialize Terraform
	cd terraform && terraform init

plan: ## Show Terraform execution plan
	@if [ -f terraform/terraform.tfvars ]; then \
		cd terraform && terraform plan; \
	else \
		echo "Error: terraform.tfvars not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

apply: ## Apply Terraform configuration
	@if [ -f terraform/terraform.tfvars ]; then \
		cd terraform && terraform apply; \
	else \
		echo "Error: terraform.tfvars not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

destroy: ## Destroy Terraform infrastructure
	cd terraform && terraform destroy

status: ## Show Terraform state, services status and GPU info
	cd terraform && terraform show
	@if [ -f ansible/inventory.ini ]; then \
		echo "\n=== Services Status ==="; \
		cd ansible && ansible -i inventory.ini gpu -m shell -a "systemctl status vllm metrics-exporter --no-pager -l"; \
		echo "\n=== GPU Information ==="; \
		cd ansible && ansible -i inventory.ini gpu -m shell -a "nvidia-smi"; \
	fi

validate: ## Validate Terraform and Ansible configuration
	cd terraform && terraform validate
	@if [ -f ansible/inventory.ini ]; then \
		cd ansible && ansible-playbook -i inventory.ini playbooks/site.yml --syntax-check; \
	else \
		echo "Ansible configuration will be checked after 'make copy-examples'"; \
	fi

fmt: ## Format Terraform files
	cd terraform && terraform fmt -recursive

# Ansible commands
install: ## Install Ansible dependencies
	cd ansible && ansible-galaxy install -r requirements.yml

deploy: set-obs-endpoint update-inventory ## Deploy GPU services with Ansible (auto-updates all config)
	@if [ -f ansible/inventory.ini ]; then \
		OBS_IP=$$(cd ../obs/terraform && terraform output -raw obs_private_ip); \
		cd ansible && OBS_VM_INTERNAL_IP=$$OBS_IP ansible-playbook -i inventory.ini playbooks/site.yml; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

update-inventory: ## Update Ansible inventory with current IPs from terraform
	@if [ -f terraform/terraform.tfstate ]; then \
		GPU_IP=$$(cd terraform && terraform output -raw gpu_public_ip); \
		OBS_IP=$$(cd ../obs/terraform && terraform output -raw obs_private_ip); \
		sed -i '' "s/gpu-vm ansible_host=.* /gpu-vm ansible_host=$$GPU_IP /" ansible/inventory.ini; \
		sed -i '' "s/obs_otlp_endpoint=.*/obs_otlp_endpoint=$$OBS_IP:4317/" ansible/inventory.ini; \
		echo "Updated inventory.ini with GPU IP: $$GPU_IP, OBS IP: $$OBS_IP"; \
	else \
		echo "Error: terraform.tfstate not found. Deploy infrastructure first with 'make apply'."; \
		exit 1; \
	fi

config: set-obs-endpoint ## Run Ansible configuration check
	@if [ -f ansible/inventory.ini ]; then \
		OBS_IP=$$(cd ../obs/terraform && terraform output -raw obs_private_ip); \
		cd ansible && OBS_VM_INTERNAL_IP=$$OBS_IP ansible-playbook -i inventory.ini playbooks/site.yml --check --diff; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

ping: ## Test connectivity to hosts
	@if [ -f ansible/inventory.ini ]; then \
		cd ansible && ansible -i inventory.ini all -m ping; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

# Service management
services: ## Manage services: vllm-logs, metrics-logs, restart-metrics, stop (usage: make services ACTION=vllm-logs|metrics-logs|restart-metrics|stop)
	@if [ -z "$(ACTION)" ]; then \
		echo "Usage: make services ACTION=vllm-logs|metrics-logs|restart-metrics|stop"; \
		exit 1; \
	fi
	@if [ -f ansible/inventory.ini ]; then \
		case "$(ACTION)" in \
			vllm-logs) cd ansible && ansible -i inventory.ini gpu -m shell -a "journalctl -u vllm -f --no-pager -n 50";; \
			metrics-logs) cd ansible && ansible -i inventory.ini gpu -m shell -a "journalctl -u metrics-exporter -f --no-pager -n 20";; \
			restart-metrics) cd ansible && ansible -i inventory.ini gpu -m shell -a "sudo systemctl restart metrics-exporter.service" --vault-password-file vault/.vault_pass;; \
			stop) cd ansible && ansible -i inventory.ini gpu -m shell -a "sudo systemctl stop vllm node_exporter dcgm-exporter";; \
			*) echo "Invalid action. Use: vllm-logs, metrics-logs, restart-metrics, or stop";; \
		esac; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

ssh: ## SSH to GPU server
	@if [ -f terraform/terraform.tfstate ]; then \
		cd terraform && terraform output -raw gpu_public_ip | xargs -I {} ssh ubuntu@{}; \
	else \
		echo "Error: No Terraform state found. Run 'make apply' first."; \
		exit 1; \
	fi

# Cleanup commands
clean: ## Clean local Terraform cache
	rm -rf terraform/.terraform
	rm -f terraform/terraform.tfstate.backup

# Full deployment workflow
setup: init install ## Initialize Terraform and install Ansible dependencies
deploy-all: apply deploy ## Deploy infrastructure and configure services
teardown: ## Stop services and destroy infrastructure (usage: make teardown ACTION=stop followed by make destroy)
	@echo "First stop services with: make services ACTION=stop"
	@echo "Then destroy infrastructure with: make destroy"

# Development helpers
copy-examples: ## Copy example files for configuration
	cp terraform/terraform.tfvars.example terraform/terraform.tfvars
	@if [ -d ansible ]; then \
		cp ansible/inventory.ini.example ansible/inventory.ini || true; \
		cp ansible/vault/vault.yml.example ansible/vault/vault.yml || true; \
		echo "Remember to encrypt vault file with: make vault-create"; \
	fi

# Observability integration
set-obs-endpoint: ## Set OBS network config in terraform.tfvars from obs stack
	@if [ -f ../obs/terraform/terraform.tfstate ]; then \
		OBS_IP=$$(cd ../obs/terraform && terraform output -raw obs_private_ip); \
		OBS_NETWORK_ID=$$(cd ../obs/terraform && terraform output -raw obs_network_id); \
		OBS_SUBNET_ID=$$(cd ../obs/terraform && terraform output -raw obs_subnet_id); \
		OBS_SUBNET_CIDR=$$(cd ../obs/terraform && terraform output -raw obs_subnet_cidr); \
		sed -i '' "s/obs_otlp_endpoint = \".*\"/obs_otlp_endpoint = \"$$OBS_IP:4317\"/" terraform/terraform.tfvars; \
		sed -i '' "s/obs_network_id = \".*\"/obs_network_id = \"$$OBS_NETWORK_ID\"/" terraform/terraform.tfvars; \
		sed -i '' "s/obs_subnet_id = \".*\"/obs_subnet_id = \"$$OBS_SUBNET_ID\"/" terraform/terraform.tfvars; \
		sed -i '' "s/obs_subnet_cidr = \".*\"/obs_subnet_cidr = \"$$OBS_SUBNET_CIDR\"/" terraform/terraform.tfvars; \
		echo "Set OBS network config: IP=$$OBS_IP:4317, CIDR=$$OBS_SUBNET_CIDR"; \
	else \
		echo "Error: OBS stack not deployed. Run 'make apply' in ../obs first."; \
		exit 1; \
	fi

test-obs: ## Test OBS connectivity
	@if [ -f ansible/inventory.ini ]; then \
		OBS_ENDPOINT=$$(grep obs_otlp_endpoint terraform/terraform.tfvars | cut -d'=' -f2 | tr -d '\" '); \
		echo "Testing connectivity to OBS: $$OBS_ENDPOINT"; \
		cd ansible && ansible -i inventory.ini gpu -m shell -a "nc -zv \$$(echo $$OBS_ENDPOINT | cut -d: -f1) \$$(echo $$OBS_ENDPOINT | cut -d: -f2)"; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi


# Vault commands (only essential ones)
vault-create: ## Create new encrypted vault file
	cd ansible && ansible-vault create vault/vault.yml

vault-edit: ## Edit encrypted vault file
	cd ansible && ansible-vault edit vault/vault.yml

vault-view: ## View encrypted vault file
	cd ansible && ansible-vault view vault/vault.yml
