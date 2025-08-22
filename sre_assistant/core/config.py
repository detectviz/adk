
# adk.yaml 設定讀取輔助
from __future__ import annotations
from pathlib import Path
import yaml

def load_adk_config(path: str = "adk.yaml") -> dict:
    """
    2025-08-22 03:37:34Z
    函式用途：`load_adk_config` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `path`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _deep_merge(dst: dict, src: dict) -> dict:
    """遞迴合併字典，src 覆蓋 dst；僅支援 dict/list/標量（簡化版）。"""
    for k, v in (src or {}).items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst

def load_combined_config(base_path: str = "adk.yaml") -> dict:
    """載入主設定 adk.yaml，並將 experts/*.yaml 逐一合併到 `experts` 區塊。
    搜尋順序：
      1) 專案根目錄的 `experts/*.yaml`
      2) 程式內建的 `sre_assistant/experts/*.yaml`
    合併規則：同鍵以 experts/*.yaml 覆蓋 adk.yaml；未提供則保留原值。
    """
    cfg = load_adk_config(base_path)
    experts = cfg.setdefault("experts", {})
    from pathlib import Path
    search_dirs = [Path("experts"), Path("sre_assistant/experts")]
    for name in ("diagnostic","remediation","postmortem","config"):
        for d in search_dirs:
            yp = d / f"{name}.yaml"
            if yp.exists():
                try:
                    y = yaml.safe_load(yp.read_text(encoding="utf-8")) or {}
                    # 期望格式：{prompt:..., model:..., tools_allowlist:[...], slo:{...}}
                    experts.setdefault(name, {})
                    _deep_merge(experts[name], y)
                    break
                except Exception:
                    continue
    return cfg