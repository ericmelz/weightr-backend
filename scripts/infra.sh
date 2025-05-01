#!/bin/bash

# -----------------------------------------------------------------------------
# Purpose: Create the 'infra' k3d cluster and install Redis.
# Usage: bash scripts/infra.sh
# Requirements: k3d, Docker, helm, jq
# -----------------------------------------------------------------------------

set -euo pipefail

CLUSTER_NAME="infra"
REDIS_RELEASE_NAME="redis"

cluster_exists() {
  k3d cluster list -o json | jq -e ".[] | select(.name == \"$1\")" > /dev/null
}

helm_release_exists() {
  helm list --all-namespaces | awk '{print $1}' | grep -qx "$1"
}

echo "Checking if cluster '$CLUSTER_NAME' exists..."

if cluster_exists "$CLUSTER_NAME"; then
  echo "Cluster '$CLUSTER_NAME' already exists."
else
  echo "Creating cluster '$CLUSTER_NAME' using project-specific config..."
  k3d cluster create "$CLUSTER_NAME" --config k8s-k3d/config.yaml -p "6379:6379@loadbalancer"
fi

echo "Checking if Redis is already installed..."

if helm_release_exists "$REDIS_RELEASE_NAME"; then
  echo "Redis is already installed. Skipping Helm install."
else
  echo "Installing Redis..."
  helm repo add bitnami https://charts.bitnami.com/bitnami || true
  helm repo update
  helm upgrade --install "$REDIS_RELEASE_NAME" bitnami/redis -f k8s-infra/redis-values.yaml
fi

echo "Testing Redis connection..."

if docker run --rm redis redis-cli -h host.docker.internal -p 6379 ping | grep -q "PONG"; then
  echo "✅ Redis connection successful."
else
  echo "❌ Redis connection failed."
  exit 1
fi


