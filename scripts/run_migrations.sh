#!/bin/bash

# Script to run database migrations

set -e

echo "Running database migrations..."

cd ms-audit

python db/migrations/migrate.py

echo "✓ Migrations completed"

