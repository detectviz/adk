# 根代理組裝（符合 ADK 導覽結構）。
# 這裡僅做薄封裝，真正實作仍在 `sre_assistant/adk_app/runtime.py` 所提供的 RUNNER。
from __future__ import annotations

def get_root_agent():
    """
    {ts}
    函式用途：回傳根代理實例或可供 ADK Runner 掛載的描述。
    參數說明：無。
    回傳：根代理（示意：直接回傳 RUNNER.main_agent）。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    try:
        from sre_assistant.adk_app.runtime import RUNNER
        return getattr(RUNNER, "main_agent", RUNNER)
    except Exception:
        return None
