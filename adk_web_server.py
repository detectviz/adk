
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ADK Web Dev UI 啟動器
# 說明：
# - 以官方 ADK Web 介面啟動開發 UI（會啟動一個內建的 FastAPI/Starlette 伺服器）
# - UI 用於檢視 Session、事件、狀態與工具 Schema，並可直接與 Agent 互動
# - 僅供開發/測試環境使用，不建議在生產環境暴露
from __future__ import annotations
import os

# 匯入 ADK Web 啟動函式（依官方文件）
from google.adk.web import start_dev_ui  # 官方提供的 Web Dev UI 啟動器

# 匯入我們的 ADK 協調器（LoopAgent）
from sre_assistant.adk_app.coordinator import coordinator

def main():
    """啟動 ADK Web Dev UI。"""
    host = os.getenv("ADK_WEB_HOST", "0.0.0.0")
    port = int(os.getenv("ADK_WEB_PORT", "8080"))
    title = os.getenv("ADK_WEB_TITLE", "SRE Assistant - ADK Dev UI")
    # 依需求載入可選設定
    start_dev_ui(
        agent=coordinator,           # 直接接我們的主協調器
        host=host,
        port=port,
        title=title,
        dev_mode=True,               # 啟用開發模式（展示完整除錯資訊）
        hot_reload=True,             # 程式碼變更即時反映
        enable_tools_panel=True,     # 工具清單/Schema/測試面板
        enable_session_inspector=True,
        enable_event_viewer=True,
        enable_state_debugger=True
    )

if __name__ == "__main__":
    main()
