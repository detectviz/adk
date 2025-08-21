
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
        aid = DB.insert_approval(tool, args)
        return Approval(id=aid, tool=tool, args=args, status="pending")

    def get(self, aid: int) -> Approval | None:
        a = DB.get_approval(aid)
        if not a: return None
        return Approval(id=a["id"], tool=a["tool"], args=a["args"], status=a["status"])

    def decide(self, aid: int, status: str, decided_by: str, reason: str | None = None) -> Approval:
        a = DB.decide_approval(aid, status, decided_by, reason)
        return Approval(id=a["id"], tool=a["tool"], args=a["args"], status=a["status"])

APPROVALS = ApprovalStore()
