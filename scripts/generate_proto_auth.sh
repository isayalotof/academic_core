#!/bin/bash

# Script to generate protobuf files for ms-auth

set -e

echo "Generating protobuf files for ms-auth..."

cd ms-auth

python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto/generated \
    --grpc_python_out=./proto/generated \
    --pyi_out=./proto/generated \
    ./proto/auth.proto

echo "✓ Protobuf files generated successfully"

# Copy to gateway for gRPC client
echo "Copying protobuf files to gateway..."
mkdir -p ../gateway/proto/generated
cp proto/generated/auth_pb2.py ../gateway/proto/generated/
cp proto/generated/auth_pb2_grpc.py ../gateway/proto/generated/
cp proto/generated/auth_pb2.pyi ../gateway/proto/generated/

echo "✓ Protobuf files copied to gateway"

