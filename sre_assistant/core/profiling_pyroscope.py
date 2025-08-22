
# Pyroscope 整合（Profiles）
# 目的：在 Python 進程中啟用 CPU/Wall/Alloc 等採樣，將結果送至 Pyroscope 伺服器
from __future__ import annotations
import os

def init_pyroscope() -> None:
    """初始化 Pyroscope 代理（若已安裝）。未安裝則靜默忽略。"""
    try:
        import pyroscope
    except Exception:
        return
    server = os.getenv("PYROSCOPE_SERVER", "http://localhost:4040")
    app_name = os.getenv("PYROSCOPE_APP_NAME", "sre-assistant")
    auth_token = os.getenv("PYROSCOPE_AUTH_TOKEN", "")
    pyroscope.configure(
        application_name=app_name,
        server_address=server,
        auth_token=auth_token or None,
        tags={"env": os.getenv("ENV","dev")},
        detect_subprocesses=True,
        oncpu=True, gil_only=False,
        enable_logging=False,
    )
