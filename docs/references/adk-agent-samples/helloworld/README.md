# Hello World 範例

一個只會傳回訊息事件的 Hello World 範例代理 (Agent)。

## 開始使用

1. 啟動伺服器

   ```bash
   uv run .
   ```

2. 執行測試用戶端

   ```bash
   uv run test_client.py
   ```

## 建置容器映像

代理 (Agent) 也可以使用容器檔案建置。

1. 導覽至 `samples/python/agents/helloworld` 目錄：

  ```bash
  cd samples/python/agents/helloworld
  ```

2. 建置容器檔案

    ```bash
    podman build . -t helloworld-a2a-server
    ```

> [!Tip]
> Podman 是 `docker` 的直接替代品，也可以在這些指令中使用。

3. 執行您的容器

    ```bash
    podman run -p 9999:9999 helloworld-a2a-server
    ```

## 驗證

若要在另一個終端機中進行驗證，請執行 A2A 用戶端：

```bash
cd samples/python/hosts/cli
uv run . --agent http://localhost:9999
```


## 免責聲明
重要提示：所提供的範例程式碼僅供示範之用，旨在說明代理對代理 (Agent-to-Agent, A2A) 協定的運作機制。在建構生產應用程式時，至關重要的是將任何在您直接控制範圍之外運作的代理 (Agent) 視為潛在不受信任的實體。

從外部代理 (Agent) 收到的所有資料——包括但不限於其代理名片 (AgentCard)、訊息、產物 (Artifact) 和任務狀態——都應視為不受信任的輸入。例如，惡意代理 (Agent) 可能會提供一個在其欄位（例如，描述、名稱、技能描述）中包含精心設計的資料的代理名片 (AgentCard)。如果此資料未經淨化就用於為大型語言模型 (LLM) 建構提示，則可能使您的應用程式面臨提示注入攻擊的風險。未能在使用前正確驗證和淨化此資料可能會在您的應用程式中引入安全漏洞。

開發人員有責任實施適當的安全措施，例如輸入驗證和安全處理憑證，以保護其系統和使用者。