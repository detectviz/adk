
# -*- coding: utf-8 -*-
# 簡易 API Key 認證與授權（以 DB 表 api_keys 為準）
from __future__ import annotations
from fastapi import Header, HTTPException
from ..core.persistence import DB

async def auth_dep(x_api_key: str = Header(default="")) -> str:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key")
    # 這裡簡化：直接查角色（實務應建立快取）
    # 若查無則 401；此處示例略過 DB 查，返回來自 Header 的 key
    return x_api_key
