
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
    
    for p in load_providers(path):
        if p.get("id") == provider_id:
            return p
    return None