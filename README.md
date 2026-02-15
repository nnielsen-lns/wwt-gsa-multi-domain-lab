# GS&A Enterprise Network Architecture Lab

## Overview

This repository documents the GS&A enterprise multi-domain lab architecture.

The purpose of this repository is to provide:

- Deterministic IP addressing design
- Structured BGP ASN allocation
- Multi-VRF macro segmentation model
- Dual WAN architecture strategy
- NetBox (Community v4.5.2) Source-of-Truth data model
- Clear ownership mapping across GS&A team members

This repository serves as both:
- Architectural documentation
- Version-controlled design reference
- Foundation for automation and infrastructure-as-code

---

## Design Principles

- Each site receives a unique /16 prefix
- One ASN per site derived from its /16
- Campus underlay uses IGP (OSPF/IS-IS)
- WAN connectivity uses eBGP to dual providers
- Internal ASNs (if required) must never leak over WAN
- VRF segmentation is consistent across sites
- NetBox is the authoritative source of truth

---

## Sites and Ownership

### Data Center
- dc-1 → 10.0.0.0/16 — owner: nate

### Meraki
- meraki-hub-1 → 10.10.0.0/16 — owner: nate
- meraki-branch-1 → 10.11.0.0/16 — owner: sam
- meraki-branch-2 → 10.12.0.0/16 — owner: nate
- meraki-branch-3 → 10.13.0.0/16 — owner: bryan
- meraki-branch-4 → 10.14.0.0/16 — owner: roger
- meraki-branch-5 → 10.15.0.0/16 — owner: mike
- meraki-branch-6 → 10.16.0.0/16 — owner: jenn
- meraki-branch-7 → 10.17.0.0/16 — owner: bob

### Catalyst Center
- catc-branch-1 → 10.20.0.0/16 — owner: nate
- catc-branch-2 → 10.21.0.0/16 — owner: nate

---

## Core Design Documents

- [IP Addressing Plan](docs/ip-addressing.md)
- [BGP ASN Plan](docs/bgp-asn-plan.md)
- [VRF Strategy](docs/vrf-strategy.md)
- [WAN Architecture](docs/wan-architecture.md)
- [NetBox Data Model](docs/netbox-data-model.md)

---

## Future Enhancements

- Automated NetBox provisioning from YAML
- Config generation (Ansible / Terraform)
- EVPN VNI & Route-Target standardization
- Policy validation via pyATS
