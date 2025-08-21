
.PHONY: dev test api cli docker build run k8s

dev:
	python -m pip install -q fastapi uvicorn pydantic pyyaml pytest jsonschema prometheus-client httpx

test:
	python -m pytest -q

api:
	uvicorn sre_assistant.server.app:app --host 0.0.0.0 --port 8000

cli:
	python -m sre_assistant.cli chat "diagnose orders latency"

docker:
	docker build -t sre-assistant:latest .

run:
	docker run --rm -p 8000:8000 -e X_API_KEY=devkey -v $$PWD/data:/mnt/data sre-assistant:latest

k8s:
	kubectl apply -f k8s/deployment.yaml
