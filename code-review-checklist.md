# 程式碼審查清單 - SRE Assistant (ADK v1.2.1)

本清單確保 SRE Assistant 程式碼庫，基於 Google Agent Development Kit (ADK) v1.2.1（2025 更新）開發，完全符合官方最佳實踐，參考 ADK 官方文檔、Python 儲存庫、樣本儲存庫、A2A Purchasing Concierge Codelab 和 Google SRE 書籍。清單涵蓋 Python API 標準、多代理架構、工具整合、A2A 協議、記憶體管理、部署、安全性和測試。每項必須逐一驗證，以消除不足，確保 SRE 工作流的企業級可靠性。

## 1. Python API 標準
- [ ] **Code-First 設計**：所有代理和工具定義採用 ADK 的 code-first 方法（例如 `from google.adk.agents import SequentialAgent`, `agent.add_tool()`）。除非明確需要（如 `agent_config.json` 用於環境特定配置），不得依賴外部配置文件。
- [ ] **代理初始化**：代理（例如 `SRECoordinator`, `DiagnosticAgent`）繼承自適當的 ADK 類別（`SequentialAgent`, `LlmAgent` 等），並設置 `name`, `model`（如 `gemini-2.5-flash`）、`instruction` 和 `temperature`（SRE 任務建議 0.1-0.3 以降低隨機性）。
- [ ] **工具綁定**：工具透過 `agent.add_tool()` 或 `tools=[...]` 動態綁定，符合 ADK 文檔的模組化要求。
- [ ] **錯誤處理**：所有代理和工具實作包含異常處理（try-except），返回結構化錯誤（如 `{"status": "error", "message": "..."}`），參考 ADK API Reference。
- [ ] **版本相容性**：明確指定 `google-adk==1.2.1` 在 `pyproject.toml`，確保與 2025 更新相容。

## 2. 多代理架構
- [ ] **層級設計**：主協調器使用 `SequentialAgent` 實現 SRE 工作流（診斷→修復→覆盤→配置），符合 Google SRE Book 的 incident response 流程。
- [ ] **子代理模組化**：子代理（`DiagnosticAgent`, `RemediationAgent` 等）位於 `sub_agents/`，各自獨立模組（包含 `agent.py`, `prompts.py`, `tools.py`），符合 ADK Samples 的模組化結構。
- [ ] **並行與循環**：診斷階段使用 `ParallelAgent`（如 `aggregation_strategy="weighted_merge"`），修復階段使用 `LoopAgent`（如 `max_iterations=3`, `backoff_strategy="exponential"`），參考 ADK Samples 的 workflow orchestration。
- [ ] **上下文傳遞**：使用 `ContextPropagator` 傳遞上下文（如 `incident_id`, `severity`），確保跨代理一致性。
- [ ] **錯誤容忍**：`SequentialAgent` 設置 `continue_on_error=True`，確保單階段失敗不中斷工作流。

## 3. 工具整合
- [ ] **工具類型**：使用 `FunctionTool` 和 `LongRunningFunctionTool`（如 `K8sRolloutRestartTool`），符合 ADK Tools 文檔。
- [ ] **參數驗證**：每個工具定義 `args_schema`（JSON Schema）以驗證輸入，參考 ADK API Reference。
- [ ] **工具註冊**：使用 `ToolRegistry` 集中管理工具（`tools.py`），支援 `get_tools_by_category()` 等查詢方法。
- [ ] **異步處理**：長時間運行工具（如 K8s 操作）使用 `LongRunningFunctionTool`，設置 `start_func`, `poll_func`, `timeout_seconds`，並支援 HITL（`require_approval`）。
- [ ] **Pre-built 工具**：整合官方 pre-built 工具（如 `SearchTool`），用於知識檢索或外部 API 呼叫。

## 4. A2A 協議
- [ ] **代理卡片**：在 `__init__.py` 使用 `AgentCard` 定義元數據（`name`, `skills`, `capabilities`），支援 `streaming=True` 和 `tags/examples`，符合 A2A Purchasing Concierge Codelab。
- [ ] **伺服器暴露**：使用 `A2AStarletteApplication` 和 FastAPI 暴露 `/.well-known/agent.json`，支援 A2A 發現。
- [ ] **客戶端調用**：在 `utils/a2a_client.py` 使用 `RemoteA2aAgent` 和 `AgentCardResolver` 調用外部代理（如 ML 異常檢測），支援 OAuth 或服務帳戶認證。
- [ ] **Streaming 支援**：處理 A2A streaming 回應（`async for chunk in response.stream()`），符合 2025 I/O 增強。
- [ ] **認證安全**：實現 token 刷新邏輯，確保長期運行穩定性。

