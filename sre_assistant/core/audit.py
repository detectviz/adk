
# -*- coding: utf-8 -*-
# 檔案：sre_assistant/core/audit.py
# 角色：提供審計寫入的抽象化函式，HITL/決策等紀錄集中於此。
from __future__ import annotations

def write_hitl_audit(db, function_call_id: str, approved: bool, approver: str, reason: str) -> None:
    """
    自動產生註解時間：{ts}
    函式用途：寫入 HITL（人工在迴圈）審批事件到資料庫；若無 db 物件則靜默跳過。
    參數說明：
    - `db`：資料庫執行介面，需具備 `execute(sql, params)` 方法。
    - `function_call_id`：工具呼叫識別。
    - `approved`：是否核可。
    - `approver`：核可者識別。
    - `reason`：補充說明。
    回傳：無。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    if not db or not hasattr(db, 'execute'):
        return
    try:
        db.execute(
            "INSERT INTO hitl_audits(function_call_id, approved, approver, reason) VALUES (%s,%s,%s,%s)",
            (function_call_id, approved, approver, reason),
        )
    except Exception:
        # 保守處理：審計寫入失敗不影響主流程
        return
