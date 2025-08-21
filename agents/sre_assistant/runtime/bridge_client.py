
# -*- coding: utf-8 -*-
# 以 Go Bridge CLI 調用系統腳本，回傳 JSON（繁體中文註解）。
import os, json, shutil, subprocess, re, asyncio
from typing import Any, Dict

class BridgeClient:
    def __init__(self, bin_path: str | None = None):
        self.bin = bin_path or os.path.join("bin","bridge-cli")
        self.path_bin = shutil.which("bridge-cli")
        self.fallback = ["go", "run", "core/cmd/bridge-cli/main.go"]
        self.valid_name_pattern = re.compile(r"^[a-z0-9_]+$")

    def _validate_input(self, text: str):
        if not self.valid_name_pattern.match(text):
            raise ValueError(f"Invalid format: {text}")

    async def exec(self, category: str, name: str, *args: str) -> Dict[str, Any]:
        self._validate_input(category)
        self._validate_input(name)

        if os.path.exists(self.bin):
            cmd_parts = [self.bin, category, name, *[str(a) for a in args]]
        elif self.path_bin:
            cmd_parts = [self.path_bin, category, name, *[str(a) for a in args]]
        else:
            cmd_parts = [*self.fallback, category, name, *[str(a) for a in args]]

        p = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await p.communicate()

        out = stdout.decode().strip()
        err = stderr.decode().strip()

        if not out:
            raise RuntimeError(f"bridge empty output: {err}")
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            raise RuntimeError(f"bridge non-json output: {out[:160]}")
