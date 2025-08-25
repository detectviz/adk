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

"""
模式發現協調代理及其子元件。
"""
import os
from typing import AsyncGenerator
from google.adk.agents import (
    Agent,
    BaseAgent,
    LlmAgent,
    ParallelAgent,
    SequentialAgent
)
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.tools import google_search
from google.genai.types import Content, Part
from .prompt import (
    COMPANY_FINDER_PROMPT,
    FORMATTER_PROMPT,
    VALIDATOR_PROMPT,
    SIGNAL_SEARCHER_PROMPT,
    SYNTHESIZER_PROMPT,
)
from .schemas import CompanyFinderOutput, ValidationResult, SignalSearcherOutput

# 公司尋找代理
company_finder_agent = LlmAgent(
    name="CompanyFinderAgent",
    model=os.getenv("GEN_ADVANCED_MODEL", "gemini-1.5-pro"),
    instruction=COMPANY_FINDER_PROMPT,
    tools=[google_search],
    output_key="company_finder_output",
)

# 公司格式化代理
company_formatter_agent = LlmAgent(
    name="CompanyFormatterAgent",
    model=os.getenv("GEN_FAST_MODEL", "gemini-1.5-flash"),
    instruction=FORMATTER_PROMPT,
    output_schema=CompanyFinderOutput,
    output_key="companies_found_structured",
    description="將關於公司的非結構化文本格式化為有效的 JSON 物件。",
)

# 驗證器代理模板
validator_agent_template = LlmAgent(
    name="ValidatorAgent",
    model=os.getenv("GEN_FAST_MODEL", "gemini-1.5-flash"),
    instruction=VALIDATOR_PROMPT,
    output_schema=ValidationResult,
    description="驗證單一公司，確保其為近期在目標市場投資的外國實體。",
)

# 信號搜尋器代理模板（研究員）
signal_searcher_agent_template = LlmAgent(
    name="SignalSearcherAgent",
    model=os.getenv("GEN_ADVANCED_MODEL", "gemini-1.5-pro"),
    instruction=SIGNAL_SEARCHER_PROMPT,
    tools=[google_search],
    output_key="signal_searcher_output", # 儲存非結構化輸出
    description="研究單一經過驗證的公司，以尋找其投資前信號。",
)

# 信號格式化器代理模板（格式化器）
signal_formatter_agent_template = LlmAgent(
    name="SignalFormatterAgent",
    model=os.getenv("GEN_FAST_MODEL", "gemini-1.5-flash"),
    instruction="""將來自信號搜尋器的以下非結構化文本格式化為 `SignalSearcherOutput` JSON 結構。

{unstructured_text}
""",
    output_schema=SignalSearcherOutput,
    output_key="research_findings", # 儲存結構化輸出
)

# 模式綜合代理
pattern_synthesizer_agent = LlmAgent(
    name="PatternSynthesizerAgent",
    model=os.getenv("GEN_ADVANCED_MODEL", "gemini-1.5-pro"),
    instruction=SYNTHESIZER_PROMPT,
    output_key="discovered_patterns",
    description="分析來自多個信號搜尋器的研究，並綜合共同模式。",
)

# 綜合協調代理
class SynthesizerOrchestratorAgent(BaseAgent):
    """
    收集所有並行研究結果，並將其格式化為單一字串，供模式綜合代理使用。
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        all_findings = []
        
        companies_found_structured = ctx.session.state.get("companies_found_structured")
        companies_list = []
        if companies_found_structured:
            companies_list = companies_found_structured.get("companies_found", [])

        if not companies_list:
            ctx.session.state["all_research_findings"] = "沒有找到可供整合的公司。"
            yield Event(author=self.name, content=Content(parts=[Part(text="沒有可供整合的研究結果。")]))
            return
        
        num_companies = len(companies_list)

        for i in range(num_companies):
            validation_result = ctx.session.state.get(f"validation_result_{i}")
            research_findings = ctx.session.state.get(f"research_findings_{i}")

            finding_str = f"--- 公司 {i+1} ---\n"
            if validation_result:
                finding_str += f"驗證：{'有效' if validation_result.get('is_valid') else '無效'}\n"
                finding_str += f"原因：{validation_result.get('reasoning')}\n"
            
            if research_findings:
                # The research_findings object is now a dictionary.
                finding_str += f"研究摘要：{research_findings.get('summary')}\n"
                finding_str += f"來源：{', '.join(research_findings.get('sources', []))}\n"
            
            all_findings.append(finding_str)
        
        # 將整合後的研究結果儲存到新的狀態變數中。
        ctx.session.state["all_research_findings"] = "\n".join(all_findings)
        
        yield Event(author=self.name, content=Content(parts=[Part(text="研究結果已整合。")]))

synthesizer_orchestrator_agent = SynthesizerOrchestratorAgent(name="SynthesizerOrchestrator")

# 研究協調代理（取代驗證與信號研究協調器）
class ResearchOrchestratorAgent(BaseAgent):
    """
    動態地建立並執行一個並行工作流程來驗證和研究公司列表。
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        companies_found_structured = ctx.session.state.get("companies_found_structured")
        if not companies_found_structured:
            yield Event(author=self.name, content=Content(parts=[Part(text="沒有要研究的公司。")]))
            return

        companies_list = companies_found_structured.get("companies_found", [])
        
        research_pipelines = []
        for i, company_data in enumerate(companies_list):
            # 對於每家公司，建立一個簡單的順序流程 (驗證器 -> 搜尋器 -> 格式化器)。
            research_pipeline = SequentialAgent(
                name=f"CompanyResearchPipeline_{i}",
                sub_agents=[
                    LlmAgent(
                        name=f"ValidatorAgent_{i}",
                        instruction=validator_agent_template.instruction.format(
                            company_to_validate=company_data, **ctx.session.state
                        ),
                        model=validator_agent_template.model,
                        output_schema=validator_agent_template.output_schema,
                        output_key=f"validation_result_{i}",
                    ),
                    LlmAgent(
                        name=f"SignalSearcher_{i}",
                        instruction=signal_searcher_agent_template.instruction.format(
                            company_data=company_data, **ctx.session.state
                        ),
                        model=signal_searcher_agent_template.model,
                        tools=signal_searcher_agent_template.tools,
                        output_key=f"signal_searcher_output_{i}",
                    ),
                    LlmAgent(
                        name=f"SignalFormatter_{i}",
                        instruction=signal_formatter_agent_template.instruction.format(
                            unstructured_text=f"{{signal_searcher_output_{i}}}"
                        ),
                        model=signal_formatter_agent_template.model,
                        output_schema=signal_formatter_agent_template.output_schema,
                        output_key=f"research_findings_{i}",
                    ),
                ],
            )
            research_pipelines.append(research_pipeline)
        
        # 建立一個新的臨時 ParallelAgent 來執行所有流程。
        parallel_researcher = ParallelAgent(
            name="DynamicParallelResearcher",
            sub_agents=research_pipelines,
        )

        async for event in parallel_researcher.run_async(ctx):
            yield event

research_orchestrator_agent = ResearchOrchestratorAgent(name="ResearchOrchestrator")

# 主要模式發現代理
pattern_discovery_agent = SequentialAgent(
    name="PatternDiscoveryAgent",
    sub_agents=[
        company_finder_agent,
        company_formatter_agent,
        research_orchestrator_agent,
        synthesizer_orchestrator_agent,
        pattern_synthesizer_agent,
    ],
    description="協調發現投資模式的技術步驟。"
)
