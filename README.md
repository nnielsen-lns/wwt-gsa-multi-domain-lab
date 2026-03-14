README.md
# WWT GSA Multi-Domain Lab

This repository contains the infrastructure automation framework used to build and operate the **WWT GSA Multi-Domain Lab**.

The goal of the lab is to simulate real enterprise network architectures across multiple domains while enabling **repeatable automation-driven demos and testing scenarios**.

The lab architecture is built around:

- NetBox (Source of Truth)
- Ansible (Configuration Automation)
- pyATS (Validation / Testing)
- GitHub Actions (CI / Orchestration)
- Proxmox-based infrastructure
- Cisco-based campus network devices

---

# Lab Control Plane

The lab uses several Intel NUC systems that provide the persistent automation and monitoring infrastructure.

| Node | Purpose |
|-----|--------|
| NUC1 | NetBox, Ansible Controller, pyATS |
| NUC2 | GitHub Actions self-hosted runner |
| NUC3 | Grafana monitoring + Windows Domain Controller |
| NUC4 | Network test endpoints / traffic generators |

Physical lab servers remain powered off unless required for larger demo scenarios.

---

# Repository Structure


inventories/ Ansible inventory definitions
playbooks/ Scenario entry-point playbooks
roles/ Reusable Ansible automation roles
scenarios/ Scenario definitions and variables
pyats/ Network validation tests
.github/workflows/ GitHub CI pipelines
scripts/ Helper scripts for operators
docs/ Lab architecture documentation
netbox/ NetBox bootstrap data
automation/ NetBox bootstrap automation


---

# Automation Architecture

The lab follows a structured automation workflow.

```

GitHub
↓
GitHub Actions
↓
Self-hosted Runner (NUC2)
↓
Ansible Controller (NUC1)
↓
Network Devices
↓
pyATS Validation


NetBox acts as the Source of Truth describing the intended architecture.

Scenario Model

Network demonstrations are implemented as scenarios.

Each scenario contains:

scenarios/<scenario_name>/
    vars.yml        scenario variables
    topology.yml    optional topology definition
    tests/          validation tests

Example scenarios:

campus_segmentation

branch_edge

iot_overlay

Current Scenario
Campus Segmentation

This scenario deploys a simple campus segmentation architecture.

Segments:

VLAN	VRF	Purpose
110	CORP	Corporate users
120	GUEST	Guest access
130	IOT	IoT devices
Deploying a Scenario

Use the helper script:

scripts/labctl.sh

Deploy:

./scripts/labctl.sh up campus_segmentation

Validate:

./scripts/labctl.sh validate campus_segmentation

Teardown:

./scripts/labctl.sh down campus_segmentation
GitHub Actions Automation

Scenarios can also be executed through GitHub Actions.

Navigate to:

Actions → Campus Segmentation Demo → Run Workflow

Select:

deploy

validate

teardown

The workflow will run on the self-hosted runner located on NUC2.

pyATS Validation

pyATS provides network validation after deployment.

Example checks:

VLANs exist

SVIs exist

VRFs exist

Access switches have correct VLANs

Run manually:

pyats run job pyats/jobs/campus_segmentation_postcheck_job.py
NetBox Source of Truth

NetBox defines the authoritative network model.

Objects modeled in NetBox include:

Sites

Devices

VRFs

VLANs

Prefix pools

Autonomous systems

Bootstrap configuration is located in:

automation/netbox-bootstrap/
NetBox Tagging Model

Tags are used to associate devices and objects with automation scenarios.

Scenario Tags
scenario-campus-segmentation
scenario-branch-edge
scenario-iot-overlay
Role Tags
role-core
role-access
role-distribution
role-wireless
role-shared-service
Automation Tags
ansible-managed
pyats-validated
demo-ready
baseline
Power / Lifecycle Tags
always-on
on-demand
burst-capacity
Running Automation Locally

Install dependencies:

pip install -r requirements.txt
ansible-galaxy collection install cisco.ios ansible.netcommon

Then run:

ansible-playbook playbooks/campus_segmentation_deploy.yml
Future Enhancements

Planned improvements:

NetBox dynamic inventory integration

Access port automation

ACL policy automation

EVPN/VXLAN scenario

Meraki branch scenario

SD-WAN integration

Automated traffic generation using NUC4

advanced pyATS validation

topology diagrams generated from NetBox

Design Philosophy

This lab is built around several core principles:

Source of Truth first

Automation over manual configuration

Repeatable demo scenarios

Infrastructure as code

Validation before and after change

Author

Nate Nielsen
Principal Solutions Architect
World Wide Technology

# Makefile Shortcuts

This repo includes a Makefile to simplify common lab operations.

## Common commands

```bash
make help
make install
make collections
make deploy-campus
make validate-campus
make pyats-campus
make teardown-campus
make netbox-bootstrap



# WWT GS&A Multi-Domain Lab

## Overview
This repo documents the GS&A enterprise multi-domain lab architecture and provides a NetBox (Community v4.5.2) SoT bootstrap via API.

Includes:
- /16 per site addressing
- Site ASN plan
- VRFs: corp, iot, guest, grt + infra-underlay (global)
- Dual WAN provider model (lab ASNs)
- NetBox data model + YAML inventory
- API bootstrap scripts

## Quick start (NetBox bootstrap)
1) Create a NetBox API token: **Admin → API Tokens**
2) Export env vars and run:

```bash
export NETBOX_URL="https://10.0.20.15"
export NETBOX_TOKEN="REPLACE_ME"

python3 -m venv .venv
source .venv/bin/activate
pip install -r automation/netbox-bootstrap/requirements.txt

# start with dry-run
python automation/netbox-bootstrap/bootstrap_netbox.py --dry-run

# then apply
python automation/netbox-bootstrap/bootstrap_netbox.py --apply

Keep tokens out of Git. Only export tokens in your shell.

Design docs

docs/ip-addressing.md

docs/bgp-asn-plan.md

docs/vrf-strategy.md

docs/wan-architecture.md

docs/netbox-data-model.md
Sites and Ownership
Site	/16 Pool	Owner
dc-1	10.0.0.0/16	nate
meraki-hub-1	10.10.0.0/16	nate
meraki-branch-1	10.11.0.0/16	sam
meraki-branch-2	10.12.0.0/16	nate
meraki-branch-3	10.13.0.0/16	bryan
meraki-branch-4	10.14.0.0/16	roger
meraki-branch-5	10.15.0.0/16	mike
meraki-branch-6	10.16.0.0/16	jenn
meraki-branch-7	10.17.0.0/16	bob
catc-branch-1	10.20.0.0/16	nate
catc-branch-2	10.21.0.0/16	nate

Notes:

dc-1 contains shared services prefix 10.0.20.0/24 (VRF: grt)

Naming conventions: lowercase, hyphen-delimited.

Owner attribution uses owner-* tags in NetBox.
