
.PHONY: a2a-proto adk-web dev-full
adk-web:
	python -m adk_web_server

dev-full: adk-web


.PHONY: export-slo
export-slo:
	python3 scripts/export_slo_rules.py


.PHONY: a2a-gen
a2a-gen:
	python -m grpc_tools.protoc -I sre_assistant/a2a --python_out=sre_assistant/a2a --grpc_python_out=sre_assistant/a2a sre_assistant/a2a/agent.proto


.PHONY: validate-config
validate-config:
	python3 scripts/validate_config.py


.PHONY: validate-metrics
validate-metrics:
	python3 scripts/validate_metrics_spec.py


.PHONY: db-migrate
db-migrate:
	python3 scripts/db_migrate.py


.PHONY: test
test:
	pytest -q


.PHONY: openapi
openapi:
	python3 scripts/generate_openapi.py


.PHONY: gen-docs
gen-docs:
	python3 scripts/generate_docs.py


.PHONY: schema-docs
schema-docs:
	python3 scripts/schema_docs.py


.PHONY: auto-tune
auto-tune:
	python3 scripts/auto_tune_model.py
