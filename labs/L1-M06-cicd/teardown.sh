#!/usr/bin/env bash
# Removes everything setup.sh created.
set -euo pipefail
kind delete cluster --name m06-lab
docker rm -f registry.lab >/dev/null 2>&1 || true
echo "removed the m06-lab cluster and the lab registry"
