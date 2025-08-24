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

import agent
from dotenv import load_dotenv
from google.adk.agents.run_config import RunConfig
from google.adk.cli.utils import logs
from google.adk.runners import InMemoryRunner
from google.adk.sessions.session import Session
from google.genai import types

load_dotenv(override=True)
logs.log_to_tmp_folder()


async def main():
  app_name = 'my_app'
  user_id_1 = 'user1'
  runner = InMemoryRunner(
      agent=agent.root_agent,
      app_name=app_name,
  )
  session_11 = await runner.session_service.create_session(
      app_name=app_name, user_id=user_id_1
  )

  async def run_prompt(session: Session, new_message: str):
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

  async def run_prompt_bytes(session: Session, new_message: str):
    content = types.Content(
        role='user',
        parts=[
            types.Part.from_bytes(
                data=str.encode(new_message), mime_type='text/plain'
            )
        ],
    )
    print('** 使用者說：', content.model_dump(exclude_none=True))
    async for event in runner.run_async(
        user_id=user_id_1,
        session_id=session.id,
        new_message=content,
        run_config=RunConfig(save_input_blobs_as_artifacts=True),
    ):
      if event.content.parts and event.content.parts[0].text:
        print(f'** {event.author}: {event.content.parts[0].text}')

  async def check_rolls_in_state(rolls_size: int):
    session = await runner.session_service.get_session(
        app_name=app_name, user_id=user_id_1, session_id=session_11.id
    )
    assert len(session.state['rolls']) == rolls_size
    for roll in session.state['rolls']:
      assert roll > 0 and roll <= 100

  start_time = time.time()
  print('開始時間：', start_time)
  print('------------------------------------')
  await run_prompt(session_11, '你好')
  await run_prompt(session_11, '擲一個 100 面的骰子')
  await check_rolls_in_state(1)
  await run_prompt(session_11, '再擲一個 100 面的骰子。')
  await check_rolls_in_state(2)
  await run_prompt(session_11, '我得到了什麼數字？')
  await run_prompt_bytes(session_11, '你好 bytes')
  print(
      await runner.artifact_service.list_artifact_keys(
          app_name=app_name, user_id=user_id_1, session_id=session_11.id
      )
  )
  end_time = time.time()
  print('------------------------------------')
  print('結束時間：', end_time)
  print('總時間：', end_time - start_time)


if __name__ == '__main__':
  asyncio.run(main())
