# 消除分散硬編碼，集中處理優先序：環境變數 > adk.yaml > 預設。
from __future__ import annotations
import os, yaml
from typing import Any, Dict, List

def _load_yaml(path: str = "adk.yaml") -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

_YAML = _load_yaml()

def get(key: str, default: Any = None) -> Any:
    """
    函式用途：以 'a.b.c' 路徑取值。先看環境變數 ADK_A_B_C，再看 adk.yaml，最後回傳預設。
    參數：key：以點號分隔的設定路徑；default：預設值。
    回傳：對應設定值或預設值。
    """
    env_key = "ADK_" + key.replace(".", "_").upper()
    if env_key in os.environ:
        return os.environ[env_key]
    # 走 YAML 路徑
    cur = _YAML
    for part in key.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur

def get_list(key: str, default: List[str] | None = None) -> List[str]:
    """
    函式用途：取出字串清單類型的設定。
    支援以逗號分隔的環境變數覆蓋。
    """
    env_key = "ADK_" + key.replace(".", "_").upper()
    if env_key in os.environ:
        return [x.strip() for x in os.environ[env_key].split(",") if x.strip()]
    val = get(key, default or [])
    if isinstance(val, list):
        return [str(x) for x in val]
    return default or []
