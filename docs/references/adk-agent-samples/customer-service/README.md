# Cymbal Home & Garden 客戶服務代理 (Agent)

本專案為 Cymbal Home & Garden 實作了一個由 AI 驅動的客戶服務代理 (agent)，Cymbal Home & Garden 是一家專門從事居家裝修、園藝及相關用品的大型零售商。此代理 (agent) 旨在提供卓越的客戶服務、協助客戶選擇產品、管理訂單、安排服務，並提供個人化建議。

## 總覽

Cymbal Home & Garden 客戶服務代理 (Agent) 旨在為客戶提供無縫且個人化的購物體驗。它利用 Gemini 來了解客戶需求、提供量身訂製的產品建議、管理訂單和安排服務。此代理 (agent) 的設計目標是友善、富有同理心且高效率，確保客戶獲得最好的服務。

## 代理 (Agent) 詳細資料

客戶服務代理 (Agent) 的主要功能包括：

| 功能 | 描述 |
| ------------------ | ----------------------- |
| _互動類型_ | 對話式 |
| _複雜度_ | 中等 |
| _代理 (Agent) 類型_ | 單一代理 (Agent) |
| _元件_ | 工具、多模態、即時 |
| _垂直領域_ | 零售 |

### 代理 (Agent) 架構

![客戶服務代理 (Agent) 工作流程](customer_service_workflow.png)

此代理 (agent) 採用多模態架構建構，結合文字和視訊輸入以提供豐富的互動體驗。它模擬與各種工具和服務的互動，包括產品目錄、庫存管理、訂單處理和預約排程系統。此代理 (agent) 還利用會話管理系統來維持跨互動的上下文並個人化客戶體驗。

值得注意的是，此代理 (agent) 並未與實際的後端整合，其行為是基於模擬的工具。如果您想將此代理 (agent) 與實際的後端整合，您需要編輯 [customer_service/tools.py](./customer_service/tools/tools.py)

由於工具是模擬的，您可能會注意到某些請求的變更將不會被套用。例如，如果使用者稍後要求代理 (agent) 列出所有商品，新加入購物車的商品將不會顯示。

### 主要功能

- **個人化客戶協助：**
  - 以姓名問候回頭客並確認其購買記錄。
  - 保持友善、富有同理心和樂於助人的語氣。
- **產品識別與推薦：**
  - 協助客戶識別植物，即使描述模糊。
  - 要求並利用視覺輔助 (視訊) 來準確識別植物。
  - 根據識別出的植物、客戶需求和地點 (例如，內華達州拉斯維加斯) 提供量身訂製的產品推薦。
  - 如果存在更好的選擇，則為客戶購物車中的商品提供替代方案。
- **訂單管理：**
  - 存取並顯示客戶購物車的內容。
  - 根據建議和客戶批准，透過新增和移除商品來修改購物車。
  - 通知客戶相關的銷售和促銷活動。
- **向上銷售與服務推廣：**
  - 建議相關服務，例如專業種植服務。
  - 處理有關定價和折扣的查詢，包括競爭對手的報價。
  - 必要時請求經理批准折扣。
- **預約排程：**
  - 安排種植服務 (或其他服務) 的預約。
  - 檢查可用的時間段並向客戶呈現。
  - 確認預約詳細資訊並發送確認/行事曆邀請。
- **客戶支援與互動：**
  - 透過簡訊或電子郵件發送與客戶購買和地點相關的植物護理說明。
  - 為忠實客戶提供未來店內購買的折扣 QR 碼。
- **基於工具的互動：**
  - 代理 (agent) 使用一組工具與使用者互動。
  - 代理 (agent) 可以在單次互動中使用多個工具。
  - 代理 (agent) 可以使用工具獲取資訊並修改使用者的交易狀態。
- **評估：**
  - 可以使用一組測試案例來評估代理 (agent)。
  - 評估基於代理 (agent) 使用工具和回應使用者要求的能力。

#### 代理 (Agent) 狀態 - 預設客戶資訊

代理 (agent) 的會話狀態預先載入了範例客戶資料，模擬真實的對話。理想情況下，此狀態應在對話開始時從 CRM 系統載入，並使用使用者的資訊。這假設代理 (agent) 會驗證使用者身分，或者使用者已經登入。如果期望修改此行為，請編輯 [get_customer(current_customer_id: str) in customer.py](./customer_service/entities/customer.py)

