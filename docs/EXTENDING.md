# 擴充指南（Tools、sub_agents）

## 新增一個 Tool
1. 在 `sre_assistant/tools/` 下新增模組檔，明確定義函式、I/O Schema、錯誤碼。避免隱式 decorator 魔法。
2. 在工具註冊表（若有）或 `adk.yaml`/`experts/*.yaml` 的 `tools_allowlist` 加入名稱。
3. 撰寫單元測試（錯誤碼、超時、冪等）。
4. 更新文件：在 `docs/TOOLS.md` 描述參數與回傳格式。

## 新增一個 sub_agent（專家代理）
1. 建立 `experts/<name>.yaml`，包含：
   - `prompt`: 專家指令
   - `tools_allowlist`: 可用工具白名單
   - （選）`model`、`slo`
2. 建立 `sub_agents/<name>/agent.py`（可複用現有薄封裝），並在 `sub_agents/<name>/prompts.py`、`tools.py` 透過 loader 讀取 YAML。
3. 在組裝流程中掛載此 sub_agent（依專案的協調器/runner）。
4. 新增測試：至少驗證 `PROMPT` 與 `list_tools()` 會反映 `experts/<name>.yaml`。

## Dev UI 與 HITL
- 訂閱 `GET /api/v1/events`，監聽 `adk_request_credential`。
- 審批 `POST /api/v1/hitl/approve`。
- 可用 `server/static/devui.html` 手動驗證。
