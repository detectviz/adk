
# -*- coding: utf-8 -*-
# 簡易審計：以檔案落地，後續可替換為 DB
from __future__ import annotations
from typing import Dict, Any
import os, json, time, uuid, pathlib

def write_audit(event: Dict[str,Any]) -> None:
    path = pathlib.Path(os.getenv("AUDIT_LOG_PATH","/mnt/data/audit.log"))
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {"id": str(uuid.uuid4()), "ts": time.time(), **event}
    with path.open("a+", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
