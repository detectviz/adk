
# -*- coding: utf-8 -*-
# HITL（Human-In-The-Loop）：以資料庫持久化審批請求。
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from .persistence import DB

@dataclass
class Approval:
    id: int
    tool: str
    args: Dict[str, Any]
    status: str

class ApprovalStore:
    def create(self, tool: str, args: Dict[str, Any]) -> Approval:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`create` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `tool`：參數用途請描述。
        - `args`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        aid = DB.insert_approval(tool, args)
        return Approval(id=aid, tool=tool, args=args, status="pending")

    def get(self, aid: int) -> Approval | None:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`get` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `aid`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        a = DB.get_approval(aid)
        if not a: return None
        return Approval(id=a["id"], tool=a["tool"], args=a["args"], status=a["status"])

    def decide(self, aid: int, status: str, decided_by: str, reason: str | None = None) -> Approval:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`decide` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `aid`：參數用途請描述。
        - `status`：參數用途請描述。
        - `decided_by`：參數用途請描述。
        - `reason`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        a = DB.decide_approval(aid, status, decided_by, reason)
        return Approval(id=a["id"], tool=a["tool"], args=a["args"], status=a["status"])

APPROVALS = ApprovalStore()