.PHONY: test-tools test-bridge test-agents test-e2e run

# 測試 Shell 工具
test-tools:
	@echo "Testing shell tools..."
	@bash core/tools/diagnostic/check_disk.sh 80
	@bash core/tools/diagnostic/check_memory.sh 80

# 測試 Go Bridge
test-bridge:
	@echo "Testing Go bridge..."
	@go test ./core/...

# 測試 Python Agents
test-agents:
	@echo "Testing Python agents..."
	@python -m pytest tests/

# 端到端測試
test-e2e:
	@echo "Running E2E tests..."
	@bash tests/e2e_test.sh

# 運行整個系統
run:
	@echo "Starting SRE Assistant..."
	@go run core/main.go &
	@python -m agents.sre_assistant

# 完整測試
test: test-tools test-bridge test-agents test-e2e
	@echo "All tests passed!"

    # === Proto 生成（Go）===
    PROTO_SRC := contracts/proto/agent_bridge.proto
    PROTO_GO_OUT := contracts/gen/go

    proto:
	mkdir -p $(PROTO_GO_OUT)
	protoc --go_out=$(PROTO_GO_OUT) --go_opt=paths=source_relative \	       --go-grpc_out=$(PROTO_GO_OUT) --go-grpc_opt=paths=source_relative \	       $(PROTO_SRC)

