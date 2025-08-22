
# -*- coding: utf-8 -*-
# 簡易 API Key 認證與授權（以 DB 表 api_keys 為準）
from __future__ import annotations
from fastapi import Header, HTTPException
from ..core.persistence import DB

async def auth_dep(x_api_key: str = Header(default="")) -> str:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`auth_dep` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `x_api_key`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key")
    # 這裡簡化：直接查角色（實務應建立快取）
    # 若查無則 401；此處示例略過 DB 查，返回來自 Header 的 key
    return x_api_key


# 開發後門：僅在 DEV_API_KEY_ENABLED=true 時允許接受 devkey（請勿在生產環境啟用）
import os
DEV_KEY_ENABLED = os.getenv("DEV_API_KEY_ENABLED","false").lower() in ("1","true","yes")
DEV_KEY = os.getenv("DEV_API_KEY","devkey")

async def auth_dep_dev(x_api_key: str = Header(default="")) -> str:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`auth_dep_dev` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `x_api_key`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    if DEV_KEY_ENABLED and x_api_key == DEV_KEY:
        return "dev"
    return await auth_dep(x_api_key)  # 回退到正式驗證