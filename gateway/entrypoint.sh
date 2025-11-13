#!/bin/bash
set -e

echo "Generating protobuf files for gateway..."
mkdir -p rpc_clients/generated

# Generate proto files from classroom.proto
if [ -f "rpc_clients/classroom.proto" ]; then
    echo "Generating classroom proto files..."
    python -m grpc_tools.protoc \
        -I./rpc_clients \
        --python_out=./rpc_clients/generated \
        --grpc_python_out=./rpc_clients/generated \
        ./rpc_clients/classroom.proto

    # Fix imports in generated gRPC files
    echo "Fixing imports in generated gRPC files..."
    sed -i 's/^import \(.*_pb2\) as \(.*__pb2\)$/from . import \1 as \2/g' rpc_clients/generated/*_pb2_grpc.py 2>/dev/null || true

    # Verify generated files
    if [ -f "rpc_clients/generated/classroom_pb2.py" ] && [ -f "rpc_clients/generated/classroom_pb2_grpc.py" ]; then
        echo "✅ Classroom proto files generated successfully"
    else
        echo "❌ Failed to generate classroom proto files"
        exit 1
    fi
else
    echo "⚠️  classroom.proto not found, skipping generation"
fi

# Generate proto files from agent.proto
if [ -f "rpc_clients/agent.proto" ]; then
    echo "Generating agent proto files..."
    python -m grpc_tools.protoc \
        -I./rpc_clients \
        --python_out=./rpc_clients/generated \
        --grpc_python_out=./rpc_clients/generated \
        ./rpc_clients/agent.proto

    # Fix imports in generated gRPC files
    echo "Fixing imports in generated agent gRPC files..."
    sed -i 's/^import \(.*_pb2\) as \(.*__pb2\)$/from . import \1 as \2/g' rpc_clients/generated/agent_pb2_grpc.py 2>/dev/null || true

    # Verify generated files
    if [ -f "rpc_clients/generated/agent_pb2.py" ] && [ -f "rpc_clients/generated/agent_pb2_grpc.py" ]; then
        echo "✅ Agent proto files generated successfully"
    else
        echo "❌ Failed to generate agent proto files"
        exit 1
    fi
else
    echo "⚠️  agent.proto not found, skipping generation"
fi

# Generate proto files from core.proto
if [ -f "rpc_clients/core.proto" ]; then
    echo "Generating core proto files..."
    python -m grpc_tools.protoc \
        -I./rpc_clients \
        --python_out=./rpc_clients/generated \
        --grpc_python_out=./rpc_clients/generated \
        ./rpc_clients/core.proto

    # Fix imports in generated gRPC files
    echo "Fixing imports in generated core gRPC files..."
    sed -i 's/^import \(.*_pb2\) as \(.*__pb2\)$/from . import \1 as \2/g' rpc_clients/generated/core_pb2_grpc.py 2>/dev/null || true

    # Verify generated files
    if [ -f "rpc_clients/generated/core_pb2.py" ] && [ -f "rpc_clients/generated/core_pb2_grpc.py" ]; then
        echo "✅ Core proto files generated successfully"
    else
        echo "❌ Failed to generate core proto files"
        exit 1
    fi
else
    echo "⚠️  core.proto not found, skipping generation"
fi

# Generate proto files for new microservices
for proto_file in tickets lms events library documents cafeteria; do
    if [ -f "rpc_clients/${proto_file}.proto" ]; then
        echo "Generating ${proto_file} proto files..."
        python -m grpc_tools.protoc \
            -I./rpc_clients \
            --python_out=./rpc_clients/generated \
            --grpc_python_out=./rpc_clients/generated \
            ./rpc_clients/${proto_file}.proto

        # Fix imports in generated gRPC files
        echo "Fixing imports in generated ${proto_file} gRPC files..."
        sed -i 's/^import \(.*_pb2\) as \(.*__pb2\)$/from . import \1 as \2/g' rpc_clients/generated/${proto_file}_pb2_grpc.py 2>/dev/null || true

        # Verify generated files
        if [ -f "rpc_clients/generated/${proto_file}_pb2.py" ] && [ -f "rpc_clients/generated/${proto_file}_pb2_grpc.py" ]; then
            echo "✅ ${proto_file} proto files generated successfully"
        else
            echo "❌ Failed to generate ${proto_file} proto files"
            exit 1
        fi
    else
        echo "⚠️  ${proto_file}.proto not found, skipping generation"
    fi
done

# Execute the main command
exec "$@"

