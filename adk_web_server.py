
from __future__ import annotations
import os
def start_dev_ui(host: str = "0.0.0.0", port: int = 8088):
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`start_dev_ui` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `host`：參數用途請描述。
    - `port`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    try:
        from google.adk.dev.web_ui import start_adk_web  # 依實際 ADK 版本調整
    except Exception as e:
        raise RuntimeError("找不到 ADK Web Dev UI，請確認安裝 google-adk") from e
    start_adk_web(host=host, port=port, config_path=os.getenv("ADK_CONFIG","adk_config.yaml"))