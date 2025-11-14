FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Ensure entrypoint has execute permissions
RUN chmod +x /app/entrypoint.sh

RUN mkdir -p proto/generated

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 50058

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "main.py"]

