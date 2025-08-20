
# -*- coding: utf-8 -*-
# 結構化 JSON 日誌（繁體中文註解）。
import json, sys, time
from typing import Any, Dict

def _now_ms() -> int:
    return int(time.time() * 1000)

def log(level: str, event: str, **fields: Any) -> None:
    rec: Dict[str, Any] = {"ts": _now_ms(), "level": level.lower(), "event": event}
    rec.update(fields)
    sys.stdout.write(json.dumps(rec, ensure_ascii=False) + "\n")
    try: sys.stdout.flush()
    except Exception: pass

def info(event: str, **fields: Any) -> None: log("INFO", event, **fields)
def warn(event: str, **fields: Any) -> None: log("WARN", event, **fields)
def error(event: str, **fields: Any) -> None: log("ERROR", event, **fields)
