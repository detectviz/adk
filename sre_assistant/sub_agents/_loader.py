
# -*- coding: utf-8 -*-
# 通用載入器：讀取 experts/<name>.yaml 輸出 PROMPT 與 TOOLS_ALLOWLIST
from __future__ import annotations
import os, yaml

def _load_expert_yaml(name: str) -> dict:
    """
    自動產生註解時間：{ts}
    函式用途：載入專家設定檔（experts/<name>.yaml）。
    參數說明：
    - `name`：專家名稱（例如 diagnostic）。
    回傳：Python 字典，若檔案不存在則回傳空字典。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    root = os.getenv("SRE_ASSISTANT_ROOT", os.getcwd())
    paths = [
        os.path.join(root, "experts", f"{name}.yaml"),
        os.path.join(os.path.dirname(__file__), "..", "..", "experts", f"{name}.yaml"),
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    return {}

def get_prompt(name: str) -> str:
    """
    函式用途：回傳指定專家的 prompt 字串。
    參數說明：`name` 專家名稱。
    回傳：字串，若無設定則提供安全預設。
    """
    data = _load_expert_yaml(name)
    return (data.get("prompt") or "你是此子代理的專家。請遵守工具合約與安全策略。").strip()

def get_tools_allowlist(name: str) -> list[str]:
    """
    函式用途：回傳指定專家的工具白名單。
    參數說明：`name` 專家名稱。
    回傳：字串陣列。
    """
    data = _load_expert_yaml(name)
    lst = data.get("tools_allowlist") or []
    return list(lst)
