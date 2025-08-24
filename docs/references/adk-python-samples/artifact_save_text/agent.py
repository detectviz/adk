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


from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types


async def log_query(tool_context: ToolContext, query: str):
  """將提供的查詢字串儲存為名為 'query' 的 'text/plain' 產物。"""
  query_bytes = query.encode('utf-8')
  artifact_part = types.Part(
      inline_data=types.Blob(mime_type='text/plain', data=query_bytes)
  )
  await tool_context.save_artifact('query', artifact_part)


root_agent = Agent(
    model='gemini-2.0-flash',
    name='log_agent',
    description='記錄使用者查詢。',
    instruction="""務必記錄使用者查詢並回覆「好的，我已經記錄下來了。」
    """,
    tools=[log_query],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # 避免關於擲骰子的誤報。
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
