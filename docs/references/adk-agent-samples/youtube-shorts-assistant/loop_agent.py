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

# 展示如何以迭代方式在迴圈中呼叫所有子代理。使用 "adk run" 或 "adk web" 執行此範例。

from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools import google_search

from .util import load_instruction_from_file

# --- 子代理 1：腳本撰寫器 (Scriptwriter) ---
scriptwriter_agent = LlmAgent(
    name="ShortsScriptwriter",
    model="gemini-2.0-flash-001",
    instruction=load_instruction_from_file("scriptwriter_instruction.txt"),
    tools=[google_search],
    output_key="generated_script",  # 將結果儲存到狀態 (state)
)

# --- 子代理 2：視覺化工具 (Visualizer) ---
visualizer_agent = LlmAgent(
    name="ShortsVisualizer",
    model="gemini-2.0-flash-001",
    instruction=load_instruction_from_file("visualizer_instruction.txt"),
    description="根據提供的腳本生成視覺概念。",
    output_key="visual_concepts",  # 將結果儲存到狀態 (state)
)

# --- 子代理 3：格式化工具 (Formatter) ---
# 此代理將讀取兩個狀態鍵，並將其組合成最終的 Markdown 格式
formatter_agent = LlmAgent(
    name="ConceptFormatter",
    model="gemini-2.0-flash-001",
    instruction="""將 state['generated_script'] 的腳本與 state['visual_concepts'] 的視覺概念結合，轉換為先前要求的最終 Markdown 格式（包含開頭、腳本與視覺效果表格、視覺筆記、行動呼籲）。""",
    description="格式化最終的 Shorts 概念。",
    output_key="final_short_concept",
)


# --- 迴圈代理工作流程 (Loop Agent Workflow) ---
youtube_shorts_agent = LoopAgent(
    name="youtube_shorts_agent",
    max_iterations=3,
    sub_agents=[scriptwriter_agent, visualizer_agent, formatter_agent],
)

# --- 執行器的根代理 (Root Agent for the Runner) ---
# 執行器現在將執行此工作流程
root_agent = youtube_shorts_agent
