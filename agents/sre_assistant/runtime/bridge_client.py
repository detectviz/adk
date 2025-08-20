
# -*- coding: utf-8 -*-
# 以 Go Bridge CLI 調用系統腳本，回傳 JSON（繁體中文註解）。
import os, json, shutil, subprocess
from typing import Any, Dict

class BridgeClient:
    def __init__(self, bin_path: str | None = None):
        self.bin = bin_path or os.path.join("bin","bridge-cli")
        self.path_bin = shutil.which("bridge-cli")
        self.fallback = ["go", "run", "core/cmd/bridge-cli/main.go"]
    def exec(self, category: str, name: str, *args: str) -> Dict[str, Any]:
        if os.path.exists(self.bin):
            cmd = [self.bin, category, name, *[str(a) for a in args]]
        elif self.path_bin:
            cmd = [self.path_bin, category, name, *[str(a) for a in args]]
        else:
            cmd = [*self.fallback, category, name, *[str(a) for a in args]]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out = p.stdout.strip()
        if not out: raise RuntimeError(f"bridge empty output: {p.stderr}")
        try: return json.loads(out)
        except json.JSONDecodeError: raise RuntimeError(f"bridge non-json output: {out[:160]}")
