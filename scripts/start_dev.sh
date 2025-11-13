#!/bin/bash

# Script to start development environment

set -e

echo "Starting development environment..."

# Generate protobuf files
echo "Generating protobuf files..."
./scripts/generate_proto.sh

# Start infrastructure
echo "Starting infrastructure..."
docker-compose up -d postgres redis rabbitmq

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Run migrations
echo "Running migrations..."
cd ms-audit
python db/migrations/migrate.py
cd ..

echo "✓ Development environment ready"
echo ""
echo "To start services:"
echo "  ms-audit:  cd ms-audit && python main.py"
echo "  gateway:   cd gateway && python main.py"
echo ""
echo "Services:"
echo "  Gateway:     http://localhost:8000"
echo "  API Docs:    http://localhost:8000/docs"
echo "  Prometheus:  http://localhost:9090"
echo "  Grafana:     http://localhost:3000"
echo "  RabbitMQ:    http://localhost:15672"

