FROM python:3.11-slim

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

# Copy and set up entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create proto generated directory
RUN mkdir -p proto/generated

# Expose ports
EXPOSE 50053

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import grpc; from proto.generated import agent_pb2_grpc, agent_pb2; channel = grpc.insecure_channel('localhost:50053'); stub = agent_pb2_grpc.AgentServiceStub(channel); stub.HealthCheck(agent_pb2.HealthCheckRequest(), timeout=5)" || exit 1

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "main.py"]

