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
