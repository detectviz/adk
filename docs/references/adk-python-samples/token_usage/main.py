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
import time
import warnings

import agent
from dotenv import load_dotenv
from google.adk import Runner
from google.adk.agents.run_config import RunConfig
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.cli.utils import logs
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.sessions.session import Session
from google.genai import types

load_dotenv(override=True)
warnings.filterwarnings('ignore', category=UserWarning)
logs.log_to_tmp_folder()


async def main():
  app_name = 'my_app'
  user_id_1 = 'user1'
  session_service = InMemorySessionService()
  artifact_service = InMemoryArtifactService()
  runner = Runner(
      app_name=app_name,
      agent=agent.root_agent,
      artifact_service=artifact_service,
      session_service=session_service,
  )
  session_11 = await session_service.create_session(
      app_name=app_name, user_id=user_id_1
  )

  total_prompt_tokens = 0
  total_candidate_tokens = 0
  total_tokens = 0

  async def run_prompt(session: Session, new_message: str):
    nonlocal total_prompt_tokens
    nonlocal total_candidate_tokens
    nonlocal total_tokens
    content = types.Content(
        role='user', parts=[types.Part.from_text(text=new_message)]
    )
    print('** 使用者說：', content.model_dump(exclude_none=True))
    async for event in runner.run_async(
        user_id=user_id_1,
        session_id=session.id,
        new_message=content,
    ):
      if event.content.parts and event.content.parts[0].text:
        print(f'** {event.author}: {event.content.parts[0].text}')
      if event.usage_metadata:
        total_prompt_tokens += event.usage_metadata.prompt_token_count or 0
        total_candidate_tokens += (
            event.usage_metadata.candidates_token_count or 0
        )
        total_tokens += event.usage_metadata.total_token_count or 0
        print(
            '回合權杖：'
            f' {event.usage_metadata.total_token_count} (提示={event.usage_metadata.prompt_token_count},'
            f' 候選={event.usage_metadata.candidates_token_count})'
        )

    print(
        f'會話權杖：{total_tokens} (提示={total_prompt_tokens},'
        f' 候選={total_candidate_tokens})'
    )

  start_time = time.time()
  print('開始時間：', start_time)
  print('------------------------------------')
  await run_prompt(session_11, '嗨')
  await run_prompt(session_11, '擲一個 100 面的骰子')
  print(
      await artifact_service.list_artifact_keys(
          app_name=app_name, user_id=user_id_1, session_id=session_11.id
      )
  )
  end_time = time.time()
  print('------------------------------------')
  print('結束時間：', end_time)
  print('總時間：', end_time - start_time)


if __name__ == '__main__':
  asyncio.run(main())
