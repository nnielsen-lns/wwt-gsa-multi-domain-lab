
IP Addressing Plan
Principles

Each site gets a unique /16 (no overlaps).

VRFs are consistent end-to-end (corp/iot/guest/grt), but prefixes are unique per site.

infra-underlay is modeled in the global routing table (VRF=None) using a Prefix Role.

dc-1 is anchored at 10.0.0.0/16 to preserve shared services 10.0.20.0/24.

Site pools (/16)

dc-1 → 10.0.0.0/16

meraki-hub-1 → 10.10.0.0/16

meraki-branch-1 → 10.11.0.0/16

meraki-branch-2 → 10.12.0.0/16

meraki-branch-3 → 10.13.0.0/16

meraki-branch-4 → 10.14.0.0/16

meraki-branch-5 → 10.15.0.0/16

meraki-branch-6 → 10.16.0.0/16

meraki-branch-7 → 10.17.0.0/16

catc-branch-1 → 10.20.0.0/16

catc-branch-2 → 10.21.0.0/16

Shared services (dc-1)

10.0.20.0/24 (VRF: grt)

VRF carving template (branch sites 10.X.0.0/16)

corp = 10.X.0.0/17

iot = 10.X.128.0/18

guest = 10.X.192.0/19

grt = 10.X.224.0/19

infra-underlay (global) = 10.X.248.0/20

DC exception: dc-1 uses a special carve to keep 10.0.20.0/24 inside grt.
See netbox/prefixes.yaml for authoritative allocations.
