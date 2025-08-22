
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


### 政策閘與 HITL（更新）
- 政策閘僅執行 **靜態拒絕與審計**，不再於外層自動觸發 HITL 或丟出例外。
- **HITL 門檻** 改為由 `adk.yaml.policy.risk_threshold` 定義，並由 **工具本身** 決定是否呼叫 `request_credential()`。
- SSE 事件 `adk_request_credential` 由工具觸發，迴圈不中斷；前端核可後由長任務輪詢續跑或使用者重試。

### 專家工具拆分
- 各專家（Diagnostic/Remediation/Postmortem/Config）之工具清單由 `adk.yaml.experts.<name>.tools_allowlist` 管理。


### Runtime 收斂與工具管理（對齊 ADK）
- 已移除自訂 `ToolRegistry`。所有工具改由 `runtime.py` 直接建立 `FunctionTool/LongRunningFunctionTool` 列表並傳入 `LlmAgent`。
- `runtime.build_runner_from_config(cfg)`：從 `adk.yaml` 載入模型、迭代上限與工具 allowlist，並組裝專家 AgentTool。


### 專家代理模組分拆
- 檔案：
  - `sre_assistant/experts/diagnostic.py`
  - `sre_assistant/experts/remediation.py`
  - `sre_assistant/experts/postmortem.py`
  - `sre_assistant/experts/config.py`
- 每個模組導出 `build_agent(tool_objs)`，會依 `adk.yaml.experts.<name>.model` 覆蓋主模型，並依 `experts.<name>.tools_allowlist` 取得工具。
- `runtime.py` 於啟動時載入工具物件後，呼叫各模組 `build_agent(...)`，再以 `AgentTool` 掛載到主代理。


### 專家 YAML 外掛化（experts/*.yaml）
- 每位專家的 `prompt/model/tools_allowlist/slo` 可在 `experts/*.yaml` 中集中管理，啟動時由 `runtime` 合併到 `adk.yaml`。
- 優先順序：`experts/*.yaml` 覆蓋 `adk.yaml.experts.*` 覆蓋 `agent.*`。

### Prometheus SLO 導出
- 執行 `make export-slo` 自動生成 `observability/slo_rules.yaml`。
- SLO 來源：`experts/*.yaml` 的 `slo` 欄位（例如 `p95_latency_seconds`、`success_rate_threshold`）。
- 指標需求：需暴露 `agent_request_duration_seconds_bucket` 與 `agent_requests_total`（本專案已在 SPEC 中定義）。


## Dev UI 與 HITL SSE 端到端
- 訂閱：`GET /api/v1/events`（SSE）
- 觸發：`POST /api/v1/hitl/mock_request`（產生 `adk_request_credential`）
- 審批：`POST /api/v1/hitl/approve`
- 簡易頁面：`server/static/devui.html` 可直接開啟驗證。


## 協調器自動工具掛載
- 系統會掃描 `sub_agents/*/tools.py` 的 `list_tools()`，彙總白名單並過濾可掛載工具。
- 實作：`sre_assistant/adk_app/assembly.py`、`adk_app/runtime.py` 的 `_filter_tools_by_subagents()`。

## Cloud Build 觸發器
- 使用 `deployment/cloudbuild.yaml` 與 `deployment/cloudbuild.trigger.json`。
- 變數：`_REGION`、`_TAG`、`_SERVICE`、`_REPO`、`_IMAGE`。
- 在 Cloud Build Triggers 匯入 `cloudbuild.trigger.json`，調整 github 值後啟用。

## 程式碼清理
- 執行 `python3 scripts/clean_dead_code.py` 檢視疑似未用模組。僅列印，請人工確認後再移除。


## A2A 對齊官方
- 已移除自訂 gRPC/proto。改為官方 `google.adk.a2a` 包裝：`adk_app/a2a_expose.py`、`adk_app/a2a_consume.py`。
- 不需 `a2a-gen`。

## HITL 機制
- 僅允許工具內呼叫 `tool_context.request_credential(...)` 觸發。
- API 層僅負責 SSE 事件與 FunctionResponse 回補，不再有外部政策閘。

## RBAC 與 devkey
- `rbac` 映射與 `tools_allowlist` 可在 `adk.yaml` 中配置。
- `ALLOW_DEV_KEY=true` 才允許 `devkey`。預設關閉。


## v15.7.6 重要變更
- 移除非 ADK 協調器與自訂 ToolRegistry/agents 目錄，統一由 `adk_app/runtime.py` 組裝。
- 移除 `core/otel_grpc.py` 與 `core/policy.py`，採用官方推薦：追蹤由 OTel 自動化，策略檢查在工具內執行。
- `k8s_long_running`：長任務狀態僅存於 `session.state`；HITL 觸發嚴格依 `adk.yaml` 與高風險命名空間。
- `runtime.py` 引入 `BuiltInPlanner` 的占位導入，保持對齊官方設計。


## v15.7.7 打包版
- 封裝自 `v15.7.6-clean` 並套用 v15.7.7 修正：移除 `sub_agents/**`，改讀 `experts/*.yaml`；HITL 判斷內聚於 `k8s_long_running.py`。


## v15.7.8 變更
- 全域移除樣板註解字樣。
- K8s 高風險命名空間改由 `adk.yaml.policy.high_risk_namespaces` 配置，預設 `['prod','production','prd']`。
- 新增 `docs/HARDCODE_AUDIT.md`，列出疑似硬編碼以供人工審核。
- 再次清理可能造成雙執行模式的殘留目錄（`sub_agents/` 等）。


### Cloud Build 環境變數注入
Cloud Run 部署時，Cloud Build 會以 substitutions 注入下列環境變數：
- `OTEL_EXPORTER_OTLP_ENDPOINT`（預設 `https://otel.googleapis.com:4317`）
- `GOOGLE_OTLP_AUTH=true`

可於 `deployment/cloudbuild.yaml` 的 `substitutions` 區塊調整 `_OTEL_ENDPOINT`。


### OpenTelemetry 初始化
- 啟用：預設開啟；可設 `OTEL_ENABLED=false` 關閉。
- 端點：由 `OTEL_EXPORTER_OTLP_ENDPOINT` 提供，Cloud Build 部署時會注入。
- Resource：`service.name` 來源優先序 `SERVICE_NAME` > `adk.yaml.agent.name` > `sre-assistant`；另設定 `cloud.provider=gcp`、`gcp.project_id`、`gcp.region`。

### experts.*.yaml 的 model 與 slo
- `experts/<name>.yaml` 可指定：
  - `model`: 例如 `gemini-2.0-pro`、`gemini-2.0-flash`
  - `slo`: 例如 `{ p95_response_ms: 2000 }`
- 由 `runtime.get_effective_models()` 與 `runtime.get_slo_targets()` 查詢，後續可用於裝配根代理與 SLO 守門。
