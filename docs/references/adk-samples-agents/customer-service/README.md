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

### Example Interaction

Here's a quick example of how a user might interact with the agent:

**User:**:
hi there

**Agent**:
Hey Alex, I see you've been a Cymbal Home & Garden customer for a couple of years now - we appreciate your business! I also see you have a few things in your cart already. How can I help you get your garden growing today?

**User**:
Yeah, so I'm a bit confused. I just bought some...uh...plants or flowers that I wanted to put in the backyard. They just say "sun loving annuals" on them. I totally spaced on picking up potting soil so I'm placing an order for pickup now. The problem is, I'm not sure if the potting soil and fertilizer I picked out are the right ones.

**Agent**:
I understand – it can be tricky when you're not quite sure what you've got! Let's figure this out together. Don't worry, we'll get your plants the right care. To best help you, would you be willing to share a quick video of the plants you've purchased? That will help me identify them and make sure you have the right supplies.

**User**:
Sure, how do I do that?

**Agent**:
I just texted you a link to the number in your profile. Just click on that, and it'll open a secure video connection.

```tool_code
print(send_call_companion_link(phone_number='+12065550123'))
```

```tool_outputs
{'status': 'success', 'message': 'Link sent to +12065550123'}
```

**User**:
Okay, I clicked the link...can you see this?

**Agent**:
Yes I can see you Alex! Can you go ahead and point the camera at your plants so I can inspect them?

**User**:
Yes of course!
...

## Evaluating the Agent

Evaluation tests assess the overall performance and capabilities of the agent in a holistic manner.

**Steps:**

1.  **Run Evaluation Tests:**

    ```bash
    pytest eval
    ```

    - This command executes all test files within the `eval` directory.

## Unit Tests

Unit tests focus on testing individual units or components of the code in isolation.

**Steps:**

1.  **Run Unit Tests:**

    ```bash
    pytest tests/unit
    ```

    - This command executes all test files within the `tests/unit` directory.

## Configuration

You can find further configuration parameters in [customer_service/config.py](./customer_service/config.py). This incudes parameters such as agent name, app name and llm model used by the agent.

## Deployment on Google Agent Engine

In order to inherit all dependencies of your agent you can build the wheel file of the agent and run the deployment.

1.  **Build Customer Service Agent WHL file**

    ```bash
    poetry build --format=wheel --output=deployment
    ```

1.  **Deploy the agent to agents engine**
    It is important to run deploy.py from within deployment folder so paths are correct

    ```bash
    cd deployment
    python deploy.py
    ```

### Testing deployment

This code snippet is an example of how to test the deployed agent.

```
import vertexai
from customer_service.config import Config
from vertexai.preview.reasoning_engines import AdkApp


configs = Config()

vertexai.init(
    project="<GOOGLE_CLOUD_LOCATION_PROJECT_ID>",
    location="<GOOGLE_CLOUD_LOCATION>"
)

# get the agent based on resource id
agent_engine = vertexai.agent_engines.get('DEPLOYMENT_RESOURCE_NAME') # looks like this projects/PROJECT_ID/locations/LOCATION/reasoningEngines/REASONING_ENGINE_ID

for event in remote_agent.stream_query(
    user_id=USER_ID,
    session_id=session["id"],
    message="Hello!",
):
    print(event)

```

## Disclaimer

This agent sample is provided for illustrative purposes only and is not intended for production use. It serves as a basic example of an agent and a foundational starting point for individuals or teams to develop their own agents.

This sample has not been rigorously tested, may contain bugs or limitations, and does not include features or optimizations typically required for a production environment (e.g., robust error handling, security measures, scalability, performance considerations, comprehensive logging, or advanced configuration options).

Users are solely responsible for any further development, testing, security hardening, and deployment of agents based on this sample. We recommend thorough review, testing, and the implementation of appropriate safeguards before using any derived agent in a live or critical system.