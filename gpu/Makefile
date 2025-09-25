.PHONY: help init plan apply destroy status clean install deploy config ssh logs

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

status: ## Show Terraform state
	cd terraform && terraform show

output: ## Show terraform outputs
	cd terraform && terraform output

validate: ## Validate Terraform configuration
	cd terraform && terraform validate

fmt: ## Format Terraform files
	cd terraform && terraform fmt -recursive

# Ansible commands
install: ## Install Ansible dependencies
	cd ansible && ansible-galaxy install -r requirements.yml

deploy: ## Deploy GPU services with Ansible
	@if [ -f ansible/inventory.ini ]; then \
		cd ansible && ansible-playbook -i inventory.ini playbooks/site.yml; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

config: ## Run Ansible configuration check
	@if [ -f ansible/inventory.ini ]; then \
		cd ansible && ansible-playbook -i inventory.ini playbooks/site.yml --check --diff; \
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

# Testing and verification
ssh: ## SSH to GPU server
	@if [ -f terraform/terraform.tfstate ]; then \
		cd terraform && terraform output -raw gpu_public_ip | xargs -I {} ssh ubuntu@{}; \
	else \
		echo "Error: No Terraform state found. Run 'make apply' first."; \
		exit 1; \
	fi

logs: ## Show vLLM service logs on remote host
	@if [ -f ansible/inventory.ini ]; then \
		cd ansible && ansible -i inventory.ini gpu -m shell -a "journalctl -u vllm -f --no-pager -n 50"; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

status-services: ## Check service status on remote host
	@if [ -f ansible/inventory.ini ]; then \
		cd ansible && ansible -i inventory.ini gpu -m shell -a "systemctl status vllm node_exporter dcgm-exporter --no-pager"; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

gpu-info: ## Show GPU information
	@if [ -f ansible/inventory.ini ]; then \
		cd ansible && ansible -i inventory.ini gpu -m shell -a "nvidia-smi"; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

# Cleanup commands
clean: ## Clean local Terraform cache
	rm -rf terraform/.terraform
	rm -f terraform/terraform.tfstate.backup

stop-services: ## Stop services on remote host
	@if [ -f ansible/inventory.ini ]; then \
		cd ansible && ansible -i inventory.ini gpu -m shell -a "sudo systemctl stop vllm node_exporter dcgm-exporter"; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

# Full deployment workflow
setup: init install ## Initialize Terraform and install Ansible dependencies

deploy-all: apply deploy ## Deploy infrastructure and configure services

teardown: stop-services destroy ## Stop services and destroy infrastructure

# Development helpers
copy-examples: ## Copy example files for configuration
	cp terraform/terraform.tfvars.example terraform/terraform.tfvars
	@if [ -d ansible ]; then \
		cp ansible/inventory.ini.example ansible/inventory.ini || true; \
	fi

edit-config: ## Edit terraform configuration
	@if [ -f terraform/terraform.tfvars ]; then \
		$$EDITOR terraform/terraform.tfvars; \
	else \
		echo "Error: terraform.tfvars not found. Run 'make copy-examples' first."; \
		exit 1; \
	fi

check-config: ## Validate all configuration files
	cd terraform && terraform validate
	@if [ -f ansible/inventory.ini ]; then \
		cd ansible && ansible-playbook -i inventory.ini playbooks/site.yml --syntax-check; \
	else \
		echo "Ansible configuration will be checked after 'make copy-examples'"; \
	fi

# Observability integration
set-obs-endpoint: ## Set OBS OTLP endpoint in terraform.tfvars from obs stack
	@if [ -f ../obs/terraform/terraform.tfstate ]; then \
		OBS_IP=$$(cd ../obs/terraform && terraform output -raw obs_private_ip); \
		sed -i '' "s/obs_otlp_endpoint = \".*\"/obs_otlp_endpoint = \"$$OBS_IP:4317\"/" terraform/terraform.tfvars; \
		echo "Set obs_otlp_endpoint to $$OBS_IP:4317"; \
	else \
		echo "Error: OBS stack not deployed. Run 'make apply' in ../obs first."; \
		exit 1; \
	fi

test-obs: ## Test OBS connectivity
	@if [ -f ansible/inventory.ini ]; then \
		cd ansible && ansible -i inventory.ini gpu -m shell -a "curl -v telnet://\$$(grep obs_otlp_endpoint ../terraform/terraform.tfvars | cut -d'=' -f2 | tr -d '\" ')"; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi
