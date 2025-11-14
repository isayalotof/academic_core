#!/bin/bash
set -e

echo "Generating protobuf files..."
mkdir -p proto/generated
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto/generated \
    --grpc_python_out=./proto/generated \
    --pyi_out=./proto/generated \
    ./proto/events.proto

sed -i 's/^import \(.*_pb2\) as \(.*__pb2\)$/from . import \1 as \2/g' proto/generated/*_pb2_grpc.py 2>/dev/null || true

if [ -f "proto/generated/events_pb2.py" ] && [ -f "proto/generated/events_pb2_grpc.py" ]; then
    echo "✅ Proto files generated successfully"
else
    echo "❌ Failed to generate proto files"
    exit 1
fi

exec "$@"

