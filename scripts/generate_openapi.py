
# 用途：輸出 FastAPI OpenAPI 規格為 YAML（示意）。
import yaml
from sre_assistant.server.app import app
def main():
    spec = app.openapi()
    with open('openapi.yaml','w',encoding='utf-8') as f:
        yaml.safe_dump(spec, f, allow_unicode=True, sort_keys=False)
if __name__=='__main__':
    main()
