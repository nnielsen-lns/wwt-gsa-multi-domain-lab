#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 2 ]; then
  echo "Usage: $0 {up|validate|down} <scenario>"
  exit 1
fi

ACTION="$1"
SCENARIO="$2"

case "$ACTION" in
  up)
    ansible-playbook "playbooks/${SCENARIO}_deploy.yml"
    ;;
  validate)
    ansible-playbook "playbooks/${SCENARIO}_validate.yml"
    ;;
  down)
    ansible-playbook "playbooks/${SCENARIO}_teardown.yml"
    ;;
  *)
    echo "Invalid action: ${ACTION}"
    exit 1
    ;;
esac
