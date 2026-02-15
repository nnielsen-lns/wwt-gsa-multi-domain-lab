
BGP ASN Plan
Provider ASNs (lab)

sp-a: 64520

sp-b: 64530

Site ASN rule

Non-DC sites: ASN = 65000 + second octet of the site /16

Example: 10.21.0.0/16 → ASN 65021

DC exception:

dc-1 (10.0.0.0/16) → ASN 65001

Site ASNs

dc-1 → 65001
meraki-hub-1 → 65010
meraki-branch-1 → 65011
meraki-branch-2 → 65012
meraki-branch-3 → 65013
meraki-branch-4 → 65014
meraki-branch-5 → 65015
meraki-branch-6 → 65016
meraki-branch-7 → 65017
catc-branch-1 → 65020
catc-branch-2 → 65021

Policy

Each site peers eBGP to both providers using the site ASN.

Campus underlay uses IGP (OSPF/IS-IS).

Any internal-only ASNs (if ever required) must not be exported across WAN.
