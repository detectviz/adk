
.PHONY: dev test run api

dev:
	python -m pip install -q fastapi uvicorn pydantic pyyaml pytest

test:
	python -m pytest -q

run:
	python -m sre_assistant.cli diagnose cpu high

api:
	uvicorn sre_assistant.server.app:app --host 0.0.0.0 --port 8000
