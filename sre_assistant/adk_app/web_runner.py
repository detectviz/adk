
from __future__ import annotations
def get_web_app():
    try:
        from google.adk.runners.web_runner import WebRunner
    except Exception as e:
        raise RuntimeError("找不到 ADK WebRunner，請確認環境") from e
    return WebRunner().get_asgi_app()
