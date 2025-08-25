# LLM 稽核員 (LLM Auditor)

此代理作為一個自動化的事實查核層，專門用於評估和加強大型語言模型（LLM）生成回應的事實基礎。其主要作用是透過系統性地將 LLM 的輸出與真實世界的資訊進行分析，以提高其可靠性；它透過識別文本中可驗證的聲明，利用網路搜尋及其內部知識來確定其準確性，產生一份詳細的調查報告，並可選擇性地重寫原始回應以糾正任何已發現的不準確之處。

## 總覽
此代理評估並改善由 LLM 生成回應的事實基礎。其主要目的是作為一個自動化的事實查核層，將 LLM 的答案與真實世界的資訊進行分析，以提高可靠性。

*   識別並分離出 LLM 生成文本中具體、可驗證的陳述。
*   使用網路搜尋工具及其訓練所用的知識來確定聲明的準確性。
*   產生一份清晰的明細，列出已識別的聲明及其驗證狀態。
*   可選擇性地根據已驗證的發現重寫原始回應以糾正不準確之處。

這個範例代理讓使用者能查詢一個 LLM，然後代理會透過提取聲明、利用搜尋工具進行驗證、產生稽核報告，並可選擇性地重寫回應來稽核對應的答案。

## 代理詳細資訊

LLM 稽核員 (LLM Auditor) 的主要功能包括：

| 功能 | 描述 |
| --- | --- |
| **互動類型** | 工作流程 (Workflow) |
| **複雜度**  | 簡單 |
| **代理類型**  | 多代理 (Multi Agent) |
| **元件**  | 工具：內建 Google 搜尋 |
| **垂直領域**  | 水平 (Horizontal) |

### 代理架構：

此圖表顯示了用於實作此工作流程的代理與工具的詳細架構。
<img src="llm_auditor_architecture.png" alt="LLM Auditor Architecture" width="800"/>

## 設定與安裝

