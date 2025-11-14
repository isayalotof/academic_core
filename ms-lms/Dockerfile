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

# Ensure entrypoint has execute permissions
RUN chmod +x /app/entrypoint.sh

# Create proto directories
RUN mkdir -p proto/generated

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose gRPC port
EXPOSE 50061

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "main.py"]

