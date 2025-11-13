#!/bin/bash
# ============================================
# GENERATE PROTO FOR MS-SCHEDULE
# ============================================
# Генерация Python кода из protobuf для ms-schedule

set -e

echo "============================================"
echo "GENERATING PROTO FOR MS-SCHEDULE"
echo "============================================"

# Перейти в ms-schedule
cd ms-schedule

# Создать директорию для generated файлов
mkdir -p proto/generated

# Генерация Python кода
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto/generated \
    --grpc_python_out=./proto/generated \
    --pyi_out=./proto/generated \
    ./proto/schedule.proto

echo ""
echo "✅ Proto files generated for ms-schedule!"
echo ""
echo "Generated files:"
ls -lh proto/generated/
echo ""

# Вернуться в корень
cd ..

echo "Done!"

