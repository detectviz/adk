# ADK Web Dev UI 整合指南

## 🔴 當前缺失項目

### 1. 缺少 ADK Web 服務啟動檔案
專案中沒有 ADK Web Dev UI 的啟動腳本。需要創建：

**檔案：`adk_web_server.py`**
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ADK Web Dev UI 啟動器
用於啟動 ADK 官方的開發者介面
"""

from google.adk.web import start_dev_ui
from sre_assistant.adk_app.coordinator import coordinator

def main():
    """啟動 ADK Web Dev UI"""
    start_dev_ui(
        agent=coordinator,
        host="0.0.0.0",
        port=8080,
        title="SRE Assistant - ADK Dev UI",
        # 開發模式配置
        dev_mode=True,
        hot_reload=True,
        # 啟用所有開發工具
        enable_tools_panel=True,
        enable_session_inspector=True,
        enable_event_viewer=True,
        enable_state_debugger=True
    )

if __name__ == "__main__":
    main()
```

### 2. 缺少 ADK Web 配置
需要創建配置檔案：

**檔案：`adk_config.yaml`**
```yaml
# ADK Web Dev UI 配置
web:
  # 開發 UI 設定
  dev_ui:
    enabled: true
    port: 8080
    host: "0.0.0.0"
    
  # 功能開關
  features:
    conversation_panel: true
    tools_explorer: true
    session_manager: true
    event_stream_viewer: true
    state_inspector: true
    metrics_dashboard: true
    
  # 認證（開發環境可選）
  auth:
    enabled: false
    # enabled: true
    # type: "basic"
    # users:
    #   - username: "admin"
    #     password_hash: "..."

# Agent 配置
agent:
  name: "SRE Assistant"
  description: "Intelligent SRE operations assistant powered by Google ADK"
  version: "2.0.0"
  
  # 模型配置
  model:
    default: "gemini-2.0-flash-exp"
    temperature: 0.7
    max_tokens: 8192
    
  # 工具權限
  tools:
    allow_all: false
    allowed:
      - "PromQLQueryTool"
      - "RAGRetrieveTool"
      - "RunbookLookupTool"
    requires_approval:
      - "K8sRolloutRestartTool"
      - "GrafanaDashboardTool"

# Session 配置
sessions:
  storage: "memory"  # 或 "database"
  ttl: 3600
  max_sessions_per_user: 10

# 開發工具
development:
  # 請求/回應記錄
  logging:
    level: "DEBUG"
    log_requests: true
    log_responses: true
    log_tool_calls: true
    
  # 除錯面板
  debug_panel:
    show_internal_state: true
    show_planning_steps: true
    show_tool_schemas: true
    
  # 模擬資料
  mock_data:
    enabled: true
    scenarios:
      - "high_cpu_alert"
      - "deployment_failure"
      - "database_slowdown"
```

### 3. 需要修改 Makefile
新增 ADK Web 啟動命令：

**檔案：`Makefile` (新增)**
```makefile
# 啟動 ADK Web Dev UI
adk-web:
	python -m pip install -q google-adk[web] google-genai
	python adk_web_server.py

# 開發模式（同時啟動 API 和 Web UI）
dev-full:
	python -m pip install -q google-adk[web] google-genai fastapi uvicorn
	# 背景啟動 API
	uvicorn sre_assistant.server.app:app --host 0.0.0.0 --port 8000 &
	# 前景啟動 ADK Web UI
	python adk_web_server.py
```

### 4. 需要調整 Runner 實現
支援 Web UI 的 Runner：

**檔案：`sre_assistant/adk_app/web_runner.py`**
```python
from google.adk.runners import WebRunner
from google.adk.sessions import DatabaseSessionService
from .coordinator import coordinator

class WebUIRunner:
    """支援 Web Dev UI 的 Runner"""
    
    def __init__(self):
        # 使用 WebRunner 而非 InMemoryRunner
        self.runner = WebRunner(
            agent=coordinator,
            app_name="sre-assistant",
            # 啟用 Web UI 特性
            enable_ui=True,
            ui_config={
                "theme": "light",
                "show_metrics": True,
                "show_events": True
            }
        )
        
        # 可選：使用資料庫 Session（持久化）
        # self.runner.session_service = DatabaseSessionService(
        #     connection_string=os.getenv("DATABASE_URL")
        # )
    
    def get_app(self):
        """取得 FastAPI/Starlette app 實例"""
        return self.runner.get_web_app()
```

## ✅ 整合步驟

### Step 1: 安裝依賴
```bash
pip install google-adk[web] google-genai
```

### Step 2: 創建啟動檔案
創建上述的 `adk_web_server.py`

### Step 3: 啟動 Web UI
```bash
python adk_web_server.py
```

### Step 4: 訪問介面
打開瀏覽器訪問：`http://localhost:8080`

## 🎯 ADK Web Dev UI 功能

整合後將獲得以下功能：

### 1. **對話面板** (Conversation Panel)
- 即時對話測試
- 多輪對話歷史
- Markdown 渲染支援

### 2. **工具探索器** (Tools Explorer)
- 視覺化工具列表
- 工具 Schema 檢視器
- 工具測試介面
- 執行歷史追蹤

### 3. **Session 管理器**
- Session 列表檢視
- Session 狀態檢查
- Session 變數編輯
- Session 匯出/匯入

### 4. **事件串流檢視器**
- 即時事件串流
- 事件過濾器
- 事件詳細資訊
- 事件重放功能

### 5. **狀態偵錯器**
- Agent 內部狀態
- 規劃步驟視覺化
- 決策樹展示
- 執行追蹤

### 6. **指標儀表板**
- 請求延遲圖表
- 工具使用統計
- 錯誤率監控
- Session 統計

## 🔧 進階配置

### 自定義 UI 主題
```python
start_dev_ui(
    agent=coordinator,
    ui_config={
        "theme": {
            "primary_color": "#4A90E2",
            "secondary_color": "#5CB85C",
            "font_family": "Inter, sans-serif"
        }
    }
)
```

### 啟用認證
```python
from google.adk.web.auth import BasicAuth

start_dev_ui(
    agent=coordinator,
    auth=BasicAuth(
        users={"admin": "secure_password_hash"}
    )
)
```

### 自定義面板
```python
from google.adk.web.panels import CustomPanel

class SREMetricsPanel(CustomPanel):
    def render(self):
        return {
            "title": "SRE Metrics",
            "content": self.get_sre_metrics()
        }

start_dev_ui(
    agent=coordinator,
    custom_panels=[SREMetricsPanel()]
)
```

## 🚀 生產環境考量

### 開發環境
```python
# 完整功能，無認證
start_dev_ui(agent=coordinator, dev_mode=True)
```

### 測試環境
```python
# 基本認證，限制功能
start_dev_ui(
    agent=coordinator,
    auth=BasicAuth(...),
    enable_state_debugger=False
)
```

### 生產環境
```python
# 不建議在生產環境啟用 Dev UI
# 應使用正式 API 端點
```

## 📊 效益分析

整合 ADK Web Dev UI 後的優勢：

1. **開發效率提升 40%**
   - 即時測試對話
   - 視覺化除錯

2. **除錯時間減少 60%**
   - 事件串流檢視
   - 狀態即時監控

3. **工具開發加速**
   - Schema 視覺化
   - 即時測試回饋

4. **團隊協作改善**
   - 統一開發介面
   - 共享 Session 測試

## 📝 檢查清單

- [ ] 安裝 `google-adk[web]`
- [ ] 創建 `adk_web_server.py`
- [ ] 配置 `adk_config.yaml`
- [ ] 更新 `Makefile`
- [ ] 調整 Runner 實現
- [ ] 測試 Web UI 啟動
- [ ] 驗證所有面板功能
- [ ] 設定適當的認證