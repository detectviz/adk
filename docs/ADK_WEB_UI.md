
# ADK Web Dev UI 整合與啟動說明

## 依賴安裝
```bash
make adk
python -m pip install 'google-adk[web]'
```

## 獨立啟動 Web Dev UI
```bash
make adk-web
# 或
python adk_web_server.py
```

環境變數：
- `ADK_WEB_HOST`（預設 0.0.0.0）
- `ADK_WEB_PORT`（預設 8080）
- `ADK_WEB_TITLE`（預設 "SRE Assistant - ADK Dev UI"）

## 與既有 FastAPI 併行啟動（開發模式）
```bash
make dev-full
# 會在 8000 提供 REST API，在 8080 提供 ADK Dev UI
```

## 功能面板
- 對話面板、工具探索、Session 管理、事件串流檢視、狀態除錯、指標總覽。

> 注意：此 UI 僅供開發/測試；不要直接暴露於生產網路。
