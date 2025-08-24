# 了解 Vertex AI Search 的資料基模 (Vertex AI Search Grounding)

[Vertex AI Search 資料基模工具 (Vertex AI Search Grounding tool)](../tools/built-in-tools.md#vertex-ai-search) 是代理開發套件 (Agent Development Kit, ADK) 中的一項強大功能，能讓 AI 代理程式存取您私有企業文件和資料儲存庫中的資訊。透過將您的代理程式與索引後的企業內容連結，您可以為使用者提供基於您組織知識庫的答案。

此功能對於需要從內部文件、政策、研究論文或任何已在您的 [Vertex AI Search](https://cloud.google.com/enterprise-search) 資料儲存區中建立索引的專有內容中獲取資訊的企業特定查詢特別有價值。當您的代理程式確定需要來自您知識庫的資訊時，它會自動搜尋您已建立索引的文件，並將結果整合到其回應中，並附上適當的來源標註。

## 您將學到什麼

在本指南中，您將了解：

- **快速設定**：如何從頭開始建立並執行一個啟用 Vertex AI Search 的代理程式
- **資料基模架構**：企業文件資料基模背後的資料流和技術流程
- **回應結構**：如何解讀資料基模回應及其元數據
- **最佳實踐**：向使用者顯示引用和文件參考的指南

## Vertex AI Search 資料基模快速入門

本快速入門將引導您建立一個具有 Vertex AI Search 資料基模功能的 ADK 代理程式。本快速入門假設您擁有一個本地 IDE（VS Code 或 PyCharm 等）、Python 3.9+ 以及終端機存取權限。

### 1. 準備 Vertex AI Search

如果您已經有 Vertex AI Search 資料儲存區及其資料儲存區 ID，則可以跳過此部分。如果沒有，請按照[開始使用自訂搜尋](https://cloud.google.com/generative-ai-app-builder/docs/try-enterprise-search#unstructured-data)中的說明，直到[建立資料儲存區](https://cloud.google.com/generative-ai-app-builder/docs/try-enterprise-search#create_a_data_store)的結尾，並選擇`非結構化資料`標籤。透過此說明，您將使用來自 [Alphabet 投資者網站](https://abc.xyz/) 的收益報告 PDF 建立一個範例資料儲存區。

完成「建立資料儲存區」部分後，請開啟[資料儲存區](https://console.cloud.google.com/gen-app-builder/data-stores/)並選擇您建立的資料儲存區，然後找到`資料儲存區 ID`：

![Vertex AI Search 資料儲存區](../assets/vertex_ai_search_grd_data_store.png)

請記下此`資料儲存區 ID`，我們稍後會用到。

### 2. 設定環境並安裝 ADK {#venv-install}

建立並啟用虛擬環境：

```bash
# 建立
python -m venv .venv

# 啟用 (每個新終端機)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

安裝 ADK：

```bash
pip install google-adk==1.5.0
```

### 3. 建立代理程式專案 {#create-agent-project}

在專案目錄下，執行以下指令：

```bash
# 步驟 1：為您的代理程式建立一個新目錄
mkdir vertex_search_agent

# 步驟 2：為代理程式建立 __init__.py
echo "from . import agent" > vertex_search_agent/__init__.py

# 步驟 3：建立 agent.py (代理程式定義) 和 .env (驗證設定)
touch vertex_search_agent/agent.py .env
```

#### 編輯 `agent.py`

將以下程式碼複製並貼到 `agent.py` 中，並根據您的專案 ID 和資料儲存區 ID，在`設定`部分替換 `YOUR_PROJECT_ID` 和 `YOUR_DATASTORE_ID`：

```python title="vertex_search_agent/agent.py"
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool

# 設定
DATASTORE_ID = "projects/YOUR_PROJECT_ID/locations/global/collections/default_collection/dataStores/YOUR_DATASTORE_ID"

root_agent = Agent(
    name="vertex_search_agent",
    model="gemini-2.5-flash",
    instruction="使用 Vertex AI Search 從內部文件中尋找資訊來回答問題。當有來源時務必引用。",
    description="具備 Vertex AI Search 功能的企業文件搜尋助理",
    tools=[VertexAiSearchTool(data_store_id=DATASTORE_ID)]
)
```

現在您應該有以下的目錄結構：

```console
my_project/
    vertex_search_agent/
        __init__.py
        agent.py
    .env
```

### 4. 驗證設定 {#choose-a-platform}

**注意：Vertex AI Search 需要 Google Cloud Platform (Vertex AI) 驗證。此工具不支援 Google AI Studio。**

  * 設定 [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
  * 從終端機執行 `gcloud auth login` 來驗證 Google Cloud。
  * 開啟 **`.env`** 檔案並複製貼上以下程式碼，並更新專案 ID 和位置。

    ```env title=".env"
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    GOOGLE_CLOUD_PROJECT=您的專案ID
    GOOGLE_CLOUD_LOCATION=您的位置
    ```


### 5. 執行您的代理程式 {#run-your-agent}

有多種方式可以與您的代理程式互動：

=== "開發者介面 (adk web)"
    執行以下指令以啟動**開發者介面**。

    ```shell
    adk web
    ```
    
    !!!info "給 Windows 使用者的提示"

        如果遇到 `_make_subprocess_transport NotImplementedError` 錯誤，請考慮改用 `adk web --no-reload`。


    **步驟 1：** 在瀏覽器中直接開啟提供的 URL（通常是 `http://localhost:8000` 或 `http://127.0.0.1:8000`）。

    **步驟 2：** 在介面的左上角，您可以在下拉式選單中選擇您的代理程式。選擇 "vertex_search_agent"。

    !!!note "疑難排解"

        如果您在下拉式選單中沒有看到 "vertex_search_agent"，請確保您是在代理程式資料夾的**父資料夾**（即 vertex_search_agent 的父資料夾）中執行 `adk web`。

    **步驟 3：** 現在您可以使用文字框與您的代理程式聊天。

=== "終端機 (adk run)"

    執行以下指令，與您的 Vertex AI Search 代理程式聊天。

    ```
    adk run vertex_search_agent
    ```
    若要結束，請使用 Cmd/Ctrl+C。

### 📝 嘗試的範例提示

透過這些問題，您可以確認代理程式確實正在呼叫 Vertex AI Search 以從 Alphabet 的報告中獲取資訊：

* Google Cloud 在 2022 年第一季的收入是多少？
* YouTube 的呢？

![Vertex AI Search 資料基模資料流](../assets/vertex_ai_search_grd_adk_web.png)

您已成功使用 ADK 建立並與您的 Vertex AI Search 代理程式互動！

## Vertex AI Search 的資料基模如何運作

使用 Vertex AI Search 的資料基模 (Grounding) 是將您的代理程式與您組織的索引文件和資料連接起來的過程，使其能夠根據私有企業內容產生準確的回應。當使用者的提示需要來自您內部知識庫的資訊時，代理程式底層的 LLM 會智慧地決定調用 `VertexAiSearchTool` 以從您已建立索引的文件中尋找相關事實。

### **資料流圖**

此圖說明了使用者查詢如何產生資料基模回應的逐步過程。

![Vertex AI Search 資料基模資料流](../assets/vertex_ai_search_grd_dataflow.png)

### **詳細說明**

資料基模代理程式使用圖中描述的資料流來檢索、處理企業資訊，並將其整合到呈現給使用者的最終答案中。

1. **使用者查詢**：終端使用者透過詢問有關內部文件或企業資料的問題與您的代理程式互動。

2. **ADK 協調**：代理開發套件 (Agent Development Kit) 協調代理程式的行為，並將使用者的訊息傳遞給代理程式的核心。

3. **LLM 分析與工具呼叫**：代理程式的 LLM（例如 Gemini 模型）會分析提示。如果它確定需要來自您已建立索引的文件的資訊，它會透過呼叫 VertexAiSearchTool 來觸發資料基模機制。這對於回答有關公司政策、技術文件或專有研究的查詢非常理想。

4. **Vertex AI Search 服務互動**：VertexAiSearchTool 與您設定的 Vertex AI Search 資料儲存區互動，該資料儲存區包含您已建立索引的企業文件。該服務會針對您的私有內容制定並執行搜尋查詢。

5. **文件檢索與排名**：Vertex AI Search 根據語義相似性和相關性評分，從您的資料儲存區中檢索並排名最相關的文件區塊。

6. **內容注入**：搜尋服務在產生最終回應之前，將檢索到的文件摘要整合到模型的內容中。這個關鍵步驟讓模型能夠基於您組織的事實資料進行「推理」。

7. **產生資料基模回應**：現在，LLM 在相關企業內容的幫助下，會產生一個包含從您的文件中檢索到的資訊的回應。

8. **帶有來源的回應呈現**：ADK 接收最終的資料基模回應，其中包含必要的來源文件參考和 groundingMetadata，並將其連同來源標註呈現給使用者。這讓終端使用者可以根據您的企業來源驗證資訊。

## 了解 Vertex AI Search 的資料基模回應

當代理程式使用 Vertex AI Search 為回應提供資料基模時，它會返回詳細資訊，包括最終的文字答案和有關用於產生該答案的文件的元數據。此元數據對於驗證回應和提供對您企業來源的歸屬至關重要。

### 資料基模回應範例

以下是模型在針對企業文件進行資料基模查詢後返回的內容物件範例。

**最終答案文字：**

```
"為醫療抄寫員開發模型帶來了幾個重大挑戰，這主要是由於醫療文件的複雜性、涉及的敏感資料以及臨床工作流程的嚴格要求。主要挑戰包括：**準確性和可靠性：** 醫療文件要求極高的準確性，因為錯誤可能導致誤診、不正確的治療和法律後果。確保 AI 模型能夠可靠地捕捉細微的醫學語言、區分主觀和客觀資訊，並準確轉錄醫病互動是一個主要障礙。**自然語言理解 (NLU) 和語音辨識：** 醫療對話通常節奏快，涉及高度專業的術語、縮寫和簡稱，並且可能由具有不同口音或說話模式的人說出... [回應繼續詳細分析隱私、整合和技術挑戰]"
```

**資料基模元數據摘要：**

這是您將收到的資料基模元數據。在 `adk web` 上，您可以在 `Response` 標籤頁找到此資訊：

```json
{
  "groundingMetadata": {
    "groundingChunks": [
      {
        "document": {
          "title": "AI in Medical Scribing: Technical Challenges",
          "uri": "projects/your-project/locations/global/dataStores/your-datastore-id/documents/doc-medical-scribe-ai-tech-challenges",
          "id": "doc-medical-scribe-ai-tech-challenges"
        }
      },
      {
        "document": {
          "title": "Regulatory and Ethical Hurdles for AI in Healthcare",
          "uri": "projects/your-project/locations/global/dataStores/your-datastore-id/documents/doc-ai-healthcare-ethics",
          "id": "doc-ai-healthcare-ethics"
        }
      }
      // ... 其他文件
    ],
    "groundingSupports": [
      {
        "groundingChunkIndices": [0, 1],
        "segment": {
          "endIndex": 637,
          "startIndex": 433,
          "text": "確保 AI 模型能夠可靠地捕捉細微的醫學語言..."
        }
      }
      // ... 其他將文字片段連結到來源文件的支援
    ],
    "retrievalQueries": [
      "自然語言處理醫學領域的挑戰",
      "AI 醫療抄寫員挑戰",
      "開發用於醫療抄寫員的 AI 的困難"
      // ... 其他執行的搜尋查詢
    ]
  }
}
```

### 如何解讀回應

元數據提供了模型產生的文字與支援它的企業文件之間的連結。以下是逐步分解：

- **groundingChunks**：這是模型參考的企業文件列表。每個區塊都包含文件標題、uri（文件路徑）和 id。

- **groundingSupports**：此列表將最終答案中的特定句子連結回 `groundingChunks`。

- **segment**：此物件識別最終文字答案的特定部分，由其 `startIndex`、`endIndex` 和 `text` 本身定義。

- **groundingChunkIndices**：此陣列包含對應於 `groundingChunks` 中所列來源的索引號碼。例如，有關「HIPAA 合規性」的文字由 `groundingChunks` 索引 1（「醫療保健中 AI 的法規和倫理障礙」文件）的資訊支援。

- **retrievalQueries**：此陣列顯示針對您的資料儲存區執行的特定搜尋查詢，以尋找相關資訊。

## 如何顯示 Vertex AI Search 的資料基模回應

與 Google 搜尋的資料基模不同，Vertex AI Search 的資料基模不需要特定的顯示元件。然而，顯示引用和文件參考可以建立信任，並讓使用者根據您組織的權威來源驗證資訊。

### 可選的引用顯示

由於提供了資料基模元數據，您可以根據應用程式需求選擇實作引用顯示：

**簡單文字顯示（最小實作）：**

```python
for event in events:
    if event.is_final_response():
        print(event.content.parts[0].text)
        
        # 可選：顯示來源計數
        if event.grounding_metadata:
            print(f"\n基於 {len(event.grounding_metadata.grounding_chunks)} 個文件")
```

**增強引用顯示（可選）：** 您可以實作互動式引用，顯示每個陳述由哪些文件支援。資料基模元數據提供了將文字片段對應到來源文件的所有必要資訊。

### 實作考量

在實作 Vertex AI Search 資料基模顯示時：

1. **文件存取**：驗證使用者對參考文件的權限
2. **簡單整合**：基本文字輸出不需要額外的顯示邏輯
3. **可選增強**：僅當您的使用案例受益於來源歸屬時才新增引用
4. **文件連結**：需要時將文件 URI 轉換為可存取的內部連結
5. **搜尋查詢**：`retrievalQueries` 陣列顯示對您的資料儲存區執行了哪些搜尋

## 總結

Vertex AI Search 資料基模 (Vertex AI Search Grounding) 將 AI 代理程式從通用助理轉變為企業特定的知識系統，能夠從您組織的私有文件中提供準確、有來源歸屬的資訊。透過將此功能整合到您的 ADK 代理程式中，您可以讓它們：

- 從您已建立索引的文件儲存庫中存取專有資訊
- 提供來源歸屬以實現透明度和信任
- 提供具有可驗證企業事實的全面答案
- 在您的 Google Cloud 環境中維護資料隱私

資料基模過程無縫地將使用者查詢與您組織的知識庫連接起來，用來自您私有文件的相關內容豐富回應，同時保持對話的流暢性。透過正確的實作，您的代理程式將成為企業資訊發現和決策的強大工具。
