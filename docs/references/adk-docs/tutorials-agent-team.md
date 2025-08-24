# Build Your First Intelligent Agent Team: A Progressive Weather Bot with ADK

<!-- Optional outer container for overall padding/spacing -->
<div style="padding: 10px 0;">

  <!-- Line 1: Open in Colab -->
  <!-- This div ensures the link takes up its own line and adds space below -->
  <div style="margin-bottom: 10px;">
    <a href="https://colab.research.google.com/github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" style="display: inline-flex; align-items: center; gap: 5px; text-decoration: none; color: #4285F4;">
      <img width="32px" src="https://www.gstatic.com/pantheon/images/bigquery/welcome_page/colab-logo.svg" alt="Google Colaboratory logo">
      <span>在 Colab 中開啟</span>
    </a>
  </div>

  <!-- Line 2: Share Links -->
  <!-- This div acts as a flex container for the "Share to" text and icons -->
  <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
    <!-- Share Text -->
    <span style="font-weight: bold;">分享至：</span>

    <!-- Social Media Links -->
    <a href="https://www.linkedin.com/sharing/share-offsite/?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="分享至 LinkedIn">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg" alt="LinkedIn logo" style="vertical-align: middle;">
    </a>
    <a href="https://bsky.app/intent/compose?text=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="分享至 Bluesky">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/7/7a/Bluesky_Logo.svg" alt="Bluesky logo" style="vertical-align: middle;">
    </a>
    <a href="https://twitter.com/intent/tweet?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="分享至 X (Twitter)">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/5/5a/X_icon_2.svg" alt="X logo" style="vertical-align: middle;">
    </a>
    <a href="https://reddit.com/submit?url=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="分享至 Reddit">
      <img width="20px" src="https://redditinc.com/hubfs/Reddit%20Inc/Brand/Reddit_Logo.png" alt="Reddit logo" style="vertical-align: middle;">
    </a>
    <a href="https://www.facebook.com/sharer/sharer.php?u=https%3A//github/google/adk-docs/blob/main/examples/python/tutorial/agent_team/adk_tutorial.ipynb" target="_blank" title="分享至 Facebook">
      <img width="20px" src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook logo" style="vertical-align: middle;">
    </a>
  </div>

</div>

