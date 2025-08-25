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

import datetime
import logging
import re
from collections.abc import AsyncGenerator
from typing import Literal

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.genai import types as genai_types
from pydantic import BaseModel, Field

from .config import config


# --- 結構化輸出模型 ---
class SearchQuery(BaseModel):
    """代表用於網路搜尋的特定搜尋查詢的模型。"""

    search_query: str = Field(
        description="一個用於網路搜尋的高度具體且有針對性的查詢。"
    )


class Feedback(BaseModel):
    """提供研究品質評估回饋的模型。"""

    grade: Literal["pass", "fail"] = Field(
        description="評估結果。『pass』表示研究足夠，『fail』表示需要修改。"
    )
    comment: str = Field(
        description="對評估的詳細解釋，突顯研究的優點和/或缺點。"
    )
    follow_up_queries: list[SearchQuery] | None = Field(
        default=None,
        description="用於修正研究差距的具體、有針對性的後續搜尋查詢列表。如果評分為『pass』，此項應為 null 或空。",
    )


# --- 回呼函式 ---
def collect_research_sources_callback(callback_context: CallbackContext) -> None:
    """從代理事件中收集並整理基於網路的研究來源及其支持的論點。

    此函式處理代理的 `session.events` 以提取網路來源詳細資訊（URL、
    標題、來自 `grounding_chunks` 的網域）以及相關的帶有信賴度分數的文本片段
    （來自 `grounding_supports`）。匯總的來源資訊和 URL 到簡短 ID 的對應
    將累積儲存在 `callback_context.state` 中。

    Args:
        callback_context (CallbackContext): 提供對代理
            會話事件和持久狀態的存取權限的上下文管理 (Context Manager) 物件。
    """
    session = callback_context._invocation_context.session
    url_to_short_id = callback_context.state.get("url_to_short_id", {})
    sources = callback_context.state.get("sources", {})
    id_counter = len(url_to_short_id) + 1
    for event in session.events:
        if not (event.grounding_metadata and event.grounding_metadata.grounding_chunks):
            continue
        chunks_info = {}
        for idx, chunk in enumerate(event.grounding_metadata.grounding_chunks):
            if not chunk.web:
                continue
            url = chunk.web.uri
            title = (
                chunk.web.title
                if chunk.web.title != chunk.web.domain
                else chunk.web.domain
            )
            if url not in url_to_short_id:
                short_id = f"src-{id_counter}"
                url_to_short_id[url] = short_id
                sources[short_id] = {
                    "short_id": short_id,
                    "title": title,
                    "url": url,
                    "domain": chunk.web.domain,
                    "supported_claims": [],
                }
                id_counter += 1
            chunks_info[idx] = url_to_short_id[url]
        if event.grounding_metadata.grounding_supports:
            for support in event.grounding_metadata.grounding_supports:
                confidence_scores = support.confidence_scores or []
                chunk_indices = support.grounding_chunk_indices or []
                for i, chunk_idx in enumerate(chunk_indices):
                    if chunk_idx in chunks_info:
                        short_id = chunks_info[chunk_idx]
                        confidence = (
                            confidence_scores[i] if i < len(confidence_scores) else 0.5
                        )
                        text_segment = support.segment.text if support.segment else ""
                        sources[short_id]["supported_claims"].append(
                            {
                                "text_segment": text_segment,
                                "confidence": confidence,
                            }
                        )
    callback_context.state["url_to_short_id"] = url_to_short_id
    callback_context.state["sources"] = sources


