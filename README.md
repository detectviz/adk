
# SRE Assistant（ADK 對齊，顯式工具註冊）

- 全面繁體中文註解
- 不使用裝飾器，改採「工具 YAML 規格 + 註冊表」
- 協調器透過 ToolRegistry 呼叫工具
- FastAPI `/api/v1/chat` 與 CLI

## 快速開始
```bash
make dev
make run
# 或
make api
```
