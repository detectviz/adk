# 品牌搜尋最佳化 - 用於搜尋最佳化的網頁瀏覽器代理 (Agent)

## 總覽

此代理 (agent) 旨在增強零售網站的產品資料。它會根據產品資料 (例如標題、描述和屬性) 產生關鍵字。然後，它會造訪一個網站、進行搜尋並分析熱門結果，以提供豐富產品標題的建議。這有助於透過識別產品資料中的差距來解決「空值和低回收率」或「零結果」搜尋等問題。此代理 (agent) 可以擴展以支援豐富描述和屬性。它使用的主要工具是：電腦使用和 bigquery 資料連線。

## 代理 (Agent) 詳細資料

此代理 (agent) 展示了具有工具呼叫和網頁爬取的多代理 (Multi Agent) 設定

| 屬性 | 詳細資料 |
|---|---|
| 互動類型 | 工作流程 |
| 複雜性 | 進階 |
| 代理 (Agent) 類型 | 多代理 (Multi Agent) |
| 多代理 (Multi Agent) 設計模式： | 路由器代理 (Router Agent) |
| 元件 | BigQuery 連線、電腦使用、工具、評估 |
| 垂直領域 | 零售 |

### 代理 (Agent) 架構

![品牌搜尋最佳化](./brand_search_optimization.png)

### 主要功能

* **工具：**

  * `function_calling`：根據使用者提供的品牌從產品目錄 (即 BigQuery 表格) 中取得資料。它以品牌字串作為輸入，並傳回資料庫記錄清單。

  * `load_artifacts_tool`：將網頁原始資料載入為成品 (artifact)，以分析元件以採取動作，例如點擊搜尋按鈕。

  * `網站爬取`：透過數個個別工具實現，例如 `go_to_url`、`take_screenshot`、`find_element_with_text`、`click_element_with_text`、`enter_text_into_element`、`scroll_down_screen`、`get_page_source`、`analyze_webpage_and_determine_action`

* **評估：** 此代理 (agent) 使用 ADK 提供的現成評估，可以使用 `sh deployment/eval.sh` 指令碼執行。

## 設定與安裝

