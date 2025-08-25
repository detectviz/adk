# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent

# agent.py 的一部分 --> 請遵循 https://google.github.io/adk-docs/get-started/quickstart/ 來學習設定

# --- 1. 為每個管線階段定義子代理 ---

# 程式碼編寫器代理
# 取得初始規格（來自使用者查詢）並編寫程式碼。
code_writer_agent = LlmAgent(
    name="CodeWriterAgent",
    model="gemini-2.5-flash",
    # 變更 3：改進的指令
    instruction="""您是 Python 程式碼產生器。
僅根據使用者的要求，編寫符合要求的 Python 程式碼。
僅輸出完整的 Python 程式碼區塊，並用三個反引號 (```python ... ```) 括起來。
請勿在程式碼區塊前後新增任何其他文字。
""",
    description="根據規格編寫初始 Python 程式碼。",
    output_key="generated_code",  # 將輸出儲存在 state['generated_code'] 中
)

# 程式碼審查員代理
# 取得前一個代理產生的程式碼（從狀態讀取）並提供回饋。
code_reviewer_agent = LlmAgent(
    name="CodeReviewerAgent",
    model="gemini-2.5-flash",
    # 變更 3：改進的指令，正確使用狀態金鑰注入
    instruction="""您是專業的 Python 程式碼審查員。
    您的任務是針對提供的程式碼提供建設性的回饋。

    **要審查的程式碼：**
    ```python
    {generated_code}
    ```

**審查標準：**
1.  **正確性：** 程式碼是否如預期般運作？是否存在邏輯錯誤？
2.  **可讀性：** 程式碼是否清晰易懂？是否遵循 PEP 8 樣式指南？
3.  **效率：** 程式碼是否合理有效率？是否有任何明顯的效能瓶頸？
4.  **邊界情況：** 程式碼是否能妥善處理潛在的邊界情況或無效輸入？
5.  **最佳實務：** 程式碼是否遵循常見的 Python 最佳實務？

**輸出：**
以簡潔的項目符號清單提供您的回饋。專注於最重要的改進點。
如果程式碼非常出色且無需變更，只需說明：「未發現重大問題。」
僅輸出審查註解或「未發現重大問題」的說明。
""",
    description="審查程式碼並提供回饋。",
    output_key="review_comments",  # 將輸出儲存在 state['review_comments'] 中
)


# 程式碼重構器代理
# 取得原始程式碼和審查註解（從狀態讀取）並重構程式碼。
code_refactorer_agent = LlmAgent(
    name="CodeRefactorerAgent",
    model="gemini-2.5-flash",
    # 變更 3：改進的指令，正確使用狀態金鑰注入
    instruction="""您是 Python 程式碼重構 AI。
您的目標是根據提供的審查註解改進給定的 Python 程式碼。

  **原始程式碼：**
  ```python
  {generated_code}
  ```

  **審查註解：**
  {review_comments}

**任務：**
仔細應用審查註解中的建議來重構原始程式碼。
如果審查註解指出「未發現重大問題」，則傳回未變更的原始程式碼。
確保最終程式碼是完整、可用，並包含必要的匯入和文件字串。

**輸出：**
僅輸出最終重構的 Python 程式碼區塊，並用三個反引號 (```python ... ```) 括起來。
請勿在程式碼區塊前後新增任何其他文字。
""",
    description="根據審查註解重構程式碼。",
    output_key="refactored_code",  # 將輸出儲存在 state['refactored_code'] 中
)


# --- 2. 建立 SequentialAgent ---
# 此代理透過依序執行子代理來協調管線。
code_pipeline_agent = SequentialAgent(
    name="CodePipelineAgent",
    sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent],
    description=(
        "執行一系列的程式碼編寫、審查和重構。"
    ),
    # 代理將按照提供的順序執行：編寫器 -> 審查員 -> 重構器
)

# 為了與 ADK 工具相容，根代理必須命名為 `root_agent`
root_agent = code_pipeline_agent
