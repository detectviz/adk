
.PHONY: dev opt adk test api e2e accept

dev:
	python -m pip install -q fastapi uvicorn pydantic pyyaml pytest jsonschema prometheus-client httpx requests sentence-transformers

opt:
	python -m pip install -q 'psycopg[binary]' kubernetes opentelemetry-sdk opentelemetry-exporter-otlp

adk:
	python -m pip install -q google-adk google-genai

test:
	python -m pytest -q -k "not integration and not e2e"

api:
	uvicorn sre_assistant.server.app:app --host 0.0.0.0 --port 8000

e2e:
	python -m pytest -q tests/e2e/test_real_integrations.py

accept:
	bash scripts/accept_v141.sh


adk-web:
	python -m pip install -q 'google-adk[web]' google-genai
	python adk_web_server.py

dev-full:
	python -m pip install -q 'google-adk[web]' google-genai fastapi uvicorn
	# 背景啟動 REST API
	uvicorn sre_assistant.server.app:app --host 0.0.0.0 --port 8000 &
	# 前景啟動 ADK Web Dev UI
	python adk_web_server.py


obs-up:
	docker compose -f obs/docker-compose.yml up -d

obs-down:
	docker compose -f obs/docker-compose.yml down -v
