# 疑難排解

本指南幫助解決 Agent Starter Pack 的常見問題。

## 驗證問題

有關 Vertex AI 驗證的詳細資訊，請參閱[官方文件](https://cloud.google.com/vertex-ai/docs/authentication)。

### 「找不到憑證 (Could not find credentials)」或「找不到專案 (Could not find project)」錯誤

**問題**：使用 Vertex AI 時出現缺少憑證的錯誤。

**解決方案**：

1.  登入 Google Cloud：`gcloud auth login --update-adc`
2.  設定正確的專案：
    ```bash
    gcloud config set project YOUR_PROJECT_ID
    gcloud auth application-default set-quota-project YOUR_PROJECT_ID
    ```

### Vertex AI API 未啟用

**問題**：由於您的專案中未啟用 Vertex AI API，導致操作失敗。

**解決方案**：

1. 啟用 Vertex AI API：
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

2. 驗證 API 是否已啟用：
   ```bash
   gcloud services list --filter=aiplatform.googleapis.com
   ```

### 權限被拒絕錯誤
**問題**：使用 Google Cloud API 時出現「權限被拒絕 (Permission denied)」錯誤。

**解決方案**：確保您的使用者或服務帳戶具有必要的 IAM 角色。例如，對於 Vertex AI，您通常需要 `roles/aiplatform.user`。使用 `gcloud projects add-iam-policy-binding` 指令或 Cloud Console 授予角色。

### 找不到指令：agent-starter-pack

**問題**：安裝後出現「找不到指令 (Command not found)」錯誤。

**解決方案**：

1. 驗證安裝：
   ```bash
   pip list | grep agent-starter-pack
   ```
2. 檢查 PATH：
   ```bash
   echo $PATH
   ```
3. 如果需要，重新安裝：
   ```bash
   pip install --user agent-starter-pack
   ```
4. 對於 pipx：
   ```bash
   pipx ensurepath
   source ~/.bashrc  # 或 ~/.zshrc
   ```

## 專案建立問題

### 專案建立失敗

**問題**：`agent-starter-pack create` 失敗。

**解決方案**：

1.  **檢查錯誤訊息：** 檢查輸出以尋找線索。
2.  **寫入權限：** 確保對目錄具有寫入權限。
3.  **專案名稱：** 僅使用小寫字母、數字和連字號。
4.  **除錯模式：** 考慮使用除錯模式以獲取更詳細的錯誤資訊：
    ```bash
    agent-starter-pack create my-project-name --debug
    ```

### Agent Engine 相關問題

考慮利用[公開產品文件](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/troubleshooting/set-up)

## 取得更多協助

如果問題仍然存在：

1.  **檢查 GitHub Issues：** 在 `agent-starter-pack` 的 GitHub 儲存庫中搜尋現有的 Github issue。
2.  **提出新的 Issue：** 提供：

    *   問題描述。
    *   重現問題的步驟。
    *   錯誤訊息 (最好使用 `--debug` 旗標執行以獲得詳細日誌)。
    *   環境：作業系統、Python 版本、`agent-starter-pack` 版本、安裝方法、shell。
