# 內容規劃代理 (Content Planner Agent)

此範例代理 (Agent) 能根據所需內容的高階描述，建立詳細的內容大綱。此代理 (Agent) 是使用 Google Agent Development Kit (ADK) 和 Python A2A SDK 編寫的。

## 先決條件

- Python 3.10 或更高版本
- [UV](https://docs.astral.sh/uv/)
- 存取 LLM 和 API 金鑰

## 執行範例

1.  導覽至範例目錄：

    ```bash
    cd samples/python/agents/content_planner
    ```

2.  使用您的 API 金鑰建立環境檔案：

   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

3.  執行代理 (Agent)：

    **注意：**
    預設情況下，代理 (Agent) 將在連接埠 10001 上啟動。若要覆寫此設定，請在以下指令末尾新增 `--port=YOUR_PORT` 選項。

    ```bash
    uv run .
    ```

4.  在另一個終端機中，執行 A2A 用戶端並使用它向代理 (Agent) 傳送訊息：

    ```bash
    # 連接到代理 (Agent) (指定具有正確連接埠的代理 URL)
    cd samples/python/hosts/cli
    uv run . --agent http://localhost:10001

    # 如果您在啟動代理 (Agent) 時變更了連接埠，請改用該連接埠
    # uv run . --agent http://localhost:YOUR_PORT
    ```

5.  若要在內容建立多代理 (Multi Agent) 系統中使用此代理 (Agent)，請查看 [content_creation](../../../python/hosts/content_creation/README.md) 範例。

## 免責聲明
重要提示：所提供的範例程式碼僅供示範之用，旨在說明代理對代理 (Agent-to-Agent, A2A) 協定的運作機制。在建構生產應用程式時，至關重要的是將任何在您直接控制範圍之外運作的代理 (Agent) 視為潛在不受信任的實體。

從外部代理 (Agent) 收到的所有資料——包括但不限於其代理名片 (AgentCard)、訊息、產物 (Artifact) 和任務狀態——都應視為不受信任的輸入。例如，惡意代理 (Agent) 可能會提供一個在其欄位（例如，描述、名稱、技能描述）中包含精心設計的資料的代理名片 (AgentCard)。如果此資料未經淨化就用於為大型語言模型 (LLM) 建構提示，則可能使您的應用程式面臨提示注入攻擊的風險。未能在使用前正確驗證和淨化此資料可能會在您的應用程式中引入安全漏洞。

開發人員有責任實施適當的安全措施，例如輸入驗證和安全處理憑證，以保護其系統和使用者。