1.  **先決條件**

    *   Python 3.11+
    *   Poetry
        *   用於依賴管理與打包。請依照官方
            [Poetry 網站](https://python-poetry.org/docs/) 的說明進行安裝。

        ```bash
        pip install poetry
        ```

    *   一個 Google Cloud Platform 專案
    *   Google Cloud CLI
        *   關於安裝，請依照官方
            [Google Cloud 網站](https://cloud.google.com/sdk/docs/install) 的說明操作。

2.  **安裝**

    ```bash
    # 複製此儲存庫。
    git clone https://github.com/google/adk-samples.git
    cd adk-samples/python/agents/llm-auditor
    # 安裝套件與依賴。
    poetry install
    ```

3.  **設定**

    *   設定 Google Cloud 憑證。

        *   您可以在您的 shell 中設定以下環境變數，或改用一個
            `.env` 檔案。

        ```bash
        export GOOGLE_GENAI_USE_VERTEXAI=true
        export GOOGLE_CLOUD_PROJECT=<your-project-id>
        export GOOGLE_CLOUD_LOCATION=<your-project-location>
        export GOOGLE_CLOUD_STORAGE_BUCKET=<your-storage-bucket>  # 僅在 Agent Engine 上部署時需要
        ```

    *   驗證您的 GCloud 帳戶。

        ```bash
        gcloud auth application-default login
        gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
        ```

    *   如果您偏好在本地執行代理而不使用 Google Vertex AI 或雲端依賴，您可以在您的 shell 中設定以下
        環境變數，或改用一個 `.env` 檔案。

        ```bash
        export GOOGLE_GENAI_USE_VERTEXAI=false
        export GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

        關於如何取得 Google Gemini API 金鑰，請參考 [Google Gemini API 快速入門](https://ai.google.dev/gemini-api/docs/quickstart?lang=python#make-first-request)。

## 執行代理

**使用 `adk`**

ADK 提供了便利的方式來在本機啟動代理並與其互動。
您可以使用 CLI 與代理對話：

```bash
adk run llm_auditor
```

或透過網頁介面：

```bash
adk web
```

`adk web` 指令會在您的機器上啟動一個網頁伺服器並印出 URL。
您可以開啟該 URL，在左上角的下拉式選單中選擇 "llm_auditor"，
右側將會出現一個聊天機器人介面。對話最初是空白的。
以下是您可以要求 LLM 稽核員 (LLM Auditor) 驗證的一些範例請求：

*   `Double check this: Earth is further away from the Sun than Mars.` (請再次確認：地球比火星離太陽更遠。)
*   `Q: Why the blueberries are blue? A: Because blueberries have pigments on
    their skin.` (問：為什麼藍莓是藍色的？答：因為藍莓的表皮有色素。)

這些請求的範例回應如下方的 [範例互動](#範例互動) 章節所示。

**程式化存取**

以下是使用 Python 與代理互動的範例：

```python
import dotenv
dotenv.load_dotenv()  # 如果您已匯出環境變數，則可略過。
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent
from llm_auditor.agent import root_agent

user_input = "Double check this: Earth is further away from the Sun than Mars."

runner = InMemoryRunner(agent=root_agent)
session = runner.session_service.create_session(
    app_name=runner.app_name, user_id="test_user"
)
content = UserContent(parts=[Part(text=user_input)])
for event in runner.run(
    user_id=session.user_id, session_id=session.id, new_message=content
):
    for part in event.content.parts:
        print(part.text)
```

您也可以利用 `google.adk.Runner` 來對互動會話等進行更精細的控制，
或將代理包裝在一個 `vertexai.preview.reasoning_engines.AdkApp` 中。

### 範例互動

以下是與 LLM 稽核員 (LLM Auditor) 的範例互動。請注意，代理的確切輸出每次可能會不同。

```
user: Double check this: Earth is further away from the Sun than Mars. (請再次確認：地球比火星離太陽更遠。)

[critic_agent]: 好的，我會再次確認這個陳述：「地球比火星離太陽更遠。」

**步驟 1：識別聲明 (CLAIMS)**

答案包含一個聲明：

* 聲明 1：地球比火星離太陽更遠。

**步驟 2：驗證每個聲明 (CLAIM)**

* 聲明 1：地球比火星離太陽更遠。
    * 脈絡：這是一個關於地球和火星相對於太陽距離的直接事實陳述。
    * 外部來源：我將使用 Google 搜尋來查詢地球和火星距離太陽的平均距離。
    * 結論：**不準確**。
    * 理由：根據搜尋結果，地球距離太陽的平均距離約為 1.5 億公里 [2, 3, 6, 9]，
      而火星距離太陽的平均距離約為 2.28 億公里 [1, 4, 5, 8, 10]。因此，火星比地球離太陽更遠，
      這與該聲明相矛盾。

**步驟 3：提供整體評估**

    * 整體結論：不準確
    * 整體理由：答案中唯一的聲明根據廣泛可得的天文數據，顯然是錯誤的。
      因此，整個答案是錯誤的。

以下是我的驗證結果摘要：

* 聲明：地球比火星離太陽更遠。
    * 答案文本中的部分：「地球比火星離太陽更遠。」
    * 結論：不準確
    * 理由：地球距離太陽的平均距離約為 1.5 億公里，而火星距離太陽的平均距離約為 2.28 億公里。
      因此，火星比地球離太陽更遠。

參考資料：

<為求清晰省略>

[reviser_agent]: 火星比地球離太陽更遠。
```

```
user: Q: Why the blueberries are blue? A: Because blueberries have pigments on
their skin. (問：為什麼藍莓是藍色的？答：因為藍莓的表皮有色素。)

[critic_agent]: 好的，我將分析「為什麼藍莓是藍色的？」這個問題的答案，以驗證其準確性和完整性。

**步驟 1：識別聲明 (CLAIMS)**

我在答案中識別出以下聲明：

*   聲明 1：藍莓是藍色的，因為它們的表皮有色素。

**步驟 2：驗證每個聲明 (CLAIM)**

現在，我將驗證已識別的聲明。

*   考量脈絡：問題詢問藍莓呈現藍色的原因。
*   諮詢外部來源：我將使用 Google 搜尋來尋找有關造成藍莓藍色的色素資訊。
*   確定結論 (VERDICT)：

    *   聲明 1：藍莓是藍色的，因為它們的表皮有色素。
        最初的答案部分正確但不完整。雖然藍莓的確在它們的表皮含有色素，特別是花青素 [2, 4, 6, 8, 9]，
        但我們感知到的藍色主要是由於果實表面的一層蠟質塗層散射藍光所致 [1, 2, 3, 5, 10, 11]。
        底下的色素實際上是深紅色的 [1, 3, 5, 10]。

*   結論：不準確。答案並非完全錯誤，因為藍莓的確在它們的表皮含有色素。
    然而，它具有誤導性，因為它將藍色完全歸因於色素，而忽略了蠟質塗層及其光散射特性的關鍵作用。

**步驟 3：提供整體評估**

*   整體結論：不準確
*   整體理由：所提供的答案雖然提到了色素，但未能解釋藍莓呈現藍色的主要原因，
    即散射藍光的蠟質塗層。因此，該答案具有誤導性且不準確。

參考資料：

<為求清晰省略>

[reviser_agent]: 藍莓之所以是藍色，是由於其表皮上的一層蠟質塗層會散射藍光。它們的表皮也含有色素。
```

## 執行測試

若要執行測試與評估，請安裝額外的依賴：

```bash
poetry install --with dev
```

然後可以從 `llm-auditor` 目錄使用 `pytest` 模組執行測試與評估：

```bash
python3 -m pytest tests
python3 -m pytest eval
```

`tests` 會對一個範例請求執行代理，並確保每個元件都能正常運作。
`eval` 則示範如何評估代理，它使用了 ADK 中的 `AgentEvaluator`。
它會向代理發送幾個請求，並期望代理的回應能合理地匹配一個預先定義的回應。


## 部署

LLM 稽核員 (LLM Auditor) 可以使用以下指令部署到 Vertex AI Agent Engine：

```bash
poetry install --with deployment
python3 deployment/deploy.py --create
```

當部署完成後，將會印出類似這樣的一行：

```
Created remote agent: projects/<PROJECT_NUMBER>/locations/<PROJECT_LOCATION>/reasoningEngines/<AGENT_ENGINE_ID>
```

如果您忘記了 AGENT_ENGINE_ID，可以使用以下指令列出現有的代理：

```bash
python3 deployment/deploy.py --list
```

輸出將會像這樣：

```
All remote agents:

123456789 ("llm_auditor")
- Create time: 2025-04-09 08:22:36.179879+00:00
- Update time: 2025-04-09 08:25:42.734584+00:00
```

您可以在 Python 中以程式化方式與已部署的代理互動：

```python
import dotenv
dotenv.load_dotenv()  # 如果您已匯出環境變數，則可略過。
from vertexai import agent_engines

agent_engine_id = "AGENT_ENGINE_ID"
user_input = "Double check this: Earth is further away from the Sun than Mars."

agent_engine = agent_engines.get(agent_engine_id)
session = agent_engine.create_session(user_id="new_user")
for event in agent_engine.stream_query(
    user_id=session["user_id"], session_id=session["id"], message=user_input
):
    for part in event["content"]["parts"]:
        print(part["text"])
```

若要刪除已部署的代理，您可以執行以下指令：

```bash
python3 deployment/deploy.py --delete --resource_id=${AGENT_ENGINE_ID}
```

## 客製化

LLM 稽核員 (LLM Auditor) 可以被客製化以更好地滿足您的需求。例如：

1.  **替換檢索機制 (Substitute the Retrieval Mechanism)：** 將 `critic` 子代理的預設 `built_in_google_search` 工具替換為針對您的資料來源量身訂製的替代檢索工具。
2.  **客製化代理指令 (Customize Agent Instructions)：** 修改指導 `critic` 和 `reviser` 子代理的提示。這讓您可以引導它們的焦點（例如，檢查是否符合特定的合規規則、確保某種寫作風格）或完善它們的回饋與修訂格式。
3.  **實作迭代處理 (Implement Iterative Processing)：** 設定 LLM 稽核員 (LLM Auditor) 以迭代方式運作。回應可以由代理重複評估和重寫，直到達到預定的品質門檻，而不是單次處理。

## 免責聲明

此代理範例僅供說明之用，不適用於生產環境。它作為一個代理的基本範例，以及個人或團隊開發自己代理的基礎起點。

此範例未經嚴格測試，可能包含錯誤或限制，且不包含生產環境通常所需的功能或優化（例如，穩健的錯誤處理、安全措施、可擴展性、效能考量、全面的日誌記錄或進階設定選項）。

使用者對基於此範例的任何進一步開發、測試、安全強化和部署負全部責任。我們建議在使用任何衍生的代理於即時或關鍵系統之前，進行徹底的審查、測試並實施適當的保護措施。
