# A2A OAuth 驗證範例代理

此範例展示了代理開發套件 (Agent Development Kit, ADK) 中的 **代理對代理 (Agent-to-Agent, A2A)** 架構與 **OAuth 驗證** 工作流程。此範例實作了一個多代理系統，其中遠端代理可以向本地代理提出 OAuth 驗證請求，然後由本地代理引導使用者完成 OAuth 流程，最後將驗證憑證回傳給遠端代理以進行 API 存取。

## 總覽

A2A OAuth 驗證範例包含：

- **根代理 (Root Agent)** (`root_agent`)：處理使用者請求並將任務委派給專門代理的主要協調者。
- **YouTube 搜尋代理 (YouTube Search Agent)** (`youtube_search_agent`)：使用 LangChain 工具處理 YouTube 影片搜尋的本地代理。
- **BigQuery 代理 (BigQuery Agent)** (`bigquery_agent`)：一個遠端的 A2A 代理，負責管理 BigQuery 操作，並需要透過 OAuth 驗證才能存取 Google Cloud。

## 架構

```
┌─────────────────┐    ┌────────────────────┐    ┌──────────────────┐
│   使用者         │───▶│   根代理           │───▶ │   BigQuery 代理   │
│   (OAuth 流程)   │    │    (本地)          │    │  (遠端 A2A)       │
│                 │    │                    │    │ (localhost:8001) │
│   OAuth UI      │◀───│                    │◀───│   OAuth 請求     │
└─────────────────┘    └────────────────────┘    └──────────────────┘
```

## 主要功能

### 1. **多代理架構 (Multi-Agent Architecture)**
- 根代理協調本地 YouTube 搜尋與遠端 BigQuery 操作。
- 展示混合式本地/遠端代理工作流程。
- 根據使用者請求類型無縫委派任務。

### 2. **OAuth 驗證工作流程**
- 遠端 BigQuery 代理向根代理提出 OAuth 驗證請求。
- 根代理引導使用者完成 Google OAuth 流程以存取 BigQuery。
- 在代理之間安全地交換權杖以進行驗證後的 API 呼叫。

### 3. **Google Cloud 整合**
- 具備完整資料集與資料表管理功能的 BigQuery 工具集。
- 透過 OAuth 保護使用者對 Google Cloud BigQuery 資源的存取。
- 支援列出、建立及管理資料集與資料表。

### 4. **LangChain 工具整合**
- 使用 LangChain 社群工具實現 YouTube 搜尋功能。
- 展示在代理工作流程中整合第三方工具。

## 設定與使用

### 前提條件

1. **設定 OAuth 憑證**：
   ```bash
   export OAUTH_CLIENT_ID=your_google_oauth_client_id
   export OAUTH_CLIENT_SECRET=your_google_oauth_client_secret
   ```

2. **啟動遠端 BigQuery 代理伺服器**：
   ```bash
   # 啟動遠端 a2a 伺服器，該伺服器在 8001 連接埠上提供 BigQuery 代理服務
   adk api_server --a2a --port 8001 contributing/samples/a2a_auth/remote_a2a
   ```

3. **執行主要代理**：
   ```bash
   # 在另一個終端機中，執行 adk web 伺服器
   adk web contributing/samples/
   ```

### 互動範例

當兩個服務都執行後，您可以與根代理進行互動：

**YouTube 搜尋 (不需驗證)：**
```
User: 搜尋 3 部泰勒絲的音樂影片
Agent: 我將協助您在 YouTube 上搜尋泰勒絲的音樂影片。
[代理將任務委派給 YouTube 搜尋代理]
Agent: 我找到了 3 部泰勒絲的音樂影片：
1. "Anti-Hero" - 官方音樂影片
2. "Shake It Off" - 官方音樂影片
3. "Blank Space" - 官方音樂影片
```

**BigQuery 操作 (需要 OAuth)：**
```
User: 列出我的 BigQuery 資料集
Agent: 我將協助您存取 BigQuery 資料集。這需要透過您的 Google 帳戶進行驗證。
[代理將任務委派給 BigQuery 代理]
Agent: 若要存取您的 BigQuery 資料，請完成 OAuth 驗證。
[啟動 OAuth 流程 - 使用者被重新導向至 Google 驗證頁面]
User: [在瀏覽器中完成 OAuth 流程]
Agent: 驗證成功！這是您的 BigQuery 資料集：
- dataset_1: 客戶分析
- dataset_2: 銷售資料
- dataset_3: 行銷指標
```

**資料集管理：**
```
User: 顯示我的「客戶分析」資料集的詳細資訊
Agent: 我將為您取得「客戶分析」資料集的詳細資訊。
[使用現有的 OAuth 權杖]
Agent: 「客戶分析」資料集詳細資訊：
- 建立日期：2024-01-15
- 位置：美國
- 資料表數量：5
- 描述：客戶行為與分析資料
```

## 程式碼結構

### 主要代理 (`agent.py`)

