#!/bin/bash

# Script to build all Docker images

set -e

echo "Building Docker images..."

# Generate proto files first
./scripts/generate_proto.sh

# Build ms-audit
echo "Building ms-audit..."
docker build -t ms-audit:latest ./ms-audit

# Build gateway
echo "Building gateway..."
docker build -t gateway:latest ./gateway

echo "✓ All images built successfully"

