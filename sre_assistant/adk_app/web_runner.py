
from __future__ import annotations
def get_web_app():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`get_web_app` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    try:
        from google.adk.runners.web_runner import WebRunner
    except Exception as e:
        raise RuntimeError("找不到 ADK WebRunner，請確認環境") from e
    return WebRunner().get_asgi_app()