- **`youtube_search_agent`**：具備 LangChain YouTube 搜尋工具的本地代理。
- **`bigquery_agent`**：用於 BigQuery 操作的遠端 A2A 代理設定。
- **`root_agent`**：具備任務委派邏輯的主要協調者。

### 遠端 BigQuery 代理 (`remote_a2a/bigquery_agent/`)

- **`agent.py`**：具備 OAuth 工具集的 BigQuery 代理實作。
- **`agent.json`**：A2A 代理的代理卡 (Agent Card)。
- **`BigQueryToolset`**：支援 OAuth 的 BigQuery 資料集與資料表管理工具。

## OAuth 驗證工作流程

OAuth 驗證流程遵循以下模式：

1. **初始請求**：使用者透過根代理請求 BigQuery 操作。
2. **委派**：根代理將任務委派給遠端 BigQuery 代理。
3. **驗證檢查**：BigQuery 代理檢查是否有有效的 OAuth 權杖。
4. **驗證請求**：若無權杖，代理向根代理提出 OAuth 請求。
5. **使用者 OAuth**：根代理引導使用者完成 Google OAuth 流程。
6. **權杖交換**：根代理將 OAuth 權杖傳送給 BigQuery 代理。
7. **API 呼叫**：BigQuery 代理使用權杖進行驗證後的 API 呼叫。
8. **回傳結果**：BigQuery 代理透過根代理將結果回傳給使用者。

## 支援的 BigQuery 操作

BigQuery 代理支援以下操作：

### 資料集操作：
- **列出資料集**：`bigquery_datasets_list` - 取得使用者所有的資料集。
- **取得資料集**：`bigquery_datasets_get` - 取得特定資料集的詳細資訊。
- **建立資料集**：`bigquery_datasets_insert` - 建立新的資料集。

### 資料表操作：
- **列出資料表**：`bigquery_tables_list` - 取得資料集中的資料表。
- **取得資料表**：`bigquery_tables_get` - 取得特定資料表的詳細資訊。
- **建立資料表**：`bigquery_tables_insert` - 在資料集中建立新的資料表。

## 擴充範例

您可以透過以下方式擴充此範例：

- 新增更多 Google Cloud 服務（如 Cloud Storage、Compute Engine 等）。
- 實作權杖更新與過期處理。
- 為不同的 BigQuery 操作新增基於角色的存取控制。
- 為其他供應商（如 Microsoft、Facebook 等）建立 OAuth 流程。
- 為驗證事件新增稽核日誌。
- 實作多租戶 OAuth 權杖管理。

## 部署至其他環境

當將遠端 BigQuery A2A 代理部署到不同環境（例如 Cloud Run、不同的主機/連接埠）時，您 **必須** 更新代理卡 JSON 檔案中的 `url` 欄位：

### 本地開發
```json
{
  "url": "http://localhost:8001/a2a/bigquery_agent",
  ...
}
```

### Cloud Run 範例
```json
{
  "url": "https://your-bigquery-service-abc123-uc.a.run.app/a2a/bigquery_agent",
  ...
}
```

### 自訂主機/連接埠範例
```json
{
  "url": "https://your-domain.com:9000/a2a/bigquery_agent",
  ...
}
```

**重要事項：** `remote_a2a/bigquery_agent/agent.json` 中的 `url` 欄位必須指向您遠端 BigQuery A2A 代理實際部署且可存取的 RPC 端點。

## 疑難排解

**連線問題：**
- 確保本地 ADK Web 伺服器在 8000 連接埠上執行。
- 確保遠端 A2A 伺服器在 8001 連接埠上執行。
- 檢查是否有防火牆阻擋 localhost 連線。
- **確認 `remote_a2a/bigquery_agent/agent.json` 中的 `url` 欄位與您遠端 A2A 伺服器的實際部署位置相符。**
- 確認傳遞給 `RemoteA2AAgent` 建構函式的代理卡 URL 與正在執行的 A2A 伺服器相符。

**OAuth 問題：**
- 確認 `.env` 檔案中的 OAuth 用戶端 ID 和密鑰已正確設定。
- 確保在 Google Cloud Console 中已正確設定 OAuth 重新導向 URI。
- 檢查 OAuth 範圍是否包含 BigQuery 存取權限。
- 確認使用者有權存取 BigQuery 專案/資料集。

**BigQuery 存取問題：**
- 確保已驗證的使用者具備 BigQuery 權限。
- 檢查 Google Cloud 專案是否已啟用 BigQuery API。
- 確認資料集與資料表名稱正確且可存取。
- 檢查 BigQuery API 呼叫的配額限制。

**代理通訊問題：**
- 檢查本地 ADK Web 伺服器與遠端 A2A 伺服器的日誌。
- 確認 OAuth 權杖在代理之間正確傳遞。
- 確保代理的指令清楚說明驗證要求。
- **再次檢查 `agent.json` 檔案中的 RPC URL 是否正確且可存取。**
