# 代理程式開發套件 (ADK) 中的日誌記錄

代理程式開發套件 (ADK) 使用 Python 標準的 `logging` 模組，提供靈活而強大的日誌記錄功能。了解如何設定和解讀這些日誌，對於監控代理程式行為和有效偵錯問題至關重要。

## 日誌記錄理念

ADK 的日誌記錄方法是提供詳細的診斷資訊，同時預設情況下不會過於冗長。它被設計為由應用程式開發人員進行設定，讓您可以根據您的特定需求，無論是在開發還是生產環境中，量身訂製日誌輸出。

- **標準函式庫：** 它使用標準的 `logging` 函式庫，因此任何適用於它的設定或處理常式都將適用於 ADK。
- **階層式日誌記錄器：** 日誌記錄器根據模組路徑進行階層式命名（例如，`google_adk.google.adk.agents.llm_agent`），從而可以對框架的哪些部分產生日誌進行精細控制。
- **使用者設定：** 框架本身不設定日誌記錄。使用框架的開發人員有責任在其應用程式的進入點設定所需的日誌記錄設定。

## 如何設定日誌記錄

您可以在初始化並執行代理程式之前，在您的主應用程式腳本（例如 `main.py`）中設定日誌記錄。最簡單的方法是使用 `logging.basicConfig`。

### 範例設定

