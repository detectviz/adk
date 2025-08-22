
# -*- coding: utf-8 -*-
# 用途：掃描 tools/ 產生簡要 API 文檔（示意）。
from pathlib import Path
def main():
    out = []
    for p in Path('sre_assistant/tools').glob('*.py'):
        out.append(f"- {p.stem}: {p}")
    Path('docs/TOOLS.md').write_text("\n".join(out), encoding='utf-8')
if __name__=='__main__':
    main()