本教學是[代理程式開發套件 (Agent Development Kit)](https://google.github.io/adk-docs/get-started/) 的 [快速入門範例](https://google.github.io/adk-docs/get-started/quickstart/) 的延伸。現在，您已準備好深入探索並建構一個更複雜的**多代理程式系統**。

我們將著手建構一個**天氣機器人代理程式團隊**，在一個簡單的基礎上逐步增加進階功能。從一個可以查詢天氣的單一代理程式開始，我們將逐步增加以下功能：

*   利用不同的 AI 模型 (Gemini、GPT、Claude)。
*   為不同的任務 (如問候和告別) 設計專門的子代理程式。
*   實現代理程式之間的智慧委派。
*   使用持久性會話狀態為代理程式提供記憶。
*   使用回呼實作關鍵的安全護欄。

**為何選擇天氣機器人團隊？**

這個使用案例雖然看似簡單，但提供了一個實用且易於理解的畫布，讓我們可以探索建構複雜、真實世界代理程式應用程式所需的核心 ADK 概念。您將學習如何建構互動、管理狀態、確保安全，以及協調多個 AI「大腦」協同工作。

**ADK 又是什麼？**

提醒您，ADK 是一個 Python 框架，旨在簡化由大型語言模型 (LLM) 驅動的應用程式的開發。它提供了強大的建構區塊，用於建立能夠推理、規劃、利用工具、與使用者動態互動以及在團隊中有效協作的代理程式。

**在這個進階教學中，您將掌握：**

*   ✅ **工具定義與使用：** 製作 Python 函式 (`tools`)，賦予代理程式特定能力 (如擷取資料)，並指示代理程式如何有效地使用它們。
*   ✅ **多 LLM 彈性：** 透過 LiteLLM 整合，設定代理程式以利用各種領先的 LLM (Gemini、GPT-4o、Claude Sonnet)，讓您可以為每個任務選擇最佳模型。
*   ✅ **代理程式委派與協作：** 設計專門的子代理程式，並啟用使用者請求的自動路由 (`auto flow`) 到團隊中最合適的代理程式。
*   ✅ **用於記憶的會話狀態：** 利用 `Session State` 和 `ToolContext` 使代理程式能夠在對話輪次之間記住資訊，從而實現更具上下文的互動。
*   ✅ **使用回呼的安全護欄：** 實作 `before_model_callback` 和 `before_tool_callback`，以根據預先定義的規則檢查、修改或阻擋請求/工具使用，從而增強應用程式的安全性和控制力。

**最終狀態期望：**

完成本教學後，您將建構一個功能性的多代理程式天氣機器人系統。此系統不僅能提供天氣資訊，還能處理對話禮儀、記住上次查詢的城市，並在定義的安全邊界內運作，所有這些都使用 ADK 進行協調。

**先決條件：**

*   ✅ **對 Python 程式設計有扎實的理解。**
*   ✅ **熟悉大型語言模型 (LLM)、API 和代理程式的概念。**
*   ❗ **至關重要：完成 ADK 快速入門教學或具備同等的 ADK 基礎知識 (Agent、Runner、SessionService、基本工具使用)。** 本教學直接建立在這些概念之上。
*   ✅ **您打算使用的 LLM 的 API 金鑰** (例如，用於 Gemini 的 Google AI Studio、OpenAI Platform、Anthropic Console)。


---

**關於執行環境的注意事項：**

本教學是針對像 Google Colab、Colab Enterprise 或 Jupyter notebooks 這樣的互動式筆記本環境而設計的。請注意以下幾點：

*   **執行非同步程式碼：** 筆記本環境處理非同步程式碼的方式不同。您會看到使用 `await` (適用於事件迴圈已在執行的情況，這在筆記本中很常見) 或 `asyncio.run()` (通常在作為獨立的 `.py` 腳本執行或在特定的筆記本設定中需要) 的範例。程式碼區塊為這兩種情況都提供了指導。
*   **手動 Runner/Session 設定：** 這些步驟涉及明確地建立 `Runner` 和 `SessionService` 實例。之所以展示這種方法，是因為它讓您能夠對代理程式的執行生命週期、會話管理和狀態持久性進行精細的控制。

**替代方案：使用 ADK 的內建工具 (Web UI / CLI / API 伺服器)**

如果您偏好使用 ADK 的標準工具自動處理 runner 和會話管理的設定，您可以在[此處](https://github.com/google/adk-docs/tree/main/examples/python/tutorial/agent_team/adk-tutorial)找到為該目的而建構的等效程式碼。該版本旨在直接使用像 `adk web` (用於 Web UI)、`adk run` (用於 CLI 互動) 或 `adk api_server` (用於公開 API) 等指令執行。請遵循該替代資源中提供的 `README.md` 說明。

---

**準備好建立您的代理程式團隊了嗎？讓我們開始吧！**

> **注意：** 本教學適用於 adk 1.0.0 及以上版本

```python
# @title 步驟 0：設定與安裝
# 安裝 ADK 和 LiteLLM 以支援多模型

!pip install google-adk -q
!pip install litellm -q

print("安裝完成。")
```


```python
# @title 匯入必要的函式庫
import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # 用於多模型支援
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # 用於建立訊息內容/部分

import warnings
# 忽略所有警告
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

print("函式庫已匯入。")
```


```python
# @title 設定 API 金鑰 (請替換為您的實際金鑰！)

# --- 重要：請將預留位置替換為您的真實 API 金鑰 ---

# Gemini API 金鑰 (從 Google AI Studio 取得：https://aistudio.google.com/app/apikey)
os.environ["GOOGLE_API_KEY"] = "您的_GOOGLE_API_金鑰" # <--- 替換

# [可選]
# OpenAI API 金鑰 (從 OpenAI Platform 取得：https://platform.openai.com/api-keys)
os.environ['OPENAI_API_KEY'] = '您的_OPENAI_API_金鑰' # <--- 替換

# [可選]
# Anthropic API 金鑰 (從 Anthropic Console 取得：https://console.anthropic.com/settings/keys)
os.environ['ANTHROPIC_API_KEY'] = '您的_ANTHROPIC_API_金鑰' # <--- 替換

# --- 驗證金鑰 (可選檢查) ---
print("API 金鑰已設定：")
print(f"Google API 金鑰已設定：{'是' if os.environ.get('GOOGLE_API_KEY') and os.environ['GOOGLE_API_KEY'] != '您的_GOOGLE_API_金鑰' else '否 (請替換預留位置！)'}")
print(f"OpenAI API 金鑰已設定：{'是' if os.environ.get('OPENAI_API_KEY') and os.environ['OPENAI_API_KEY'] != '您的_OPENAI_API_金鑰' else '否 (請替換預留位置！)'}")
print(f"Anthropic API 金鑰已設定：{'是' if os.environ.get('ANTHROPIC_API_KEY') and os.environ['ANTHROPIC_API_KEY'] != '您的_ANTHROPIC_API_金鑰' else '否 (請替換預留位置！)'}")

# 設定 ADK 直接使用 API 金鑰 (此多模型設定不使用 Vertex AI)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


# @markdown **安全注意事項：** 最佳實踐是安全地管理 API 金鑰 (例如，使用 Colab Secrets 或環境變數)，而不是直接在筆記本中硬式編碼。請替換上面的預留位置字串。
```


```python
# --- 定義模型常數以便於使用 ---

# 更多支援的模型可在此處參考：https://ai.google.dev/gemini-api/docs/models#model-variations
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

# 更多支援的模型可在此處參考：https://docs.litellm.ai/docs/providers/openai#openai-chat-completion-models
MODEL_GPT_4O = "openai/gpt-4.1" # 您也可以嘗試：gpt-4.1-mini, gpt-4o 等。

# 更多支援的模型可在此處參考：https://docs.litellm.ai/docs/providers/anthropic
MODEL_CLAUDE_SONNET = "anthropic/claude-sonnet-4-20250514" # 您也可以嘗試：claude-opus-4-20250514 , claude-3-7-sonnet-20250219 等。

print("\n環境已設定。")
```

---

## 步驟 1：您的第一個代理程式 - 基本天氣查詢

讓我們從建構天氣機器人的基本元件開始：一個能夠執行特定任務——查詢天氣資訊的單一代理程式。這涉及建立兩個核心部分：

1. **一個工具：** 一個 Python 函式，賦予代理程式擷取天氣資料的*能力*。
2. **一個代理程式：** AI「大腦」，理解使用者的請求，知道它有一個天氣工具，並決定何時以及如何使用它。

---

**1\. 定義工具 (`get_weather`)**

在 ADK 中，**工具**是賦予代理程式超越純文字生成之具體能力的建構區塊。它們通常是執行特定動作的常規 Python 函式，例如呼叫 API、查詢資料庫或執行計算。

我們的第一個工具將提供一個*模擬*的天氣報告。這讓我們可以專注於代理程式的結構，而無需立即需要外部 API 金鑰。稍後，您可以輕鬆地將此模擬函式換成呼叫真實天氣服務的函式。

**核心概念：文件字串至關重要！** 代理程式的 LLM 在很大程度上依賴函式的**文件字串**來理解：

* 工具*做什麼*。
* *何時*使用它。
* 它需要*什麼參數* (`city: str`)。
* 它傳回*什麼資訊*。

**最佳實踐：** 為您的工具撰寫清晰、具描述性且準確的文件字串。這對於 LLM 正確使用該工具至關重要。


```python
# @title 定義 get_weather 工具
def get_weather(city: str) -> dict:
    """擷取指定城市的目前天氣報告。

    Args:
        city (str): 城市名稱 (例如，「New York」、「London」、「Tokyo」)。

    Returns:
        dict: 一個包含天氣資訊的字典。
              包含一個 'status' 鍵 ('success' 或 'error')。
              如果 'success'，則包含一個 'report' 鍵，其中包含天氣詳細資訊。
              如果 'error'，則包含一個 'error_message' 鍵。
    """
    print(f"--- 工具：為城市呼叫 get_weather：{city} ---") # 記錄工具執行
    city_normalized = city.lower().replace(" ", "") # 基本正規化

    # 模擬天氣資料
    mock_weather_db = {
        "newyork": {"status": "success", "report": "紐約天氣晴朗，溫度為 25°C。"},
        "london": {"status": "success", "report": "倫敦多雲，溫度為 15°C。"},
        "tokyo": {"status": "success", "report": "東京有小雨，溫度為 18°C。"},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"抱歉，我沒有 '{city}' 的天氣資訊。"}

# 範例工具用法 (可選測試)
print(get_weather("New York"))
print(get_weather("Paris"))
```

---

**2\. 定義代理程式 (`weather_agent`)**

現在，讓我們建立**代理程式**本身。ADK 中的 `Agent` 負責協調使用者、LLM 和可用工具之間的互動。

我們為其設定了幾個關鍵參數：

* `name`：此代理程式的唯一識別碼 (例如，「weather_agent_v1」)。
* `model`：指定要使用的 LLM (例如，`MODEL_GEMINI_2_0_FLASH`)。我們將從一個特定的 Gemini 模型開始。
* `description`：代理程式整體目的的簡潔摘要。當其他代理程式需要決定是否將任務委派給*此*代理程式時，這會變得至關重要。
* `instruction`：關於如何行為、其角色、目標以及特別是*如何以及何時*利用其指派的 `tools` 的詳細指導。
* `tools`：一個包含代理程式允許使用的實際 Python 工具函式的列表 (例如，`[get_weather]`)。

**最佳實踐：** 提供清晰且具體的 `instruction` 提示。指令越詳細，LLM 就越能理解其角色以及如何有效地使用其工具。如果需要，請明確說明錯誤處理。

**最佳實踐：** 選擇具描述性的 `name` 和 `description` 值。這些由 ADK 內部使用，對於像自動委派 (稍後介紹) 這樣的功能至關重要。


```python
# @title 定義天氣代理程式
# 使用前面定義的模型常數之一
AGENT_MODEL = MODEL_GEMINI_2_0_FLASH # 從 Gemini 開始

weather_agent = Agent(
    name="weather_agent_v1",
    model=AGENT_MODEL, # 可以是 Gemini 的字串或 LiteLlm 物件
    description="提供特定城市的天氣資訊。",
    instruction="您是一個樂於助人的天氣助理。"
                "當使用者詢問特定城市的天氣時，"
                "請使用 'get_weather' 工具尋找資訊。"
                "如果工具傳回錯誤，請禮貌地通知使用者。"
                "如果工具成功，請清楚地呈現天氣報告。",
    tools=[get_weather], # 直接傳遞函式
)

print(f"代理程式 '{weather_agent.name}' 已使用模型 '{AGENT_MODEL}' 建立。")
```

---

**3\. 設定 Runner 和 Session Service**

若要管理對話並執行代理程式，我們還需要兩個元件：

* `SessionService`：負責管理不同使用者和會話的對話歷史和狀態。`InMemorySessionService` 是一個簡單的實作，將所有內容儲存在記憶體中，適用於測試和簡單的應用程式。它會追蹤交換的訊息。我們將在步驟 4 中更深入地探討狀態持久性。
* `Runner`：協調互動流程的引擎。它接收使用者輸入，將其路由到適當的代理程式，根據代理程式的邏輯管理對 LLM 和工具的呼叫，透過 `SessionService` 處理會話更新，並產生代表互動進度的事件。


```python
# @title 設定 Session Service 和 Runner

# --- 會話管理 ---
# 核心概念：SessionService 儲存對話歷史和狀態。
# InMemorySessionService 是本教學中用於簡單、非持久性儲存的服務。
session_service = InMemorySessionService()

# 定義用於識別互動上下文的常數
APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001" # 為了簡單起見，使用固定 ID

# 建立將進行對話的特定會話
session = await session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)
print(f"會話已建立：應用程式='{APP_NAME}'，使用者='{USER_ID}'，會話='{SESSION_ID}'")

# --- Runner ---
# 核心概念：Runner 協調代理程式執行迴圈。
runner = Runner(
    agent=weather_agent, # 我們要執行的代理程式
    app_name=APP_NAME,   # 將執行與我們的應用程式關聯
    session_service=session_service # 使用我們的會話管理器
)
print(f"已為代理程式 '{runner.agent.name}' 建立 Runner。")
```

---

**4\. 與代理程式互動**

我們需要一種方法來向我們的代理程式傳送訊息並接收其回應。由於 LLM 呼叫和工具執行可能需要時間，ADK 的 `Runner` 是以非同步方式運作的。

我們將定義一個 `async` 輔助函式 (`call_agent_async`)，它會：

1. 接收一個使用者查詢字串。
2. 將其打包成 ADK `Content` 格式。
3. 呼叫 `runner.run_async`，提供使用者/會話上下文和新訊息。
4. 迭代由 runner 產生的**事件**。事件代表代理程式執行中的步驟 (例如，請求工具呼叫、收到工具結果、中間的 LLM 思考、最終回應)。
5. 使用 `event.is_final_response()` 識別並列印**最終回應**事件。

**為何使用 `async`？** 與 LLM 和潛在工具 (如外部 API) 的互動是 I/O 密集型操作。使用 `asyncio` 可以讓程式有效地處理這些操作，而不會阻塞執行。


```python
# @title 定義代理程式互動函式

from google.genai import types # 用於建立訊息內容/部分

async def call_agent_async(query: str, runner, user_id, session_id):
  """向代理程式傳送查詢並列印最終回應。"""
  print(f"\n>>> 使用者查詢：{query}")

  # 以 ADK 格式準備使用者訊息
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "代理程式未產生最終回應。" # 預設值

  # 核心概念：run_async 執行代理程式邏輯並產生事件。
  # 我們迭代事件以尋找最終答案。
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      # 您可以取消註解以下這行以查看執行期間的*所有*事件
      # print(f"  [事件] 作者：{event.author}，類型：{type(event).__name__}，最終：{event.is_final_response()}，內容：{event.content}")

      # 核心概念：is_final_response() 標記該輪次的結束訊息。
      if event.is_final_response():
          if event.content and event.content.parts:
             # 假設文字回應在第一部分
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # 處理潛在的錯誤/升級
             final_response_text = f"代理程式已升級：{event.error_message or '無特定訊息。'}"
          # 如果需要，在此處新增更多檢查 (例如，特定的錯誤代碼)
          break # 找到最終回應後停止處理事件

  print(f"<<< 代理程式回應：{final_response_text}")
```

---

**5\. 執行對話**

最後，讓我們透過向代理程式傳送幾個查詢來測試我們的設定。我們將 `async` 呼叫包裝在一個主 `async` 函式中，並使用 `await` 執行它。

觀察輸出：

* 查看使用者查詢。
* 注意當代理程式使用工具時的 `--- 工具：呼叫 get_weather... ---` 日誌。
* 觀察代理程式的最終回應，包括它如何處理天氣資料不可用 (對於巴黎) 的情況。


```python
# @title 執行初始對話

# 我們需要一個 async 函式來等待我們的互動輔助函式
async def run_conversation():
    await call_agent_async("倫敦的天氣如何？",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

    await call_agent_async("巴黎呢？",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID) # 預期工具的錯誤訊息

    await call_agent_async("告訴我紐約的天氣",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

# 在非同步上下文中使用 await 執行對話 (如 Colab/Jupyter)
await run_conversation()

# --- 或 ---

# 如果作為標準 Python 腳本 (.py 檔案) 執行，請取消註解以下幾行：
# import asyncio
# if __name__ == "__main__":
#     try:
#         asyncio.run(run_conversation())
#     except Exception as e:
#         print(f"發生錯誤：{e}")
```

---

恭喜！您已成功建構並與您的第一個 ADK 代理程式互動。它能理解使用者的請求，使用工具尋找資訊，並根據工具的結果適當地回應。

在下一步中，我們將探討如何輕鬆地切換為此代理程式提供動力的底層語言模型。

## 步驟 2：使用 LiteLLM 實現多模型 [可選]

在步驟 1 中，我們建構了一個由特定 Gemini 模型驅動的功能性天氣代理程式。雖然對於其特定任務有效，但真實世界的應用程式通常受益於使用*不同*大型語言模型 (LLM) 的彈性。為什麼？

*   **效能：** 有些模型在特定任務上表現出色 (例如，編碼、推理、創意寫作)。
*   **成本：** 不同模型的價格點不同。
*   **能力：** 模型提供多樣化的功能、上下文視窗大小和微調選項。
*   **可用性/備援：** 擁有替代方案可確保您的應用程式即使在一個供應商遇到問題時仍能正常運作。

ADK 透過與 [**LiteLLM**](https://github.com/BerriAI/litellm) 函式庫的整合，使模型之間的切換變得無縫。LiteLLM 作為一個一致的介面，可與 100 多種不同的 LLM 連接。

**在此步驟中，我們將：**

1.  學習如何使用 `LiteLlm` 包裝器，設定 ADK `Agent` 以使用來自 OpenAI (GPT) 和 Anthropic (Claude) 等供應商的模型。
2.  定義、設定 (使用它們自己的會話和執行器) 並立即測試我們的天氣代理程式的實例，每個實例都由不同的 LLM 支援。
3.  與這些不同的代理程式互動，以觀察它們在使用相同底層工具時回應的潛在差異。

---

**1\. 匯入 `LiteLlm`**

我們在初始設定 (步驟 0) 中匯入了這個，但它是多模型支援的關鍵元件：


```python
# @title 1. 匯入 LiteLlm
from google.adk.models.lite_llm import LiteLlm
```

**2\. 定義和測試多模型代理程式**

我們不再只傳遞一個模型名稱字串 (預設為 Google 的 Gemini 模型)，而是將所需的模型識別碼字串包裝在 `LiteLlm` 類別中。

*   **核心概念：`LiteLlm` 包裝器：** `LiteLlm(model="供應商/模型名稱")` 語法告訴 ADK 透過 LiteLLM 函式庫將此代理程式的請求路由到指定的模型供應商。

請確保您已在步驟 0 中設定了 OpenAI 和 Anthropic 所需的 API 金鑰。我們將使用 `call_agent_async` 函式 (先前定義，現在接受 `runner`、`user_id` 和 `session_id`) 在每個代理程式設定後立即與其互動。

以下每個區塊將：

*   使用特定的 LiteLLM 模型 (`MODEL_GPT_4O` 或 `MODEL_CLAUDE_SONNET`) 定義代理程式。
*   為該代理程式的測試執行建立一個*新的、獨立的* `InMemorySessionService` 和會話。這可以在此示範中保持對話歷史的隔離。
*   建立一個為特定代理程式及其會話服務設定的 `Runner`。
*   立即呼叫 `call_agent_async` 以傳送查詢並測試代理程式。

**最佳實踐：** 使用模型名稱的常數 (如步驟 0 中定義的 `MODEL_GPT_4O`、`MODEL_CLAUDE_SONNET`) 以避免打字錯誤並使程式碼更易於管理。

**錯誤處理：** 我們將代理程式定義包裝在 `try...except` 區塊中。這可以防止在特定供應商的 API 金鑰遺失或無效時整個程式碼儲存格失敗，從而讓教學能夠繼續使用*已設定*的模型。

首先，讓我們使用 OpenAI 的 GPT-4o 建立並測試代理程式。


```python
# @title 定義和測試 GPT 代理程式

# 確保在您的環境中定義了步驟 1 中的 'get_weather' 函式。
# 確保先前定義了 'call_agent_async'。

# --- 使用 GPT-4o 的代理程式 ---
weather_agent_gpt = None # 初始化為 None
runner_gpt = None      # 將 runner 初始化為 None

try:
    weather_agent_gpt = Agent(
        name="weather_agent_gpt",
        # 關鍵變更：包裝 LiteLLM 模型識別碼
        model=LiteLlm(model=MODEL_GPT_4O),
        description="提供天氣資訊 (使用 GPT-4o)。",
        instruction="您是一個由 GPT-4o 驅動的樂於助人的天氣助理。"
                    "對城市天氣請求使用 'get_weather' 工具。"
                    "根據工具輸出的狀態，清楚地呈現成功報告或禮貌的錯誤訊息。",
        tools=[get_weather], # 重複使用相同的工具
    )
    print(f"代理程式 '{weather_agent_gpt.name}' 已使用模型 '{MODEL_GPT_4O}' 建立。")

    # InMemorySessionService 是本教學中用於簡單、非持久性儲存的服務。
    session_service_gpt = InMemorySessionService() # 建立一個專用的服務

    # 定義用於識別互動上下文的常數
    APP_NAME_GPT = "weather_tutorial_app_gpt" # 此測試的唯一應用程式名稱
    USER_ID_GPT = "user_1_gpt"
    SESSION_ID_GPT = "session_001_gpt" # 為了簡單起見，使用固定 ID

    # 建立將進行對話的特定會話
    session_gpt = await session_service_gpt.create_session(
        app_name=APP_NAME_GPT,
        user_id=USER_ID_GPT,
        session_id=SESSION_ID_GPT
    )
    print(f"會話已建立：應用程式='{APP_NAME_GPT}'，使用者='{USER_ID_GPT}'，會話='{SESSION_ID_GPT}'")

    # 為此代理程式及其會話服務建立一個特定的 runner
    runner_gpt = Runner(
        agent=weather_agent_gpt,
        app_name=APP_NAME_GPT,       # 使用特定的應用程式名稱
        session_service=session_service_gpt # 使用特定的會話服務
        )
    print(f"已為代理程式 '{runner_gpt.agent.name}' 建立 Runner。")

    # --- 測試 GPT 代理程式 ---
    print("\n--- 測試 GPT 代理程式 ---")
    # 確保 call_agent_async 使用正確的 runner、user_id、session_id
    await call_agent_async(query = "東京的天氣如何？",
                           runner=runner_gpt,
                           user_id=USER_ID_GPT,
                           session_id=SESSION_ID_GPT)
    # --- 或 ---

    # 如果作為標準 Python 腳本 (.py 檔案) 執行，請取消註解以下幾行：
    # import asyncio
    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "東京的天氣如何？",
    #                      runner=runner_gpt,
    #                       user_id=USER_ID_GPT,
    #                       session_id=SESSION_ID_GPT)
    #     except Exception as e:
    #         print(f"發生錯誤：{e}")

except Exception as e:
    print(f"❌ 無法建立或執行 GPT 代理程式 '{MODEL_GPT_4O}'。請檢查 API 金鑰和模型名稱。錯誤：{e}")

```

接下來，我們將為 Anthropic 的 Claude Sonnet 做同樣的事情。


```python
# @title 定義和測試 Claude 代理程式

# 確保在您的環境中定義了步驟 1 中的 'get_weather' 函式。
# 確保先前定義了 'call_agent_async'。

# --- 使用 Claude Sonnet 的代理程式 ---
weather_agent_claude = None # 初始化為 None
runner_claude = None      # 將 runner 初始化為 None

try:
    weather_agent_claude = Agent(
        name="weather_agent_claude",
        # 關鍵變更：包裝 LiteLLM 模型識別碼
        model=LiteLlm(model=MODEL_CLAUDE_SONNET),
        description="提供天氣資訊 (使用 Claude Sonnet)。",
        instruction="您是一個由 Claude Sonnet 驅動的樂於助人的天氣助理。"
                    "對城市天氣請求使用 'get_weather' 工具。"
                    "分析工具的字典輸出 ('status', 'report'/'error_message')。"
                    "清楚地呈現成功報告或禮貌的錯誤訊息。",
        tools=[get_weather], # 重複使用相同的工具
    )
    print(f"代理程式 '{weather_agent_claude.name}' 已使用模型 '{MODEL_CLAUDE_SONNET}' 建立。")

    # InMemorySessionService 是本教學中用於簡單、非持久性儲存的服務。
    session_service_claude = InMemorySessionService() # 建立一個專用的服務

    # 定義用於識別互動上下文的常數
    APP_NAME_CLAUDE = "weather_tutorial_app_claude" # 唯一的應用程式名稱
    USER_ID_CLAUDE = "user_1_claude"
    SESSION_ID_CLAUDE = "session_001_claude" # 為了簡單起見，使用固定 ID

    # 建立將進行對話的特定會話
    session_claude = await session_service_claude.create_session(
        app_name=APP_NAME_CLAUDE,
        user_id=USER_ID_CLAUDE,
        session_id=SESSION_ID_CLAUDE
    )
    print(f"會話已建立：應用程式='{APP_NAME_CLAUDE}'，使用者='{USER_ID_CLAUDE}'，會話='{SESSION_ID_CLAUDE}'")

    # 為此代理程式及其會話服務建立一個特定的 runner
    runner_claude = Runner(
        agent=weather_agent_claude,
        app_name=APP_NAME_CLAUDE,       # 使用特定的應用程式名稱
        session_service=session_service_claude # 使用特定的會話服務
        )
    print(f"已為代理程式 '{runner_claude.agent.name}' 建立 Runner。")

    # --- 測試 Claude 代理程式 ---
    print("\n--- 測試 Claude 代理程式 ---")
    # 確保 call_agent_async 使用正確的 runner、user_id、session_id
    await call_agent_async(query = "請告訴我倫敦的天氣。",
                           runner=runner_claude,
                           user_id=USER_ID_CLAUDE,
                           session_id=SESSION_ID_CLAUDE)

    # --- 或 ---

    # 如果作為標準 Python 腳本 (.py 檔案) 執行，請取消註解以下幾行：
    # import asyncio
    # if __name__ == "__main__":
    #     try:
    #         asyncio.run(call_agent_async(query = "請告訴我倫敦的天氣。",
    #                      runner=runner_claude,
    #                       user_id=USER_ID_CLAUDE,
    #                       session_id=SESSION_ID_CLAUDE)
    #     except Exception as e:
    #         print(f"發生錯誤：{e}")


except Exception as e:
    print(f"❌ 無法建立或執行 Claude 代理程式 '{MODEL_CLAUDE_SONNET}'。請檢查 API 金鑰和模型名稱。錯誤：{e}")
```

仔細觀察這兩個程式碼區塊的輸出。您應該會看到：

1.  每個代理程式 (`weather_agent_gpt`、`weather_agent_claude`) 都成功建立 (如果 API 金鑰有效)。
2.  為每個代理程式設定了專用的會話和執行器。
3.  每個代理程式在處理查詢時都能正確識別出需要使用 `get_weather` 工具 (您會看到 `--- 工具：呼叫 get_weather... ---` 的日誌)。
4.  *底層的工具邏輯*保持不變，總是傳回我們的模擬資料。
5.  然而，每個代理程式產生的**最終文字回應**在措辭、語氣或格式上可能會略有不同。這是因為指令提示是由不同的 LLM (GPT-4o vs. Claude Sonnet) 解釋和執行的。

此步驟展示了 ADK + LiteLLM 提供的強大功能和彈性。您可以輕鬆地實驗和部署使用各種 LLM 的代理程式，同時保持您的核心應用程式邏輯 (工具、基本的代理程式結構) 的一致性。

在下一步中，我們將超越單一代理程式，建立一個小型團隊，讓代理程式可以互相委派任務！

---

## 步驟 3：建立代理程式團隊 - 問候與告別的委派

在步驟 1 和 2 中，我們建立並實驗了一個專注於天氣查詢的單一代理程式。雖然對於其特定任務有效，但真實世界的應用程式通常涉及處理更廣泛的使用者互動。我們可以繼續為我們的單一天氣代理程式新增更多工具和複雜的指令，但這很快就會變得難以管理且效率低下。

一個更穩健的方法是建立一個**代理程式團隊**。這涉及：

1. 建立多個**專門的代理程式**，每個代理程式都為特定功能而設計 (例如，一個用於天氣，一個用於問候，一個用於計算)。
2. 指定一個**根代理程式** (或協調器) 來接收初始的使用者請求。
3. 讓根代理程式能夠根據使用者的意圖將請求**委派**給最合適的專門子代理程式。

**為何要建立代理程式團隊？**

* **模組化：** 更容易開發、測試和維護個別代理程式。
* **專業化：** 每個代理程式都可以針對其特定任務進行微調 (指令、模型選擇)。
* **可擴展性：** 透過新增新代理程式來新增新功能更簡單。
* **效率：** 允許為更簡單的任務 (如問候) 使用可能更簡單/更便宜的模型。

**在此步驟中，我們將：**

1. 為處理問候 (`say_hello`) 和告別 (`say_goodbye`) 定義簡單的工具。
2. 建立兩個新的專門子代理程式：`greeting_agent` 和 `farewell_agent`。
3. 更新我們的主要天氣代理程式 (`weather_agent_v2`) 以充當**根代理程式**。
4. 使用其子代理程式設定根代理程式，以啟用**自動委派**。
5. 透過向根代理程式傳送不同類型的請求來測試委派流程。

---

**1\. 為子代理程式定義工具**

首先，讓我們建立將作為我們專業代理程式工具的簡單 Python 函式。請記住，清晰的文件字串對於將使用它們的代理程式至關重要。


```python
# @title 為問候和告別代理程式定義工具
from typing import Optional # 確保匯入 Optional

# 確保步驟 1 中的 'get_weather' 可用，如果獨立執行此步驟。
# def get_weather(city: str) -> dict: ... (來自步驟 1)

def say_hello(name: Optional[str] = None) -> str:
    """提供一個簡單的問候。如果提供了姓名，將會使用它。

    Args:
        name (str, optional): 要問候的人的姓名。如果未提供，則預設為通用問候語。

    Returns:
        str: 一個友好的問候訊息。
    """
    if name:
        greeting = f"你好，{name}！"
        print(f"--- 工具：使用姓名呼叫 say_hello：{name} ---")
    else:
        greeting = "你好！" # 如果姓名為 None 或未明確傳遞，則為預設問候語
        print(f"--- 工具：在沒有特定姓名的情況下呼叫 say_hello (name_arg_value: {name}) ---")
    return greeting

def say_goodbye() -> str:
    """提供一個簡單的告別訊息以結束對話。"""
    print(f"--- 工具：呼叫 say_goodbye ---")
    return "再見！祝您有美好的一天。"

print("問候和告別工具已定義。")

# 可選的自我測試
print(say_hello("Alice"))
print(say_hello()) # 使用無參數測試 (應使用預設的「你好！」)
print(say_hello(name=None)) # 使用姓名明確為 None 測試 (應使用預設的「你好！」)
```

---

**2\. 定義子代理程式 (問候與告別)**

現在，為我們的專家建立 `Agent` 實例。請注意它們高度專注的 `instruction`，以及至關重要的，它們清晰的 `description`。`description` 是*根代理程式*用來決定*何時*委派給這些子代理程式的主要資訊。

**最佳實踐：** 子代理程式的 `description` 欄位應準確、簡潔地總結其特定能力。這對於有效的自動委派至關重要。

**最佳實踐：** 子代理程式的 `instruction` 欄位應針對其有限的範圍進行調整，告訴它們確切該做什麼以及*不該*做什麼 (例如，「您*唯一*的任務是...」)。


```python
# @title 定義問候和告別子代理程式

# 如果您想使用 Gemini 以外的模型，請確保已匯入 LiteLlm 並設定了 API 金鑰 (來自步驟 0/2)
# from google.adk.models.lite_llm import LiteLlm
# 應定義 MODEL_GPT_4O、MODEL_CLAUDE_SONNET 等。
# 否則，繼續使用：model = MODEL_GEMINI_2_0_FLASH

# --- 問候代理程式 ---
greeting_agent = None
try:
    greeting_agent = Agent(
        # 為一個簡單的任務使用一個可能不同/更便宜的模型
        model = MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # 如果您想實驗其他模型
        name="greeting_agent",
        instruction="您是問候代理程式。您唯一的任務是使用 'say_hello' 工具向使用者提供友好的問候。"
                    "如果使用者提供了他們的姓名，請確保將其傳遞給工具。"
                    "不要參與任何其他對話或任務。",
        description="使用 'say_hello' 工具處理簡單的問候和你好。", # 對於委派至關重要
        tools=[say_hello],
    )
    print(f"✅ 代理程式 '{greeting_agent.name}' 已使用模型 '{greeting_agent.model}' 建立。")
except Exception as e:
    print(f"❌ 無法建立問候代理程式。請檢查 API 金鑰 ({greeting_agent.model})。錯誤：{e}")

# --- 告別代理程式 ---
farewell_agent = None
try:
    farewell_agent = Agent(
        # 可以使用相同或不同的模型
        model = MODEL_GEMINI_2_0_FLASH,
        # model=LiteLlm(model=MODEL_GPT_4O), # 如果您想實驗其他模型
        name="farewell_agent",
        instruction="您是告別代理程式。您唯一的任務是使用 'say_goodbye' 工具提供一個禮貌的告別訊息。"
                    "當使用者表示他們要離開或結束對話時 (例如，使用像 'bye'、'goodbye'、'thanks bye'、'see you' 這樣的詞)，請使用此工具。"
                    "不要執行任何其他操作。",
        description="使用 'say_goodbye' 工具處理簡單的告別和再見。", # 對於委派至關重要
        tools=[say_goodbye],
    )
    print(f"✅ 代理程式 '{farewell_agent.name}' 已使用模型 '{farewell_agent.model}' 建立。")
except Exception as e:
    print(f"❌ 無法建立告別代理程式。請檢查 API 金鑰 ({farewell_agent.model})。錯誤：{e}")
```

---

**3\. 定義根代理程式 (天氣代理程式 v2) 及其子代理程式**

現在，我們升級我們的 `weather_agent`。主要的變更是：

* 新增 `sub_agents` 參數：我們傳遞一個包含我們剛才建立的 `greeting_agent` 和 `farewell_agent` 實例的列表。
* 更新 `instruction`：我們明確地告訴根代理程式*關於*其子代理程式以及*何時*應將任務委派給它們。

**核心概念：自動委派 (Auto Flow)** 透過提供 `sub_agents` 列表，ADK 啟用自動委派。當根代理程式收到使用者查詢時，其 LLM 不僅會考慮其自身的指令和工具，還會考慮每個子代理程式的 `description`。如果 LLM 確定查詢更符合子代理程式描述的能力 (例如，「處理簡單的問候」)，它將自動產生一個特殊的內部動作，以將該輪次的*控制權轉移*給該子代理程式。然後，子代理程式使用其自己的模型、指令和工具來處理查詢。

**最佳實踐：** 確保根代理程式的指令清楚地指導其委派決策。按名稱提及子代理程式，並描述應發生委派的條件。


```python
# @title 定義根代理程式及其子代理程式

# 在定義根代理程式之前，請確保已成功建立子代理程式。
# 同時確保已定義原始的 'get_weather' 工具。
root_agent = None
runner_root = None # 初始化 runner

if greeting_agent and farewell_agent and 'get_weather' in globals():
    # 讓我們為根代理程式選擇一個有能力的 Gemini 模型來處理協調
    root_agent_model = MODEL_GEMINI_2_0_FLASH

    weather_agent_team = Agent(
        name="weather_agent_v2", # 給它一個新的版本名稱
        model=root_agent_model,
        description="主協調代理程式。處理天氣請求並將問候/告別委派給專家。",
        instruction="您是主要的天氣代理程式，負責協調一個團隊。您的主要職責是提供天氣資訊。"
                    "僅對特定的天氣請求 (例如，「倫敦的天氣」) 使用 'get_weather' 工具。"
                    "您有專門的子代理程式："
                    "1. 'greeting_agent'：處理像 'Hi'、'Hello' 這樣的簡單問候。將這些委派給它。"
                    "2. 'farewell_agent'：處理像 'Bye'、'See you' 這樣的簡單告別。將這些委派給它。"
                    "分析使用者的查詢。如果是問候，委派給 'greeting_agent'。如果是告別，委派給 'farewell_agent'。"
                    "如果是天氣請求，請自己使用 'get_weather' 處理。"
                    "對於其他任何事情，請適當地回應或說明您無法處理。",
        tools=[get_weather], # 根代理程式仍需要天氣工具來執行其核心任務
        # 關鍵變更：在此處連結子代理程式！
        sub_agents=[greeting_agent, farewell_agent]
    )
    print(f"✅ 根代理程式 '{weather_agent_team.name}' 已使用模型 '{root_agent_model}' 建立，並帶有子代理程式：{[sa.name for sa in weather_agent_team.sub_agents]}")

else:
    print("❌ 無法建立根代理程式，因為一個或多個子代理程式初始化失敗或 'get_weather' 工具遺失。")
    if not greeting_agent: print(" - 問候代理程式遺失。")
    if not farewell_agent: print(" - 告別代理程式遺失。")
    if 'get_weather' not in globals(): print(" - get_weather 函式遺失。")


```

---

**4\. 與代理程式團隊互動**

現在我們已經定義了我們的根代理程式 (`weather_agent_team` - *注意：確保此變數名稱與前一個程式碼區塊中定義的名稱相符，可能是 `# @title Define the Root Agent with Sub-Agents`，它可能已將其命名為 `root_agent`*) 及其專門的子代理程式，讓我們來測試委派機制。

以下程式碼區塊將：

1.  定義一個 `async` 函式 `run_team_conversation`。
2.  在此函式內部，為此測試執行建立一個*新的、專用的* `InMemorySessionService` 和一個特定的會話 (`session_001_agent_team`)。這可以隔離對話歷史以測試團隊動態。
3.  建立一個設定為使用我們的 `weather_agent_team` (根代理程式) 和專用會話服務的 `Runner` (`runner_agent_team`)。
4.  使用我們更新的 `call_agent_async` 函式向 `runner_agent_team` 傳送不同類型的查詢 (問候、天氣請求、告別)。我們明確地為此特定測試傳遞 runner、使用者 ID 和會話 ID。
5.  立即執行 `run_team_conversation` 函式。

我們預期會有以下流程：

1.  「你好！」查詢會傳送到 `runner_agent_team`。
2.  根代理程式 (`weather_agent_team`) 接收到它，並根據其指令和 `greeting_agent` 的描述，委派任務。
3.  `greeting_agent` 處理查詢，呼叫其 `say_hello` 工具，並產生回應。
4.  「紐約的天氣如何？」查詢*不會*被委派，而是由根代理程式直接使用其 `get_weather` 工具處理。
5.  「謝謝，再見！」查詢會被委派給 `farewell_agent`，後者會使用其 `say_goodbye` 工具。




```python
# @title 與代理程式團隊互動
import asyncio # 確保匯入 asyncio

# 確保已定義根代理程式 (例如，來自前一個儲存格的 'weather_agent_team' 或 'root_agent')。
# 確保已定義 call_agent_async 函式。

# 在定義對話函式之前，檢查根代理程式變數是否存在
root_agent_var_name = 'root_agent' # 步驟 3 指南中的預設名稱
if 'weather_agent_team' in globals(): # 檢查使用者是否改用此名稱
    root_agent_var_name = 'weather_agent_team'
elif 'root_agent' not in globals():
    print("⚠️ 未找到根代理程式 ('root_agent' 或 'weather_agent_team')。無法定義 run_team_conversation。")
    # 如果程式碼區塊無論如何都會執行，請指派一個虛擬值以防止 NameError
    root_agent = None # 或設定一個旗標以防止執行

# 僅當根代理程式存在時才定義並執行
if root_agent_var_name in globals() and globals()[root_agent_var_name]:
    # 為對話邏輯定義主 async 函式。
    # 此函式內部的 'await' 關鍵字對於非同步操作是必要的。
    async def run_team_conversation():
        print("\n--- 測試代理程式團隊委派 ---")
        session_service = InMemorySessionService()
        APP_NAME = "weather_tutorial_agent_team"
        USER_ID = "user_1_agent_team"
        SESSION_ID = "session_001_agent_team"
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        print(f"會話已建立：應用程式='{APP_NAME}'，使用者='{USER_ID}'，會話='{SESSION_ID}'")

        actual_root_agent = globals()[root_agent_var_name]
        runner_agent_team = Runner( # 或使用 InMemoryRunner
            agent=actual_root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"已為代理程式 '{actual_root_agent.name}' 建立 Runner。")

        # --- 使用 await 的互動 (在 async def 中是正確的) ---
        await call_agent_async(query = "你好！",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query = "紐約的天氣如何？",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)
        await call_agent_async(query = "謝謝，再見！",
                               runner=runner_agent_team,
                               user_id=USER_ID,
                               session_id=SESSION_ID)

    # --- 執行 `run_team_conversation` async 函式 ---
    # 根據您的環境選擇以下方法之一。
    # 注意：這可能需要所用模型的 API 金鑰！

    # 方法 1：直接 await (筆記本/非同步 REPL 的預設方法)
    # 如果您的環境支援頂層 await (如 Colab/Jupyter notebooks)，
    # 這意味著事件迴圈已在執行，因此您可以直接 await 函式。
    print("正在嘗試使用 'await' 執行 (筆記本的預設方法)...")
    await run_team_conversation()

    # 方法 2：asyncio.run (適用於標準 Python 腳本 [.py])
    # 如果您將此程式碼作為標準 Python 腳本從終端機執行，
    # 腳本上下文是同步的。需要 `asyncio.run()` 來
    # 建立和管理事件迴圈以執行您的 async 函式。
    # 若要使用此方法：
    # 1. 註解掉上面的 `await run_team_conversation()` 行。
    # 2. 取消註解以下區塊：
    """
    import asyncio
    if __name__ == "__main__": # 確保僅在直接執行腳本時才執行
        print("正在使用 'asyncio.run()' 執行 (適用於標準 Python 腳本)...")
        try:
            # 這會建立一個事件迴圈，執行您的 async 函式，並關閉迴圈。
            asyncio.run(run_team_conversation())
        except Exception as e:
            print(f"發生錯誤：{e}")
    """

else:
    # 如果先前未找到根代理程式變數，則會列印此訊息
    print("\n⚠️ 正在跳過代理程式團隊對話執行，因為根代理程式在前一步驟中未成功定義。")
```

---

仔細查看輸出日誌，特別是 `--- 工具：... 已呼叫 ---` 訊息。您應該會觀察到：

*   對於「你好！」，呼叫了 `say_hello` 工具 (表示 `greeting_agent` 處理了它)。
*   對於「紐約的天氣如何？」，呼叫了 `get_weather` 工具 (表示根代理程式處理了它)。
*   對於「謝謝，再見！」，呼叫了 `say_goodbye` 工具 (表示 `farewell_agent` 處理了它)。

這確認了**自動委派**的成功！根代理程式在其指令和其 `sub_agents` 的 `description` 的指導下，正確地將使用者請求路由到團隊中最合適的專家代理程式。

您現在已經用多個協作代理程式建構了您的應用程式。這種模組化設計是建構更複雜、更有能力的代理程式系統的基礎。在下一步中，我們將使用會話狀態讓我們的代理程式能夠在輪次之間記住資訊。

## 步驟 4：使用會話狀態新增記憶和個人化

到目前為止，我們的代理程式團隊可以透過委派處理不同的任務，但每次互動都是從頭開始——代理程式沒有會話中過去對話或使用者偏好的記憶。為了創造更複雜、更具上下文感知的體驗，代理程式需要**記憶**。ADK 透過**會話狀態**提供此功能。

**什麼是會話狀態？**

* 它是一個 Python 字典 (`session.state`)，與特定的使用者會話 (由 `APP_NAME`、`USER_ID`、`SESSION_ID` 識別) 相關聯。
* 它在該會話的*多個對話輪次*中持久化資訊。
* 代理程式和工具可以讀取和寫入此狀態，從而讓它們能夠記住詳細資訊、調整行為並個人化回應。

**代理程式如何與狀態互動：**

1. **`ToolContext` (主要方法)：** 工具可以接受一個 `ToolContext` 物件 (如果宣告為最後一個參數，則由 ADK 自動提供)。此物件可透過 `tool_context.state` 直接存取會話狀態，從而允許工具在執行*期間*讀取偏好或儲存結果。
2. **`output_key` (自動儲存代理程式回應)：** 可以使用 `output_key="your_key"` 設定 `Agent`。然後，ADK 將自動將代理程式在一輪中的最終文字回應儲存到 `session.state["your_key"]` 中。

**在此步驟中，我們將透過以下方式增強我們的天氣機器人團隊：**

1. 使用一個**新的** `InMemorySessionService` 來隔離地展示狀態。
2. 使用 `temperature_unit` 的使用者偏好初始化會話狀態。
3. 建立一個狀態感知版本的天氣工具 (`get_weather_stateful`)，它透過 `ToolContext` 讀取此偏好並調整其輸出格式 (攝氏/華氏)。
4. 更新根代理程式以使用此狀態感知工具，並使用 `output_key` 設定它，以自動將其最終天氣報告儲存到會話狀態。
5. 執行一個對話以觀察初始狀態如何影響工具，手動狀態變更如何改變後續行為，以及 `output_key` 如何持久化代理程式的回應。

---

**1\. 初始化新的會話服務和狀態**

為了清楚地展示狀態管理而不受先前步驟的干擾，我們將實例化一個新的 `InMemorySessionService`。我們還將建立一個具有初始狀態的會話，該狀態定義了使用者偏好的溫度單位。


```python
# @title 1. 初始化新的會話服務和狀態

# 匯入必要的會話元件
from google.adk.sessions import InMemorySessionService

# 為此狀態示範建立一個新的會話服務實例
session_service_stateful = InMemorySessionService()
print("✅ 已為狀態示範建立新的 InMemorySessionService。")

# 為本教學的此部分定義一個新的會話 ID
SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"

# 定義初始狀態資料 - 使用者最初偏好攝氏度
initial_state = {
    "user_preference_temperature_unit": "Celsius"
}

# 建立會話，提供初始狀態
session_stateful = await session_service_stateful.create_session(
    app_name=APP_NAME, # 使用一致的應用程式名稱
    user_id=USER_ID_STATEFUL,
    session_id=SESSION_ID_STATEFUL,
    state=initial_state # <<< 在建立期間初始化狀態
)
print(f"✅ 已為使用者 '{USER_ID_STATEFUL}' 建立會話 '{SESSION_ID_STATEFUL}'。")

# 驗證初始狀態是否已正確設定
retrieved_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id = SESSION_ID_STATEFUL)
print("\n--- 初始會話狀態 ---")
if retrieved_session:
    print(retrieved_session.state)
else:
    print("錯誤：無法檢索會話。")
```

---

**2\. 建立狀態感知天氣工具 (`get_weather_stateful`)**

現在，我們建立一個新版本的天氣工具。其主要功能是接受 `tool_context: ToolContext`，這讓它可以存取 `tool_context.state`。它將讀取 `user_preference_temperature_unit` 並相應地格式化溫度。


* **核心概念：`ToolContext`** 此物件是讓您的工具邏輯能夠與會話上下文互動的橋樑，包括讀取和寫入狀態變數。如果將其定義為工具函式的最後一個參數，ADK 會自動注入它。


* **最佳實踐：** 從狀態中讀取時，請使用 `dictionary.get('key', default_value)` 來處理鍵可能不存在的情況，確保您的工具不會崩潰。


```python
from google.adk.tools.tool_context import ToolContext

def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """擷取天氣，並根據會話狀態轉換溫度單位。"""
    print(f"--- 工具：為 {city} 呼叫 get_weather_stateful ---")

    # --- 從狀態中讀取偏好設定 ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # 預設為攝氏度
    print(f"--- 工具：正在讀取狀態 'user_preference_temperature_unit'：{preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # 模擬天氣資料 (內部始終以攝氏度儲存)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # 根據狀態偏好格式化溫度
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # 計算華氏溫度
            temp_unit = "°F"
        else: # 預設為攝氏度
            temp_value = temp_c
            temp_unit = "°C"

        report = f"{city.capitalize()} 的天氣是 {condition}，溫度為 {temp_value:.0f}{temp_unit}。"
        result = {"status": "success", "report": report}
        print(f"--- 工具：已在 {preferred_unit} 中產生報告。結果：{result} ---")

        # 寫回狀態的範例 (此工具中為可選)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- 工具：已更新狀態 'last_city_checked_stateful'：{city} ---")

        return result
    else:
        # 處理找不到城市的情況
        error_msg = f"抱歉，我沒有 '{city}' 的天氣資訊。"
        print(f"--- 工具：找不到城市 '{city}'。---")
        return {"status": "error", "error_message": error_msg}

print("✅ 已定義狀態感知 'get_weather_stateful' 工具。")

```

---

**3\. 重新定義子代理程式並更新根代理程式**

為確保此步驟是獨立的並能正確建構，我們首先完全按照步驟 3 的方式重新定義 `greeting_agent` 和 `farewell_agent`。然後，我們定義我們的新根代理程式 (`weather_agent_v4_stateful`)：

* 它使用新的 `get_weather_stateful` 工具。
* 它包含用於委派的問候和告別子代理程式。
* **至關重要的是**，它設定了 `output_key="last_weather_report"`，這會自動將其最終的天氣回應儲存到會話狀態中。


```python
# @title 3. 重新定義子代理程式並使用 output_key 更新根代理程式

# 確保必要的匯入：Agent、LiteLlm、Runner
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
# 確保已定義工具 'say_hello'、'say_goodbye' (來自步驟 3)
# 確保已定義模型常數 MODEL_GPT_4O、MODEL_GEMINI_2_0_FLASH 等。

# --- 重新定義問候代理程式 (來自步驟 3) ---
greeting_agent = None
try:
    # 使用定義的模型常數
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent", # 保持原始名稱以保持一致性
        instruction="您是問候代理程式。您唯一的任務是使用 'say_hello' 工具提供友好的問候。不要做其他任何事情。",
        description="使用 'say_hello' 工具處理簡單的問候和你好。",
        tools=[say_hello],
    )
    print(f"✅ 已重新定義代理程式 '{greeting_agent.name}'。")
except Exception as e:
    print(f"❌ 無法重新定義問候代理程式。請檢查模型/API 金鑰 ({greeting_agent.model})。錯誤：{e}")

# --- 重新定義告別代理程式 (來自步驟 3) ---
farewell_agent = None
try:
    # 使用定義的模型常數
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent", # 保持原始名稱
        instruction="您是告別代理程式。您唯一的任務是使用 'say_goodbye' 工具提供禮貌的告別訊息。不要執行任何其他操作。",
        description="使用 'say_goodbye' 工具處理簡單的告別和再見。",
        tools=[say_goodbye],
    )
    print(f"✅ 已重新定義代理程式 '{farewell_agent.name}'。")
except Exception as e:
    print(f"❌ 無法重新定義告別代理程式。請檢查模型/API 金鑰 ({farewell_agent.model})。錯誤：{e}")


# --- 定義更新後的根代理程式 ---
root_agent_stateful = None
runner_root_stateful = None # 初始化 runner

# 在繼續之前檢查所有元件
if greeting_agent and farewell_agent and 'get_weather_stateful' in globals():

    root_agent_model = MODEL_GEMINI_2_0_FLASH # 選擇協調模型

    root_agent_stateful = Agent(
        name="weather_agent_v4_stateful", # 新的版本名稱
        model=root_agent_model,
        description="主代理程式：提供天氣 (狀態感知單位)，委派問候/告別，將報告儲存到狀態。",
        instruction="您是主要的天氣代理程式。您的工作是使用 'get_weather_stateful' 提供天氣。"
                    "該工具將根據儲存在狀態中的使用者偏好格式化溫度。"
                    "將簡單的問候委派給 'greeting_agent'，將告別委派給 'farewell_agent'。"
                    "僅處理天氣請求、問候和告別。",
        tools=[get_weather_stateful], # 使用狀態感知工具
        sub_agents=[greeting_agent, farewell_agent], # 包括子代理程式
        output_key="last_weather_report" # <<< 自動儲存代理程式的最終天氣回應
    )
    print(f"✅ 已使用狀態感知工具和 output_key 建立根代理程式 '{root_agent_stateful.name}'。")

    # --- 為此根代理程式和新的會話服務建立 Runner ---
    if 'session_service_stateful' in globals():
        runner_root_stateful = Runner(
            agent=root_agent_stateful,
            app_name=APP_NAME,
            session_service=session_service_stateful # 使用新的狀態感知會話服務
        )
        print(f"✅ 已為狀態感知根代理程式 '{runner_root_stateful.agent.name}' 使用狀態感知會話服務建立 Runner。")
    else:
        print("❌ 無法建立 runner。缺少步驟 4 中的 'session_service_stateful'。")

else:
    print("❌ 無法建立狀態感知根代理程式。缺少先決條件或初始化失敗：")
    if not greeting_agent: print("   - greeting_agent 定義遺失。")
    if not farewell_agent: print("   - farewell_agent 定義遺失。")
    if 'get_weather_stateful' not in globals(): print("   - 'get_weather_stateful' 工具遺失。")

```

---

**4\. 互動並測試狀態流程**

現在，讓我們使用 `runner_root_stateful` (與我們的狀態感知代理程式和 `session_service_stateful` 相關聯) 執行一個旨在測試狀態互動的對話。我們將使用先前定義的 `call_agent_async` 函式，確保我們傳遞正確的 runner、使用者 ID (`USER_ID_STATEFUL`) 和會話 ID (`SESSION_ID_STATEFUL`)。

對話流程將是：

1.  **檢查天氣 (倫敦)：** `get_weather_stateful` 工具應從第 1 節中初始化的會話狀態中讀取初始的「攝氏」偏好。根代理程式的最終回應 (倫敦的攝氏天氣報告) 應透過 `output_key` 設定儲存到 `state['last_weather_report']` 中。
2.  **手動更新狀態：** 我們將*直接修改*儲存在 `InMemorySessionService` 實例 (`session_service_stateful`) 中的狀態。
    *   **為何直接修改？** `session_service.get_session()` 方法傳回會話的*副本*。修改該副本不會影響後續代理程式執行中使用的狀態。對於 `InMemorySessionService` 的此測試場景，我們存取內部 `sessions` 字典以將 `user_preference_temperature_unit` 的*實際*儲存值變更為「華氏」。*注意：在真實應用程式中，狀態變更通常由工具或代理程式邏輯傳回 `EventActions(state_delta=...)` 來觸發，而不是直接手動更新。*
3.  **再次檢查天氣 (紐約)：** `get_weather_stateful` 工具現在應從狀態中讀取更新後的「華氏」偏好，並相應地轉換溫度。根代理程式的*新*回應 (紐約的華氏天氣) 將因 `output_key` 而覆寫 `state['last_weather_report']` 中的先前值。
4.  **問候代理程式：** 驗證對 `greeting_agent` 的委派在狀態修改後仍能正常運作。此互動將成為在此特定序列中由 `output_key` 儲存的*最後*回應。
5.  **檢查最終狀態：** 對話結束後，我們最後一次檢索會話 (取得一個副本) 並列印其狀態，以確認 `user_preference_temperature_unit` 確實是「華氏」，觀察由 `output_key` 儲存的最終值 (在此執行中將是問候語)，並查看由工具寫入的 `last_city_checked_stateful` 值。



```python
# @title 4. 互動以測試狀態流程和 output_key
import asyncio # 確保匯入 asyncio

# 確保來自前一個儲存格的狀態感知 runner (runner_root_stateful) 可用
# 確保已定義 call_agent_async、USER_ID_STATEFUL、SESSION_ID_STATEFUL、APP_NAME

if 'runner_root_stateful' in globals() and runner_root_stateful:
    # 為狀態感知對話邏輯定義主 async 函式。
    # 此函式內部的 'await' 關鍵字對於非同步操作是必要的。
    async def run_stateful_conversation():
        print("\n--- 測試狀態：溫度單位轉換與 output_key ---")

        # 1. 檢查天氣 (使用初始狀態：攝氏)
        print("--- 第 1 輪：請求倫敦天氣 (預期攝氏) ---")
        await call_agent_async(query= "倫敦的天氣如何？",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 2. 手動更新狀態偏好為華氏 - 直接修改儲存
        print("\n--- 手動更新狀態：將單位設定為華氏 ---")
        try:
            # 直接存取內部儲存 - 這特定於 InMemorySessionService 用於測試
            # 注意：在具有持久性服務 (Database、VertexAI) 的生產環境中，您通常會
            # 透過代理程式動作或可用的特定服務 API 更新狀態，
            # 而不是直接操作內部儲存。
            stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
            stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
            # 可選：如果任何邏輯依賴它，您可能也想更新時間戳
            # import time
            # stored_session.last_update_time = time.time()
            print(f"--- 已儲存的會話狀態已更新。目前的 'user_preference_temperature_unit'：{stored_session.state.get('user_preference_temperature_unit', '未設定')} ---") # 新增 .get 以確保安全
        except KeyError:
            print(f"--- 錯誤：無法從內部儲存中為使用者 '{USER_ID_STATEFUL}' 在應用程式 '{APP_NAME}' 中檢索會話 '{SESSION_ID_STATEFUL}' 以更新狀態。請檢查 ID 以及是否已建立會話。---")
        except Exception as e:
             print(f"--- 更新內部會話狀態時發生錯誤：{e} ---")

        # 3. 再次檢查天氣 (工具現在應使用華氏)
        # 這也會透過 output_key 更新 'last_weather_report'
        print("\n--- 第 2 輪：請求紐約天氣 (預期華氏) ---")
        await call_agent_async(query= "告訴我紐約的天氣。",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

        # 4. 測試基本委派 (應仍能正常運作)
        # 這將再次更新 'last_weather_report'，覆寫紐約的天氣報告
        print("\n--- 第 3 輪：傳送問候 ---")
        await call_agent_async(query= "嗨！",
                               runner=runner_root_stateful,
                               user_id=USER_ID_STATEFUL,
                               session_id=SESSION_ID_STATEFUL
                              )

    # --- 執行 `run_stateful_conversation` async 函式 ---
    # 根據您的環境選擇以下方法之一。

    # 方法 1：直接 await (筆記本/非同步 REPL 的預設方法)
    # 如果您的環境支援頂層 await (如 Colab/Jupyter notebooks)，
    # 這意味著事件迴圈已在執行，因此您可以直接 await 函式。
    print("正在嘗試使用 'await' 執行 (筆記本的預設方法)...")
    await run_stateful_conversation()

    # 方法 2：asyncio.run (適用於標準 Python 腳本 [.py])
    # 如果您將此程式碼作為標準 Python 腳本從終端機執行，
    # 腳本上下文是同步的。需要 `asyncio.run()` 來
    # 建立和管理事件迴圈以執行您的 async 函式。
    # 若要使用此方法：
    # 1. 註解掉上面的 `await run_stateful_conversation()` 行。
    # 2. 取消註解以下區塊：
    """
    import asyncio
    if __name__ == "__main__": # 確保僅在直接執行腳本時才執行
        print("正在使用 'asyncio.run()' 執行 (適用於標準 Python 腳本)...")
        try:
            # 這會建立一個事件迴圈，執行您的 async 函式，並關閉迴圈。
            asyncio.run(run_stateful_conversation())
        except Exception as e:
            print(f"發生錯誤：{e}")
    """

    # --- 在對話後檢查最終會話狀態 ---
    # 此區塊在任一執行方法完成後執行。
    print("\n--- 檢查最終會話狀態 (在護欄測試後) ---")
    # 使用與此狀態感知會話相關聯的會話服務實例
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id=SESSION_ID_STATEFUL)
    if final_session:
        # 使用 .get() 以更安全地存取可能遺失的鍵
        print(f"護欄觸發旗標：{final_session.state.get('guardrail_block_keyword_triggered', '未設定 (或 False)')}")
        print(f"上次天氣報告：{final_session.state.get('last_weather_report', '未設定')}") # 如果成功，應為倫敦天氣
        print(f"溫度單位：{final_session.state.get('user_preference_temperature_unit', '未設定')}") # 應為華氏
        # print(f"完整狀態字典：{final_session.state}") # 用於詳細檢視
    else:
        print("\n❌ 錯誤：無法檢索最終會話狀態。")

else:
    print("\n⚠️ 正在跳過狀態測試對話。狀態感知根代理程式 runner ('runner_root_stateful') 不可用。")
```

---

透過檢視對話流程和最終的會話狀態列印輸出，您可以確認：

*   **狀態讀取：** 天氣工具 (`get_weather_stateful`) 正確地從狀態中讀取了 `user_preference_temperature_unit`，最初對倫敦使用「攝氏」。
*   **狀態更新：** 直接修改成功地將儲存的偏好變更為「華氏」。
*   **狀態讀取 (更新後)：** 該工具隨後在被詢問紐約天氣時讀取了「華氏」並執行了轉換。
*   **工具狀態寫入：** 該工具成功地將 `last_city_checked_stateful` (在第二次天氣檢查後為「紐約」) 透過 `tool_context.state` 寫入狀態。
*   **委派：** 對 `greeting_agent` 的「嗨！」委派在狀態修改後仍能正常運作。
*   **`output_key`：** `output_key="last_weather_report"` 成功地儲存了根代理程式在*每個*輪次中的*最終*回應，其中根代理程式是最終回應者。在此序列中，最後的回應是問候語 (「你好！」)，因此它覆寫了狀態鍵中的天氣報告。
*   **最終狀態：** 最終檢查確認偏好持久化為「華氏」。

您現在已成功地整合了會話狀態，以使用 `ToolContext` 個人化代理程式行為，為測試 `InMemorySessionService` 手動操作狀態，並觀察了 `output_key` 如何提供一個簡單的機制來將代理程式的最後回應儲存到狀態。在接下來的步驟中，我們將使用回呼實作安全護欄，對狀態管理的這種基礎理解至關重要。

## 步驟 5：新增安全性 - 使用 `before_model_callback` 的輸入護欄

我們的代理程式團隊變得越來越有能力，能夠記住偏好並有效地使用工具。然而，在真實世界的場景中，我們通常需要安全機制來在潛在有問題的請求到達核心大型語言模型 (LLM) *之前*控制代理程式的行為。

ADK 提供了**回呼**——允許您掛鉤到代理程式執行生命週期中特定點的函式。`before_model_callback` 對於輸入安全特別有用。

**什麼是 `before_model_callback`？**

* 它是一個您定義的 Python 函式，ADK 會在代理程式將其編譯的請求 (包括對話歷史、指令和最新的使用者訊息) 傳送到底層 LLM *之前*執行。
* **目的：** 檢查請求，如有必要則修改它，或根據預先定義的規則完全阻擋它。

**常見使用案例：**

* **輸入驗證/過濾：** 檢查使用者輸入是否符合標準或包含不允許的內容 (如 PII 或關鍵字)。
* **護欄：** 防止有害、離題或違反政策的請求被 LLM 處理。
* **動態提示修改：** 在傳送之前，將及時資訊 (例如，從會話狀態) 新增到 LLM 請求上下文中。

**運作方式：**

1. 定義一個接受 `callback_context: CallbackContext` 和 `llm_request: LlmRequest` 的函式。

    * `callback_context`：提供對代理程式資訊、會話狀態 (`callback_context.state`) 等的存取。
    * `llm_request`：包含要傳送給 LLM 的完整負載 (`contents`、`config`)。

2. 在函式內部：

    * **檢查：** 檢查 `llm_request.contents` (特別是最後的使用者訊息)。
    * **修改 (謹慎使用)：** 您*可以*變更 `llm_request` 的部分內容。
    * **阻擋 (護欄)：** 傳回一個 `LlmResponse` 物件。ADK 將立即傳回此回應，*跳過*該輪次的 LLM 呼叫。
    * **允許：** 傳回 `None`。ADK 會繼續使用 (可能已修改的) 請求呼叫 LLM。

**在此步驟中，我們將：**

1. 定義一個 `before_model_callback` 函式 (`block_keyword_guardrail`)，它會檢查使用者的輸入中是否有特定的關鍵字「BLOCK」。
2. 更新我們的狀態感知根代理程式 (`weather_agent_v4_stateful`，來自步驟 4) 以使用此回呼。
3. 為此更新後的代理程式建立一個新的 runner，但使用*相同的狀態感知會話服務*以維持狀態的連續性。
4. 透過傳送正常和包含關鍵字的請求來測試護欄。

---

**1\. 定義護欄回呼函式**

此函式將檢查 `llm_request` 內容中的最後一則使用者訊息。如果找到「BLOCK」(不區分大小寫)，它會建構並傳回一個 `LlmResponse` 以阻擋流程；否則，它會傳回 `None`。


```python
# @title 1. 定義 before_model_callback 護欄

# 確保可用的必要匯入
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types # 用於建立回應內容
from typing import Optional

def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    檢查最新的使用者訊息中是否有 'BLOCK'。如果找到，則阻擋 LLM 呼叫
    並傳回一個預先定義的 LlmResponse。否則，傳回 None 以繼續。
    """
    agent_name = callback_context.agent_name # 取得正在攔截其模型呼叫的代理程式名稱
    print(f"--- 回呼：正在為代理程式執行 block_keyword_guardrail：{agent_name} ---")

    # 從請求歷史中擷取最新使用者訊息的文字
    last_user_message_text = ""
    if llm_request.contents:
        # 尋找角色為 'user' 的最新訊息
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # 為了簡單起見，假設文字在第一部分
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break # 找到最後的使用者訊息文字

    print(f"--- 回呼：正在檢查最後的使用者訊息：'{last_user_message_text[:100]}...' ---") # 記錄前 100 個字元

    # --- 護欄邏輯 ---
    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper(): # 不區分大小寫的檢查
        print(f"--- 回呼：找到 '{keyword_to_block}'。正在阻擋 LLM 呼叫！---")
        # 可選地，在狀態中設定一個旗標以記錄阻擋事件
        callback_context.state["guardrail_block_keyword_triggered"] = True
        print(f"--- 回呼：已設定狀態 'guardrail_block_keyword_triggered'：True ---")

        # 建構並傳回一個 LlmResponse 以停止流程並改為傳回此回應
        return LlmResponse(
            content=types.Content(
                role="model", # 模仿代理程式角度的回應
                parts=[types.Part(text=f"我無法處理此請求，因為它包含被阻擋的關鍵字 '{keyword_to_block}'。")],
            )
            # 注意：如果需要，您也可以在此處設定 error_message 欄位
        )
    else:
        # 未找到關鍵字，允許請求繼續傳送給 LLM
        print(f"--- 回呼：未找到關鍵字。允許為 {agent_name} 呼叫 LLM。---")
        return None # 傳回 None 表示 ADK 應正常繼續

print("✅ 已定義 block_keyword_guardrail 函式。")

```

---

**2\. 更新根代理程式以使用回呼**

我們重新定義根代理程式，新增 `before_model_callback` 參數並將其指向我們新的護欄函式。為了清楚起見，我們將給它一個新的版本名稱。

*重要：* 如果子代理程式 (`greeting_agent`、`farewell_agent`) 和狀態感知工具 (`get_weather_stateful`) 在先前的步驟中尚未可用，我們需要在此上下文中重新定義它們，以確保根代理程式定義可以存取其所有元件。


```python
# @title 2. 使用 before_model_callback 更新根代理程式


# --- 重新定義子代理程式 (確保它們在此上下文中存在) ---
greeting_agent = None
try:
    # 使用定義的模型常數
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent", # 保持原始名稱以保持一致性
        instruction="您是問候代理程式。您唯一的任務是使用 'say_hello' 工具提供友好的問候。不要做其他任何事情。",
        description="使用 'say_hello' 工具處理簡單的問候和你好。",
        tools=[say_hello],
    )
    print(f"✅ 已重新定義子代理程式 '{greeting_agent.name}'。")
except Exception as e:
    print(f"❌ 無法重新定義問候代理程式。請檢查模型/API 金鑰 ({greeting_agent.model})。錯誤：{e}")

farewell_agent = None
try:
    # 使用定義的模型常數
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent", # 保持原始名稱
        instruction="您是告別代理程式。您唯一的任務是使用 'say_goodbye' 工具提供禮貌的告別訊息。不要執行任何其他操作。",
        description="使用 'say_goodbye' 工具處理簡單的告別和再見。",
        tools=[say_goodbye],
    )
    print(f"✅ 已重新定義子代理程式 '{farewell_agent.name}'。")
except Exception as e:
    print(f"❌ 無法重新定義告別代理程式。請檢查模型/API 金鑰 ({farewell_agent.model})。錯誤：{e}")


# --- 定義帶有回呼的根代理程式 ---
root_agent_model_guardrail = None
runner_root_model_guardrail = None

# 在繼續之前檢查所有元件
if ('greeting_agent' in globals() and greeting_agent and
    'farewell_agent' in globals() and farewell_agent and
    'get_weather_stateful' in globals() and
    'block_keyword_guardrail' in globals()):

    # 使用定義的模型常數
    root_agent_model = MODEL_GEMINI_2_0_FLASH

    root_agent_model_guardrail = Agent(
        name="weather_agent_v5_model_guardrail", # 新的版本名稱以示清晰
        model=root_agent_model,
        description="主代理程式：處理天氣，委派問候/告別，包含輸入關鍵字護欄。",
        instruction="您是主要的天氣代理程式。使用 'get_weather_stateful' 提供天氣。"
                    "將簡單的問候委派給 'greeting_agent'，將告別委派給 'farewell_agent'。"
                    "僅處理天氣請求、問候和告別。",
        tools=[get_weather],
        sub_agents=[greeting_agent, farewell_agent], # 參考重新定義的子代理程式
        output_key="last_weather_report", # 保留步驟 4 的 output_key
        before_model_callback=block_keyword_guardrail # <<< 指派護欄回呼
    )
    print(f"✅ 已使用 before_model_callback 建立根代理程式 '{root_agent_model_guardrail.name}'。")

    # --- 為此代理程式建立 Runner，使用相同的狀態感知會話服務 ---
    # 確保 session_service_stateful 存在於步驟 4
    if 'session_service_stateful' in globals():
        runner_root_model_guardrail = Runner(
            agent=root_agent_model_guardrail,
            app_name=APP_NAME,
            session_service=session_service_stateful # <<< 使用步驟 4/5 的服務
        )
        print(f"✅ 已為護欄代理程式 '{runner_root_model_guardrail.agent.name}' 使用狀態感知會話服務建立 Runner。")
    else:
        print("❌ 無法建立 runner。缺少步驟 4/5 的 'session_service_stateful'。")

else:
    print("❌ 無法使用模型護欄建立根代理程式。一個或多個先決條件遺失或初始化失敗：")
    if not greeting_agent: print("   - 問候代理程式")
    if not farewell_agent: print("   - 告別代理程式")
    if 'get_weather_stateful' not in globals(): print("   - 'get_weather_stateful' 工具")
    if 'block_keyword_guardrail' not in globals(): print("   - 'block_keyword_guardrail' 回呼")
```

---

**3\. 互動以測試護欄**

讓我們測試護欄的行為。我們將使用與步驟 4 中相同的會話 (`SESSION_ID_STATEFUL`) 來顯示狀態在這些變更中是持久的。

1. 傳送一個正常的天氣請求 (應通過護欄並執行)。
2. 傳送一個包含「BLOCK」的請求 (應被回呼攔截)。
3. 傳送一個問候 (應通過根代理程式的護欄，被委派，並正常執行)。


```python
# @title 3. 互動以測試模型輸入護欄
import asyncio # 確保匯入 asyncio

# 確保護欄代理程式的 runner 可用
if 'runner_root_model_guardrail' in globals() and runner_root_model_guardrail:
    # 為護欄測試對話定義主 async 函式。
    # 此函式內部的 'await' 關鍵字對於非同步操作是必要的。
    async def run_guardrail_test_conversation():
        print("\n--- 測試模型輸入護欄 ---")

        # 使用帶有回呼和現有狀態感知會話 ID 的代理程式的 runner
        # 定義一個輔助 lambda 以便更清晰地進行互動呼叫
        interaction_func = lambda query: call_agent_async(query,
                                                         runner_root_model_guardrail,
                                                         USER_ID_STATEFUL, # 使用現有的使用者 ID
                                                         SESSION_ID_STATEFUL # 使用現有的會話 ID
                                                        )
        # 1. 正常請求 (回呼允許，應使用先前狀態變更的華氏溫度)
        print("--- 第 1 輪：請求倫敦天氣 (預期允許，華氏) ---")
        await interaction_func("倫敦的天氣如何？")

        # 2. 包含被阻擋關鍵字的請求 (回呼攔截)
        print("\n--- 第 2 輪：使用被阻擋的關鍵字請求 (預期被阻擋) ---")
        await interaction_func("BLOCK 東京天氣的請求") # 回呼應捕捉到 "BLOCK"

        # 3. 正常問候 (回呼允許根代理程式，發生委派)
        print("\n--- 第 3 輪：傳送問候 (預期允許) ---")
        await interaction_func("再次問好")

    # --- 執行 `run_guardrail_test_conversation` async 函式 ---
    # 根據您的環境選擇以下方法之一。

    # 方法 1：直接 await (筆記本/非同步 REPL 的預設方法)
    # 如果您的環境支援頂層 await (如 Colab/Jupyter notebooks)，
    # 這意味著事件迴圈已在執行，因此您可以直接 await 函式。
    print("正在嘗試使用 'await' 執行 (筆記本的預設方法)...")
    await run_guardrail_test_conversation()

    # 方法 2：asyncio.run (適用於標準 Python 腳本 [.py])
    # 如果您將此程式碼作為標準 Python 腳本從終端機執行，
    # 腳本上下文是同步的。需要 `asyncio.run()` 來
    # 建立和管理事件迴圈以執行您的 async 函式。
    # 若要使用此方法：
    # 1. 註解掉上面的 `await run_guardrail_test_conversation()` 行。
    # 2. 取消註解以下區塊：
    """
    import asyncio
    if __name__ == "__main__": # 確保僅在直接執行腳本時才執行
        print("正在使用 'asyncio.run()' 執行 (適用於標準 Python 腳本)...")
        try:
            # 這會建立一個事件迴圈，執行您的 async 函式，並關閉迴圈。
            asyncio.run(run_guardrail_test_conversation())
        except Exception as e:
            print(f"發生錯誤：{e}")
    """

    # --- 在對話後檢查最終會話狀態 ---
    # 此區塊在任一執行方法完成後執行。
    # 可選：檢查狀態中由回呼設定的觸發旗標
    print("\n--- 檢查最終會話狀態 (在護欄測試後) ---")
    # 使用與此狀態感知會話相關聯的會話服務實例
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id=SESSION_ID_STATEFUL)
    if final_session:
        # 使用 .get() 以更安全地存取
        print(f"護欄觸發旗標：{final_session.state.get('guardrail_block_keyword_triggered', '未設定 (或 False)')}")
        print(f"上次天氣報告：{final_session.state.get('last_weather_report', '未設定')}") # 如果成功，應為倫敦天氣
        print(f"溫度單位：{final_session.state.get('user_preference_temperature_unit', '未設定')}") # 應為華氏
        # print(f"完整狀態字典：{final_session.state}") # 用於詳細檢視
    else:
        print("\n❌ 錯誤：無法檢索最終會話狀態。")

else:
    print("\n⚠️ 正在跳過模型護欄測試。Runner ('runner_root_model_guardrail') 不可用。")
```

---

觀察執行流程：

1. **倫敦天氣：** `before_model_callback` 為 `weather_agent_v5_model_guardrail` 執行，檢查訊息，列印「未找到關鍵字。允許 LLM 呼叫。」，並傳回 `None`。代理程式繼續，呼叫 `get_weather_stateful` 工具 (它使用步驟 4 中狀態變更的「華氏」偏好)，並傳回天氣。此回應透過 `output_key` 更新 `last_weather_report`。
2. **BLOCK 請求：** `before_model_callback` 再次為 `weather_agent_v5_model_guardrail` 執行，檢查訊息，找到「BLOCK」，列印「正在阻擋 LLM 呼叫！」，設定狀態旗標，並傳回預先定義的 `LlmResponse`。代理程式的底層 LLM *永遠不會*為此輪次被呼叫。使用者會看到回呼的阻擋訊息。
3. **再次問好：** `before_model_callback` 為 `weather_agent_v5_model_guardrail` 執行，允許請求。然後，根代理程式委派給 `greeting_agent`。*注意：在根代理程式上定義的 `before_model_callback` 不會自動應用於子代理程式。* `greeting_agent` 正常繼續，呼叫其 `say_hello` 工具，並傳回問候語。

您已成功實作一個輸入安全層！`before_model_callback` 提供了一個強大的機制，可以在進行昂貴或有潛在風險的 LLM 呼叫*之前*強制執行規則並控制代理程式行為。接下來，我們將應用類似的概念，在工具使用本身周圍新增護欄。

## 步驟 6：新增安全性 - 工具參數護欄 (`before_tool_callback`)

在步驟 5 中，我們新增了一個護欄，以在使用者輸入到達 LLM *之前*檢查並可能阻擋它。現在，我們將在 LLM 決定使用工具*之後*，但在該工具實際執行*之前*，新增另一層控制。這對於驗證 LLM 希望傳遞給工具的*參數*很有用。

ADK 為此精確目的提供了 `before_tool_callback`。

**什麼是 `before_tool_callback`？**

* 它是一個 Python 函式，在特定工具函式執行*之前*，在 LLM 請求其使用並決定參數之後執行。
* **目的：** 驗證工具參數，根據特定輸入阻止工具執行，動態修改參數，或強制執行資源使用策略。

**常見使用案例：**

* **參數驗證：** 檢查 LLM 提供的參數是否有效、在允許的範圍內或符合預期的格式。
* **資源保護：** 防止使用可能昂貴、存取受限資料或引起不必要副作用的輸入呼叫工具 (例如，阻擋某些參數的 API 呼叫)。
* **動態參數修改：** 在工具執行前，根據會話狀態或其他上下文資訊調整參數。

**運作方式：**

1. 定義一個接受 `tool: BaseTool`、`args: Dict[str, Any]` 和 `tool_context: ToolContext` 的函式。

    * `tool`：即將被呼叫的工具物件 (檢查 `tool.name`)。
    * `args`：LLM 為該工具產生的參數字典。
    * `tool_context`：提供對會話狀態 (`tool_context.state`)、代理程式資訊等的存取。

2. 在函式內部：

    * **檢查：** 檢查 `tool.name` 和 `args` 字典。
    * **修改：** *直接*變更 `args` 字典中的值。如果您傳回 `None`，則工具會使用這些修改後的參數執行。
    * **阻擋/覆寫 (護欄)：** 傳回一個**字典**。ADK 將此字典視為工具呼叫的*結果*，完全*跳過*原始工具函式的執行。該字典理想上應符合其所阻擋工具的預期傳回格式。
    * **允許：** 傳回 `None`。ADK 會繼續使用 (可能已修改的) 參數執行實際的工具函式。

**在此步驟中，我們將：**

1. 定義一個 `before_tool_callback` 函式 (`block_paris_tool_guardrail`)，它專門檢查 `get_weather_stateful` 工具是否以城市「巴黎」被呼叫。
2. 如果偵測到「巴黎」，回呼將阻擋該工具並傳回一個自訂的錯誤字典。
3. 更新我們的根代理程式 (`weather_agent_v6_tool_guardrail`) 以包含 `before_model_callback` 和這個新的 `before_tool_callback`。
4. 為此代理程式建立一個新的 runner，使用相同的狀態感知會話服務。
5. 透過請求允許的城市和被阻擋的城市 (「巴黎」) 的天氣來測試流程。

---

**1\. 定義工具護欄回呼函式**

此函式針對 `get_weather_stateful` 工具。它會檢查 `city` 參數。如果是「巴黎」，它會傳回一個看起來像工具自身錯誤回應的錯誤字典。否則，它會透過傳回 `None` 來允許工具執行。


```python
# @title 1. 定義 before_tool_callback 護欄

# 確保可用的必要匯入
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from typing import Optional, Dict, Any # 用於類型提示

def block_paris_tool_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    檢查 'get_weather_stateful' 是否為 '巴黎' 被呼叫。
    如果是，則阻擋工具執行並傳回一個特定的錯誤字典。
    否則，透過傳回 None 來允許工具呼叫繼續。
    """
    tool_name = tool.name
    agent_name = tool_context.agent_name # 嘗試工具呼叫的代理程式
    print(f"--- 回呼：正在為代理程式 '{agent_name}' 中的工具 '{tool_name}' 執行 block_paris_tool_guardrail ---")
    print(f"--- 回呼：正在檢查參數：{args} ---")

    # --- 護欄邏輯 ---
    target_tool_name = "get_weather_stateful" # 符合 FunctionTool 使用的函式名稱
    blocked_city = "paris"

    # 檢查是否是正確的工具且城市參數是否符合被阻擋的城市
    if tool_name == target_tool_name:
        city_argument = args.get("city", "") # 安全地取得 'city' 參數
        if city_argument and city_argument.lower() == blocked_city:
            print(f"--- 回呼：偵測到被阻擋的城市 '{city_argument}'。正在阻擋工具執行！---")
            # 可選地更新狀態
            tool_context.state["guardrail_tool_block_triggered"] = True
            print(f"--- 回呼：已設定狀態 'guardrail_tool_block_triggered'：True ---")

            # 傳回一個符合工具預期錯誤輸出格式的字典
            # 此字典成為工具的結果，跳過實際的工具執行。
            return {
                "status": "error",
                "error_message": f"政策限制：目前已透過工具護欄停用對 '{city_argument.capitalize()}' 的天氣檢查。"
            }
        else:
             print(f"--- 回呼：城市 '{city_argument}' 對於工具 '{tool_name}' 是允許的。---")
    else:
        print(f"--- 回呼：工具 '{tool_name}' 不是目標工具。正在允許。---")


    # 如果上面的檢查沒有傳回字典，則允許工具執行
    print(f"--- 回呼：正在允許工具 '{tool_name}' 繼續。---")
    return None # 傳回 None 允許實際的工具函式執行

print("✅ 已定義 block_paris_tool_guardrail 函式。")


```

---

**2\. 更新根代理程式以使用兩個回呼**

我們再次重新定義根代理程式 (`weather_agent_v6_tool_guardrail`)，這次在步驟 5 的 `before_model_callback` 旁邊新增 `before_tool_callback` 參數。

*獨立執行注意事項：* 與步驟 5 類似，在定義此代理程式之前，請確保所有先決條件 (子代理程式、工具、`before_model_callback`) 都已定義或在執行上下文中可用。


```python
# @title 2. 使用兩個回呼更新根代理程式 (獨立)

# --- 確保已定義先決條件 ---
# (包括或確保執行以下定義：Agent、LiteLlm、Runner、ToolContext、
#  MODEL 常數、say_hello、say_goodbye、greeting_agent、farewell_agent、
#  get_weather_stateful、block_keyword_guardrail、block_paris_tool_guardrail)

# --- 重新定義子代理程式 (確保它們在此上下文中存在) ---
greeting_agent = None
try:
    # 使用定義的模型常數
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent", # 保持原始名稱以保持一致性
        instruction="您是問候代理程式。您唯一的任務是使用 'say_hello' 工具提供友好的問候。不要做其他任何事情。",
        description="使用 'say_hello' 工具處理簡單的問候和你好。",
        tools=[say_hello],
    )
    print(f"✅ 已重新定義子代理程式 '{greeting_agent.name}'。")
except Exception as e:
    print(f"❌ 無法重新定義問候代理程式。請檢查模型/API 金鑰 ({greeting_agent.model})。錯誤：{e}")

farewell_agent = None
try:
    # 使用定義的模型常數
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent", # 保持原始名稱
        instruction="您是告別代理程式。您唯一的任務是使用 'say_goodbye' 工具提供禮貌的告別訊息。不要執行任何其他操作。",
        description="使用 'say_goodbye' 工具處理簡單的告別和再見。",
        tools=[say_goodbye],
    )
    print(f"✅ 已重新定義子代理程式 '{farewell_agent.name}'。")
except Exception as e:
    print(f"❌ 無法重新定義告別代理程式。請檢查模型/API 金鑰 ({farewell_agent.model})。錯誤：{e}")

# --- 定義帶有兩個回呼的根代理程式 ---
root_agent_tool_guardrail = None
runner_root_tool_guardrail = None

if ('greeting_agent' in globals() and greeting_agent and
    'farewell_agent' in globals() and farewell_agent and
    'get_weather_stateful' in globals() and
    'block_keyword_guardrail' in globals() and
    'block_paris_tool_guardrail' in globals()):

    root_agent_model = MODEL_GEMINI_2_0_FLASH

    root_agent_tool_guardrail = Agent(
        name="weather_agent_v6_tool_guardrail", # 新的版本名稱以示清晰
        model=root_agent_model,
        description="主代理程式：處理天氣，委派，包含輸入和工具護欄。",
        instruction="您是主要的天氣代理程式。使用 'get_weather_stateful' 提供天氣。"
                    "將問候委派給 'greeting_agent'，將告別委派給 'farewell_agent'。"
                    "僅處理天氣、問候和告別。",
        tools=[get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent],
        output_key="last_weather_report",
        before_model_callback=block_keyword_guardrail, # 保留模型護欄
        before_tool_callback=block_paris_tool_guardrail # <<< 新增工具護欄
    )
    print(f"✅ 已使用兩個回呼建立根代理程式 '{root_agent_tool_guardrail.name}'。")

    # --- 為此代理程式建立 Runner，使用相同的狀態感知會話服務 ---
    if 'session_service_stateful' in globals():
        runner_root_tool_guardrail = Runner(
            agent=root_agent_tool_guardrail,
            app_name=APP_NAME,
            session_service=session_service_stateful # <<< 使用步驟 4/5 的服務
        )
        print(f"✅ 已為工具護欄代理程式 '{runner_root_tool_guardrail.agent.name}' 使用狀態感知會話服務建立 Runner。")
    else:
        print("❌ 無法建立 runner。缺少步驟 4/5 的 'session_service_stateful'。")

else:
    print("❌ 無法使用工具護欄建立根代理程式。一個或多個先決條件遺失或初始化失敗。")

```

---

**3\. 互動以測試工具護欄**

讓我們測試互動流程，再次使用與先前步驟相同的狀態感知會話 (`SESSION_ID_STATEFUL`)。

1. 請求「紐約」的天氣：通過兩個回呼，工具執行 (使用來自狀態的華氏偏好)。
2. 請求「巴黎」的天氣：通過 `before_model_callback`。LLM 決定呼叫 `get_weather_stateful(city='Paris')`。`before_tool_callback` 攔截，阻擋工具，並傳回錯誤字典。代理程式轉發此錯誤。
3. 請求「倫敦」的天氣：正常通過兩個回呼，工具執行。


```python
# @title 3. 互動以測試工具參數護欄
import asyncio # 確保匯入 asyncio

# 確保工具護欄代理程式的 runner 可用
if 'runner_root_tool_guardrail' in globals() and runner_root_tool_guardrail:
    # 為工具護欄測試對話定義主 async 函式。
    # 此函式內部的 'await' 關鍵字對於非同步操作是必要的。
    async def run_tool_guardrail_test():
        print("\n--- 測試工具參數護欄 ('巴黎' 被阻擋) ---")

        # 使用帶有兩個回呼和現有狀態感知會話的代理程式的 runner
        # 定義一個輔助 lambda 以便更清晰地進行互動呼叫
        interaction_func = lambda query: call_agent_async(query,
                                                         runner_root_tool_guardrail,
                                                         USER_ID_STATEFUL, # 使用現有的使用者 ID
                                                         SESSION_ID_STATEFUL # 使用現有的會話 ID
                                                        )
        # 1. 允許的城市 (應通過兩個回呼，使用華氏狀態)
        print("--- 第 1 輪：請求紐約天氣 (預期允許) ---")
        await interaction_func("紐約的天氣如何？")

        # 2. 被阻擋的城市 (應通過模型回呼，但被工具回呼阻擋)
        print("\n--- 第 2 輪：請求巴黎天氣 (預期被工具護欄阻擋) ---")
        await interaction_func("巴黎呢？") # 工具回呼應攔截此請求

        # 3. 另一個允許的城市 (應再次正常運作)
        print("\n--- 第 3 輪：請求倫敦天氣 (預期允許) ---")
        await interaction_func("告訴我倫敦的天氣。")

    # --- 執行 `run_tool_guardrail_test` async 函式 ---
    # 根據您的環境選擇以下方法之一。

    # 方法 1：直接 await (筆記本/非同步 REPL 的預設方法)
    # 如果您的環境支援頂層 await (如 Colab/Jupyter notebooks)，
    # 這意味著事件迴圈已在執行，因此您可以直接 await 函式。
    print("正在嘗試使用 'await' 執行 (筆記本的預設方法)...")
    await run_tool_guardrail_test()

    # 方法 2：asyncio.run (適用於標準 Python 腳本 [.py])
    # 如果您將此程式碼作為標準 Python 腳本從終端機執行，
    # 腳本上下文是同步的。需要 `asyncio.run()` 來
    # 建立和管理事件迴圈以執行您的 async 函式。
    # 若要使用此方法：
    # 1. 註解掉上面的 `await run_tool_guardrail_test()` 行。
    # 2. 取消註解以下區塊：
    """
    import asyncio
    if __name__ == "__main__": # 確保僅在直接執行腳本時才執行
        print("正在使用 'asyncio.run()' 執行 (適用於標準 Python 腳本)...")
        try:
            # 這會建立一個事件迴圈，執行您的 async 函式，並關閉迴圈。
            asyncio.run(run_tool_guardrail_test())
        except Exception as e:
            print(f"發生錯誤：{e}")
    """

    # --- 在對話後檢查最終會話狀態 ---
    # 此區塊在任一執行方法完成後執行。
    # 可選：檢查狀態中由工具阻擋觸發的旗標
    print("\n--- 檢查最終會話狀態 (在工具護欄測試後) ---")
    # 使用與此狀態感知會話相關聯的會話服務實例
    final_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id= SESSION_ID_STATEFUL)
    if final_session:
        # 使用 .get() 以更安全地存取
        print(f"工具護欄觸發旗標：{final_session.state.get('guardrail_tool_block_triggered', '未設定 (或 False)')}")
        print(f"上次天氣報告：{final_session.state.get('last_weather_report', '未設定')}") # 如果成功，應為倫敦天氣
        print(f"溫度單位：{final_session.state.get('user_preference_temperature_unit', '未設定')}") # 應為華氏
        # print(f"完整狀態字典：{final_session.state}") # 用於詳細檢視
    else:
        print("\n❌ 錯誤：無法檢索最終會話狀態。")

else:
    print("\n⚠️ 正在跳過工具護欄測試。Runner ('runner_root_tool_guardrail') 不可用。")
```

---

分析輸出：

1. **紐約：** `before_model_callback` 允許請求。LLM 請求 `get_weather_stateful`。`before_tool_callback` 執行，檢查參數 (`{'city': 'New York'}`)，看到它不是「巴黎」，列印「正在允許工具...」並傳回 `None`。實際的 `get_weather_stateful` 函式執行，從狀態中讀取「華氏」，並傳回天氣報告。代理程式轉發此回應，並透過 `output_key` 儲存。
2. **巴黎：** `before_model_callback` 允許請求。LLM 請求 `get_weather_stateful(city='Paris')`。`before_tool_callback` 執行，檢查參數，偵測到「巴黎」，列印「正在阻擋工具執行！」，設定狀態旗標，並傳回錯誤字典 `{'status': 'error', 'error_message': '政策限制...'}`。實際的 `get_weather_stateful` 函式**永遠不會執行**。代理程式收到錯誤字典，*就好像它是工具的輸出一樣*，並根據該錯誤訊息制定回應。
3. **倫敦：** 行為與紐約類似，通過兩個回呼並成功執行工具。新的倫敦天氣報告會覆寫狀態中的 `last_weather_report`。

您現在已新增一個關鍵的安全層，不僅控制*什麼*到達 LLM，還控制*如何*根據 LLM 產生的特定參數使用代理程式的工具。像 `before_model_callback` 和 `before_tool_callback` 這樣的回呼對於建構穩健、安全且符合政策的代理程式應用程式至關重要。



---


## 結論：您的代理程式團隊已準備就緒！

恭喜！您已成功地從建構一個單一、基本的天氣代理程式，到使用代理程式開發套件 (ADK) 建構一個複雜的多代理程式團隊。

**讓我們回顧一下您已完成的內容：**

*   您從一個配備單一工具 (`get_weather`) 的**基礎代理程式**開始。
*   您使用 LiteLLM 探索了 ADK 的**多模型彈性**，使用不同的 LLM (如 Gemini、GPT-4o 和 Claude) 執行相同的核心邏輯。
*   您透過建立專門的子代理程式 (`greeting_agent`、`farewell_agent`) 並啟用從根代理程式進行**自動委派**，擁抱了**模組化**。
*   您使用**會話狀態**為您的代理程式提供了**記憶**，讓它們能夠記住使用者偏好 (`temperature_unit`) 和過去的互動 (`output_key`)。
*   您使用 `before_model_callback` (阻擋特定的輸入關鍵字) 和 `before_tool_callback` (根據城市「巴黎」等參數阻擋工具執行) 實作了關鍵的**安全護欄**。

透過建構這個漸進式天氣機器人團隊，您已獲得了建構複雜、智慧型應用程式所需的核心 ADK 概念的實作經驗。

**主要收穫：**

*   **代理程式與工具：** 定義能力和推理的基本建構區塊。清晰的指令和文件字串至關重要。
*   **Runners 與 Session Services：** 協調代理程式執行和維護對話上下文的引擎和記憶體管理系統。
*   **委派：** 設計多代理程式團隊可以實現專業化、模組化和更好地管理複雜任務。代理程式的 `description` 是自動流程的關鍵。
*   **會話狀態 (`ToolContext`、`output_key`)：** 建立具有上下文感知、個人化和多輪對話代理程式的必要條件。
*   **回呼 (`before_model`、`before_tool`)：** 在關鍵操作 (LLM 呼叫或工具執行) *之前*實作安全、驗證、政策強制執行和動態修改的強大掛鉤。
*   **彈性 (`LiteLlm`)：** ADK 讓您能夠為工作選擇最佳的 LLM，平衡效能、成本和功能。

**下一步該去哪裡？**

您的天氣機器人團隊是一個很好的起點。以下是一些進一步探索 ADK 和增強您的應用程式的想法：

1.  **真實天氣 API：** 將您的 `get_weather` 工具中的 `mock_weather_db` 替換為對真實天氣 API (如 OpenWeatherMap、WeatherAPI) 的呼叫。
2.  **更複雜的狀態：** 在會話狀態中儲存更多使用者偏好 (例如，偏好的位置、通知設定) 或對話摘要。
3.  **完善委派：** 實驗不同的根代理程式指令或子代理程式描述，以微調委派邏輯。您可以新增一個「預報」代理程式嗎？
4.  **進階回呼：**
    *   使用 `after_model_callback` 在 LLM 產生回應*之後*可能重新格式化或清理其回應。
    *   使用 `after_tool_callback` 處理或記錄工具傳回的結果。
    *   為代理程式層級的進入/退出邏輯實作 `before_agent_callback` 或 `after_agent_callback`。
5.  **錯誤處理：** 改善代理程式處理工具錯誤或非預期 API 回應的方式。也許在工具內新增重試邏輯。
6.  **持久性會話儲存：** 探索 `InMemorySessionService` 的替代方案，以持久地儲存會話狀態 (例如，使用像 Firestore 或 Cloud SQL 這樣的資料庫——需要自訂實作或未來的 ADK 整合)。
7.  **串流 UI：** 將您的代理程式團隊與 Web 框架 (如 FastAPI，如 ADK 串流快速入門所示) 整合，以建立即時聊天介面。

代理程式開發套件為建構複雜的 LLM 驅動應用程式提供了穩固的基礎。透過掌握本教學中涵蓋的概念——工具、狀態、委派和回呼——您已準備好應對日益複雜的代理程式系統。

祝您建構愉快！
