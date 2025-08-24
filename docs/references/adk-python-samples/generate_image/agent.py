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
from google.adk.tools import load_artifacts
from google.adk.tools.tool_context import ToolContext
from google.genai import Client
from google.genai import types

# 目前只有 Vertex AI 支援圖片生成。
client = Client()


async def generate_image(prompt: str, tool_context: 'ToolContext'):
  """根據提示生成圖片。"""
  response = client.models.generate_images(
      model='imagen-3.0-generate-002',
      prompt=prompt,
      config={'number_of_images': 1},
  )
  if not response.generated_images:
    return {'status': '失敗'}
  image_bytes = response.generated_images[0].image.image_bytes
  await tool_context.save_artifact(
      'image.png',
      types.Part.from_bytes(data=image_bytes, mime_type='image/png'),
  )
  return {
      'status': '成功',
      'detail': '圖片已成功生成並儲存於產物中。',
      'filename': 'image.png',
  }


root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='root_agent',
    description="""一個能生成圖片並回答相關問題的代理 (Agent)。""",
    instruction="""您是一個根據使用者提示生成或編輯圖片的代理 (Agent)。
""",
    tools=[generate_image, load_artifacts],
)
