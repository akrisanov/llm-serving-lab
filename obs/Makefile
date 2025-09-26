.PHONY: help init plan apply destroy status clean install deploy config vault-create vault-edit vault-view test ssh

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

status: ## Show Terraform state
	cd terraform && terraform show

validate: ## Validate Terraform configuration
	cd terraform && terraform validate

fmt: ## Format Terraform files
	cd terraform && terraform fmt -recursive

# Ansible commands
install: ## Install Ansible dependencies
	cd ansible && ansible-galaxy install -r requirements.yml

deploy: ## Deploy services with Ansible
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

facts: ## Gather facts from hosts
	cd ansible && ansible -i inventory.ini all -m setup

# Vault commands
vault-create: ## Create new encrypted vault file
	cd ansible && ansible-vault create group_vars/obs/vault.yml

vault-edit: ## Edit encrypted vault file
	cd ansible && ansible-vault edit group_vars/obs/vault.yml

vault-view: ## View encrypted vault file
	cd ansible && ansible-vault view group_vars/obs/vault.yml

vault-encrypt: ## Encrypt existing vault file
	cd ansible && ansible-vault encrypt group_vars/obs/vault.yml

vault-decrypt: ## Decrypt vault file
	cd ansible && ansible-vault decrypt group_vars/obs/vault.yml

vault-password: ## Create vault password file for automatic authentication
	@read -s -p "Enter vault password: " password; \
	echo; \
	echo "$$password" > ansible/group_vars/.vault_pass; \
	chmod 600 ansible/group_vars/.vault_pass; \
	echo "Vault password file created at ansible/group_vars/.vault_pass"

# Testing and verification
test: ## Run connectivity and service tests
	cd ansible && ansible-playbook -i inventory.ini playbooks/site.yml --tags verify

ssh: ## SSH to obs server
	@if [ -f terraform/terraform.tfstate ]; then \
		cd terraform && terraform output -raw obs_vm_ip | xargs -I {} ssh ubuntu@{}; \
	else \
		echo "Error: No Terraform state found. Run 'make apply' first."; \
		exit 1; \
	fi

logs: ## Show service logs on remote host
	@if [ -f ansible/inventory.ini ]; then \
		cd ansible && ansible -i inventory.ini obs -m shell -a "cd /opt/obs && docker compose logs"; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

status-services: ## Check service status on remote host
	@if [ -f ansible/inventory.ini ]; then \
		cd ansible && ansible -i inventory.ini obs -m shell -a "cd /opt/obs && docker compose ps"; \
	else \
		echo "Error: inventory.ini not found. Run 'make copy-examples' and configure it first."; \
		exit 1; \
	fi

# Cleanup commands
clean: ## Clean local Terraform and Ansible cache
	rm -rf terraform/.terraform
	rm -rf ansible/collections
	rm -f terraform/terraform.tfstate.backup

clean-remote: ## Stop and remove services on remote host
	cd ansible && ansible -i inventory.ini obs -m shell -a "cd /opt/obs && docker compose down -v"

# Full deployment workflow
setup: init install ## Initialize Terraform and install Ansible dependencies

deploy-all: apply deploy ## Deploy infrastructure and configure services

teardown: clean-remote destroy ## Stop services and destroy infrastructure

# Development helpers
copy-examples: ## Copy example files for configuration
	cp terraform/terraform.tfvars.example terraform/terraform.tfvars
	cp ansible/inventory.ini.example ansible/inventory.ini

check-config: ## Validate all configuration files
	cd terraform && terraform validate
	cd ansible && ansible-playbook -i inventory.ini playbooks/site.yml --syntax-check
