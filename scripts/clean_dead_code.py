
# -*- coding: utf-8 -*-
# 檔案：scripts/clean_dead_code.py
# 用途：以啟發式掃描可能未被引用的 .py 檔，僅列印清單不自動刪除。
import os, re, sys, pathlib

def main()->int:
    root = pathlib.Path('.')
    py_files = [p for p in root.rglob('*.py') if 'venv' not in p.parts and '.pytest_cache' not in p.parts]
    imports = set()
    for p in py_files:
        try:
            for m in re.findall(r"from\s+([\w\.]+)\s+import|import\s+([\w\.]+)", p.read_text(encoding='utf-8')):
                mod = (m[0] or m[1]).split('.')[0]
                if mod: imports.add(mod)
        except Exception:
            pass
    # 極簡：若檔名根模組未出現在 imports 中且非入口檔，列為疑似未使用
    suspects = []
    for p in py_files:
        name = p.stem
        if name not in {'app','agent','runtime','setup','__init__'} and name not in imports:
            suspects.append(str(p))
    print("Possible unused modules (heuristic):\n" + "\n".join(sorted(suspects)))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
