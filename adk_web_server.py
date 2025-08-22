from __future__ import annotations
import os
def start_dev_ui(host: str = "0.0.0.0", port: int = 8088):
    
    try:
        from google.adk.dev.web_ui import start_adk_web  # 依實際 ADK 版本調整
    except Exception as e:
        raise RuntimeError("找不到 ADK Web Dev UI，請確認安裝 google-adk") from e
    start_adk_web(host=host, port=port, config_path=os.getenv("ADK_CONFIG","adk_config.yaml"))