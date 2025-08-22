
# 檔案：sre_assistant/adk_app/assembly.py
# 角色：裝配協調器所需的工具白名單，從 sub_agents/*/tools.py 自動彙總。
from __future__ import annotations
import importlib, pkgutil

def gather_subagent_tool_allowlist() -> set[str]:
    """
    {ts}
    函式用途：掃描 `sub_agents.*.tools` 模組並彙總工具白名單。
    參數說明：無。
    回傳：工具名稱集合（去重後）。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    allow = set()
    # 逐一嘗試載入已知子代理
    for name in ("diagnostic","remediation","postmortem","config"):
        mod_name = f"sub_agents.{name}.tools"
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, "list_tools"):
                for t in mod.list_tools():
                    if isinstance(t, str):
                        allow.add(t)
        except Exception:
            continue
    return allow
