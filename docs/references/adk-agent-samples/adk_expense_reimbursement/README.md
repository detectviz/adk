# ADK 費用報銷代理 (Agent)

此範例使用代理開發套件 (Agent Development Kit, ADK) 來建立一個簡單的「費用報銷」代理 (Agent)，並將其作為 A2A 伺服器託管。

此代理 (Agent) 接收來自客戶端的文字請求，如果缺少任何詳細資訊，則會傳回一個網頁表單供客戶端（或其使用者）填寫。客戶端填寫表單後，代理 (Agent) 將完成任務。

## 先決條件

- Python 3.9 或更高版本
- [UV](https://docs.astral.sh/uv/)
- 存取 LLM 和 API 金鑰

## 執行範例

1. 導覽至範例目錄：

    ```bash
    cd samples/python/agents/adk_expense_reimbursement
    ```

2. 建立包含您的 API 金鑰的環境檔案：

   ```bash
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

3. 執行一個代理 (Agent)：

    ```bash
    uv run .
    ```

4. 在另一個終端機中，執行 A2A 客戶端：

    ```bash
    # 連接到代理 (Agent) (指定具有正確通訊埠的代理 URL)
    cd samples/python/hosts/cli
    uv run . --agent http://localhost:10002

    # 如果您在啟動代理 (Agent) 時變更了通訊埠，請改用該通訊埠
    # uv run . --agent http://localhost:YOUR_PORT
    ```

## 免責聲明

重要提示：此處提供的範例程式碼僅供示範之用，旨在說明代理對代理 (A2A) 協定的運作機制。在建構實際應用程式時，至關重要的是將任何在您直接控制範圍之外運作的代理 (Agent) 視為潛在不受信任的實體。

所有從外部代理 (Agent) 接收的資料——包括但不限於其 AgentCard、訊息、產物和任務狀態——都應作為不受信任的輸入來處理。舉例來說，一個惡意代理 (Agent) 可能在其 AgentCard 的欄位（例如：description、name、skills.description）中提供經過精心設計的資料。如果這些資料在未經清理的情況下被用來建構大型語言模型 (LLM) 的提示，可能會使您的應用程式遭受提示注入攻擊 (prompt injection attacks)。若未能在使用前對這些資料進行適當的驗證和清理，可能會為您的應用程式帶來安全漏洞。

開發人員有責任實施適當的安全措施，例如輸入驗證和安全處理憑證，以保護他們的系統和使用者。
