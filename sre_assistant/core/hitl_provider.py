
# HITL Provider 載入器：讀取 providers.yaml，供工具在 request_credential 時引用
from __future__ import annotations
from typing import Dict, Any, List, Optional
import os, yaml, pathlib

DEFAULT_PATH = os.getenv("HITL_PROVIDERS_PATH", "sre_assistant/hitl/providers.yaml")

def load_providers(path: Optional[str] = None) -> List[Dict[str,Any]]:
    """載入 provider 清單；若檔案不存在返回空陣列。"""
    p = pathlib.Path(path or DEFAULT_PATH)
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return data.get("providers", []) if isinstance(data, dict) else []

def get_provider(provider_id: str, path: Optional[str] = None) -> Optional[Dict[str,Any]]:
    """
    2025-08-22 03:37:34Z
    函式用途：`get_provider` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `provider_id`：參數用途請描述。
    - `path`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    for p in load_providers(path):
        if p.get("id") == provider_id:
            return p
    return None