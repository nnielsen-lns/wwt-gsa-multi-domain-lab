# NetBox Tagging Model

## Scenario Tags
- scenario-campus-segmentation
- scenario-branch-edge
- scenario-iot-overlay

## Functional Role Tags
- role-core
- role-access
- role-distribution
- role-wireless
- role-shared-service
- role-test-endpoint

## Automation Tags
- ansible-managed
- pyats-validated
- demo-ready
- baseline

## Power / Lifecycle Tags
- always-on
- on-demand
- burst-capacity

## Interface Custom Field
intent_role:
- uplink
- access-corp
- access-guest
- access-iot
- trunk
- mgmt
- test-endpoint

## Device Custom Fields
scenario_default:
- campus_segmentation
- branch_edge
- none

validation_profile:
- campus_basic
- branch_basic
- none

power_profile:
- always_on
- on_demand
