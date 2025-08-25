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
潛在客戶開發協調代理及其子元件。
"""

import os
from typing import AsyncGenerator
from google.adk.agents import (
    BaseAgent,
    LlmAgent,
    ParallelAgent,
    SequentialAgent,
)
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.tools import google_search
from google.genai.types import Content, Part
from .prompt import (
    LEAD_FINDER_PROMPT,
    LEAD_SIGNAL_ANALYZER_PROMPT,
    REPORT_COMPILER_PROMPT,
)
from .schemas import LeadFinderOutput, LeadSignalAnalyzerOutput
from ..pattern_discovery.agent import validator_agent_template # 重用驗證器

# 潛在客戶尋找代理
lead_finder_agent = LlmAgent(
    name="LeadFinderAgent",
    model=os.getenv("GEN_ADVANCED_MODEL", "gemini-1.5-pro"),
    instruction=LEAD_FINDER_PROMPT,
    tools=[google_search],
    output_key="lead_finder_output",
)

# 潛在客戶格式化代理（類似於公司格式化代理）
lead_formatter_agent = LlmAgent(
    name="LeadFormatterAgent",
    model=os.getenv("GEN_FAST_MODEL", "gemini-1.5-flash"),
    instruction="將來自潛在客戶尋找器的非結構化文本格式化為 `LeadFinderOutput` JSON 結構。",
    output_schema=LeadFinderOutput,
    output_key="leads_found_structured",
)

# 潛在客戶信號分析器代理模板（研究員）
lead_signal_analyzer_template = LlmAgent(
    name="LeadSignalAnalyzerAgent",
    model=os.getenv("GEN_ADVANCED_MODEL", "gemini-1.5-pro"),
    instruction=LEAD_SIGNAL_ANALYZER_PROMPT,
    tools=[google_search],
    output_key="lead_signal_analyzer_output", # 保存非結構化輸出
)

# 潛在客戶信號格式化代理模板（格式化器）
lead_signal_formatter_template = LlmAgent(
    name="LeadSignalFormatterAgent",
    model=os.getenv("GEN_FAST_MODEL", "gemini-1.5-flash"),
    instruction="""將來自潛在客戶信號分析器的以下非結構化文本格式化為 `LeadSignalAnalyzerOutput` JSON 結構。

{unstructured_text}
""",
    output_schema=LeadSignalAnalyzerOutput,
    output_key="lead_analysis_findings", # 保存結構化輸出
)

# 報告編譯代理
report_compiler_agent = LlmAgent(
    name="ReportCompilerAgent",
    model=os.getenv("GEN_ADVANCED_MODEL", "gemini-1.5-pro"),
    instruction=REPORT_COMPILER_PROMPT,
)

# 報告協調代理
class ReportOrchestratorAgent(BaseAgent):
    """
    收集所有並行的潛在客戶研究結果，並將它們格式化為單一字串，以供報告編譯代理使用。
    """
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        all_findings = []
        leads_found_structured = ctx.session.state.get("leads_found_structured")
        if leads_found_structured:
            leads_list = leads_found_structured.get("potential_leads", [])
            for i, lead_data in enumerate(leads_list):
                validation_result = ctx.session.state.get(f"lead_validation_result_{i}")
                analysis_findings = ctx.session.state.get(f"lead_analysis_findings_{i}")

                if validation_result and validation_result.get("is_valid"):
                    finding_str = f"--- 潛在客戶: {lead_data.get('company_name')} ---\n"
                    if analysis_findings:
                        summary = analysis_findings.get('summary', '沒有可用的摘要。')
                        sources = analysis_findings.get('sources', [])
                        finding_str += f"分析摘要: {summary}\n"
                        finding_str += "來源:\n" + "\n".join(f"- {source}" for source in sources)
                    else:
                        finding_str += "沒有可用的分析結果。\n"
                    all_findings.append(finding_str)
        
        ctx.session.state["all_lead_findings"] = "\n\n".join(all_findings)
        yield Event(author=self.name, content=Content(parts=[Part(text="潛在客戶研究結果已整合。")]))

report_orchestrator_agent = ReportOrchestratorAgent(name="ReportOrchestrator")

# 潛在客戶研究協調代理
class LeadResearchOrchestratorAgent(BaseAgent):
    """
    動態建立並執行一個並行工作流程，以驗證和分析潛在客戶列表。
    """
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        leads_found_structured = ctx.session.state.get("leads_found_structured")
        if not leads_found_structured:
            yield Event(author=self.name, content=Content(parts=[Part(text="沒有要分析的潛在客戶。")]))
            return

        leads_list = leads_found_structured.get("potential_leads", [])
        
        research_pipelines = []
        for i, lead_data in enumerate(leads_list):
            research_pipeline = SequentialAgent(
                name=f"LeadResearchPipeline_{i}",
                sub_agents=[
                    LlmAgent(
                        name=f"LeadValidator_{i}",
                        instruction=validator_agent_template.instruction.format(
                            company_to_validate=lead_data, **ctx.session.state
                        ),
                        model=validator_agent_template.model,
                        output_schema=validator_agent_template.output_schema,
                        output_key=f"lead_validation_result_{i}",
                    ),
                    LlmAgent(
                        name=f"LeadSignalAnalyzer_{i}",
                        instruction=lead_signal_analyzer_template.instruction.format(
                            company_data=lead_data, **ctx.session.state
                        ),
                        model=lead_signal_analyzer_template.model,
                        tools=lead_signal_analyzer_template.tools,
                        output_key=f"lead_signal_analyzer_output_{i}",
                    ),
                    LlmAgent(
                        name=f"LeadSignalFormatter_{i}",
                        instruction=lead_signal_formatter_template.instruction.format(
                            unstructured_text=f"{{lead_signal_analyzer_output_{i}}}"
                        ),
                        model=lead_signal_formatter_template.model,
                        output_schema=lead_signal_formatter_template.output_schema,
                        output_key=f"lead_analysis_findings_{i}",
                    ),
                ],
            )
            research_pipelines.append(research_pipeline)
        
        parallel_researcher = ParallelAgent(
            name="DynamicLeadResearcher",
            sub_agents=research_pipelines,
        )

        async for event in parallel_researcher.run_async(ctx):
            yield event

lead_research_orchestrator_agent = LeadResearchOrchestratorAgent(name="LeadResearchOrchestrator")

# 主要潛在客戶開發代理
lead_generation_agent = SequentialAgent(
    name="LeadGenerationAgent",
    sub_agents=[
        lead_finder_agent,
        lead_formatter_agent,
        lead_research_orchestrator_agent,
        report_orchestrator_agent,
        report_compiler_agent,
    ],
    description="協調尋找和篩選新投資潛在客戶的工作流程。",
)
