
# SRE Assistant (ADK)

ADK 驅動的智慧 SRE 助理。以單一協調器代理，結合診斷/修復/覆盤專家與顯式工具，支援 HITL、RAG、真連接 Prometheus/K8s/Grafana，並內建 ADK Web Dev UI。

## 快速開始
```bash
make dev opt adk
make api         # 啟動 REST API → http://localhost:8000
make adk-web     # 啟動 ADK Dev UI → http://localhost:8080
```

### 重要環境變數
- `SESSION_BACKEND=memory|db`，`SESSION_DB_URI=sqlite:///./sessions.db`。
- `PROM_URL`、`GRAFANA_URL`、`GRAFANA_TOKEN`、`KUBECONFIG|K8S_IN_CLUSTER`、`K8S_NS`、`K8S_DEPLOY`。
- `RAG_CORPUS` 或 `PG_DSN`（pgvector）。

## 主要能力
- 對話：`/api/v1/chat`，或 SSE：`/api/v1/chat_sse`、`/api/v1/resume_sse`。
- HITL：工具內觸發 `request_credential`，前端回傳 `FunctionResponse` 後續跑。
- Dev UI：檢視 Sessions、Events、State、Tools 與即時互動。

## 測試與驗收
```bash
make test        # 單元與非 e2e
make e2e         # 真連接 E2E（需設定環境）
make accept      # 一鍵驗收（v14.1）
```

## 文件
- `SPEC.md`、`docs/ADK_WEB_UI.md`、`docs/ACCEPTANCE_V14_1.md`
- `AGENT.md`、`TESTING_GUIDE.md`、`DEVELOPMENT_SETUP.md`


## A2A（Agent-to-Agent）
```bash
make a2a-expose   # 暴露本地 DiagnosticExpert 為 A2A 服務（:8001）
make a2a-consume  # 範例：從主協調器建立 RemoteA2aAgent
# 驗收：GET http://localhost:8001/.well-known/agent.json
```

## Kubernetes 滾動重啟
- 模組：`sre_assistant/tools/k8s_rollout.py`，先 RBAC 預檢，再觸發 rollout 並輪詢完成。
- 需變數：`KUBECONFIG` 或 `K8S_IN_CLUSTER=true`。

## GCP Observability
- 檔案：`sre_assistant/core/telemetry_gcp.py`、`docs/GCP_OBSERVABILITY.md`
- 啟動：設定 `GCP_OBS_ENABLED=true` 與必要憑證與專案變數。


## A2A（ADK 官方）
- 暴露：使用 `sre_assistant/adk_app/a2a_expose.py:create_app(agent)` 取得 ASGI app，由 Uvicorn 掛載。
- 消費：使用 `sre_assistant/adk_app/a2a_consume.py:get_remote_agent(endpoint)` 取得 `RemoteA2aAgent`。
- 不要自行定義或維護 gRPC/proto。

## 長任務狀態
- 改以 `ToolContext.session.state['lr_ops']` 儲存；HITL API 讀寫 Session 狀態，支援多副本。

## 設定檔說明
- `adk.yaml`：**代理行為**設定（模型、工具白名單、需審批清單、安全策略）。
- `adk_config.yaml`：**開發工具/Dev UI** 設定（Web Dev UI、Runner 旗標）。
> 可保留分離設計；若要合併，請將 `web/features` 與 `runner` 區塊搬至 `adk.yaml` 的 `dev_ui` 與 `runner` 節點，並更新讀取邏輯。

### ADK SessionService 導向
- 於生產環境請安裝並使用 **google.adk.sessions.DatabaseSessionService**；程式已自動導向官方實作。
- 未安裝時退回本地最小實作，僅供開發測試。

### HITL 閉環
- `k8s_long_running._poll_restart()` 現已呼叫 `ctx.get_auth_response(...)` 以取得核可/拒絕結果，並更新 `Session.state['lr_ops']`。

### 協調器自動載入設定（adk.yaml）
- 模型：`agent.model`。
- 迭代上限：`runner.max_iterations`。未設定則使用環境變數 `ADK_MAX_ITER` 或預設 10。
- 工具清單：`agent.tools_allowlist`。若留空則載入所有已註冊工具。
- 在執行前會套用「政策閘包裝器」進行靜態拒絕，對齊 before_tool_callback 的職責。

### 政策閘 + HITL 自動注入
- 風險等級達門檻（預設 `POLICY_HITL_THRESHOLD=High`）或屬於 `tools_require_approval` 清單時，政策閘會：
  1) 嘗試呼叫工具的 `ToolContext.request_credential(...)` 觸發前端表單；
  2) 拋出 `HitlPendingError` 阻斷執行，待前端核可後再由使用者重試或長任務續跑。

### Dev UI 工具清單
- 端點：`GET /api/v1/tools/effective` 會回傳實際可用工具與是否需要核可欄位，供前端選單渲染。

## 專案主入口（ADK 模式）
- **sre_assistant/adk_app/runtime.py**：讀取 `adk.yaml`、載入工具、建立協調器 RUNNER，並提供 `get_web_app()` 供 ADK Web Dev UI 掛載。
- **備援**：`sre_assistant/core/assistant.py` 為「非 ADK 模式」協調器，僅供除錯與教學，生產不建議使用。

## 入口點
- **ADK 模式主入口**：`sre_assistant/adk_app/runtime.py`（建構 RUNNER）。
- API 啟動：`sre_assistant/server/app.py`（FastAPI + SSE），內部引用 `runtime.RNNER`。
- 備援協調器：`sre_assistant/core/assistant.py` 僅供非 ADK 情境下本地開發測試。

## 專家與 AgentTool
- `experts/experts.py` 定義 Diagnostic/Remediation/Postmortem/Config 四個專家，以 `AgentTool` 掛載到主代理。
- 工具適配層：`adapters/adk_runtime.py` 將函式工具轉為 ADK `FunctionTool/LongRunningFunctionTool`。