#### 工具

此代理 (agent) 可以存取以下工具：

- `send_call_companion_link(phone_number: str) -> str`: 發送視訊連線的連結。
- `approve_discount(type: str, value: float, reason: str) -> str`: 批准折扣 (在預定義的限制內)。
- `sync_ask_for_approval(type: str, value: float, reason: str) -> str`: 向經理請求折扣批准。
- `update_salesforce_crm(customer_id: str, details: str) -> dict`: 在 Salesforce 中更新客戶記錄。
- `access_cart_information(customer_id: str) -> dict`: 檢索客戶的購物車內容。
- `modify_cart(customer_id: str, items_to_add: list, items_to_remove: list) -> dict`: 更新客戶的購物車。
- `get_product_recommendations(plant_type: str, customer_id: str) -> dict`: 建議合適的產品。
- `check_product_availability(product_id: str, store_id: str) -> dict`: 檢查產品庫存。
- `schedule_planting_service(customer_id: str, date: str, time_range: str, details: str) -> dict`: 預約種植服務。
- `get_available_planting_times(date: str) -> list`: 檢索可用的時間段。
- `send_care_instructions(customer_id: str, plant_type: str, delivery_method: str) -> dict`: 發送植物護理資訊。
- `generate_qr_code(customer_id: str, discount_value: float, discount_type: str, expiration_days: int) -> dict`: 建立折扣 QR 碼。

## 設定與安裝

### 先決條件

- Python 3.11+
- Poetry (用於依賴管理)
- Google ADK SDK (透過 Poetry 安裝)
- Google Cloud Project (用於 Vertex AI Gemini 整合)

