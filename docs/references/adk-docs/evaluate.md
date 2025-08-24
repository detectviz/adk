# 為何要評估代理

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前僅支援 Python。Java 支援計畫中/即將推出。" }

在傳統軟體開發中，單元測試和整合測試提供了程式碼功能符合預期並在變更中保持穩定的信心。這些測試提供了明確的「通過/失敗」信號，指導進一步的開發。然而，大型語言模型 (LLM) 代理引入了一定程度的可變性，使得傳統的測試方法不足以應對。

由於模型的機率性，確定性的「通過/失敗」斷言通常不適用於評估代理性能。相反，我們需要對最終輸出和代理的軌跡（達到解決方案所採取的步驟順序）進行質化評估。這涉及評估代理決策的品質、其推理過程和最終結果。

這似乎需要大量的額外工作來設定，但自動化評估的投資很快就會得到回報。如果您打算超越原型階段，這是一個強烈建議的最佳實踐。

![intro_components.png](../assets/evaluate_agent.png)

## 準備代理評估

在自動化代理評估之前，請定義明確的目標和成功標準：

* **定義成功：** 對於您的代理來說，什麼構成成功的結果？
* **識別關鍵任務：** 您的代理必須完成哪些基本任務？
* **選擇相關指標：** 您將追蹤哪些指標來衡量性能？

這些考量將指導評估情境的建立，並能夠有效監控代理在實際部署中的行為。

## 評估什麼？

為了彌合概念驗證和生產就緒的 AI 代理之間的差距，一個健全且自動化的評估框架至關重要。與評估主要關注最終輸出的生成模型不同，代理評估需要更深入地了解決策過程。代理評估可以分為兩個部分：

1. **評估軌跡和工具使用：** 分析代理為達到解決方案所採取的步驟，包括其選擇的工具、策略及其方法的效率。
2. **評估最終回應：** 評估代理最終輸出的品質、相關性和正確性。

軌跡只是代理在返回給使用者之前所採取的一系列步驟。我們可以將其與我們期望代理採取的步驟列表進行比較。

### 評估軌跡和工具使用

在回應使用者之前，代理通常會執行一系列動作，我們稱之為「軌跡」。它可能會將使用者輸入與會話歷史進行比較以消除術語的歧義，或查詢政策文件、搜尋知識庫或調用 API 來儲存票證。我們稱之為動作的「軌跡」。評估代理的性能需要將其實際軌跡與預期的或理想的軌跡進行比較。這種比較可以揭示代理過程中的錯誤和低效率。預期軌跡代表了基本事實——我們預期代理應該採取的步驟列表。

例如：

```python
# 軌跡評估將比較
expected_steps = ["determine_intent", "use_tool", "review_results", "report_generation"]
actual_steps = ["determine_intent", "use_tool", "review_results", "report_generation"]
```

存在幾種基於基本事實的軌跡評估：

1. **完全匹配：** 需要與理想軌跡完全匹配。
2. **順序匹配：** 需要按正確的順序執行正確的動作，允許額外的動作。
3. **任意順序匹配：** 需要執行正確的動作，順序不限，允許額外的動作。
4. **精確度：** 衡量預測動作的相關性/正確性。
5. **召回率：** 衡量預測中捕獲了多少基本動作。
6. **單一工具使用：** 檢查是否包含特定動作。

選擇正確的評估指標取決於您代理的具體要求和目標。例如，在高風險情境中，完全匹配可能至關重要，而在較靈活的情況下，順序或任意順序匹配可能就足夠了。

## ADK 如何進行評估

ADK 提供了兩種方法來根據預定義的資料集和評估標準評估代理性能。雖然概念上相似，但它們在可處理的資料量上有所不同，這通常決定了每種方法的適用案例。

### 第一種方法：使用測試檔案

這種方法涉及建立單獨的測試檔案，每個檔案代表一個單一、簡單的代理-模型互動（一個會話）。它在代理開發活躍期間最為有效，可作為一種單元測試形式。這些測試旨在快速執行，並應專注於簡單的會話複雜性。每個測試檔案包含一個單一會話，其中可能包含多個輪次。一輪代表使用者和代理之間的一次互動。每一輪包括

- `使用者內容`：使用者發出的查詢。
- `預期的中繼工具使用軌跡`：我們期望代理為了正確回應使用者查詢而進行的工具呼叫。
- `預期的中繼代理回應`：這些是代理（或子代理）在產生最終答案的過程中生成的自然語言回應。這些自然語言回應通常是多代理系統的產物，其中您的根代理依賴子代理來實現目標。這些中繼回應可能對終端使用者不感興趣，但對於系統的開發人員/所有者來說，它們至關重要，因為它們讓您相信代理是透過正確的路徑產生最終回應的。
- `最終回應`：代理的預期最終回應。

