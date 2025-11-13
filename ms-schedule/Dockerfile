# ============================================
# MS-SCHEDULE DOCKERFILE
# ============================================

FROM python:3.11-slim

LABEL maintainer="University Schedule System"
LABEL service="ms-schedule"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create exports directory
RUN mkdir -p /app/exports

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose gRPC port
EXPOSE 50055

# Expose metrics port
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import grpc; channel = grpc.insecure_channel('localhost:50055'); channel.channel_ready()" || exit 1

# Run application
CMD ["python", "main.py"]

