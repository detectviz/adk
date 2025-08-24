# 模型上下文協定工具

本指南將引導您了解兩種將模型上下文協定 (MCP) 與 ADK 整合的方法。

## 什麼是模型上下文協定 (MCP)？

模型上下文協定 (MCP) 是一個開放標準，旨在標準化大型語言模型 (LLM)，如 Gemini 和 Claude，與外部應用程式、資料來源和工具的通訊方式。您可以把它想像成一個通用的連接機制，簡化了 LLM 獲取上下文、執行操作以及與各種系統互動的方式。

MCP 遵循客戶端-伺服器架構，定義了**資料** (資源)、**互動式範本** (提示) 和**可操作函式** (工具) 如何由 **MCP 伺服器**公開，並由 **MCP 客戶端** (可以是 LLM 主機應用程式或 AI 代理程式) 使用。

本指南涵蓋兩種主要的整合模式：

1. **在 ADK 中使用現有的 MCP 伺服器：** ADK 代理程式充當 MCP 客戶端，利用外部 MCP 伺服器提供的工具。
2. **透過 MCP 伺服器公開 ADK 工具：** 建立一個包裝 ADK 工具的 MCP 伺服器，使其可供任何 MCP 客戶端存取。

## 先決條件

在開始之前，請確保您已完成以下設定：

