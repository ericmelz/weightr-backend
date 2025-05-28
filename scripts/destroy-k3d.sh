#!/bin/bash

set -euo pipefail

CLUSTER_NAME="dev"

k3d cluster delete $CLUSTER_NAME