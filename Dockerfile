
# 以 Python slim 建置，對齊顯式工具範式
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir fastapi uvicorn pydantic pyyaml jsonschema prometheus-client httpx
EXPOSE 8000
ENV PYTHONPATH=/app
CMD ["uvicorn", "sre_assistant.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