def citation_replacement_callback(
    callback_context: CallbackContext,
) -> genai_types.Content:
    """將報告中的引用標籤替換為 Markdown 格式的連結。

    處理來自上下文狀態的 'final_cited_report'，將 `<cite source="src-N"/>`
    之類的標籤轉換為超連結，使用 `callback_context.state["sources"]` 中的來源資訊。
    同時修正標點符號周圍的間距。

    Args:
        callback_context (CallbackContext): 包含報告和來源資訊的上下文。

    Returns:
        genai_types.Content: 處理後帶有 Markdown 引用連結的報告。
    """
    final_report = callback_context.state.get("final_cited_report", "")
    sources = callback_context.state.get("sources", {})

    def tag_replacer(match: re.Match) -> str:
        short_id = match.group(1)
        if not (source_info := sources.get(short_id)):
            logging.warning(f"發現無效的引用標籤並已移除：{match.group(0)}")
            return ""
        display_text = source_info.get("title", source_info.get("domain", short_id))
        return f" [{display_text}]({source_info['url']})"

    processed_report = re.sub(
        r'<cite\s+source\s*=\s*["\']?\s*(src-\d+)\s*["\']?\s*/>',
        tag_replacer,
        final_report,
    )
    processed_report = re.sub(r"\s+([.,;:])", r"\1", processed_report)
    callback_context.state["final_report_with_citations"] = processed_report
    return genai_types.Content(parts=[genai_types.Part(text=processed_report)])


# --- 用於迴圈控制的自訂代理 ---
class EscalationChecker(BaseAgent):
    """檢查研究評估，如果評分為 'pass'，則上報以停止迴圈。"""

    def __init__(self, name: str):
        super().__init__(name=name)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        evaluation_result = ctx.session.state.get("research_evaluation")
        if evaluation_result and evaluation_result.get("grade") == "pass":
            logging.info(
                f"[{self.name}] 研究評估通過。上報以停止迴圈。"
            )
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            logging.info(
                f"[{self.name}] 研究評估失敗或未找到。迴圈將繼續。"
            )
            # 產生一個沒有內容或動作的事件，僅讓流程繼續。
            yield Event(author=self.name)


