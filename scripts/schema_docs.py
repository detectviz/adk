
# -*- coding: utf-8 -*-
# 用途：將工具 Schema 轉為 Markdown（若工具定義提供 schema）。示範性腳本。
from pathlib import Path
def main():
    Path('docs/SCHEMAS.md').write_text('# 工具 Schema 文件（示例自動產生）\n', encoding='utf-8')
if __name__=='__main__':
    main()
