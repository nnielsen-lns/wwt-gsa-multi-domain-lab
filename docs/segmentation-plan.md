# Segmentation Plan (Macro + Micro)

## Macro segmentation (VRF)
Global VRFs:
- corp
- iot
- guest
- grt
- infra (transport/global; not an SD-WAN tenant VPN)

## SD-WAN VPN IDs (end-to-end)
- grt   = VPN 900
- corp  = VPN 920
- guest = VPN 930
- iot   = VPN 940

## RD / RT conventions
RD (per-site, per-VRF): <site_asn>:<vpn_id>
RT (global membership): 65000:<vpn_id>

Examples:
- catc-branch-1 (ASN 65020), corp:
  - RD 65020:920
  - RT import/export 65000:920

## EVPN/VXLAN (DC and EVPN domains)
L3VNI convention: 10<vpn_id>
- grt 10900
- corp 10920
- guest 10930
- iot 10940

## Stitching policy (route leaking)
Default: no inter-VRF routing. Stitch only where explicitly required.

Recommended baseline:
- corp <-> grt : allowed (shared services + enterprise services)
- iot  <-> grt : allowed (restricted shared services only; least privilege)
- guest <-> any: not allowed (DIA only), optional exception for DNS/NTP only

Primary stitching point:
- Fusion/border devices (campus/SDA) and/or DC edge

Micro segmentation (SGT/GBP):
- Enforced by ISE + Catalyst Center / SDA policy
- Does not replace macro segmentation; it adds identity-based control within/between segments.
