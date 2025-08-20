# Makefile for SRE Assistant
# -------------------------
# This Makefile provides commands for building, testing, and running the SRE Assistant.
#
# Core Commands:
#   up:         Starts all services (Go Core + Python ADK).
#   down:       Stops all services.
#   test:       Runs all tests (tools, core, agents, e2e).
#   validate:   Performs a full implementation validation.
#   fix-issues: Attempts to automatically fix common issues.
#   proto-check:Validates the protobuf contracts.
#
.PHONY: all up down run clean test test-tools test-core test-agents test-e2e validate fix-issues proto-check

# --- Variables ---
PYTHON_ADK_MAIN = agents.sre_assistant
GO_CORE_MAIN = core/main.go
GO_CORE_PID_FILE = /tmp/sre_assistant_core.pid
PYTHON_ADK_PID_FILE = /tmp/sre_assistant_adk.pid

# --- Core Lifecycle ---

# 啟動所有服務 (Start all services)
up:
	@echo "🚀 Starting SRE Assistant..."
	@echo "Starting Go Core..."
	@nohup go run $(GO_CORE_MAIN) > core.log 2>&1 & echo $$! > $(GO_CORE_PID_FILE)
	@echo "Starting Python ADK..."
	@nohup python -m $(PYTHON_ADK_MAIN) > python_adk.log 2>&1 & echo $$! > $(PYTHON_ADK_PID_FILE)
	@echo "✅ SRE Assistant is running. Core PID: $$(cat $(GO_CORE_PID_FILE)), ADK PID: $$(cat $(PYTHON_ADK_PID_FILE))"
	@echo "Logs are being written to core.log and python_adk.log"
	@echo "Access the web UI at http://localhost:8000"

# 停止所有服務 (Stop all services)
down:
	@echo "🛑 Stopping SRE Assistant..."
	@if [ -f $(GO_CORE_PID_FILE) ]; then \
		echo "Stopping Go Core..."; \
		kill $$(cat $(GO_CORE_PID_FILE)); \
		rm $(GO_CORE_PID_FILE); \
	else \
		echo "Go Core process file not found, might not be running."; \
	fi
	@if [ -f $(PYTHON_ADK_PID_FILE) ]; then \
		echo "Stopping Python ADK..."; \
		kill $$(cat $(PYTHON_ADK_PID_FILE)); \
		rm $(PYTHON_ADK_PID_FILE); \
	else \
		echo "Python ADK process file not found, might not be running."; \
	fi
	@echo "✅ All services stopped."

# --- Testing & Validation ---

# 完整測試 (Run all tests)
test: test-tools test-core test-agents test-e2e
	@echo "✅ All tests passed!"

# 測試 Shell 工具 (Test Shell tools)
test-tools:
	@echo "🔬 Testing shell tools..."
	@bash core/tools/diagnostic/check_disk.sh 80
	@if [ -f core/tools/diagnostic/check_memory.sh ]; then \
		bash core/tools/diagnostic/check_memory.sh 80; \
	else \
		echo "WARNING: check_memory.sh not found, skipping test."; \
	fi

# 測試 Go 核心 (Test Go Core)
test-core:
	@echo "🔬 Testing Go core..."
	@go test ./core/...

# 測試 Python Agents (Test Python Agents)
test-agents:
	@echo "🔬 Testing Python agents..."
	@python -m pytest tests/

# 端到端測試 (End-to-end tests)
test-e2e:
	@echo "🔬 Running E2E tests..."
	@bash tests/e2e/e2e_test.sh

# --- Quality & Maintenance ---

# 完整實作驗證 (Validate implementation)
validate:
	@echo "🔎 Validating full implementation..."
	@make test

# 自動修復常見問題 (Fix common issues)
fix-issues:
	@echo "🛠️ Attempting to fix common issues..."
	@echo "Note: This is a placeholder. No common issues are fixed automatically yet."

# 檢查 Proto 契約 (Check protobuf contracts)
proto-check:
	@echo "🔎 Checking protobuf contracts..."
	@if ! command -v buf &> /dev/null; then \
		echo "ERROR: buf is not installed. Please install it to check protobuf contracts."; \
		exit 1; \
	fi
	@buf lint contracts/
	@echo "✅ Protobuf contracts are valid."

# 清理 (Clean up)
clean: down
	@echo "🧹 Cleaning up log files..."
	@rm -f core.log python_adk.log
	@echo "✅ Cleanup complete."