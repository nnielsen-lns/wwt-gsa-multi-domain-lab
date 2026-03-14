.PHONY: help install collections deploy-campus validate-campus validate-campus-full \
        pyats-campus teardown-campus netbox-bootstrap lint tree \
        github-runner-status git-status git-add git-commit git-push \
        show-env check-env

# Optional local environment file
# Example .env:
# ANSIBLE_USER=admin
# ANSIBLE_PASSWORD=changeme
# NETBOX_URL=http://netbox.local
# NETBOX_TOKEN=supersecrettoken
-include .env
export

PYTHON ?= python3
PIP ?= pip3
ANSIBLE ?= ansible-playbook
PYATS ?= pyats
INVENTORY ?= inventories/production/hosts.yml
SCENARIO ?= campus_segmentation
RUNNER_DIR ?= /opt/actions-runner

help:
	@echo ""
	@echo "WWT GSA Multi-Domain Lab Make Targets"
	@echo ""
	@echo "Setup:"
	@echo "  make install                 Install Python dependencies"
	@echo "  make collections            Install required Ansible collections"
	@echo "  make check-env              Show whether common env vars are set"
	@echo "  make show-env               Print current tool and path variables"
	@echo ""
	@echo "Campus scenario:"
	@echo "  make deploy-campus          Deploy campus segmentation scenario"
	@echo "  make validate-campus        Run Ansible validation"
	@echo "  make pyats-campus           Run pyATS postcheck"
	@echo "  make validate-campus-full   Run Ansible + pyATS validation"
	@echo "  make teardown-campus        Tear down campus segmentation scenario"
	@echo ""
	@echo "NetBox:"
	@echo "  make netbox-bootstrap       Run NetBox bootstrap loader"
	@echo ""
	@echo "Quality checks:"
	@echo "  make lint                   Syntax check playbooks"
	@echo "  make tree                   Show top-level repo structure"
	@echo ""
	@echo "Git helpers:"
	@echo "  make git-status             Show git status"
	@echo "  make git-add                git add ."
	@echo "  make git-commit MSG='...'   Commit with message"
	@echo "  make git-push               Push current branch"
	@echo ""
	@echo "Runner:"
	@echo "  make github-runner-status   Check self-hosted runner directory/service"
	@echo ""

install:
	$(PIP) install -r requirements.txt

collections:
	ansible-galaxy collection install cisco.ios ansible.netcommon

deploy-campus:
	$(ANSIBLE) -i $(INVENTORY) playbooks/campus_segmentation_deploy.yml

validate-campus:
	$(ANSIBLE) -i $(INVENTORY) playbooks/campus_segmentation_validate.yml

pyats-campus:
	$(PYATS) run job pyats/jobs/campus_segmentation_postcheck_job.py

validate-campus-full: validate-campus pyats-campus

teardown-campus:
	$(ANSIBLE) -i $(INVENTORY) playbooks/campus_segmentation_teardown.yml

netbox-bootstrap:
	$(PYTHON) automation/netbox-bootstrap/bootstrap_netbox.py

lint:
	$(ANSIBLE) -i $(INVENTORY) playbooks/campus_segmentation_deploy.yml --syntax-check
	$(ANSIBLE) -i $(INVENTORY) playbooks/campus_segmentation_validate.yml --syntax-check
	$(ANSIBLE) -i $(INVENTORY) playbooks/campus_segmentation_teardown.yml --syntax-check

tree:
	@echo "inventories/"
	@echo "playbooks/"
	@echo "roles/"
	@echo "scenarios/"
	@echo "pyats/"
	@echo ".github/workflows/"
	@echo "scripts/"
	@echo "docs/"
	@echo "netbox/"
	@echo "automation/"

show-env:
	@echo "PYTHON=$(PYTHON)"
	@echo "PIP=$(PIP)"
	@echo "ANSIBLE=$(ANSIBLE)"
	@echo "PYATS=$(PYATS)"
	@echo "INVENTORY=$(INVENTORY)"
	@echo "SCENARIO=$(SCENARIO)"
	@echo "RUNNER_DIR=$(RUNNER_DIR)"
	@echo "NETBOX_URL=$${NETBOX_URL:-<unset>}"
	@echo "NETBOX_TOKEN=$${NETBOX_TOKEN:+<set>}"
	@echo "ANSIBLE_USER=$${ANSIBLE_USER:-<unset>}"
	@echo "ANSIBLE_PASSWORD=$${ANSIBLE_PASSWORD:+<set>}"

check-env:
	@echo "Checking common environment variables..."
	@sh -c ' \
	[ -n "$$ANSIBLE_USER" ] && echo "ANSIBLE_USER: set" || echo "ANSIBLE_USER: unset"; \
	[ -n "$$ANSIBLE_PASSWORD" ] && echo "ANSIBLE_PASSWORD: set" || echo "ANSIBLE_PASSWORD: unset"; \
	[ -n "$$NETBOX_URL" ] && echo "NETBOX_URL: set" || echo "NETBOX_URL: unset"; \
	[ -n "$$NETBOX_TOKEN" ] && echo "NETBOX_TOKEN: set" || echo "NETBOX_TOKEN: unset"; \
	'

git-status:
	git status

git-add:
	git add .

git-commit:
	@if [ -z "$(MSG)" ]; then \
		echo "Usage: make git-commit MSG='your commit message'"; \
		exit 1; \
	fi
	git commit -m "$(MSG)"

git-push:
	git push

github-runner-status:
	@echo "Checking GitHub Actions runner..."
	@if [ -d "$(RUNNER_DIR)" ]; then \
		echo "Runner directory exists: $(RUNNER_DIR)"; \
	else \
		echo "Runner directory not found: $(RUNNER_DIR)"; \
	fi
	@if command -v systemctl >/dev/null 2>&1; then \
		systemctl --no-pager --full status actions.runner.* 2>/dev/null || echo "No runner systemd service found"; \
	else \
		echo "systemctl not available on this host"; \
	fi
