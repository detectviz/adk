# ADK Architecture Doc 4

---

## 架構藍圖

> 基於 Google Agent Development Kit (ADK) 的官方文檔和最佳實踐，ARCHITECTURE.md 作為專案的架構藍圖，必須明確定義 ADK 的關鍵要素，以確保系統設計符合框架的模組化、可擴展性和生產級要求。這些要素不僅涵蓋核心組件，還包括多代理互動模式、狀態管理和執行機制。以下是必須包含的關鍵要素定義，按邏輯分類列出，每項附帶解釋及其在 SRE Assistant 專案中的應用建議：

### 1. **代理定義與類型 (Agents and Types)**
   - **必須定義**：代理的核心屬性，包括名稱、模型 (e.g., Gemini Pro)、描述、指令 (instructions)、工具列表 (tools)、安全設定 (safety_settings) 和生成配置 (generate_content_config，如 temperature、max_output_tokens)。
   - **為何關鍵**：代理是 ADK 的基本單位，定義確保一致性和可測試性。支持多種類型，如 LLM Agents (語言模型驅動)、Workflow Agents (工作流協調)和 Custom Agents (自訂邏輯)。
   - **說明建議**：描述 SRE Assistant 的主代理 (e.g., SREWorkflow 作為 SequentialAgent 或 ParallelAgent) 和子代理 (e.g., IncidentHandlerAgent 作為 LLM Agent)，並提供範例配置代碼片段。

### 2. **工具整合 (Tools Integration)**
   - **必須定義**：工具的註冊和類型，包括 FunctionTools (標準函數)、AgentTools (代理作為工具)和 LongRunningFunctionTools (長運行任務，如人類介入 HITL)。
   - **為何關鍵**：工具是代理執行行動的核心，支持外部整合 (e.g., Grafana API) 和內部調用。必須強調工具的無狀態設計、註解完整性和本地測試。
   - **說明建議**：列出共享工具註冊表 (tool_registry.py)，如 PrometheusQueryTool 的簽名和配置，並說明如何將子代理封裝為 AgentTool 以支持聯邦化。

### 3. **多代理層級與模式 (Multi-Agent Hierarchy and Patterns)**
   - **必須定義**：代理層級 (parent-sub agents)、常見模式 (e.g., Coordinator/Dispatcher、Sequential Pipeline、Parallel Fan-Out/Gather、Hierarchical Decomposition、Review/Critique、Iterative Refinement、Human-in-the-Loop)。
   - **為何關鍵**：ADK 強調多代理系統以提升效率和容錯，支持關注點分離和動態路由。
   - **說明建議**：使用 Mermaid 圖展示 SREIntelligentDispatcher 作為 Coordinator，定義 VerificationAgent 作為 Self-Critic 模式，並說明 A2A 通訊 (e.g., gRPC) 如何實現點對點互動。

### 4. **工作流代理 (Workflow Agents)**
   - **必須定義**：特定工作流類型，如 SequentialAgent (循序執行)、ParallelAgent (並行執行)和 LoopAgent (循環精煉)。
   - **為何關鍵**：這些代理管理任務流，處理複雜邏輯如診斷並行分析或修復迭代。
   - **說明建議**：說明 SREWorkflow 如何使用 ParallelAgent 並行查詢 Loki/Tempo/Mimir，並定義 max_iterations 以避免無限循環。

### 5. **互動與通訊機制 (Interaction and Communication Mechanisms)**
   - **必須定義**：共享會話狀態 (session.state)、LLM 驅動轉移 (transfer_to_agent)、顯式調用 (AgentTool) 和事件 (Events) 作為通訊單位。
   - **為何關鍵**：確保代理間無縫協作，避免緊耦合，支持被動 (狀態讀寫) 和主動 (轉移/調用) 通訊。
   - **說明建議**：描述如何使用 session.state 儲存診斷結果，並在高風險操作中使用 HumanApprovalTool 實現 HITL。

### 6. **狀態與記憶管理 (State and Memory Management)**
   - **必須定義**：短期記憶 (Session Service，如 DatabaseSessionService for PostgreSQL)、長期記憶 (MemoryProvider，如 Weaviate for RAG) 和狀態作用域 (session/user/app)。
   - **為何關鍵**：維持上下文連續性，支持生產級持久化和多實例部署。避免使用 InMemorySessionService 在生產環境。
   - **說明建議**：定義 Unified Memory 層，強調自訂 Provider 模式，並說明如何使用 after-agent 回調自動更新記憶庫。

### 7. **事件與回調 (Events and Callbacks)**
   - **必須定義**：事件作為執行步驟 (e.g., escalate=True 以終止循環)和回調鉤子 (e.g., before_model_callback for 輸入驗證、before_tool_callback for 工具控制)。
   - **為何關鍵**：事件驅動架構支持模組化和錯誤處理，回調提升安全性和自訂化。
   - **說明建議**：說明事件總線 (EventBus) 如何處理代理間訊息，並定義回調用於認證強化或錯誤恢復。

### 8. **評估與可觀測性 (Evaluation and Observability)**
   - **必須定義**：評估框架 (AgentEvaluator、軌跡/最終回應評估)、可觀測性 (OpenTelemetry 追蹤、指標如 latency/token usage) 和監控模式。
   - **為何關鍵**：確保代理可靠性、成本控制和除錯，支持 CI/CD 整合。
   - **說明建議**：整合 LGTM Stack，定義 Grafana 儀表板追蹤 LLM 跨度，並說明評估管線如何測量診斷準確率。

### 9. **錯誤處理與韌性 (Error Handling and Resilience)**
   - **必須定義**：斷路器 (Circuit Breaker)、降級策略 (Fallbacks)、錯誤恢復工具和 SLO (e.g., p99 latency < 500ms)。
   - **為何關鍵**：生產級系統需處理故障，避免級聯效應。
   - **說明建議**：定義 recover_from_error 工具，並整合 Service Mesh (e.g., Istio) for mTLS。

### 10. **部署與擴展 (Deployment and Extensibility)**
   - **必須定義**：部署目標 (e.g., Kubernetes/Cloud Run)、Provider 模式 (e.g., AuthProvider) 和擴展點 (e.g., 自訂 SessionService)。
   - **為何關鍵**：ADK 支持本地 (adk web) 到雲端 (Vertex AI) 部署，強調無狀態和可插拔設計。
   - **說明建議**：提供配置範例 (YAML) 和漸進演進路徑，從 MVP 到聯邦化。