1. **先決條件：**
    * Python 3.11+
    * Poetry
        * 用於依賴管理和打包。請按照官方 [Poetry 網站](https://python-poetry.org/docs/) 上的說明進行安裝。
    * Google Cloud Platform 上的專案
    * 從 [此處](https://aistudio.google.com) 取得您的 API 金鑰。(如果您想從 Vertex AI 使用 Gemini，則不需要)

2. **設定：**
    * 環境檔案設定
        * 複製範例環境檔案 `cp env.example .env`
        * 設定 `DISABLE_WEB_DRIVER=1`
        * 在 `.env` 檔案中為以下變數新增值
            * `GOOGLE_CLOUD_PROJECT=<YOUR_PROJECT>`
            * `GOOGLE_CLOUD_LOCATION=<YOUR_LOCATION>`

    * **API 金鑰：**
        * 您的 API 金鑰應新增至 `.env` 中的 `GOOGLE_API_KEY` 變數下
        * 您不需要同時設定 Google API 金鑰和 Vertex AI。任一設定皆可。
    * **BigQuery 設定**
        * BigQuery DATASET_ID 應在 `.env` 中的 `DATASET_ID` 下
        * BigQuery TABLE_ID 應在 `.env` 中的 `TABLE_ID` 下
        * BigQuery 表格設定可以使用以下 `sh deployment/run.sh` 自動完成，或按照 `BigQuery 設定` 部分中的步驟手動完成。

    * **其他設定：**
        * 您可以透過變更 `.env` 下的 `MODEL` 來變更 Gemini 模型
        * 當設定為 `1` 時，`DISABLE_WEB_DRIVER` 將使您能夠執行單元測試。有關詳細資訊，請參閱下面的 `單元測試` 部分。**注意** 在不測試時，預設將此旗標保持為 0。

3.  **使用您的 Google Cloud 帳戶進行驗證：**
    ```bash
    gcloud auth application-default login
    ```

4. **安裝：**

    * 使用 `deployment/run.sh` 安裝依賴項並填入資料庫

        `````bash
        # 複製此儲存庫。
        git clone https://github.com/google/adk-samples.git
        cd adk-samples/python/agents/brand-search-optimization

        # 執行此指令碼
        # 1. 建立並啟用新的虛擬環境
        # 2. 安裝 python 套件
        # 3. 使用 `.env` 檔案中設定的變數填入 BigQuery 資料
        sh deployment/run.sh
        `````

    * 設定 `DISABLE_WEB_DRIVER=0`

## 執行代理 (Agent)

您必須執行 `adk run brand_search_optimization` 才能讓代理 (agent) 執行。

您也可以使用 `adk web` 執行網頁應用程式。

`adk web` 命令將在您的電腦上啟動一個網頁伺服器並列印 URL。您可以開啟該 URL 並在聊天機器人介面中與代理 (agent) 互動。UI 最初是空白的。

從下拉式功能表中選取「brand-search-optimization」。

> **注意** 這應該會透過 web-driver 開啟一個新的 chrome 視窗。如果沒有，請確保 `.env` 檔案中的 `DISABLE_WEB_DRIVER=0`。

### 品牌名稱

* 如果您執行了 `deployment/run.sh` 指令碼。代理 (agent) 將預先設定為品牌 `BSOAgentTestBrand`。當代理 (agent) 詢問品牌名稱時，請提供 `BSOAgentTestBrand` 作為您的品牌名稱。
* 對於自訂資料，請修改品牌名稱。
* 當您提供品牌名稱時，代理 (agent) 流程會觸發。

> **注意**
>
> * 不要關閉代理 (agent) 開啟的額外 chrome 視窗。
> * 在代理 (agent) 提供關鍵字清單後，要求代理 (agent) 搜尋網站。例如「你能搜尋網站嗎？」、「你能在網站上搜尋關鍵字嗎？」、「幫我在網站上搜尋關鍵字」等。
> * 造訪 Google Shopping 網站時，您需要在第一次執行時完成驗證碼。完成驗證碼後，代理 (agent) 應在後續執行中執行。

### 互動範例

提供了一個範例會話，以說明品牌搜尋最佳化工具如何針對品牌 BSOAgentTestBrand 與 Google Shopping 一起運作 - [`example_interaction.md`](tests/example_interaction.md)

此檔案包含使用者與各種代理 (agent) 和工具之間的完整對話記錄，從關鍵字尋找到前 3 個搜尋結果標題之間的完整比較報告。

> **免責聲明** 此範例使用 Google Shopping 網站進行示範，但您有責任確保您遵守該網站的服務條款。

## 評估代理 (Agent)

這會使用 ADK 的評估元件，使用 `eval/data/` 內的 evalset 和 `eval/data/test_config.json` 中定義的設定來評估品牌搜尋最佳化代理 (agent)。

您必須在 `brand-search-optimization` 目錄內，然後執行

```bash
sh deployment/eval.sh
```

## 單元測試

按照以下步驟使用 `pytest` 執行單元測試

1. 在 `.env` 中修改此項 `DISABLE_WEB_DRIVER=1`

2. 執行 `sh deployment/test.sh`

此指令碼使用 `tests/unit/test_tools.py` 中 BigQuery 工具的模擬 BQ 用戶端執行單元測試。

## 部署代理 (Agent)

可以使用以下命令將代理 (agent) 部署到 Vertex AI Agent Engine：

在 `.env` -> `DISABLE_WEB_DRIVER=1` 中修改此項

```bash
python deployment/deploy.py --create
```

您也可以為您的使用案例修改部署指令碼。

## 自訂

如何自訂

* **修改對話流程：** 若要讓代理 (agent) 比較描述而非標題，您可以變更 `brand_search_optimization/sub_agents/search_results/prompt.py` 中的提示，具體來說，可以變更 `SEARCH_RESULT_AGENT_PROMPT` 下的 `<Gather Information>` 部分。
* **變更資料來源：** 可以透過變更 `.env` 檔案中的值將 BigQuery 表格設定為指向某個表格。
* **變更網站：** 此處的範例網站是 Google Shopping，請替換為您自己的網站，並相應地修改任何程式碼。

### BigQuery 設定

#### 自動化

`sh deployment/run.sh` 會執行一個指令碼，用範例資料填入 BigQuery 表格。它在幕後呼叫 `python tools/bq_populate_data.py` 指令碼。

#### 資料集和表格權限

如果您想在非您擁有的 BigQuery 表格上執行代理 (agent)，
請參閱 [此處](./customization.md) 的說明以授予必要的權限。

#### 手動步驟

檢查 `deployment/bq_data_setup.sql` 中的 SQL 查詢以手動新增資料

## 疑難排解與常見問題

### BigQuery 資料不存在

這與 - 找不到資料集、在該位置找不到資料集、使用者沒有 bigquery 資料集的權限有關

錯誤：

```bash
google.api_core.exceptions.NotFound: 404 Not found: Dataset ...:products_data_agent was not found in location US; reason: notFound, message: Not found: Dataset ...:products_data_agent was not found in location US
```

修正：
確保您遵循 `BigQuery 設定` 部分

### Selenium 問題

這與 Selenium / Webdriver 問題有關

錯誤：

```bash
selenium.common.exceptions.SessionNotCreatedException: Message: session not created: probably user data directory is already in use, please specify a unique value for --user-data-dir argument, or don't use --user-data-dir
```

修正：移除資料目錄

```bash
rm -rf /tmp/selenium
```

### 代理 (Agent) 流程問題

#### 已知問題

* 當網站強制執行機器人檢查以及搜尋元素被隱藏時，代理 (agent) 無法可靠地執行。
* 代理 (agent) 不建議下一步 - 這發生在關鍵字尋找階段之後。在這種情況下，要求代理 (agent) 搜尋熱門關鍵字。例如「你能搜尋關鍵字嗎？」或更明確地說「將我轉到網頁瀏覽器代理 (agent)」
* 代理 (agent) 再次詢問關鍵字 - 例如「好的，我會去 XYZ.com。你想在 XYZ 上搜尋什麼關鍵字？」。請再次提供關鍵字。


## 免責聲明

此代理 (agent) 範例僅供說明之用，不適用於生產環境。它可作為代理 (agent) 的基本範例，以及個人或團隊開發自己的代理 (agent) 的基礎起點。

此範例未經嚴格測試，可能包含錯誤或限制，並且不包含生產環境通常所需的功能或最佳化 (例如，強固的錯誤處理、安全措施、可擴展性、效能考量、全面的日誌記錄或進階設定選項)。

使用者對基於此範例的代理 (agent) 的任何進一步開發、測試、安全強化和部署負全部責任。我們建議在使用任何衍生的代理 (agent) 於即時或關鍵系統之前，進行徹底的審查、測試並實施適當的保護措施。