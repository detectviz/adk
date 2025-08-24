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

import asyncio

from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# [步驟 2] 匯入外掛程式。
from .count_plugin import CountInvocationPlugin


async def hello_world(tool_context: ToolContext, query: str):
  print(f'Hello world: query is [{query}]')


root_agent = Agent(
    model='gemini-2.0-flash',
    name='hello_world',
    description='印出 hello world 與使用者查詢。',
    instruction="""使用 hello_world 工具印出 hello world 與使用者查詢。
    """,
    tools=[hello_world],
)


async def main():
  """代理程式的主要進入點。"""
  prompt = 'hello world'
  runner = InMemoryRunner(
      agent=root_agent,
      app_name='test_app_with_plugin',
      # [步驟 2] 在此處新增您的外掛程式。您可以新增多個外掛程式。
      plugins=[CountInvocationPlugin()],
  )
  session = await runner.session_service.create_session(
      user_id='user',
      app_name='test_app_with_plugin',
  )

  async for event in runner.run_async(
      user_id='user',
      session_id=session.id,
      new_message=types.Content(
          role='user', parts=[types.Part.from_text(text=prompt)]
      ),
  ):
    print(f'** Got event from {event.author}')


if __name__ == '__main__':
  asyncio.run(main())
