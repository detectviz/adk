
.PHONY: a2a-proto adk-web dev-full
a2a-proto:
	python -m grpc_tools.protoc -I sre_assistant/adk_app/proto \	  --python_out=sre_assistant/adk_app/proto \	  --grpc_python_out=sre_assistant/adk_app/proto \	  sre_assistant/adk_app/proto/a2a.proto

adk-web:
	python -m adk_web_server

dev-full: a2a-proto adk-web