## 5. 記憶體管理
- [ ] **SessionService 擴展**：`memory.py` 繼承 `InMemorySessionService`，整合 Spanner 和 Vertex RAG（使用 `MatchingEngineIndexEndpoint` 的 `upsert_datapoints`/`find_neighbors`）。
- [ ] **向量嵌入**：使用官方 `TextEmbeddingModel`（如 `textembedding-gecko`）生成嵌入向量，避免自訂 `generate_embedding`。
- [ ] **持久化**：支援 Redis/PostgreSQL 作為備用後端，確保生產環境狀態持久化。
- [ ] **緩存管理**：使用 `AgentCache`（如 `SRECacheManager`）實現 LRU 緩存，設置 `ttl_seconds` 和 `cache_on` 策略（如 Prometheus 查詢緩存 60s）。
- [ ] **數據一致性**：確保 `store_incident` 和 `search_similar_incidents` 支援事務性操作。

## 6. 部署
- [ ] **容器化**：`Dockerfile` 使用 `python:3.12-slim` 作為基礎鏡像，包含 `google-adk==1.2.1`。
- [ ] **Vertex AI Agent Engine**：`deploy.py` 使用 `vertex_ai.deploy_agent` API，指定 `gen2` 執行環境，支援 streaming。
- [ ] **Cloud Build**：`cloudbuild.yaml` 配置自動建構和部署到 Cloud Run 或 Vertex AI。
- [ ] **環境變數**：使用 `.env.example` 定義 `GEMINI_API_KEY`, `GOOGLE_CLOUD_PROJECT` 等，參考 ADK Deployment 文檔。
- [ ] **自動擴展**：K8s 部署使用 HPA（Horizontal Pod Autoscaler），確保高並發性能。

## 7. 安全性
- [ ] **Safety Framework**：使用 `SafetyFramework` 和 `SafetyPolicy`（如 `SRESafetyFramework`）實現生產環境保護（`require_approval`）和數據安全（`require_encryption`）。
- [ ] **認證與授權**：`SREAuthService` 支援 Google Cloud IAM 和 API Key，實現 RBAC（基於角色的存取控制）。
- [ ] **審計日誌**：`AuditLog` 記錄所有操作（`action`, `risk_level`），透過 `AuditCallback` 輸出到日誌系統。
- [ ] **HITL 機制**：高風險操作（如 K8s 重啟）使用 `LongRunningFunctionTool` 的 `require_approval`，透過 SSE 推送人工審批請求。
- [ ] **數據加密**：敏感數據（如 `incident_data`）在傳輸和儲存時加密，符合 ADK Safety 文檔。

## 8. 測試
- [ ] **單元測試**：`test/test_agent.py` 覆蓋代理和工具邏輯（使用 pytest），如 `test_diagnostic_expert_metrics_analysis`。
- [ ] **整合測試**：測試完整工作流（如 `test_full_workflow`），驗證 `workflow_completed`。
- [ ] **E2E 測試**：模擬 HITL 流程（如 `test_hitl_approval_flow`），使用 HTTP 客戶端測試 API。
- [ ] **效能測試**：使用 k6 測試（如 `latency < 30s`），確保符合 SLO（P95 延遲 < 30s）。
- [ ] **覆蓋率**：確保測試覆蓋率 >80%，包括 callbacks 和 A2A 調用。

## 9. SRE 最佳實踐（參考 Google SRE Book）
- [ ] **Incident Response**：`SequentialAgent` 實現診斷→修復→覆盤順序，符合 SRE incident response 流程。
- [ ] **錯誤預算**：`ConfigAgent` 包含工具計算 SLO 違規（如 `FunctionTool` 計算 unavailability），觸發警報。
- [ ] **Blame-Free Postmortem**：`PostmortemAgent` 使用 “5 Whys” 模板生成報告，包含 `root_cause` 和 `action_items`。
- [ ] **自動化**：工具（如 `K8sRolloutRestartTool`）支援 rollback，減少人工操作，符合 MTTR 優化。
- [ ] **監控整合**：Prometheus 指標（如 `sre_assistant:request_success_rate`）與 ADK 評估框架整合，支援 SLO 追蹤。

