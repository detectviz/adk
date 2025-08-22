
# 回放/重跑：從 decisions 表載入步驟 JSON，建立新決策執行相同工具。
from __future__ import annotations
import json, time, uuid
from typing import Dict, Any, List
from .persistence import DB
from .intents import Step, StepResult, SCHEMA_VERSION

def parse_steps(raw_json: str) -> List[Step]:
    """
    2025-08-22 03:37:34Z
    函式用途：`parse_steps` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `raw_json`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    import pydantic
    data = json.loads(raw_json or "[]")
    steps = []
    for d in data:
        steps.append(Step(tool=d.get("tool"), args=d.get("args") or {}, require_approval=d.get("require_approval", False)))
    return steps

def get_decision(decision_id: int) -> Dict[str, Any] | None:
    """
    2025-08-22 03:37:34Z
    函式用途：`get_decision` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `decision_id`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    items = DB.list_decisions(limit=1, offset=0)
    # 簡化：提供單筆查詢需追加方法，這裡直接掃描最近決策
    for it in items:
        if it["id"] == decision_id:
            return it
    # 若不在最近清單，可擴充 DB 方法；此示例先返回 None
    return None