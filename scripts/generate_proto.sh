#!/bin/bash

# Script to generate protobuf files

set -e

echo "Generating protobuf files for ms-audit..."

cd ms-audit

python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto/generated \
    --grpc_python_out=./proto/generated \
    --pyi_out=./proto/generated \
    ./proto/classroom.proto

echo "✓ Protobuf files generated successfully"

# Copy to gateway for gRPC client
echo "Copying protobuf files to gateway..."
mkdir -p ../gateway/proto/generated
cp proto/generated/*.py ../gateway/proto/generated/
cp proto/generated/*.pyi ../gateway/proto/generated/

echo "✓ Protobuf files copied to gateway"

