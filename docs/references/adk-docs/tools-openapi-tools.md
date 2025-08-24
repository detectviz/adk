# OpenAPI 整合

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援正在計劃/即將推出。"}

## 使用 OpenAPI 整合 REST API

ADK 透過直接從 [OpenAPI 規格 (v3.x)](https://swagger.io/specification/) 自動產生可呼叫的工具，簡化了與外部 REST API 的互動。這消除了為每個 API 端點手動定義個別函式工具的需求。

!!! tip "核心優勢"
    使用 `OpenAPIToolset` 從您現有的 API 文件 (OpenAPI 規格) 立即建立代理程式工具 (`RestApiTool`)，使代理程式能夠無縫地呼叫您的 Web 服務。

## 主要元件

* **`OpenAPIToolset`**：這是您將使用的主要類別。您使用您的 OpenAPI 規格將其初始化，它會處理工具的解析和產生。
* **`RestApiTool`**：此類別代表一個單一、可呼叫的 API 操作 (例如 `GET /pets/{petId}` 或 `POST /pets`)。`OpenAPIToolset` 會為您規格中定義的每個操作建立一個 `RestApiTool` 實例。

## 運作方式

當您使用 `OpenAPIToolset` 時，該過程涉及以下主要步驟：

1. **初始化與解析**：
    * 您以 Python 字典、JSON 字串或 YAML 字串的形式向 `OpenAPIToolset` 提供 OpenAPI 規格。
    * 工具集會在內部解析規格，解析任何內部參考 (`$ref`) 以了解完整的 API 結構。

2. **操作發現**：
    * 它會識別您規格的 `paths` 物件中定義的所有有效 API 操作 (例如 `GET`、`POST`、`PUT`、`DELETE`)。

3. **工具產生**：
    * 對於每個發現的操作，`OpenAPIToolset` 會自動建立一個對應的 `RestApiTool` 實例。
    * **工具名稱**：衍生自規格中的 `operationId` (轉換為 `snake_case`，最多 60 個字元)。如果缺少 `operationId`，則會從方法和路徑產生一個名稱。
    * **工具描述**：使用操作中的 `summary` 或 `description` 供 LLM 使用。
    * **API 詳細資訊**：在內部儲存所需的 HTTP 方法、路徑、伺服器基礎 URL、參數 (路徑、查詢、標頭、cookie) 和請求主體結構描述。

4. **`RestApiTool` 功能**：每個產生的 `RestApiTool`：
    * **結構描述產生**：根據操作的參數和請求主體動態建立一個 `FunctionDeclaration`。此結構描述會告訴 LLM 如何呼叫該工具 (預期哪些參數)。
    * **執行**：當 LLM 呼叫時，它會使用 LLM 提供的參數和 OpenAPI 規格中的詳細資訊來建構正確的 HTTP 請求 (URL、標頭、查詢參數、主體)。它會處理驗證 (如果已設定) 並使用 `requests` 函式庫執行 API 呼叫。
    * **回應處理**：將 API 回應 (通常是 JSON) 傳回給代理程式流程。

5. **驗證**：您可以在初始化 `OpenAPIToolset` 時設定全域驗證 (如 API 金鑰或 OAuth - 有關詳細資訊，請參閱[驗證](tools-authentication.md))。此驗證設定會自動應用於所有產生的 `RestApiTool` 實例。

## 使用工作流程

請按照以下步驟將 OpenAPI 規格整合到您的代理程式中：

1. **取得規格**：取得您的 OpenAPI 規格文件 (例如，從 `.json` 或 `.yaml` 檔案載入，或從 URL 擷取)。
2. **實例化工具集**：建立一個 `OpenAPIToolset` 實例，傳入規格內容和類型 (`spec_str`/`spec_dict`, `spec_str_type`)。如果 API 需要，請提供驗證詳細資訊 (`auth_scheme`, `auth_credential`)。

    ```python
    from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

    # 使用 JSON 字串的範例
    openapi_spec_json = '...' # 您的 OpenAPI JSON 字串
    toolset = OpenAPIToolset(spec_str=openapi_spec_json, spec_str_type="json")

    # 使用字典的範例
    # openapi_spec_dict = {...} # 您的 OpenAPI 規格作為字典
    # toolset = OpenAPIToolset(spec_dict=openapi_spec_dict)
    ```

3. **新增至代理程式**：將檢索到的工具包含在您的 `LlmAgent` 的 `tools` 列表中。

    ```python
    from google.adk.agents import LlmAgent

    my_agent = LlmAgent(
        name="api_interacting_agent",
        model="gemini-2.0-flash", # 或您偏好的模型
        tools=[toolset], # 傳入工具集
        # ... 其他代理程式設定 ...
    )
    ```

4. **指示代理程式**：更新您代理程式的指令，告知它新的 API 功能以及它可以使用的工具名稱 (例如 `list_pets`、`create_pet`)。從規格產生的工具描述也將有助於 LLM。
5. **執行代理程式**：使用 `Runner` 執行您的代理程式。當 LLM 決定需要呼叫其中一個 API 時，它將產生一個針對適當 `RestApiTool` 的函式呼叫，然後該工具將自動處理 HTTP 請求。

## 範例

此範例示範如何從一個簡單的寵物店 OpenAPI 規格 (使用 `httpbin.org` 進行模擬回應) 產生工具，並透過代理程式與它們互動。

???+ "程式碼：寵物店 API"

    ```python title="openapi_example.py"
    --8<-- "examples/python/snippets/tools/openapi_tool.py"
    ```
