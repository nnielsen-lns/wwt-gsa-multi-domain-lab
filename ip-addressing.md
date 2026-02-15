# IP Addressing Plan

## Design Principles

- Each site receives a dedicated /16.
- No overlapping space.
- VRF segmentation carved inside each /16.
- DC shared services reside inside dc-1 grt pool.

## DC-1

10.0.0.0/16

Shared services:
10.0.20.0/24 (VRF: grt)

## Site Pools

10.10.0.0/16 → meraki-hub-1
10.11.0.0/16 → meraki-branch-1
10.12.0.0/16 → meraki-branch-2
10.13.0.0/16 → meraki-branch-3
10.14.0.0/16 → meraki-branch-4
10.15.0.0/16 → meraki-branch-5
10.16.0.0/16 → meraki-branch-6
10.17.0.0/16 → meraki-branch-7
10.20.0.0/16 → catc-branch-1
10.21.0.0/16 → catc-branch-2
