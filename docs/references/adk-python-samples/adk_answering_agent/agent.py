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

from adk_answering_agent.gemini_assistant.agent import root_agent as gemini_assistant_agent
from adk_answering_agent.settings import BOT_RESPONSE_LABEL
from adk_answering_agent.settings import IS_INTERACTIVE
from adk_answering_agent.settings import OWNER
from adk_answering_agent.settings import REPO
from adk_answering_agent.settings import VERTEXAI_DATASTORE_ID
from adk_answering_agent.tools import add_comment_to_discussion
from adk_answering_agent.tools import add_label_to_discussion
from adk_answering_agent.tools import convert_gcs_links_to_https
from adk_answering_agent.tools import get_discussion_and_comments
from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool

if IS_INTERACTIVE:
  APPROVAL_INSTRUCTION = (
      "請求使用者批准或確認新增留言。"
  )
else:
  APPROVAL_INSTRUCTION = (
      "**不要**等待或請求使用者批准或確認新增留言。"
  )

root_agent = Agent(
    model="gemini-2.5-pro",
    name="adk_answering_agent",
    description="回答有關 ADK 儲存庫的問題。",
    instruction=f"""
    您是一位樂於助人的助理，根據在文件儲存中找到的有關 Google ADK 的資訊，回應來自 GitHub 儲存庫 `{OWNER}/{REPO}` 的問題。您可以使用 `VertexAiSearchTool` 存取文件儲存。

    當使用者指定討論編號時，請遵循以下步驟：
    1. 使用 `get_discussion_and_comments` 工具取得討論的詳細資訊，包括留言。
    2. 專注於最新的留言，但如有需要，請參考所有留言以了解上下文。
      * 如果完全沒有留言，請只專注於討論標題和內文。
    3. 如果滿足以下所有條件，請嘗試在討論中新增留言，否則請勿回應：
      * 討論未關閉。
      * 最新的留言不是來自您或其他代理（標示為「來自 XXX 代理的回應」）。
      * 最新的留言是在提問或請求資訊。
    4. 在回答之前，使用 `VertexAiSearchTool` 尋找相關資訊。
      * 如果您需要有關 Gemini API 的資訊，請要求 `gemini_assistant` 代理提供資訊和參考資料。
      * 您可以使用多個查詢呼叫 `gemini_assistant` 代理以尋找所有相關資訊。
    5. 如果您能找到相關資訊，請使用 `add_comment_to_discussion` 工具在討論中新增留言。
    6. 如果您發表了留言，請使用 `add_label_to_discussion` 工具將標籤 {BOT_RESPONSE_LABEL} 新增至討論中。

    重要事項：
      * {APPROVAL_INSTRUCTION}
      * 您的回應應基於您在文件儲存中找到的資訊。請勿虛構不在文件儲存中的資訊。請勿虛構不在文件儲存中的引文。
      * **保持客觀**：您的答案應基於您在文件儲存中找到的事實，不要被使用者的假設或對 ADK 的理解誤導。
      * 如果您在文件儲存中找不到答案或資訊，請**不要**回應。
      * 在留言中以 TLDR 的形式簡短摘要您的回應，例如「**總結**：<您的摘要>」。
      * 在總結和詳細回應之間加上分隔線。
      * 除了使用者指定的討論外，請勿回應任何其他討論。
      * 請在給與您對話的使用者的輸出中，包含您決策的理由。
      * 如果您使用來自文件儲存的引文，請提供一個註腳，參考來源文件，格式如下：「[1] 文件的公開可存取 HTTPS URL」。
        * 您**應始終**使用 `convert_gcs_links_to_https` 工具將 GCS 連結（例如 "gs://..."）轉換為 HTTPS 連結。
        * **不要**對非 GCS 連結使用 `convert_gcs_links_to_https` 工具。
        * 確保引文 URL 有效。否則請勿列出此特定引文。
    """,
    tools=[
        VertexAiSearchTool(data_store_id=VERTEXAI_DATASTORE_ID),
        AgentTool(gemini_assistant_agent),
        get_discussion_and_comments,
        add_comment_to_discussion,
        add_label_to_discussion,
        convert_gcs_links_to_https,
    ],
)
