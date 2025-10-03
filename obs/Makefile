.PHONY: help init plan apply destroy status clean install deploy config vault-create vault-edit vault-view ssh

# Default target
help: ## Show this help message
	@echo "Observability Stack Management"
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

status: ## Show Terraform state and service status
	cd terraform && terraform show
	@if [ -f ansible/inventory.ini ]; then \
		echo "\n=== Service Status ==="; \
		cd ansible && ansible -i inventory.ini obs -m shell -a "cd /opt/obs && docker compose ps"; \
	fi

validate: ## Validate Terraform and Ansible configuration
	cd terraform && terraform validate
	cd ansible && ansible-playbook -i inventory.ini playbooks/site.yml --syntax-check

fmt: ## Format Terraform files
	cd terraform && terraform fmt -recursive

# Ansible commands
install: ## Install Ansible dependencies
	cd ansible && ansible-galaxy install -r requirements.yml

deploy: update-inventory ## Deploy services with Ansible (auto-updates inventory)
	@if [ -f ansible/inventory.ini ]; then \
		cd ansible && ansible-playbook -i inventory.ini playbooks/site.yml; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

update-inventory: ## Update Ansible inventory with current IP from terraform
	@if [ -f terraform/terraform.tfstate ]; then \
		OBS_IP=$$(cd terraform && terraform output -raw obs_public_ip); \
		sed -i '' "s/obs-vm ansible_host=.* /obs-vm ansible_host=$$OBS_IP /" ansible/inventory.ini; \
		echo "Updated inventory.ini with IP: $$OBS_IP"; \
	else \
		echo "Error: terraform.tfstate not found. Deploy infrastructure first with 'make apply'."; \
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

# Vault commands (only essential ones)
vault-create: ## Create new encrypted vault file
	cd ansible && ansible-vault create group_vars/obs/vault.yml

vault-edit: ## Edit encrypted vault file
	cd ansible && ansible-vault edit group_vars/obs/vault.yml

vault-view: ## View encrypted vault file
	cd ansible && ansible-vault view group_vars/obs/vault.yml

# Service management
services: ## Manage services: restart, logs, or stop (usage: make services ACTION=restart|logs|stop)
	@if [ -z "$(ACTION)" ]; then \
		echo "Usage: make services ACTION=restart|logs|stop|status"; \
		exit 1; \
	fi
	@if [ -f ansible/inventory.ini ]; then \
		case "$(ACTION)" in \
			restart) cd ansible && ansible -i inventory.ini obs -m shell -a "cd /opt/obs && docker compose restart";; \
			logs) cd ansible && ansible -i inventory.ini obs -m shell -a "cd /opt/obs && docker compose logs -f --tail=50";; \
			stop) cd ansible && ansible -i inventory.ini obs -m shell -a "cd /opt/obs && docker compose down";; \
			status) cd ansible && ansible -i inventory.ini obs -m shell -a "cd /opt/obs && docker compose ps";; \
			*) echo "Invalid action. Use: restart, logs, stop, or status";; \
		esac; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

ssh: ## SSH to obs server
	@if [ -f terraform/terraform.tfstate ]; then \
		cd terraform && terraform output -raw obs_public_ip | xargs -I {} ssh ubuntu@{}; \
	else \
		echo "Error: No Terraform state found. Run 'make apply' first."; \
		exit 1; \
	fi

# Cleanup commands
clean: ## Clean local Terraform and Ansible cache
	rm -rf terraform/.terraform
	rm -rf ansible/collections
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
	cp ansible/inventory.ini.example ansible/inventory.ini