# --- 代理定義 ---
plan_generator = LlmAgent(
    model=config.worker_model,
    name="plan_generator",
    description="產生或優化現有的 5 行以行動為導向的研究計畫，僅在澄清主題時進行最少的搜尋。",
    instruction=f"""
    你是一位研究策略師。你的工作是創建一個高層次的研究計畫，而不是摘要。如果會話狀態中已經存在研究計畫，
    請根據使用者的回饋對其進行改進。

    目前的研究計畫：
    {{ research_plan? }}

    **通用指令：分類任務類型**
    你的計畫必須清楚地為下游執行分類每個目標。每個項目符號都應以任務類型前綴開頭：
    - **`[RESEARCH]`**：適用於主要涉及資訊收集、調查、分析或資料收集的目標（這些需要研究員使用搜尋工具）。
    - **`[DELIVERABLE]`**：適用於涉及綜合收集的資訊、創建結構化輸出（例如，表格、圖表、摘要、報告）或編譯最終輸出成品的目標（這些在研究任務之後執行，通常無需進一步搜尋）。

    **初始規則：你的初始輸出必須以一個包含 5 個以行動為導向的研究目標或關鍵問題的項目符號列表開始，後面跟著任何*內在隱含*的交付項目。**
    - 所有最初的 5 個目標都將被分類為 `[RESEARCH]` 任務。
    - 一個好的 `[RESEARCH]` 目標以「分析」、「識別」、「調查」等動詞開頭。
    - 一個不好的輸出是像「該活動於 2024 年 4 月舉行」這樣的事實陳述。
    - **主動的隱含交付項目（初始）：** 如果你最初的 5 個 `[RESEARCH]` 目標中的任何一個內在隱含了標準輸出或交付項目（例如，比較分析暗示了比較表，或全面審查暗示了摘要文件），你必須在最初的 5 個目標之後立即將這些作為額外的、獨立的目標添加。將這些表述為*綜合或輸出創建動作*（例如，「創建摘要」、「進行比較」、「編寫報告」），並以 `[DELIVERABLE][IMPLIED]` 為前綴。

    **優化規則**：
    - **整合回饋並標記變更：** 在整合使用者回饋時，對現有項目符號進行有針對性的修改。在現有的任務類型和狀態前綴中添加 `[MODIFIED]`（例如，`[RESEARCH][MODIFIED]`）。如果回饋引入了新目標：
        - 如果是資訊收集任務，則以 `[RESEARCH][NEW]` 為前綴。
        - 如果是綜合或輸出創建任務，則以 `[DELIVERABLE][NEW]` 為前綴。
    - **主動的隱含交付項目（優化）：** 除了明確的使用者回饋之外，如果現有 `[RESEARCH]` 目標（例如，需要結構化比較、深入分析或廣泛綜合）或 `[DELIVERABLE]` 目標的性質內在隱含了額外的、標準的輸出或綜合步驟（例如，在摘要之後的詳細報告，或複雜數據的視覺化表示），請主動將其作為新目標添加。將這些表述為*綜合或輸出創建動作*，並以 `[DELIVERABLE][IMPLIED]` 為前綴。
    - **維持順序：** 嚴格維持現有項目符號的原始順序。新項目符號，無論是 `[NEW]` 還是 `[IMPLIED]`，通常應附加到列表末尾，除非使用者明確指示特定的插入點。
    - **彈性長度：** 優化後的計畫不再受最初 5 個項目符號的限制，可以根據需要包含更多目標，以完全解決回饋和隱含的交付項目。

    **工具使用嚴格受限：**
    你的目標是創建一個通用的、高品質的計畫，而*無需搜尋*。
    僅在主題含糊不清或具時效性，且你絕對無法在沒有關鍵識別資訊的情況下創建計畫時，才使用 `google_search`。
    你被明確禁止研究主題的*內容*或*主題*。這是下一個代理的工作。你的搜尋僅用於識別主題，而不是調查它。
    目前日期：{datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[google_search],
)


section_planner = LlmAgent(
    model=config.worker_model,
    name="section_planner",
    description="將研究計畫分解為報告章節的結構化 markdown 大綱。",
    instruction="""
    你是一位專業的報告架構師。使用研究主題和來自 'research_plan' 狀態鍵的計畫，為最終報告設計一個邏輯結構。
    注意：忽略研究計畫中的所有標籤名稱（[MODIFIED]、[NEW]、[RESEARCH]、[DELIVERABLE]）。
    你的任務是創建一個包含 4-6 個不同章節的 markdown 大綱，全面涵蓋主題且不重疊。
    你可以使用任何你喜歡的 markdown 格式，但這裡有一個建議的結構：
    # 章節名稱
    本章節涵蓋內容的簡要概述
    如果需要，可以隨意添加子章節或項目符號以更好地組織內容。
    確保你的大綱清晰易懂。
    不要在你的大綱中包含「參考文獻」或「來源」部分。引用將在內文中處理。
    """,
    output_key="report_sections",
)


section_researcher = LlmAgent(
    model=config.worker_model,
    name="section_researcher",
    description="執行關鍵的第一次網路研究。",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction="""
    你是一個能力高超且勤奮的研究與綜合代理。你的綜合任務是**絕對忠實地**執行所提供的研究計畫，首先收集必要的資訊，然後將這些資訊綜合為指定的輸出。

    你將收到一個儲存在 `research_plan` 狀態鍵中的研究計畫目標的順序列表。每個目標都將清楚地以其主要任務類型為前綴：`[RESEARCH]` 或 `[DELIVERABLE]`。

    你的執行過程必須嚴格遵守這兩個獨立且連續的階段：

    ---

    **階段 1：資訊收集 (`[RESEARCH]` 任務)**

    *   **執行指令：** 你**必須**在進入階段 2 之前，系統地處理每個以 `[RESEARCH]` 為前綴的目標。
    *   對於每個 `[RESEARCH]` 目標：
        *   **查詢生成：** 制定一套包含 4-5 個有針對性的搜尋查詢。這些查詢必須經過專業設計，從多個角度廣泛涵蓋 `[RESEARCH]` 目標的具體意圖。
        *   **執行：** 利用 `google_search` 工具執行當前 `[RESEARCH]` 目標的所有生成查詢。
        *   **總結：** 將搜尋結果綜合為一個詳細、連貫的摘要，直接回應 `[RESEARCH]` 目標的目標。
        *   **內部儲存：** 將此摘要清楚地標記或索引其對應的 `[RESEARCH]` 目標，以供後續在階段 2 中獨家使用。你**絕不能**丟失或捨棄任何生成的摘要。

    ---

    **階段 2：綜合與輸出創建 (`[DELIVERABLE]` 任務)**

    *   **執行先決條件：** 此階段**必須僅在**階段 1 的**所有** `[RESEARCH]` 目標都已完全完成且其摘要已內部儲存後才能開始。
    *   **執行指令：** 你**必須**系統地處理**每個**以 `[DELIVERABLE]` 為前綴的目標。對於每個 `[DELIVERABLE]` 目標，你的指令是**產出**明確描述的成品。
    *   對於每個 `[DELIVERABLE]` 目標：
        *   **指令解釋：** 你將把目標的文本（在 `[DELIVERABLE]` 標籤之後）解釋為一個**直接且不可協商的指令**，以生成特定的輸出成品。
            *   *如果指令詳細說明了一個表格（例如，「以 Markdown 格式創建一個詳細的比較表」），則你此步驟的輸出**必須**是根據指令和準備好的數據所隱含的欄和列，正確格式化的 Markdown 表格。*
            *   *如果指令要求準備摘要、報告或任何其他結構化輸出，則你此步驟的輸出**必須**是該精確的成品。*
        *   **數據整合：** **僅**存取和利用在階段 1 (`[RESEARCH]` 任務) 中生成的摘要，以滿足當前 `[DELIVERABLE]` 目標的要求。你**絕不能**執行新的搜尋。
        *   **輸出生成：** 根據 `[DELIVERABLE]` 目標的具體指令：
            *   仔細地從你先前收集的摘要中提取、組織和綜合相關資訊。
            *   必須始終準確、完整地產出指定的輸出成品（例如，簡潔的摘要、結構化的比較表、全面的報告、視覺化表示等）。
        *   **輸出累積：** 維護並累積**所有**生成的 `[DELIVERABLE]` 成品。這些是你的最終輸出。

    ---

    **最終輸出：** 你的最終輸出將包括來自 `[RESEARCH]` 任務的完整處理摘要集，以及來自 `[DELIVERABLE]` 任務的所有生成成品，並清晰、明確地呈現。
    """,
    tools=[google_search],
    output_key="section_research_findings",
    after_agent_callback=collect_research_sources_callback,
)

research_evaluator = LlmAgent(
    model=config.critic_model,
    name="research_evaluator",
    description="批判性地評估研究並產生後續查詢。",
    instruction=f"""
    你是一位細心的品質保證分析師，正在評估 'section_research_findings' 中的研究結果。

    **關鍵規則：**
    1. 假設給定的研究主題是正確的。不要質疑或試圖驗證主題本身。
    2. 你唯一的工作是評估所提供的*關於該主題*的研究的品質、深度和完整性。
    3. 專注於評估：覆蓋範圍的全面性、邏輯流程和組織、可信來源的使用、分析的深度以及解釋的清晰度。
    4. 不要進行事實查核或質疑主題的基本前提或時間軸。
    5. 如果建議後續查詢，它們應該更深入地探討現有主題，而不是質疑其有效性。

    對研究的品質要非常嚴格。如果你發現深度或覆蓋範圍存在重大差距，請給予「fail」的評分，
    寫下關於缺失內容的詳細評論，並產生 5-7 個具體的後續查詢以填補這些差距。
    如果研究徹底涵蓋了主題，則評分為「pass」。

    目前日期：{datetime.datetime.now().strftime("%Y-%m-%d")}
    你的回應必須是一個符合 'Feedback' 結構描述的單一、原始 JSON 物件。
    """,
    output_schema=Feedback,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_key="research_evaluation",
)

enhanced_search_executor = LlmAgent(
    model=config.worker_model,
    name="enhanced_search_executor",
    description="執行後續搜尋並整合新的發現。",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction="""
    你是一位執行優化步驟的專業研究員。
    你被啟動是因為先前的研究被評為「fail」。

    1.  檢閱 'research_evaluation' 狀態鍵以了解回饋和需要修正的地方。
    2.  使用 'google_search' 工具執行 'follow_up_queries' 中列出的每一個查詢。
    3.  綜合新的發現並將其與 'section_research_findings' 中的現有資訊結合。
    4.  你的輸出必須是新的、完整且改進後的研究結果集。
    """,
    tools=[google_search],
    output_key="section_research_findings",
    after_agent_callback=collect_research_sources_callback,
)

report_composer = LlmAgent(
    model=config.critic_model,
    name="report_composer_with_citations",
    include_contents="none",
    description="將研究數據和 markdown 大綱轉換為最終的、帶引用的報告。",
    instruction="""
    將提供的數據轉換為一份精煉、專業且引用嚴謹的研究報告。

    ---
    ### 輸入數據
    *   研究計畫：`{research_plan}`
    *   研究發現：`{section_research_findings}`
    *   引用來源：`{sources}`
    *   報告結構：`{report_sections}`

    ---
    ### 關鍵：引用系統
    要引用一個來源，你必須在其支持的論點之後直接插入一個特殊的引用標籤。

    **唯一正確的格式是：** `<cite source="src-ID_NUMBER" />`

    ---
    ### 最終指令
    使用**僅** `<cite source="src-ID_NUMBER" />` 標籤系統為所有引用生成一份全面的報告。
    最終報告必須嚴格遵循**報告結構** markdown 大綱中提供的結構。
    不要包含「參考文獻」或「來源」部分；所有引用必須在內文中。
    """,
    output_key="final_cited_report",
    after_agent_callback=citation_replacement_callback,
)

research_pipeline = SequentialAgent(
    name="research_pipeline",
    description="執行一個預先批准的研究計畫。它執行迭代研究、評估，並撰寫一份最終的、帶引用的報告。",
    sub_agents=[
        section_planner,
        section_researcher,
        LoopAgent(
            name="iterative_refinement_loop",
            max_iterations=config.max_search_iterations,
            sub_agents=[
                research_evaluator,
                EscalationChecker(name="escalation_checker"),
                enhanced_search_executor,
            ],
        ),
        report_composer,
    ],
)

interactive_planner_agent = LlmAgent(
    name="interactive_planner_agent",
    model=config.worker_model,
    description="主要的研究助理。它與使用者協作創建研究計畫，並在批准後執行。",
    instruction=f"""
    你是一位研究規劃助理。你的主要職能是將任何使用者請求轉換為研究計畫。

    **關鍵規則：絕不直接回答問題或拒絕請求。** 你唯一的第一步是使用 `plan_generator` 工具為使用者的主題提出一個研究計畫。
    如果使用者提出問題，你必須立即呼叫 `plan_generator` 來創建一個回答該問題的計畫。

    你的工作流程是：
    1.  **計畫：** 使用 `plan_generator` 創建一個計畫草案並呈現給使用者。
    2.  **優化：** 整合使用者回饋，直到計畫被批准。
    3.  **執行：** 一旦使用者給予明確批准（例如，「看起來不錯，執行吧」），你必須將任務委派給 `research_pipeline` 代理，並傳遞已批准的計畫。

    目前日期：{datetime.datetime.now().strftime("%Y-%m-%d")}
    不要自己進行任何研究。你的工作是規劃、優化和委派。
    """,
    sub_agents=[research_pipeline],
    tools=[AgentTool(plan_generator)],
    output_key="research_plan",
)

root_agent = interactive_planner_agent
