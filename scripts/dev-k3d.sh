#!/bin/bash

set -euo pipefail

CLUSTER_NAME="dev2"

echo "Checking if cluster '$CLUSTER_NAME' exists..."

if k3d cluster list | grep -q "^$CLUSTER_NAME"; then
  echo "Cluster '$CLUSTER_NAME' already exists."
else
  echo "Creating cluster '$CLUSTER_NAME' using project-specific config..."
  k3d cluster create "$CLUSTER_NAME" --config k8s-k3d/config.yaml -p "8880:80@loadbalancer"
fi

echo "Development cluster '$CLUSTER_NAME' is ready."
