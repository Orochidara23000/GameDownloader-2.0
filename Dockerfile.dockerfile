# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN chmod +x startup.sh && \
    apt-get update && \
    apt-get install -y curl tar && \
    rm -rf /var/lib/apt/lists/*

CMD ["./startup.sh"]