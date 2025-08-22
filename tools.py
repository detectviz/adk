
# 共用工具轉接（非詳實定義；實際工具仍於 sre_assistant/tools 之下）。
from __future__ import annotations
def list_shared_tools()->list[str]:
    """
    {ts}
    函式用途：回傳專案中共用的工具名稱列表，供 Dev UI 顯示或 ADK 掛載。
    參數說明：無。
    回傳：工具名稱陣列。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    return ["rag_search","ingest_text","K8sRolloutRestartLongRunningTool"]
