# 檔案：sre_assistant/core/auth.py
# 角色：API Key 驗證；devkey 僅在 ALLOW_DEV_KEY=true 時啟用。
import os
from fastapi import Header, HTTPException

def require_api_key(x_api_key: str = Header(default="", alias="X-API-Key")) -> str:
    """
    函式用途：驗證 API Key。若 ALLOW_DEV_KEY=true 則允許 'devkey' 作為開發後門。
    參數說明：`x_api_key`：HTTP Header 'X-API-Key'。
    回傳：key 字串。
    """
    allow_dev = os.getenv("ALLOW_DEV_KEY","false").lower() in ("1","true","yes")
    if not x_api_key:
        raise HTTPException(401, "missing X-API-Key")
    if x_api_key == "devkey" and not allow_dev:
        raise HTTPException(403, "devkey disabled")
    return x_api_key
