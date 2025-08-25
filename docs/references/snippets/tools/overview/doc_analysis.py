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

from google.adk.tools import ToolContext, FunctionTool
from google.genai import types


def process_document(
    document_name: str, analysis_query: str, tool_context: ToolContext
) -> dict:
    """使用記憶體中的上下文來分析文件。"""

    # 1. 載入產物
    print(f"工具：正在嘗試載入產物：{document_name}")
    document_part = tool_context.load_artifact(document_name)

    if not document_part:
        return {"status": "error", "message": f"找不到文件 '{document_name}'。"}

    document_text = document_part.text  # 為簡單起見，假設是文字
    print(f"工具：已載入文件 '{document_name}'（{len(document_text)} 個字元）。")

    # 2. 在記憶體中搜尋相關上下文
    print(f"工具：正在記憶體中搜尋與 '{analysis_query}' 相關的上下文")
    memory_response = tool_context.search_memory(
        f"用於分析關於 {analysis_query} 的文件的上下文"
    )
    memory_context = "\n".join(
        [
            m.events[0].content.parts[0].text
            for m in memory_response.memories
            if m.events and m.events[0].content
        ]
    )  # 簡化提取
    print(f"工具：找到的記憶體上下文：{memory_context[:100]}...")

    # 3. 執行分析（佔位符）
    analysis_result = f"關於 '{analysis_query}' 的 '{document_name}' 的分析，使用記憶體上下文：[佔位符分析結果]"
    print("工具：已執行分析。")

    # 4. 將分析結果儲存為新的產物
    analysis_part = types.Part.from_text(text=analysis_result)
    new_artifact_name = f"analysis_{document_name}"
    version = asyncio.run(tool_context.save_artifact(new_artifact_name, analysis_part))
    print(f"工具：已將分析結果儲存為 '{new_artifact_name}' 版本 {version}。")

    return {
        "status": "success",
        "analysis_artifact": new_artifact_name,
        "version": version,
    }


doc_analysis_tool = FunctionTool(func=process_document)

# 在代理中：
# 假設先前已儲存產物 'report.txt'。
# 假設記憶體服務已設定並包含相關的過去資料。
# my_agent = Agent(..., tools=[doc_analysis_tool], artifact_service=..., memory_service=...)
