# 模板設定參考

本文件提供模板設定選項的詳細參考。

## 設定檔

- **內建模板**：使用 `templateconfig.yaml` 檔案
- **遠端模板**：在 `pyproject.toml` 的 `[tool.agent-starter-pack.settings]` 區段下進行設定

兩種模板的設定欄位是相同的。

## 頂層欄位

| 欄位                | 類型   | 必要     | 描述                                                                                             |
| ------------------- | ------ | -------- | ------------------------------------------------------------------------------------------------------- |
| `base_template`     | string | 是 (僅限遠端代理) | 遠端模板將繼承的內建代理名稱 (例如 `adk_base`, `agentic_rag`)。 |
| `name`              | string | 是       | 您的模板的顯示名稱，會顯示在 `list` 指令中。                                         |
| `description`       | string | 是       | 您的模板的簡短描述，也會顯示在 `list` 指令中。                                 |
| `example_question`  | string | 否       | 一個範例問題或提示，將會包含在產生的專案的 `README.md` 中。             |
| `settings`          | object | 否       | 一個包含模板詳細設定的巢狀物件。請參閱下方的 `settings` 區段。       |

## `settings` 物件

此物件包含控制所產生專案功能和行為的欄位。

| 欄位                        | 類型           | 描述                                                                                                                                 |
| --------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `deployment_targets`        | list(string)   | 您的模板支援的部署目標清單。選項：`agent_engine`, `cloud_run`。                                                  |
| `tags`                      | list(string)   | 用於分類的標籤清單。`adk` 標籤可啟用與代理開發套件 (Agent Development Kit) 的特殊整合。                                 |
| `frontend_type`             | string         | 指定要使用的前端。範例：`streamlit`, `live_api_react`。預設為 `streamlit`。                                             |
| `agent_directory`           | string         | 放置代理程式碼的目錄名稱。預設為 `app`。可由 CLI 的 `--agent-directory` 參數覆寫。    |
| `requires_data_ingestion`   | boolean        | 若為 `true`，將提示使用者設定資料儲存庫。                                                                              |
| `requires_session`          | boolean        | 若為 `true`，當使用 `cloud_run` 目標時，將提示使用者選擇一個會話儲存類型 (例如 `alloydb`)。                    |
| `interactive_command`       | string         | 在代理程式碼建立後，用於啟動代理的 `make` 指令 (例如 `make playground`, `make dev`)。預設為 `playground`。 |
| `extra_dependencies`        | list(string)   | **注意：** 遠端模板會忽略此欄位。它由入門套件的內建模板在內部使用。您的 `pyproject.toml` 是依賴項的唯一真實來源。 |
