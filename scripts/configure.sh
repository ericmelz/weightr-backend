#!/bin/bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONF_SRC_DIR="$PROJECT_ROOT/var/conf/weightr-backend"
CONF_DEST_DIR="$HOME/Data/var/conf/weightr-backend"
ENV_TEMPLATE="$CONF_SRC_DIR/.env.dev.template"
ENV_FINAL="$CONF_DEST_DIR/.env.dev"
ENV_DOCKER_TEMPLATE="$CONF_SRC_DIR/.env.dev.docker.template"
ENV_DOCKER_FINAL="$CONF_DEST_DIR/.env.dev.docker"
VENV_DIR="$PROJECT_ROOT/.venv"

NON_INTERACTIVE=false

# Parse command-line args
for arg in "$@"; do
  if [[ "$arg" == "--non-interactive" ]]; then
    NON_INTERACTIVE=true
  fi
done

# Ensure CONF_DEST_DIR exists
mkdir -p "$CONF_DEST_DIR"

# Step 1: Install uv if missing
if ! command -v uv &>/dev/null; then
  echo "uv not found. Installing via pip..."
  python3 -m pip install --upgrade pip
  python3 -m pip install uv
fi

# Step 2: Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# Step 3: Install dependencies
echo "Installing dependencies with uv..."
uv pip install -e ".[dev]"

# Step 4: Copy .env.dev.template to .env
echo "Copying environment template..."
cp "$ENV_TEMPLATE" "$ENV_FINAL"
cp "$ENV_DOCKER_TEMPLATE" "$ENV_DOCKER_FINAL"

# Step 5: Prompt user for secrets
if [ "$NON_INTERACTIVE" = false ]; then
  read -p "Enter your WITHINGS_CLIENT_ID: " CLIENT_ID
  read -p "Enter your WITHINGS_CLIENT_SECRET: " CLIENT_SECRET

  # Step 6: Inject secrets into .env
  sed -i '' "s/^WITHINGS_CLIENT_ID=.*/WITHINGS_CLIENT_ID=$CLIENT_ID/" "$ENV_FINAL"
  sed -i '' "s/^WITHINGS_CLIENT_SECRET=.*/WITHINGS_CLIENT_SECRET=$CLIENT_SECRET/" "$ENV_FINAL"
  sed -i '' "s/^WITHINGS_CLIENT_ID=.*/WITHINGS_CLIENT_ID=$CLIENT_ID/" "$ENV_DOCKER_FINAL"
  sed -i '' "s/^WITHINGS_CLIENT_SECRET=.*/WITHINGS_CLIENT_SECRET=$CLIENT_SECRET/" "$ENV_DOCKER_FINAL"
else
  echo "Skipped secrets prompts (--non-interactive detected)"
fi

echo ".env configuration complete."

# Step 7: Verify setup by running tests
echo "Verifying setup by running tests..."
uv run pytest
