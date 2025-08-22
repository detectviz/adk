
# 簡化 Dockerfile（API 層）
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir fastapi uvicorn[standard] opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc google-auth grpcio
EXPOSE 8000
CMD ["uvicorn","sre_assistant.server.app:app","--host","0.0.0.0","--port","8000"]