若要啟用詳細的日誌記錄，包括 `DEBUG` 等級的訊息，請將以下內容新增到您的腳本頂部：

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# 您的 ADK 代理程式程式碼如下...
# from google.adk.agents import LlmAgent
# ...
```

### 使用 ADK CLI 設定日誌記錄

當使用 ADK 內建的 Web 或 API 伺服器執行代理程式時，您可以直接從命令列輕鬆控制日誌的詳細程度。`adk web`、`adk api_server` 和 `adk deploy cloud_run` 指令都接受一個 `--log-level` 選項。

這提供了一種方便的方式來設定日誌記錄等級，而無需修改代理程式的原始碼。

**使用 `adk web` 的範例：**

若要以 `DEBUG` 等級的日誌記錄啟動 Web 伺服器，請執行：

```bash
adk web --log-level DEBUG path/to/your/agents_dir
```

`--log-level` 選項可用的日誌等級有：
- `DEBUG`
- `INFO` (預設)
- `WARNING`
- `ERROR`
- `CRITICAL`

> 對於 `DEBUG` 等級，您也可以使用 `-v` 或 `--verbose` 作為 `--log_level DEBUG` 的捷徑。例如：
> 
> ```bash
> adk web -v path/to/your/agents_dir
> ```

此命令列設定會覆寫您程式碼中可能為 ADK 的日誌記錄器設定的任何程式化設定（如 `logging.basicConfig`）。

### 日誌等級

ADK 使用標準的日誌等級來分類訊息的重要性：

-   `DEBUG`：最詳細的等級。用於細微的診斷資訊，例如傳送給大型語言模型 (LLM) 的完整提示、詳細的狀態變更和內部邏輯流程。**對於偵錯至關重要。**
-   `INFO`：關於代理程式生命週期的一般資訊。這包括代理程式啟動、會話建立和工具執行等事件。
-   `WARNING`：表示潛在問題或使用了已棄用的功能。代理程式可以繼續運作，但問題可能需要注意。
-   `ERROR`：發生了嚴重錯誤，導致代理程式無法執行操作。

> **注意：** 建議在生產環境中使用 `INFO` 或 `WARNING`，並僅在主動排除問題時才啟用 `DEBUG`，因為 `DEBUG` 日誌可能非常冗長，且可能包含敏感資訊。

## 記錄了什麼

根據設定的日誌等級，您可以預期看到以下資訊：

| 等級      | 記錄的資訊類型                                                                                                 |
| :-------- | :--------------------------------------------------------------------------------------------------------------------- |
| **DEBUG** | - **完整的 LLM 提示：** 傳送給語言模型的完整請求，包括系統指令、歷史記錄和工具。 |
|           | - 來自服務的詳細 API 回應。                                                                                |
|           | - 內部狀態轉換和變數值。                                                                      |
| **INFO**  | - 代理程式初始化和啟動。                                                                                    |
|           | - 會話建立和刪除事件。                                                                                |
|           | - 工具的執行，包括工具名稱和參數。                                                          |
| **WARNING**| - 使用已棄用的方法或參數。                                                                             |
|           | - 系統可以從中恢復的非關鍵性錯誤。                                                                 |
| **ERROR** | - 對外部服務（例如 LLM、會話服務）的 API 呼叫失敗。                                                  |
|           | - 代理程式執行期間未處理的例外。                                                                         |
|           | - 設定錯誤。                                                                                                |

## 閱讀和理解日誌

`basicConfig` 範例中的 `format` 字串決定了每個日誌訊息的結構。讓我們分解一個範例日誌條目：

`2025-07-08 11:22:33,456 - DEBUG - google_adk.google.adk.models.google_llm - LLM Request: contents { ... }`

-   `2025-07-08 11:22:33,456`：`%(asctime)s` - 記錄日誌的時間戳。
-   `DEBUG`：`%(levelname)s` - 訊息的嚴重性等級。
-   `google_adk.google.adk.models.google_llm`：`%(name)s` - 日誌記錄器的名稱。這個階層式名稱會確切地告訴您 ADK 框架中的哪個模組產生了該日誌。在這種情況下，是 Google LLM 模型包裝器。
-   `Request to LLM: contents { ... }`：`%(message)s` - 實際的日誌訊息。

透過閱讀日誌記錄器名稱，您可以立即找出日誌的來源，並了解其在代理程式架構中的上下文。

## 使用日誌進行偵錯：一個實際範例

**情境：** 您的代理程式沒有產生預期的輸出，您懷疑傳送給 LLM 的提示不正確或缺少資訊。

**步驟：**

1.  **啟用 DEBUG 日誌記錄：** 在您的 `main.py` 中，將日誌記錄等級設定為 `DEBUG`，如設定範例所示。

    ```python
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    ```

2.  **執行您的代理程式：** 像平常一樣執行您代理程式的任務。

3.  **檢查日誌：** 在主控台輸出中尋找來自 `google.adk.models.google_llm` 日誌記錄器的訊息，該訊息以 `LLM Request:` 開頭。

    ```log
    ...
    2025-07-10 15:26:13,778 - DEBUG - google_adk.google.adk.models.google_llm - Sending out request, model: gemini-2.0-flash, backend: GoogleLLMVariant.GEMINI_API, stream: False
    2025-07-10 15:26:13,778 - DEBUG - google_adk.google.adk.models.google_llm - 
    LLM Request:
    -----------------------------------------------------------
    System Instruction:

          您擲骰子並回答有關骰子擲出結果的問題。
          您可以擲不同大小的骰子。
          您可以透過並行呼叫函式（在一個請求和一個回合中）來並行使用多個工具。
          可以討論以前的骰子角色，並評論骰子擲出的結果。
          當要求您擲骰子時，您必須使用骰子面數呼叫 roll_die 工具。請務必傳入一個整數。不要傳入字串。
          您永遠不應該自己擲骰子。
          檢查質數時，請使用整數列表呼叫 check_prime 工具。請務必傳入一個整數列表。您永遠不應該傳入字串。
          在呼叫工具之前，您不應該檢查質數。
          當要求您擲骰子並檢查質數時，您應始終進行以下兩個函式呼叫：
          1. 您應首先呼叫 roll_die 工具以獲得擲骰結果。在呼叫 check_prime 工具之前，請等待函式回應。
          2. 從 roll_die 工具獲得函式回應後，您應使用 roll_die 結果呼叫 check_prime 工具。
            2.1 如果使用者要求您根據以前的擲骰結果檢查質數，請確保將以前的擲骰結果包含在列表中。
          3. 當您回應時，您必須包含步驟 1 中的 roll_die 結果。
          在要求擲骰和檢查質數時，您應始終執行前述 3 個步驟。
          您不應依賴先前關於質數結果的歷史記錄。
        

    您是一個代理程式。您的內部名稱是 "hello_world_agent"。

    關於您的描述是「可以擲 8 面骰子並檢查質數的 hello world 代理程式」。
    -----------------------------------------------------------
    Contents:
    {"parts":[{"text":"擲一個 6 面骰子"}],"role":"user"}
    {"parts":[{"function_call":{"args":{"sides":6},"name":"roll_die"}}],"role":"model"}
    {"parts":[{"function_response":{"name":"roll_die","response":{"result":2}}}],"role":"user"}
    -----------------------------------------------------------
    Functions:
    roll_die: {'sides': {'type': <Type.INTEGER: 'INTEGER'>}} 
    check_prime: {'nums': {'items': {'type': <Type.INTEGER: 'INTEGER'>}, 'type': <Type.ARRAY: 'ARRAY'>}} 
    -----------------------------------------------------------

    2025-07-10 15:26:13,779 - INFO - google_genai.models - AFC is enabled with max remote calls: 10.
    2025-07-10 15:26:14,309 - INFO - google_adk.google.adk.models.google_llm - 
    LLM Response:
    -----------------------------------------------------------
    Text:
    我擲了一個 6 面骰子，結果是 2。
    ...
    ```

4.  **分析提示：** 透過檢查記錄請求的 `System Instruction`、`contents`、`functions` 部分，您可以驗證：
    -   系統指令是否正確？
    -   對話歷史（`user` 和 `model` 的輪次）是否準確？
    -   是否包含了最新的使用者查詢？
    -   是否向模型提供了正確的工具？
    -   模型是否正確地呼叫了工具？
    -   模型需要多長時間回應？

這個詳細的輸出讓您可以直接從日誌檔案中診斷各種問題，從不正確的提示工程到工具定義的問題。
