
.PHONY: dev opt adk test api

dev:
	python -m pip install -q fastapi uvicorn pydantic pyyaml pytest jsonschema prometheus-client httpx sentence-transformers

opt:
	python -m pip install -q 'psycopg[binary]' kubernetes opentelemetry-sdk opentelemetry-exporter-otlp

adk:
	python -m pip install -q google-adk google-genai

test:
	python -m pytest -q -k "not integration"

api:
	uvicorn sre_assistant.server.app:app --host 0.0.0.0 --port 8000
