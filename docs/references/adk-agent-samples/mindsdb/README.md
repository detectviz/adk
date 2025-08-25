## MindsDB 企業資料代理 (MindsDB Enterprise Data Agent)

由 Gemini 2.5 flash + MindsDB 提供支援。此範例使用 A2A 連接、查詢和分析來自數百個聯合資料來源的資料，包括資料庫、資料湖和 SaaS 應用程式。

該代理接收使用者的自然語言查詢，並將其轉換為適用於 MindsDB 的 SQL 查詢，處理跨多個來源的資料聯合。它可以：

- 從各種來源查詢資料，包括資料庫、資料湖和 SaaS 應用程式
- 執行跨聯合資料來源的分析
- 處理關於您資料的自然語言問題
- 從多個資料來源傳回結構化結果
<img width="597" alt="image" src="https://github.com/user-attachments/assets/3e070239-f2a1-4771-8840-6517bd0c6545" />

## 先決條件

- Python 3.9 或更高版本
- MindsDB 帳戶和 API 憑證 (https://mdb.ai)
- 建立一個 MindsDB Mind（一個可以從資料庫查詢資料的 AI 模型），預設我們使用示範版本：`Sales_Data_Expert_Demo_Mind`

## 環境變數

在 mdb.ai 中，一旦您建立了一個 Mind（一個可以從資料庫查詢資料的 AI 模型），您就可以在代理中使用它。

在專案目錄中建立一個 `.env` 檔案，並包含以下變數：

```
MINDS_API_KEY=your_mindsdb_api_key
MIND_NAME=your_mindsdb_model_name
```

- `MINDS_API_KEY`：您的 MindsDB API 金鑰（必要）
- `MIND_NAME`：要使用的 MindsDB Mind 的名稱（必要）

## 執行範例

1. 導覽至範例目錄：
    ```bash
    cd samples/python/agents/mindsdb
    ```

2. 執行代理：
    ```bash
    uv run .
    ```

3. 在另一個終端機中，執行 A2A 客戶端：
    ```bash
    # 連接到代理（指定代理 URL 及正確的埠號）
    cd samples/python/hosts/cli
    uv run . --agent http://localhost:10006

    # 如果您在啟動代理時變更了埠號，請改用該埠號
    # uv run . --agent http://localhost:YOUR_PORT
    ```
4. 向代理詢問有關您資料的問題。

## 範例查詢

您可以提出像這樣的問題：

- "What percentage of prospects are executives?" (潛在客戶中高階主管的百分比是多少？)
- "What is the distribution of companies by size?" (公司的規模分佈如何？)

代理將處理跨不同來源連接和分析資料的複雜性。


## 免責聲明
重要提示：所提供的範例程式碼僅供示範之用，並說明代理對代理 (A2A) 協定的機制。在建置生產應用程式時，將任何在您直接控制之外運作的代理視為潛在不受信任的實體至關重要。

從外部代理接收的所有資料——包括但不限於其代理卡 (AgentCard)、訊息、成品和任務狀態——都應作為不受信任的輸入處理。例如，惡意代理可能會提供一個在其欄位（例如，描述、名稱、技能描述）中包含精心設計資料的代理卡。如果在使用此類資料建構大型語言模型 (LLM) 的提示時未經清理，可能會使您的應用程式面臨提示注入攻擊的風險。未能在使用前正確驗證和清理此類資料可能會給您的應用程式帶來安全漏洞。

開發人員有責任實施適當的安全措施，例如輸入驗證和安全處理憑證，以保護其系統和使用者。