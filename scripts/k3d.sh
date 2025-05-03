#!/bin/bash

set -euo pipefail

CLUSTER_NAME="dev"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VAR_DIR="$PROJECT_ROOT/var"

if k3d cluster list | grep -q "^$CLUSTER_NAME"; then
  echo "Cluster '$CLUSTER_NAME' already exists.  Skipping creation"
else
  echo "Creating cluster '$CLUSTER_NAME' using project-specific config..."
  k3d cluster create "$CLUSTER_NAME" --config k8s-k3d/config.yaml \
      -p "8880:80@loadbalancer" \
      --volume "$VAR_DIR:/mnt/var@server:0"

  # This is a bug that I don't have a better solution for fixing...
  echo "Fixing ~/.kube/config"
  sed -i '' 's|server: https://host.docker.internal|server: https://127.0.0.1|g' ~/.kube/config

  if [ -z "${GPG_PASSPHRASE}" ]; then
    export GPG_PASSPHRASE=$(openssl rand -base64 32)
    echo "Generated new GPG_PASSPHRASE: $GPG_PASSPHRASE"
    echo "Add it to your ~/.zshrc using"
    echo "echo 'export GPG_PASSPHRASE=$GPG_PASSPHRASE' >> ~/.zshrc"
  else
    echo "Using existing GPG_PASSPHRASE"
  fi

  echo "Installing the encryption key..."
  kubectl create secret generic gpg-passphrase \
          --from-literal=GPG_PASSPHRASE=$GPG_PASSPHRASE
fi

if [ -z "${GPG_PASSPHRASE}" ]; then
  echo "*** ERROR: GPG_PASSPHRASE is not set!!! Set this before running the script!"
  exit 1
fi

echo "Encrypting configuration..."
rm -f $VAR_DIR/conf/weightr-backend/.env.dev.docker.gpg
cat "$VAR_DIR/conf/weightr-backend/.env.dev.docker"| \
     gpg --symmetric --cipher-alg AES256 \
         --batch --passphrase "$GPG_PASSPHRASE" \
         -o "$VAR_DIR/conf/weightr-backend/.env.dev.docker.gpg"

# Note: you can decrypt using
# gpg --batch --yes --passphrase $GPG_PASSPHRASE \
#     -o var/conf/weightr-backend/.env.dev.docker.decrypted \
#     -d var/conf/weightr-backend/.env.dev.docker.gpg


echo "Building docker image..."
docker build -t weightr-backend:latest .

echo "Importing docker image..."
k3d image import weightr-backend:latest -c $CLUSTER_NAME

echo "Deploying resources to k3d..."
helm upgrade --install weightr-backend ./helm

echo "Restarting deployment..."
kubectl rollout restart deployment weightr-backend

echo "Development cluster '$CLUSTER_NAME' is ready."
