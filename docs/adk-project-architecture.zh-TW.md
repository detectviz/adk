# ADK 專案總覽與架構

參考資料：https://github.com/google/adk-python/blob/main/contributing/adk_project_overview_and_architecture.md

Google Agent Development Kit (ADK) for Python

## 核心哲學與架構

- **程式碼優先 (Code-First)**：所有東西都在 Python 程式碼中定義，以便於版本控制、測試和 IDE 支援。避免使用圖形化介面 (GUI) 來定義邏輯。

- **模組化與組合 (Modularity & Composition)**：我們透過組合多個更小、更專業的 Agent 來建立複雜的多 Agent 系統。

- **部署環境無關 (Deployment-Agnostic)**：Agent 的核心邏輯與其部署環境分離。同一個 `agent.py` 可以在本機執行以進行測試、透過 API 提供服務，或部署到雲端。

## 基礎抽象層 (我們的詞彙)

- **Agent**：藍圖。它定義了 Agent 的身份、指令和工具。它是一個宣告式的設定物件。

- **Tool (工具)**：一種能力。一個 Agent 可以呼叫來與世界互動的 Python 函式 (例如，搜尋、API 呼叫)。

- **Runner (執行器)**：引擎。它負責協調「思考-行動」(Reason-Act) 的循環、管理大型語言模型 (LLM) 的呼叫，並執行工具。

- **Session (會話)**：對話狀態。它為單一、連續的對話保留歷史記錄。

- **Memory (記憶)**：跨不同會話的長期記憶。

- **Artifact Service (產物服務)**：管理非文字資料，如檔案。

## 標準專案結構

請遵守此結構，以確保與 ADK 工具的相容性。

```bash
my_adk_project/
└── src/
    └── my_app/
        ├── agents/
        │   ├── my_agent/
        │   │   ├── __init__.py   # 必須包含: from . import agent \
        │   │   └── agent.py      # 必須包含: root_agent = Agent(...) \
        │   └── another_agent/
        │       ├── __init__.py
        │       └── agent.py\
```

`agent.py`：必須定義 Agent 並將其指派給名為 `root_agent` 的變數。這是 ADK 工具找到它的方式。

`__init__.py`：在每個 Agent 目錄中，它必須包含 `from . import agent` 以便讓 Agent 可以被發現。

## 本機開發與除錯

- **互動式介面 (adk web)**：這是我們主要的除錯工具。它是一個解耦的系統：
    - **後端**：一個用 `adk api_server` 啟動的 FastAPI 伺服器。
    - **前端**：一個連接到後端的 Angular 應用程式。
    - 使用「Events」分頁來檢查完整的執行追蹤 (提示、工具呼叫、回應)。

- **命令列介面 (adk run)**：用於在終端機中進行快速、無狀態的功能檢查。

- **程式化 (pytest)**：用於編寫自動化的單元和整合測試。

## API 層 (FastAPI)

我們使用 FastAPI 將 Agent 作為生產級 API 公開。

- `get_fast_api_app`：這是 `google.adk.cli.fast_api` 中的關鍵輔助函式，可以從我們的 Agent 目錄建立一個 FastAPI 應用程式。

- **標準端點**：產生的應用程式包含標準路由，如 `/list-apps` 和 `/run_sse` (用於串流回應)。網路傳輸格式為駝峰式命名 (camelCase)。

- **自訂端點**：我們可以將自己的路由 (例如 `/health`) 添加到輔助函式返回的 app 物件中。

```python
from google.adk.cli.fast_api import get_fast_api_app
app = get_fast_api_app(agent_dir="./agents")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

## 部署到生產環境

`adk cli` 提供了 `adk deploy` 命令，可以部署到 Google Vertex Agent Engine、Google Cloud Run、Google GKE。

## 測試與評估策略

測試是分層的，像金字塔一樣。

### 第一層：單元測試 (底層)

- **測試什麼**：獨立測試單個 `Tool` 函式。
- **如何測試**：在 `tests/test_tools.py` 中使用 `pytest`。驗證確定性邏輯。

### 第二層：整合測試 (中層)

- **測試什麼**：測試 Agent 的內部邏輯以及與工具的互動。
- **如何測試**：在 `tests/test_agent.py` 中使用 `pytest`，通常會模擬 (mock) LLM 或外部服務。

### 第三層：評估測試 (頂層)

- **測試什麼**：使用真實的 LLM 評估端到端的表現。這關乎品質，而不僅僅是通過/失敗。
- **如何測試**：使用 ADK 評估框架。
    - **測試案例**：建立包含輸入和參考 (預期的工具呼叫和最終回應) 的 JSON 檔案。
    - **指標**：`tool_trajectory_avg_score` (它是否正確使用工具？) 和 `response_match_score` (最終答案是否良好？)。
- **如何執行**：透過 `adk web` (UI)、`pytest` (用於 CI/CD) 或 `adk eval` (CLI) 執行。