您可以為檔案指定任何名稱，例如 `evaluation.test.json`。框架僅檢查 `.test.json` 後綴，檔名的前一部分不受限制。這是一個包含幾個範例的測試檔案：

注意：測試檔案現在由一個正式的 Pydantic 資料模型支援。兩個關鍵的模式檔案是 [Eval Set](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 和 [Eval Case](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py)

*（注意：註解僅用於解釋目的，應移除以使 JSON 有效。）*

```json
# 請注意，為了使本文件更易於閱讀，某些欄位已被移除。
{
  "eval_set_id": "home_automation_agent_light_on_off_set",
  "name": "",
  "description": "這是一個評估集，用於單元測試代理的 `x` 行為",
  "eval_cases": [
    {
      "eval_id": "eval_case_id",
      "conversation": [
        {
          "invocation_id": "b7982664-0ab6-47cc-ab13-326656afdf75", # 調用的唯一識別碼。
          "user_content": { # 使用者在此次調用中提供的內容。這是查詢。
            "parts": [
              {
                "text": "關掉臥室的 device_2。"
              }
            ],
            "role": "user"
          },
          "final_response": { # 作為基準參考的代理最終回應。
            "parts": [
              {
                "text": "我已將 device_2 的狀態設定為關閉。"
              }
            ],
            "role": "model"
          },
          "intermediate_data": {
            "tool_uses": [ # 按時間順序排列的工具使用軌跡。
              {
                "args": {
                  "location": "Bedroom",
                  "device_id": "device_2",
                  "status": "OFF"
                },
                "name": "set_device_info"
              }
            ],
            "intermediate_responses": [] # 任何中繼子代理回應。
          },
        }
      ],
      "session_input": { # 初始會話輸入。
        "app_name": "home_automation_agent",
        "user_id": "test_user",
        "state": {}
      },
    }
  ],
}
```

測試檔案可以組織成資料夾。可選地，資料夾還可以包含一個 `test_config.json` 檔案，用於指定評估標準。

#### 如何遷移不受 Pydantic 模式支援的測試檔案？

注意：如果您的測試檔案不符合 [EvalSet](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 模式檔案，則本節與您相關。

請使用 `AgentEvaluator.migrate_eval_data_to_new_schema` 將您現有的 `*.test.json` 檔案遷移到 Pydantic 支援的模式。

該實用程式會接收您目前的測試資料檔案和一個可選的初始會話檔案，並產生一個以新格式序列化資料的單一輸出 json 檔案。鑑於新模式更具凝聚力，舊的測試資料檔案和初始會話檔案都可以忽略（或移除）。

### 第二種方法：使用 Evalset 檔案

evalset 方法利用一個名為「evalset」的專用資料集來評估代理-模型互動。與測試檔案類似，evalset 包含範例互動。然而，一個 evalset 可以包含多個、可能很長的會話，使其非常適合模擬複雜的多輪對話。由於其能夠表示複雜會話，evalset 非常適合整合測試。由於其更廣泛的性質，這些測試通常比單元測試執行得更少。

一個 evalset 檔案包含多個「evals」，每個 eval 代表一個不同的會話。每個 eval 由一個或多個「輪次」組成，其中包括使用者查詢、預期的工具使用、預期的中繼代理回應和一個參考回應。這些欄位的含義與測試檔案方法中的相同。每個 eval 由一個唯一的名稱標識。此外，每個 eval 都包含一個關聯的初始會話狀態。

手動建立 evalset 可能很複雜，因此提供了 UI 工具來幫助捕獲相關會話並輕鬆地將其轉換為 evalset 中的 evals。請參閱下文，了解有關使用 Web UI 進行評估的更多資訊。這是一個包含兩個會話的範例 evalset。

注意：eval set 檔案現在由一個正式的 Pydantic 資料模型支援。兩個關鍵的模式檔案是 [Eval Set](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 和 [Eval Case](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py)

*（注意：註解僅用於解釋目的，應移除以使 JSON 有效。）*

```json
# 請注意，為了使本文件更易於閱讀，某些欄位已被移除。
{
  "eval_set_id": "eval_set_example_with_multiple_sessions",
  "name": "包含多個會話的評估集",
  "description": "此評估集是一個範例，顯示一個評估集可以有多個會話。",
  "eval_cases": [
    {
      "eval_id": "session_01",
      "conversation": [
        {
          "invocation_id": "e-0067f6c4-ac27-4f24-81d7-3ab994c28768",
          "user_content": {
            "parts": [
              {
                "text": "你能做什麼？"
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {

                "text": "我可以擲不同大小的骰子，並檢查數字是否為質數。"
              }
            ],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          },
        },
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user",
        "state": {}
      },
    },
    {
      "eval_id": "session_02",
      "conversation": [
        {
          "invocation_id": "e-92d34c6d-0a1b-452a-ba90-33af2838647a",
          "user_content": {
            "parts": [
              {
                "text": "擲一個 19 面的骰子"
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {
                "text": "我擲出了 17。"
              }
            ],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          },
        },
        {
          "invocation_id": "e-bf8549a1-2a61-4ecc-a4ee-4efbbf25a8ea",
          "user_content": {
            "parts": [
              {
                "text": "擲一個 10 面的骰子兩次，然後檢查 9 是否為質數"
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {
                "text": "我從骰子擲出了 4 和 7，而 9 不是質數。\n"
              }
            ],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "id": "adk-1a3f5a01-1782-4530-949f-07cf53fc6f05",
                "args": {
                  "sides": 10
                },
                "name": "roll_die"
              },
              {
                "id": "adk-52fc3269-caaf-41c3-833d-511e454c7058",
                "args": {
                  "sides": 10
                },
                "name": "roll_die"
              },
              {
                "id": "adk-5274768e-9ec5-4915-b6cf-f5d7f0387056",
                "args": {
                  "nums": [
                    9
                  ]
                },
                "name": "check_prime"
              }
            ],
            "intermediate_responses": [
              [
                "data_processing_agent",
                [
                  {
                    "text": "我已經擲了兩次 10 面的骰子。第一次擲出 5，第二次擲出 3。\n"
                  }
                ]
              ]
            ]
          },
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user",
        "state": {}
      },
    }
  ],
}
```

#### 如何遷移不受 Pydantic 模式支援的 eval set 檔案？

注意：如果您的 eval set 檔案不符合 [EvalSet](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 模式檔案，則本節與您相關。

根據誰在維護 eval set 資料，有兩種途徑：

1.  **由 ADK UI 維護的 Eval set 資料** 如果您使用 ADK UI 來維護您的 Eval set 資料，則您*無需採取任何行動*。

2.  **手動開發和維護並在 ADK eval CLI 中使用的 Eval set 資料** 遷移工具正在開發中，在此之前，ADK eval CLI 指令將繼續支援舊格式的資料。

### 評估標準

評估標準定義了如何根據 evalset 衡量代理的性能。支援以下指標：

* `tool_trajectory_avg_score`：此指標將代理在評估期間的實際工具使用情況與 `expected_tool_use` 欄位中定義的預期工具使用情況進行比較。每個匹配的工具使用步驟得分為 1，不匹配則得分為 0。最終分數是這些匹配的平均值，代表工具使用軌跡的準確性。
* `response_match_score`：此指標將代理的最終自然語言回應與儲存在 `reference` 欄位中的預期最終回應進行比較。我們使用 [ROUGE](https://en.wikipedia.org/wiki/ROUGE_\(metric\)) 指標來計算兩個回應之間的相似性。

如果未提供評估標準，則使用以下預設設定：

* `tool_trajectory_avg_score`：預設為 1.0，要求工具使用軌跡 100% 匹配。
* `response_match_score`：預設為 0.8，允許代理的自然語言回應有少量誤差。

這是一個 `test_config.json` 檔案的範例，指定了自訂評估標準：

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.8
  }
}
```

## 如何使用 ADK 執行評估

作為開發人員，您可以使用 ADK 透過以下方式評估您的代理：

1. **網頁介面 (**`adk web`**):** 透過網頁介面互動式地評估代理。
2. **程式化 (**`pytest`**):** 使用 `pytest` 和測試檔案將評估整合到您的測試流程中。
3. **命令列介面 (**`adk eval`**):** 直接從命令列對現有的評估集檔案執行評估。

### 1\. `adk web` \- 透過 Web UI 執行評估

Web UI 提供了一種互動式的方式來評估代理、產生評估資料集並詳細檢查代理行為。

#### 步驟 1：建立並儲存測試案例

1. 執行 `adk web <path_to_your_agents_folder>` 來啟動網頁伺服器。
2. 在網頁介面中，選擇一個代理並與其互動以建立一個會話。
3. 導覽至介面右側的 **Eval** 分頁。
4. 建立一個新的 eval set 或選擇一個現有的。
5. 按一下 **"Add current session"** 將對話儲存為一個新的評估案例。

#### 步驟 2：檢視和編輯您的測試案例

儲存案例後，您可以按一下列表中的 ID 來檢查它。若要進行變更，請按一下 **Edit current eval case** 圖示（鉛筆）。此互動式檢視可讓您：

* **修改** 代理的文字回應以微調測試情境。
* 從對話中**刪除**個別的代理訊息。
* 如果不再需要，**刪除**整個評估案例。

![adk-eval-case.gif](../assets/adk-eval-case.gif)

#### 步驟 3：使用自訂指標執行評估

1. 從您的 evalset 中選擇一個或多個測試案例。
2. 按一下 **Run Evaluation**。將會出現一個 **EVALUATION METRIC** 對話方塊。
3. 在對話方塊中，使用滑桿設定以下閾值：
    * **Tool trajectory avg score**
    * **Response match score**
4. 按一下 **Start** 以使用您的自訂標準執行評估。評估歷史記錄將記錄每次執行的指標。

![adk-eval-config.gif](../assets/adk-eval-config.gif)

#### 步驟 4：分析結果

執行完成後，您可以分析結果：

* **分析執行失敗**：按一下任何 **Pass** 或 **Fail** 結果。對於失敗，您可以將滑鼠懸停在 `Fail` 標籤上，以並排比較 **實際 vs. 預期輸出** 以及導致失敗的分數。

### 使用追蹤檢視進行偵錯

ADK Web UI 包含一個強大的 **Trace** 分頁，用於偵錯代理行為。此功能適用於任何代理會話，不僅僅是在評估期間。

**Trace** 分頁提供了一種詳細且互動式的方式來檢查代理的執行流程。追蹤會按使用者訊息自動分組，便於追蹤事件鏈。

每個追蹤列都是互動式的：

* **懸停**在追蹤列上會反白顯示聊天視窗中的相應訊息。
* **按一下**追蹤列會開啟一個詳細的檢查面板，其中有四個分頁：
    * **Event**：原始事件資料。
    * **Request**：傳送給模型的請求。
    * **Response**：從模型收到的回應。
    * **Graph**：工具呼叫和代理邏輯流程的視覺化表示。

![adk-trace1.gif](../assets/adk-trace1.gif)
![adk-trace2.gif](../assets/adk-trace2.gif)

追蹤檢視中的藍色列表示從該互動中產生了一個事件。按一下這些藍色列將開啟底部的事件詳細資訊面板，提供對代理執行流程的更深入見解。

### 2\. `pytest` \- 程式化執行測試

您還可以使用 **`pytest`** 來執行測試檔案，作為整合測試的一部分。

#### 範例指令

```shell
pytest tests/integration/
```

#### 範例測試程式碼

這是一個 `pytest` 測試案例的範例，它執行一個單一的測試檔案：

```py
from google.adk.evaluation.agent_evaluator import AgentEvaluator
import pytest

@pytest.mark.asyncio
async def test_with_single_test_file():
    """透過會話檔案測試代理的基本能力。"""
    await AgentEvaluator.evaluate(
        agent_module="home_automation_agent",
        eval_dataset_file_path_or_dir="tests/integration/fixture/home_automation_agent/simple_test.test.json",
    )
```

這種方法可讓您將代理評估整合到您的 CI/CD 流程或更大的測試套件中。如果您想為您的測試指定初始會話狀態，您可以將會話詳細資訊儲存在一個檔案中，並將其傳遞給 `AgentEvaluator.evaluate` 方法。

### 3\. `adk eval` \- 透過 CLI 執行評估

您也可以透過命令列介面 (CLI) 執行 eval set 檔案的評估。這會執行與 UI 上相同的評估，但有助於自動化，即您可以將此指令作為常規建置產生和驗證過程的一部分。

指令如下：

```shell
adk eval \
    <AGENT_MODULE_FILE_PATH> \
    <EVAL_SET_FILE_PATH> \
    [--config_file_path=<PATH_TO_TEST_JSON_CONFIG_FILE>] \
    [--print_detailed_results]
```

例如：

```shell
adk eval \
    samples_for_testing/hello_world \
    samples_for_testing/hello_world/hello_world_eval_set_001.evalset.json
```

以下是每個命令列引數的詳細資訊：

* `AGENT_MODULE_FILE_PATH`：包含名為「agent」的模組的 `__init__.py` 檔案的路徑。「agent」模組包含一個 `root_agent`。
* `EVAL_SET_FILE_PATH`：評估檔案的路徑。您可以指定一個或多個 eval set 檔案路徑。對於每個檔案，預設會執行所有 evals。如果您只想從一個 eval set 中執行特定的 evals，請先建立一個以逗號分隔的 eval 名稱列表，然後將其作為後綴添加到 eval set 檔名中，並用冒號 `:` 分隔。
* 例如：`sample_eval_set_file.json:eval_1,eval_2,eval_3`
  `這將只從 sample_eval_set_file.json 中執行 eval_1、eval_2 和 eval_3`
* `CONFIG_FILE_PATH`：設定檔的路徑。
* `PRINT_DETAILED_RESULTS`：在主控台上列印詳細結果。
