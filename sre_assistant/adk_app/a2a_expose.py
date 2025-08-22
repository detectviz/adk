
# -*- coding: utf-8 -*-
# 以 ADK 官方 to_a2a 將本地 Agent 暴露為 A2A 端點（不要自行實作 gRPC/proto）。
from __future__ import annotations
import os

try:
    from google.adk.a2a import to_a2a  # 官方 API（以實際版本為準）
    from google.adk.agents import LoopAgent
except Exception as e:
    to_a2a = None
    LoopAgent = None

def create_app(agent: "LoopAgent"):
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`create_app` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `agent`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    if to_a2a is None or agent is None:
        raise RuntimeError("缺少 google-adk 套件或 agent 實例，無法建立 A2A 應用")
    # 回傳可由 Uvicorn/Gunicorn 掛載的 ASGI app
    return to_a2a(agent)