* **設定 ADK：** 遵循快速入門中的標準 ADK [設定說明](../get-started/quickstart.md/#venv-install)。
* **安裝/更新 Python/Java：** MCP 需要 Python 3.9 或更高版本，或 Java 17+。
* **設定 Node.js 和 npx：** **(僅限 Python)** 許多社群 MCP 伺服器是以 Node.js 套件的形式分發，並使用 `npx` 執行。如果您尚未安裝 Node.js (其中包含 npx)，請先安裝。詳細資訊請參閱 [https://nodejs.org/en](https://nodejs.org/en)。
* **驗證安裝：** **(僅限 Python)** 確認 `adk` 和 `npx` 在您已啟用的虛擬環境中的 PATH 中：

```shell
# 這兩個指令都應該會列印出可執行檔的路徑。
which adk
which npx
```

## 1. 在 `adk web` 中將 MCP 伺服器與 ADK 代理程式一起使用 (ADK 作為 MCP 客戶端)

本節示範如何將來自外部 MCP (模型上下文協定) 伺服器的工具整合到您的 ADK 代理程式中。當您的 ADK 代理程式需要使用由公開 MCP 介面的現有服務所提供的功能時，這是**最常見**的整合模式。您將看到如何將 `MCPToolset` 類別直接新增到代理程式的 `tools` 列表中，從而實現與 MCP 伺服器的無縫連接、發現其工具，並使其可供您的代理程式使用。這些範例主要著重於在 `adk web` 開發環境中的互動。

### `MCPToolset` 類別

`MCPToolset` 類別是 ADK 用於整合來自 MCP 伺服器的工具的主要機制。當您在代理程式的 `tools` 列表中包含 `MCPToolset` 實例時，它會自動處理與指定 MCP 伺服器的互動。其運作方式如下：

1.  **連線管理：** 在初始化時，`MCPToolset` 會建立並管理與 MCP 伺服器的連線。這可以是本地伺服器進程 (使用 `StdioConnectionParams` 透過標準輸入/輸出進行通訊) 或遠端伺服器 (使用 `SseConnectionParams` 透過伺服器發送事件)。當代理程式或應用程式終止時，該工具集也會處理此連線的正常關閉。
2.  **工具發現與適配：** 連線後，`MCPToolset` 會查詢 MCP 伺服器以取得其可用工具 (透過 `list_tools` MCP 方法)。然後，它會將這些發現的 MCP 工具的結構描述轉換為與 ADK 相容的 `BaseTool` 實例。
3.  **向代理程式公開：** 然後，這些經過適配的工具會像原生 ADK 工具一樣提供給您的 `LlmAgent` 使用。
4.  **代理工具呼叫：** 當您的 `LlmAgent` 決定使用這些工具之一時，`MCPToolset` 會透明地將呼叫 (使用 `call_tool` MCP 方法) 代理到 MCP 伺服器，傳送必要的參數，並將伺服器的回應傳回給代理程式。
5.  **篩選 (可選)：** 您可以在建立 `MCPToolset` 時使用 `tool_filter` 參數，以從 MCP 伺服器中選擇特定的工具子集，而不是將所有工具都公開給您的代理程式。

以下範例示範如何在 `adk web` 開發環境中使用 `MCPToolset`。對於需要對 MCP 連線生命週期進行更精細控制或未使用 `adk web` 的場景，請參閱本頁後面的「在 `adk web` 之外的您自己的代理程式中使用 MCP 工具」一節。

### 範例 1：檔案系統 MCP 伺服器

此範例示範如何連接到提供檔案系統操作的本地 MCP 伺服器。

#### 步驟 1：使用 `MCPToolset` 定義您的代理程式

建立一個 `agent.py` 檔案 (例如，在 `./adk_agent_samples/mcp_agent/agent.py` 中)。`MCPToolset` 直接在您的 `LlmAgent` 的 `tools` 列表中實例化。

*   **重要：** 將 `args` 列表中的 `"/path/to/your/folder"` 替換為您本地系統上 MCP 伺服器可以存取的實際資料夾的**絕對路徑**。
*   **重要：** 將 `.env` 檔案放在 `./adk_agent_samples` 目錄的父目錄中。

```python
# ./adk_agent_samples/mcp_agent/agent.py
import os # 路徑操作所需
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StdioServerParameters

# 如果可能，動態定義路徑是一種很好的做法，
# 或確保使用者了解需要絕對路徑。
# 在此範例中，我們將建構一個相對於此檔案的路徑，
# 假設 '/path/to/your/folder' 與 agent.py 位於同一目錄中。
# 如果您的設定需要，請將此替換為實際的絕對路徑。
TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "/path/to/your/folder")
# 確保 TARGET_FOLDER_PATH 是 MCP 伺服器的絕對路徑。
# 如果您建立了 ./adk_agent_samples/mcp_agent/your_folder，

root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='filesystem_assistant_agent',
    instruction='幫助使用者管理他們的檔案。您可以列出檔案、讀取檔案等。',
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",  # npx 自動確認安裝的參數
                        "@modelcontextprotocol/server-filesystem",
                        # 重要：這必須是 npx 進程可以存取的資料夾的絕對路徑。
                        # 請替換為您系統上的有效絕對路徑。
                        # 例如："/Users/youruser/accessible_mcp_files"
                        # 或使用動態建構的絕對路徑：
                        os.path.abspath(TARGET_FOLDER_PATH),
                    ],
                ),
            ),
            # 可選：篩選從 MCP 伺服器公開的工具
            # tool_filter=['list_directory', 'read_file']
        )
    ],
)
```


#### 步驟 2：建立一個 `__init__.py` 檔案

確保在與 `agent.py` 相同的目錄中有一個 `__init__.py`，使其成為 ADK 可發現的 Python 套件。

```python
# ./adk_agent_samples/mcp_agent/__init__.py
from . import agent
```

#### 步驟 3：執行 `adk web` 並互動

在您的終端機中，導覽至 `mcp_agent` 的父目錄 (例如 `adk_agent_samples`) 並執行：

```shell
cd ./adk_agent_samples # 或您對等的父目錄
adk web
```

!!!info "給 Windows 使用者的提示"

    如果遇到 `_make_subprocess_transport NotImplementedError` 錯誤，請考慮改用 `adk web --no-reload`。


一旦 ADK Web UI 在您的瀏覽器中載入：

1.  從代理程式下拉式選單中選擇 `filesystem_assistant_agent`。
2.  嘗試像這樣的提示：
    *   「列出目前目錄中的檔案。」
    *   「你能讀取名為 sample.txt 的檔案嗎？」(假設您已在 `TARGET_FOLDER_PATH` 中建立它)。
    *   「`another_file.md` 的內容是什麼？」

您應該會看到代理程式與 MCP 檔案系統伺服器互動，並且伺服器的回應 (檔案清單、檔案內容) 會透過代理程式轉發。如果您將 `npx` 進程的輸出導向 stderr，`adk web` 主控台 (您執行指令的終端機) 可能也會顯示其日誌。

<img src="../../assets/adk-tool-mcp-filesystem-adk-web-demo.png" alt="MCP with ADK Web - FileSystem Example">


### 範例 2：Google 地圖 MCP 伺服器

此範例示範如何連接到 Google 地圖 MCP 伺服器。

#### 步驟 1：取得 API 金鑰並啟用 API

1.  **Google 地圖 API 金鑰：** 按照 [使用 API 金鑰](https://developers.google.com/maps/documentation/javascript/get-api-key#create-api-keys) 的說明取得 Google 地圖 API 金鑰。
2.  **啟用 API：** 在您的 Google Cloud 專案中，確保已啟用以下 API：
    *   Directions API
    *   Routes API
    有關說明，請參閱 [Google 地圖平台入門](https://developers.google.com/maps/get-started#enable-api-sdk) 文件。

#### 步驟 2：使用 `MCPToolset` 定義您的 Google 地圖代理程式

修改您的 `agent.py` 檔案 (例如，在 `./adk_agent_samples/mcp_agent/agent.py` 中)。將 `YOUR_GOOGLE_MAPS_API_KEY` 替換為您取得的實際 API 金鑰。

```python
# ./adk_agent_samples/mcp_agent/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StdioServerParameters

# 從環境變數中檢索 API 金鑰或直接插入。
# 使用環境變數通常更安全。
# 確保在您執行 'adk web' 的終端機中設定此環境變數。
# 範例：export GOOGLE_MAPS_API_KEY="您的實際金鑰"
google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

if not google_maps_api_key:
    # 測試的備用方案或直接指派 - 不建議用於生產環境
    google_maps_api_key = "在此處貼上您的GOOGLE_MAPS_API_KEY" # 如果不使用環境變數，請替換
    if google_maps_api_key == "在此處貼上您的GOOGLE_MAPS_API_KEY":
        print("警告：未設定 GOOGLE_MAPS_API_KEY。請將其設定為環境變數或在腳本中設定。")
        # 如果金鑰至關重要但未找到，您可能需要引發錯誤或退出。

root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='maps_assistant_agent',
    instruction='使用 Google 地圖工具幫助使用者進行地圖繪製、路線規劃和尋找地點。',
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-google-maps",
                    ],
                    # 將 API 金鑰作為環境變數傳遞給 npx 進程
                    # 這是 Google 地圖的 MCP 伺服器期望金鑰的方式。
                    env={
                        "GOOGLE_MAPS_API_KEY": google_maps_api_key
                    }
                ),
            ),
            # 如果需要，您可以篩選特定的地圖工具：
            # tool_filter=['get_directions', 'find_place_by_id']
        )
    ],
)
```

#### 步驟 3：確保 `__init__.py` 存在

如果您在範例 1 中已建立此檔案，則可以跳過此步驟。否則，請確保在 `./adk_agent_samples/mcp_agent/` 目錄中有一個 `__init__.py`：

```python
# ./adk_agent_samples/mcp_agent/__init__.py
from . import agent
```

#### 步驟 4：執行 `adk web` 並互動

1.  **設定環境變數 (建議)：**
    在執行 `adk web` 之前，最好在您的終端機中將您的 Google 地圖 API 金鑰設定為環境變數：
    ```shell
    export GOOGLE_MAPS_API_KEY="您的實際GOOGLE_MAPS_API_KEY"
    ```
    將 `您的實際GOOGLE_MAPS_API_KEY` 替換為您的金鑰。

2.  **執行 `adk web`**：
    導覽至 `mcp_agent` 的父目錄 (例如 `adk_agent_samples`) 並執行：
    ```shell
    cd ./adk_agent_samples # 或您對等的父目錄
    adk web
    ```

3.  **在 UI 中互動**：
    *   選擇 `maps_assistant_agent`。
    *   嘗試像這樣的提示：
        *   「從 GooglePlex 到 SFO 的路線。」
        *   「在金門公園附近找咖啡店。」
        *   「從法國巴黎到德國柏林的路線是什麼？」

您應該會看到代理程式使用 Google 地圖 MCP 工具來提供路線或基於位置的資訊。

<img src="../../assets/adk-tool-mcp-maps-adk-web-demo.png" alt="MCP with ADK Web - Google Maps Example">


## 2. 使用 ADK 工具建立 MCP 伺服器 (公開 ADK 的 MCP 伺服器)

此模式允許您包裝現有的 ADK 工具，並使其可供任何標準的 MCP 客戶端應用程式使用。本節中的範例透過自訂建置的 MCP 伺服器公開 ADK `load_web_page` 工具。

### 步驟摘要

您將使用 `mcp` 函式庫建立一個標準的 Python MCP 伺服器應用程式。在此伺服器中，您將：

1.  實例化您想要公開的 ADK 工具 (例如 `FunctionTool(load_web_page)`)。
2.  實作 MCP 伺服器的 `@app.list_tools()` 處理常式以通告 ADK 工具。這涉及使用 `google.adk.tools.mcp_tool.conversion_utils` 中的 `adk_to_mcp_tool_type` 公用程式將 ADK 工具定義轉換為 MCP 結構描述。
3.  實作 MCP 伺服器的 `@app.call_tool()` 處理常式。此處理常式將：
    *   從 MCP 客戶端接收工具呼叫請求。
    *   識別請求是否針對您包裝的 ADK 工具之一。
    *   執行 ADK 工具的 `.run_async()` 方法。
    *   將 ADK 工具的結果格式化為符合 MCP 規範的回應 (例如 `mcp.types.TextContent`)。

### 先決條件

在與您的 ADK 安裝相同的 Python 環境中安裝 MCP 伺服器函式庫：

```shell
pip install mcp
```

### 步驟 1：建立 MCP 伺服器腳本

為您的 MCP 伺服器建立一個新的 Python 檔案，例如 `my_adk_mcp_server.py`。

### 步驟 2：實作伺服器邏輯

將以下程式碼新增到 `my_adk_mcp_server.py`。此腳本設定了一個 MCP 伺服器，該伺服器公開了 ADK `load_web_page` 工具。

```python
# my_adk_mcp_server.py
import asyncio
import json
import os
from dotenv import load_dotenv

# MCP 伺服器匯入
from mcp import types as mcp_types # 使用別名以避免衝突
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio # 用於作為 stdio 伺服器執行

# ADK 工具匯入
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.load_web_page import load_web_page # 範例 ADK 工具
# ADK <-> MCP 轉換公用程式
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

# --- 載入環境變數 (如果 ADK 工具需要它們，例如 API 金鑰) ---
load_dotenv() # 如果需要，請在同一目錄中建立一個 .env 檔案

# --- 準備 ADK 工具 ---
# 實例化您想要公開的 ADK 工具。
# 此工具將被包裝並由 MCP 伺服器呼叫。
print("正在初始化 ADK load_web_page 工具...")
adk_tool_to_expose = FunctionTool(load_web_page)
print(f"ADK 工具 '{adk_tool_to_expose.name}' 已初始化並準備好透過 MCP 公開。")
# --- 結束 ADK 工具準備 ---

# --- MCP 伺服器設定 ---
print("正在建立 MCP 伺服器實例...")
# 使用 mcp.server 函式庫建立一個具名的 MCP 伺服器實例
app = Server("adk-tool-exposing-mcp-server")

# 實作 MCP 伺服器的處理常式以列出可用工具
@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """MCP 處理常式，用於列出此伺服器公開的工具。"""
    print("MCP 伺服器：收到 list_tools 請求。")
    # 將 ADK 工具的定義轉換為 MCP 工具結構描述格式
    mcp_tool_schema = adk_to_mcp_tool_type(adk_tool_to_expose)
    print(f"MCP 伺服器：正在通告工具：{mcp_tool_schema.name}")
    return [mcp_tool_schema]

# 實作 MCP 伺服器的處理常式以執行工具呼叫
@app.call_tool()
async def call_mcp_tool(
    name: str, arguments: dict
) -> list[mcp_types.Content]: # MCP 使用 mcp_types.Content
    """MCP 處理常式，用於執行 MCP 客戶端請求的工具呼叫。"""
    print(f"MCP 伺服器：收到對 '{name}' 的 call_tool 請求，參數為：{arguments}")

    # 檢查請求的工具名稱是否與我們包裝的 ADK 工具相符
    if name == adk_tool_to_expose.name:
        try:
            # 執行 ADK 工具的 run_async 方法。
            # 注意：此處 tool_context 為 None，因為此 MCP 伺服器
            # 是在完整的 ADK Runner 調用之外執行 ADK 工具。
            # 如果 ADK 工具需要 ToolContext 功能 (如狀態或驗證)，
            # 則此直接調用可能需要更複雜的處理。
            adk_tool_response = await adk_tool_to_expose.run_async(
                args=arguments,
                tool_context=None,
            )
            print(f"MCP 伺服器：ADK 工具 '{name}' 已執行。回應：{adk_tool_response}")

            # 將 ADK 工具的回應 (通常是字典) 格式化為符合 MCP 規範的格式。
            # 在此，我們將回應字典序列化為 TextContent 中的 JSON 字串。
            # 根據 ADK 工具的輸出和客戶端需求調整格式。
            response_text = json.dumps(adk_tool_response, indent=2)
            # MCP 期望一個 mcp_types.Content 部分的列表
            return [mcp_types.TextContent(type="text", text=response_text)]

        except Exception as e:
            print(f"MCP 伺服器：執行 ADK 工具 '{name}' 時發生錯誤：{e}")
            # 以 MCP 格式傳回錯誤訊息
            error_text = json.dumps({"error": f"執行工具 '{name}' 失敗：{str(e)}"})
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        # 處理對未知工具的呼叫
        print(f"MCP 伺服器：此伺服器找不到/未公開工具 '{name}'。")
        error_text = json.dumps({"error": f"此伺服器未實作工具 '{name}'。"})
        return [mcp_types.TextContent(type="text", text=error_text)]

# --- MCP 伺服器執行器 ---
async def run_mcp_stdio_server():
    """執行 MCP 伺服器，透過標準輸入/輸出監聽連線。"""
    # 使用 mcp.server.stdio 函式庫中的 stdio_server 上下文管理器
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        print("MCP Stdio 伺服器：正在與客戶端進行交握...")
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name, # 使用上面定義的伺服器名稱
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    # 定義伺服器功能 - 請參閱 MCP 文件以取得選項
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
        print("MCP Stdio 伺服器：執行迴圈已完成或客戶端已中斷連線。")

if __name__ == "__main__":
    print("正在啟動 MCP 伺服器以透過 stdio 公開 ADK 工具...")
    try:
        asyncio.run(run_mcp_stdio_server())
    except KeyboardInterrupt:
        print("\nMCP 伺服器 (stdio) 已由使用者停止。")
    except Exception as e:
        print(f"MCP 伺服器 (stdio) 遇到錯誤：{e}")
    finally:
        print("MCP 伺服器 (stdio) 進程正在結束。")
# --- 結束 MCP 伺服器 ---
```

### 步驟 3：使用 ADK 代理程式測試您的自訂 MCP 伺服器

現在，建立一個 ADK 代理程式，它將充當您剛才建立的 MCP 伺服器的客戶端。此 ADK 代理程式將使用 `MCPToolset` 連接到您的 `my_adk_mcp_server.py` 腳本。

建立一個 `agent.py` (例如，在 `./adk_agent_samples/mcp_client_agent/agent.py` 中)：

```python
# ./adk_agent_samples/mcp_client_agent/agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StdioServerParameters

# 重要：請將此替換為您的 my_adk_mcp_server.py 腳本的絕對路徑
PATH_TO_YOUR_MCP_SERVER_SCRIPT = "/path/to/your/my_adk_mcp_server.py" # <<< 替換

if PATH_TO_YOUR_MCP_SERVER_SCRIPT == "/path/to/your/my_adk_mcp_server.py":
    print("警告：未設定 PATH_TO_YOUR_MCP_SERVER_SCRIPT。請在 agent.py 中更新它。")
    # 如果路徑至關重要，可選擇性地引發錯誤

root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='web_reader_mcp_client_agent',
    instruction="使用 'load_web_page' 工具從使用者提供的 URL 擷取內容。",
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='python3', # 執行您的 MCP 伺服器腳本的指令
                    args=[PATH_TO_YOUR_MCP_SERVER_SCRIPT], # 參數是腳本的路徑
                )
            )
            # tool_filter=['load_web_page'] # 可選：確保只載入特定的工具
        )
    ],
)
```

以及在相同目錄中的 `__init__.py`：
```python
# ./adk_agent_samples/mcp_client_agent/__init__.py
from . import agent
```

**若要執行測試：**

1.  **啟動您的自訂 MCP 伺服器 (可選，用於單獨觀察)：**
    您可以在一個終端機中直接執行您的 `my_adk_mcp_server.py` 以查看其日誌：
    ```shell
    python3 /path/to/your/my_adk_mcp_server.py
    ```
    它會列印「正在啟動 MCP 伺服器...」並等待。如果 `StdioConnectionParams` 中的 `command` 已設定為執行它，則 ADK 代理程式 (透過 `adk web` 執行) 將會連接到此進程。
    *(或者，當代理程式初始化時，`MCPToolset` 將自動啟動此伺服器腳本作為子進程)。*

2.  **為客戶端代理程式執行 `adk web`：**
    導覽至 `mcp_client_agent` 的父目錄 (例如 `adk_agent_samples`) 並執行：
    ```shell
    cd ./adk_agent_samples # 或您對等的父目錄
    adk web
    ```

3.  **在 ADK Web UI 中互動：**
    *   選擇 `web_reader_mcp_client_agent`。
    *   嘗試像這樣的提示：「從 https://example.com 載入內容」

ADK 代理程式 (`web_reader_mcp_client_agent`) 將使用 `MCPToolset` 啟動並連接到您的 `my_adk_mcp_server.py`。您的 MCP 伺服器將收到 `call_tool` 請求，執行 ADK `load_web_page` 工具，並傳回結果。然後 ADK 代理程式將轉發此資訊。您應該會看到來自 ADK Web UI (及其終端機) 和可能來自您的 `my_adk_mcp_server.py` 終端機 (如果您單獨執行它) 的日誌。

此範例示範了如何將 ADK 工具封裝在 MCP 伺服器中，使其可供更廣泛的符合 MCP 規範的客戶端存取，而不僅僅是 ADK 代理程式。

請參閱[文件](https://modelcontextprotocol.io/quickstart/server#core-mcp-concepts)，以嘗試使用 Claude Desktop。

## 在您自己的代理程式中，在 `adk web` 之外使用 MCP 工具

如果您符合以下情況，本節與您相關：

* 您正在使用 ADK 開發自己的代理程式
* 並且，您**沒有**使用 `adk web`，
* 並且，您正在透過自己的 UI 公開代理程式


使用 MCP 工具需要與使用常規工具有不同的設定，因為 MCP 工具的規格是從遠端執行或在另一個進程中執行的 MCP 伺服器非同步擷取的。

以下範例是從上面的「範例 1：檔案系統 MCP 伺服器」範例修改而來。主要區別在於：

1. 您的工具和代理程式是異步建立的
2. 您需要妥善管理退出堆疊，以便在與 MCP 伺服器的連線關閉時，您的代理程式和工具能被正確地銷毀。

```python
# agent.py (根據需要修改 get_tools_async 和其他部分)
# ./adk_agent_samples/mcp_agent/agent.py
import os
import asyncio
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService # 可選
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams, StdioConnectionParams, StdioServerParameters

# 從父目錄中的 .env 檔案載入環境變數
# 將此放在靠近頂部的位置，在使用 API 金鑰等環境變數之前
load_dotenv('../.env')

# 確保 TARGET_FOLDER_PATH 是 MCP 伺服器的絕對路徑。
TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "/path/to/your/folder")

# --- 步驟 1：代理程式定義 ---
async def get_agent_async():
  """建立一個配備來自 MCP 伺服器工具的 ADK 代理程式。"""
  toolset = MCPToolset(
      # 使用 StdioConnectionParams 進行本地進程通訊
      connection_params=StdioConnectionParams(
          server_params = StdioServerParameters(
            command='npx', # 執行伺服器的指令
            args=["-y",    # 指令的參數
                "@modelcontextprotocol/server-filesystem",
                TARGET_FOLDER_PATH],
          ),
      ),
      tool_filter=['read_file', 'list_directory'] # 可選：篩選特定的工具
      # 對於遠端伺服器，您將改用 SseConnectionParams：
      # connection_params=SseConnectionParams(url="http://remote-server:port/path", headers={...})
  )

  # 在代理程式中使用
  root_agent = LlmAgent(
      model='gemini-2.0-flash', # 根據可用性調整模型名稱
      name='enterprise_assistant',
      instruction='幫助使用者存取他們的檔案系統',
      tools=[toolset], # 將 MCP 工具提供給 ADK 代理程式
  )
  return root_agent, toolset

# --- 步驟 2：主要執行邏輯 ---
async def async_main():
  session_service = InMemorySessionService()
  # 此範例可能不需要產物服務
  artifacts_service = InMemoryArtifactService()

  session = await session_service.create_session(
      state={}, app_name='mcp_filesystem_app', user_id='user_fs'
  )

  # TODO：將查詢變更為與您指定的資料夾相關。
  # 例如，「列出 'documents' 子資料夾中的檔案」或「讀取檔案 'notes.txt'」
  query = "列出 tests 資料夾中的檔案"
  print(f"使用者查詢：'{query}'")
  content = types.Content(role='user', parts=[types.Part(text=query)])

  root_agent, toolset = await get_agent_async()

  runner = Runner(
      app_name='mcp_filesystem_app',
      agent=root_agent,
      artifact_service=artifacts_service, # 可選
      session_service=session_service,
  )

  print("正在執行代理程式...")
  events_async = runner.run_async(
      session_id=session.id, user_id=session.user_id, new_message=content
  )

  async for event in events_async:
    print(f"收到事件：{event}")

  # 清理由代理程式框架自動處理
  # 但如果需要，您也可以手動關閉：
  print("正在關閉 MCP 伺服器連線...")
  await toolset.close()
  print("清理完成。")

if __name__ == '__main__':
  try:
    asyncio.run(async_main())
  except Exception as e:
    print(f"發生錯誤：{e}")
```


## 主要考量

在使用 MCP 和 ADK 時，請記住以下幾點：

* **協定與函式庫：** MCP 是一種協定規範，定義了通訊規則。ADK 是一個用於建構代理程式的 Python 函式庫/框架。MCPToolset 透過在 ADK 框架內實作 MCP 協定的客戶端來橋接這兩者。反之，在 Python 中建構 MCP 伺服器需要使用 model-context-protocol 函式庫。

* **ADK 工具與 MCP 工具：**

    * ADK 工具 (BaseTool、FunctionTool、AgentTool 等) 是專為在 ADK 的 LlmAgent 和 Runner 中直接使用而設計的 Python 物件。
    * MCP 工具是 MCP 伺服器根據協定結構描述公開的功能。MCPToolset 使這些工具看起來像 LlmAgent 的 ADK 工具。
    * Langchain/CrewAI 工具是這些函式庫中的特定實作，通常是簡單的函式或類別，缺乏 MCP 的伺服器/協定結構。ADK 為某些互通性提供了包裝器 (LangchainTool、CrewaiTool)。

* **非同步性質：** ADK 和 MCP Python 函式庫都大量基於 asyncio Python 函式庫。工具實作和伺服器處理常式通常應該是非同步函式。

* **有狀態的會話 (MCP)：** MCP 在客戶端和伺服器實例之間建立有狀態的、持久的連線。這與典型的無狀態 REST API 不同。

    * **部署：** 這種有狀態性可能會給擴展和部署帶來挑戰，特別是對於處理許多使用者的遠端伺服器。最初的 MCP 設計通常假設客戶端和伺服器位於同一位置。管理這些持久性連線需要仔細的基礎設施考量 (例如，負載平衡、會話親和性)。
    * **ADK MCPToolset：** 管理此連線生命週期。範例中顯示的 exit_stack 模式對於確保在 ADK 代理程式完成時正確終止連線 (以及可能的伺服器進程) 至關重要。

## 更多資源

* [模型上下文協定文件](https://modelcontextprotocol.io/ )
* [MCP 規範](https://modelcontextprotocol.io/specification/)
* [MCP Python SDK 與範例](https://github.com/modelcontextprotocol/)
