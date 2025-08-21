
# 專案建置腳本：提供依賴安裝、測試、命令列執行與啟動 API 伺服器
.PHONY: dev test run api

# 安裝開發相依（含 jsonschema 與 prometheus-client 用於驗證與指標）
dev:
	python -m pip install -q fastapi uvicorn pydantic pyyaml pytest jsonschema prometheus-client

# 執行測試套件
test:
	python -m pytest -q

# 以 CLI 方式進行一次對話（示範）
run:
	python -m sre_assistant.cli diagnose cpu high

# 啟動 FastAPI 伺服器
api:
	uvicorn sre_assistant.server.app:app --host 0.0.0.0 --port 8000
