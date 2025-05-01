#!/bin/bash

set -euo pipefail

CLUSTER_NAME="dev2"

k3d cluster delete $CLUSTER_NAME