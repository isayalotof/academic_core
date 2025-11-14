FROM python:3.11-slim

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

# Ensure entrypoint has execute permissions
RUN chmod +x /app/entrypoint.sh

# Create directory for migrations if needed
RUN mkdir -p db/migrations proto/generated

# Expose ports
EXPOSE 50052

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import grpc; from proto.generated import auth_pb2_grpc, auth_pb2; channel = grpc.insecure_channel('localhost:50052'); stub = auth_pb2_grpc.AuthServiceStub(channel); stub.HealthCheck(auth_pb2.HealthCheckRequest(), timeout=5)" || exit 1

# Use entrypoint script (via sh to handle permission issues with volumes)
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
CMD ["python", "main.py"]

# d