### 安裝
1.  **先決條件：**

    對於 Agent Engine 部署步驟，您將需要
    一個 Google Cloud 專案。建立專案後，
    [安裝 Google Cloud SDK](https://cloud.google.com/sdk/docs/install)。
    然後執行以下命令以使用您的專案進行驗證：
    ```bash
    gcloud auth login
    ```
    您還需要啟用某些 API。執行以下命令以啟用
    所需的 API：
    ```bash
    gcloud services enable aiplatform.googleapis.com
    ```

1.  複製儲存庫：

    ```bash
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/customer-service
    ```

    在本教學課程的其餘部分，**請確保您保持在 `agents/customer-service` 目錄中**。

2.  使用 Poetry 安裝依賴項：

- 如果您之前沒有安裝過 poetry，請先執行 `pip install poetry`。然後您可以使用以下指令建立您的虛擬環境並安裝所有依賴項：

  ```bash
  poetry install
  ```

  要啟用虛擬環境，請執行：

  ```bash
  poetry env activate
  ```

3.  設定 Google Cloud 憑證：

    - 確保您有一個 Google Cloud 專案。
    - 確保您已在專案中啟用 Vertex AI API。
    - 設定 `GOOGLE_GENAI_USE_VERTEXAI`、`GOOGLE_CLOUD_PROJECT` 和 `GOOGLE_CLOUD_LOCATION` 環境變數。您可以在您的 `.env` 檔案中設定它們 (修改 .env_sample 檔案並將其重新命名為 .env) 或直接在您的 shell 中設定。或者，您可以編輯 [customer_service/config.py](./customer_service/config.py)

    ```bash
    export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_NAME_HERE
    export GOOGLE_GENAI_USE_VERTEXAI=1
    export GOOGLE_CLOUD_LOCATION=us-central1
    ```

## 執行代理 (Agent)

您可以在終端機中使用 ADK 命令執行代理 (agent)。
從根專案目錄：

1.  在 CLI 中執行代理 (agent)：

    ```bash
    adk run customer_service
    ```

2.  使用 ADK Web UI 執行代理 (agent)：
    ```bash
    adk web
    ```
    從下拉式選單中選取 customer_service

### 範例互動

這是一個使用者如何與代理 (agent) 互動的快速範例：

**使用者：**
嗨，你好

**代理 (Agent)：**
嘿，Alex，我看到您成為 Cymbal Home & Garden 的顧客已經好幾年了 - 我們非常感謝您的惠顧！我也看到您的購物車裡已經有幾樣東西了。今天有什麼可以幫助您打造您的花園呢？

**使用者：**
是的，我有點困惑。我剛買了一些……嗯……我想種在後院的植物或花。它們上面只寫著「喜陽一年生植物」。我完全忘了買盆栽土，所以我現在下單自取。問題是，我不確定我選的盆栽土和肥料是否正確。

**代理 (Agent)：**
我了解 – 當您不太確定自己買了什麼時，確實會有點棘手！讓我們一起解決這個問題。別擔心，我們會為您的植物提供適當的照護。為了能最好地幫助您，您願意分享一段您所購買植物的簡短影片嗎？那將有助於我識別它們，並確保您有正確的用品。

**使用者：**
當然，我該怎麼做？

**代理 (Agent)：**
我剛才將一個連結以簡訊方式傳送到您個人資料中的電話號碼。只需點擊該連結，它就會開啟一個安全的視訊連線。

```tool_code
print(send_call_companion_link(phone_number='+12065550123'))
```

```tool_outputs
{'status': 'success', 'message': 'Link sent to +12065550123'}
```

**使用者**：
好的，我點擊了連結……你看得到嗎？

**代理 (Agent)**：
是的，我看到您了，Alex！您可以將攝影機對準您的植物，以便我檢查它們嗎？

**使用者**：
當然！
...

## 評估代理 (Agent)

評估測試從整體上評估代理 (Agent) 的整體效能和能力。

**步驟：**

1.  **執行評估測試：**

    ```bash
    pytest eval
    ```

    - 此指令會執行 `eval` 目錄中的所有測試檔案。

## 單元測試

單元測試專注於獨立測試程式碼的個別單元或元件。

**步驟：**

1.  **執行單元測試：**

    ```bash
    pytest tests/unit
    ```

    - 此指令會執行 `tests/unit` 目錄中的所有測試檔案。

## 設定

您可以在 [customer_service/config.py](./customer_service/config.py) 中找到更多設定參數。這包括代理 (Agent) 名稱、應用程式名稱和代理 (Agent) 使用的 llm 模型等參數。

## 在 Google Agent Engine 上部署

為了繼承代理 (Agent) 的所有相依性，您可以建置代理 (Agent) 的 wheel 檔案並執行部署。

1.  **建置客戶服務代理 (Agent) 的 WHL 檔案**

    ```bash
    poetry build --format=wheel --output=deployment
    ```

2.  **將代理 (Agent) 部署到 Agent Engine**
    從 deployment 資料夾內執行 deploy.py 很重要，這樣路徑才會正確。

    ```bash
    cd deployment
    python deploy.py
    ```

### 測試部署

此程式碼片段是如何測試已部署代理 (Agent) 的範例。

```
import vertexai
from customer_service.config import Config
from vertexai.preview.reasoning_engines import AdkApp


configs = Config()

vertexai.init(
    project="<GOOGLE_CLOUD_LOCATION_PROJECT_ID>",
    location="<GOOGLE_CLOUD_LOCATION>"
)

# 根據資源 ID 取得代理 (Agent)
agent_engine = vertexai.agent_engines.get('DEPLOYMENT_RESOURCE_NAME') # 格式如下 projects/PROJECT_ID/locations/LOCATION/reasoningEngines/REASONING_ENGINE_ID

for event in remote_agent.stream_query(
    user_id=USER_ID,
    session_id=session["id"],
    message="Hello!",
):
    print(event)

```

## 免責聲明

此代理 (Agent) 範例僅供說明之用，不適用於生產環境。它作為代理 (Agent) 的一個基本範例，並為個人或團隊開發自己的代理 (Agent) 提供了一個基礎起點。

此範例未經嚴格測試，可能包含錯誤或限制，且不包含生產環境通常所需的功能或最佳化（例如，穩健的錯誤處理、安全措施、可擴展性、效能考量、全面的日誌記錄或進階設定選項）。

使用者對基於此範例的代理 (Agent) 的任何進一步開發、測試、安全強化和部署負全部責任。我們建議在即時或關鍵系統中使用任何衍生代理 (Agent) 之前，進行徹底的審查、測試並實施適當的保護措施。