
# -*- coding: utf-8 -*-
# 以 ADK 官方 RemoteA2aAgent 消費遠端 Agent（不要手寫 gRPC）。
from __future__ import annotations

try:
    from google.adk.a2a import RemoteA2aAgent  # 官方 API（以實際版本為準）
except Exception:
    RemoteA2aAgent = None

def get_remote_agent(endpoint: str):
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`get_remote_agent` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `endpoint`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    if RemoteA2aAgent is None:
        raise RuntimeError("缺少 google-adk 套件，無法使用 RemoteA2aAgent")
    return RemoteA2aAgent(endpoint)