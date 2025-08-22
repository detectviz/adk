
# -*- coding: utf-8 -*-
# 腳手架：快速建立「工具 YAML + Python 實作」骨架。
import os, sys, textwrap

BASE = os.path.join(os.path.dirname(__file__), "..", "sre_assistant", "tools")
SPEC_DIR = os.path.join(BASE, "specs")

TEMPLATE_PY = '''# -*- coding: utf-8 -*-
# {tool_name} 工具實作（樣板）：請依需求改寫，並補充錯誤處理。
from __future__ import annotations
from typing import Dict, Any
from ..adk_compat.executor import ExecutionError

def {py_func}(**kwargs) -> Dict[str, Any]:
    # TODO: 實作工具邏輯
    # 建議：對輸入做額外驗證，並在例外時 raise ExecutionError(代碼, 訊息)
    return {{"ok": True}}
'''

TEMPLATE_YAML = '''schema_version: '1.0'
name: {tool_name}
description: {desc}
args_schema:
  type: object
  required: []
  properties: {{}}
returns_schema:
  type: object
  properties: {{}}
errors:
  E_BACKEND: 上游錯誤
  E_SCHEMA: 結構不符
timeout_seconds: 15
idempotent: true
retry:
  max_retries: 0
risk_level: Low
'''

def main():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`main` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    if len(sys.argv) < 3:
        print("用法: python -m scripts.scaffold_tool <ToolName> <py_func_name> [desc]")
        sys.exit(1)
    tool_name = sys.argv[1]
    py_func = sys.argv[2]
    desc = sys.argv[3] if len(sys.argv) > 3 else f"{tool_name} 的工具"
    py_path = os.path.join(BASE, f"{py_func}.py")
    yaml_path = os.path.join(SPEC_DIR, f"{tool_name}.yaml")
    os.makedirs(os.path.dirname(py_path), exist_ok=True)
    os.makedirs(os.path.dirname(yaml_path), exist_ok=True)
    with open(py_path, "w", encoding="utf-8") as f:
        f.write(TEMPLATE_PY.format(tool_name=tool_name, py_func=py_func))
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(TEMPLATE_YAML.format(tool_name=tool_name, desc=desc))
    print("已產生：", py_path, yaml_path)

if __name__ == "__main__":
    main()