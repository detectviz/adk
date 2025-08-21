
# -*- coding: utf-8 -*-
# ADK Web Runner 封裝（選用）：
# - 當希望把 Dev UI 整合到既有 FastAPI 服務時，可使用 WebRunner.get_web_app()
# - 預設仍建議以 adk_web_server.py 獨立啟動 Dev UI；此檔作為擴充選項
from __future__ import annotations
import os
from typing import Any

try:
    from google.adk.runners import WebRunner
except Exception:
    WebRunner = None  # 若環境未安裝 web 變體，保留降級路徑

from .coordinator import coordinator

def get_dev_ui_app() -> Any:
    """回傳可掛載於 ASGI/FastAPI 的 Dev UI app（若可用）。"""
    if WebRunner is None:
        raise RuntimeError("未安裝 google-adk[web] 套件，無法使用 WebRunner")
    runner = WebRunner(
        agent=coordinator,
        app_name=os.getenv("APP_NAME","sre-assistant"),
        enable_ui=True,
        ui_config={
            "theme": "dark",
            "show_metrics": True,
            "show_events": True,
        }
    )
    return runner.get_web_app()