## 10. 文件與可維護性
- [ ] **程式碼註釋**：每個代理、工具和方法包含清晰註釋，說明功能和參考（如 “參考 ADK Samples: RAG agent”）。
- [ ] **README 更新**：`README.md` 包含專案概述、安裝步驟、運行範例和資源映射。
- [ ] **目錄結構**：符合 ADK Samples（如 `sub_agents/`, `tools.py`），模組化且一致。
- [ ] **版本控制**：提交訊息遵循語義化規範（e.g., `feat: add DiagnosticAgent`, `fix: update A2A auth`）。
- [ ] **參考資源**：`docs/references/` 包含 ADK 文檔、樣本和 SRE 書籍的整理文件，輔助開發。

## 11. 性能與擴展性
- [ ] **緩存優化**：`SRECacheManager` 緩存 Prometheus 查詢（60s）和 runbook（24h），減少響應時間。
- [ ] **異步並行**：工具調用（如 `PromQLQueryTool`）使用異步（`async/await`），提升併發性能。
- [ ] **代理熱註冊**：支援動態添加子代理（`SRECoordinator.register_sub_agent`），符合 ADK 擴展性。
- [ ] **負載均衡**：部署配置支援 K8s HPA 或 Cloud Run 自動擴展，處理高流量。
- [ ] **效能基準**：確保 P95 延遲 < 30s，可用性 > 99.9%，符合 SLO。

## 使用指南
1. **逐項檢查**：開發者在提交 pull request 前，使用本清單逐項驗證程式碼。
2. **自動化檢查**：整合 linter（如 flake8）檢查 Python 規範，CI/CD 運行 pytest 和 k6 測試。
3. **審查流程**：至少兩名審查者確認所有項目通過，參考 ADK 文檔和 SRE 書籍解決爭議。
4. **更新頻率**：每季檢查 ADK 更新（如 v1.3.x），同步清單。

## 參考資源
- ADK 官方文檔：官方文檔，提供 ADK 的詳細介紹和使用方法。
	- [內部](docs/references/adk-docs)
	- [外部](https://google.github.io/adk-docs)

- ADK Python Repository：包含用於測試不同功能的範例。這些範例通常比較簡單，僅用於測試一個或幾個場景。
	- [內部](docs/references/adk-python-samples)
	- [外部](https://github.com/google/adk-python/tree/main/contributing/samples)

- ADK Samples Repository：更複雜的 e2e 範例，供客戶直接使用或修改。
	- [內部](docs/references/adk-samples-agents)
	- [外部](https://github.com/google/adk-samples/tree/main/python/agents)

- A2A Samples Repository：a2a 範例，供客戶直接使用或修改。
	- [內部](docs/references/a2a-samples)
	- [外部](https://github.com/a2aproject/a2a-samples/tree/main/samples/python)

- A2A Purchasing Concierge Sample：購物助理的 A2A 示例。
	- [內部](docs/references/other-samples/purchasing-concierge-intro-a2a)
	- [外部](https://github.com/alphinside/purchasing-concierge-intro-a2a-codelab-starter)

- Google SRE Book：谷歌 SRE 書籍，提供 SRE 最佳實踐。
	- [內部](docs/references/google-sre-book)
	- [外部](https://sre.google/sre-book/)

## 審查清單
- [ ] **Code-First 設計**：所有代理和工具定義採用 ADK 的 code-first 方法（例如 `from google.adk.agents import SequentialAgent`, `agent.add_tool()`）。除非明確需要（如 `agent_config.json` 用於環境特定配置），不得依賴外部配置文件。
- [ ] **代理初始化**：代理（例如 `SRECoordinator`, `DiagnosticAgent`）繼承自適當的 ADK 類別（`SequentialAgent`, `LlmAgent` 等），並設置 `name`, `model`（如 `gemini-2.5-flash`）、`instruction` 和 `temperature`（SRE 任務建議 0.1-0.3 以降低隨機性）。
- [ADK Python Repository](https://github.com/google/adk-python/tree/main/contributing/samples)
> 包含用於測試不同功能的範例。這些範例通常比較簡單，僅用於測試一個或幾個場景。
- [ADK Samples Repository](https://github.com/google/adk-samples/tree/main/python/agents)
> e2e 範例，供客戶直接使用或修改。
- [A2A Samples Repository](https://github.com/a2aproject/a2a-samples/tree/main/samples/python)
> a2a 範例，供客戶直接使用或修改。
- [A2A Purchasing Concierge Sample](https://github.com/alphinside/purchasing-concierge-intro-a2a-codelab-starter)
> 購物助理的 A2A 示例。
- [Google SRE Book](https://sre.google/sre-book/)
> 谷歌 SRE 書籍，提供 SRE 最佳實踐。


通過本清單，SRE Assistant 程式碼將完全符合 ADK v1.2.1 標準和 SRE 原則，無技術不足，具備企業級可靠性。