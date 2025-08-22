
.PHONY: a2a-proto adk-web dev-full
adk-web:
	python -m adk_web_server

dev-full: adk-web
