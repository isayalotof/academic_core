FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

RUN mkdir -p proto/generated

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 50056

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "main.py"]

