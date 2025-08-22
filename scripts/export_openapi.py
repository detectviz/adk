
# 產出 OpenAPI 規格檔至 /mnt/data/openapi.json
import json, os
from sre_assistant.server.app import app

spec = app.openapi()
out = "/mnt/data/openapi.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(spec, f, ensure_ascii=False, indent=2)
print(out)
