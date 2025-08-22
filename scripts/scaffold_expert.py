
# -*- coding: utf-8 -*-
# 腳手架：快速建立專家代理骨架。
import os, sys, textwrap

BASE = os.path.join(os.path.dirname(__file__), "..", "sre_assistant", "experts")

TEMPLATE = '''# -*- coding: utf-8 -*-
# {name} 專家代理（樣板）：請補全指令與工具清單。
from __future__ import annotations

class {name}:
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.name = "{name}"
        self.model = model
        # TODO: 初始化工具清單與提示詞
    def plan(self, goal: str):
        # TODO: 生成步驟
        return []
'''

def main():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`main` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    if len(sys.argv) < 2:
        print("用法: python -m scripts.scaffold_expert <ExpertClassName>")
        sys.exit(1)
    name = sys.argv[1]
    p = os.path.join(BASE, f"{name.lower()}.py")
    with open(p, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(name=name))
    print("已產生：", p)

if __name__ == "__main__":
    main()