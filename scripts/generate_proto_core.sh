#!/bin/bash

# Script to generate Python gRPC code from ms-core proto files
# Usage: bash scripts/generate_proto_core.sh

set -e

echo "========================================"
echo "Generating gRPC code for MS-CORE"
echo "========================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if grpc_tools is installed
if ! python -c "import grpc_tools" 2>/dev/null; then
    echo -e "${RED}✗ grpc_tools not found${NC}"
    echo "Installing grpc_tools..."
    pip install grpcio-tools
fi

# Navigate to ms-core directory
cd ms-core

# Create generated directory if it doesn't exist
mkdir -p proto/generated

# Generate Python code
echo "Generating Python gRPC code..."
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto/generated \
    --grpc_python_out=./proto/generated \
    --pyi_out=./proto/generated \
    ./proto/core.proto

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Successfully generated gRPC code${NC}"
    
    # List generated files
    echo ""
    echo "Generated files:"
    ls -lh proto/generated/core_pb2*
else
    echo -e "${RED}✗ Failed to generate gRPC code${NC}"
    exit 1
fi

echo ""
echo "========================================"
echo "Generation complete!"
echo "========================================"

