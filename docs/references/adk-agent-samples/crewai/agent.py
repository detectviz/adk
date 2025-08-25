"""基於 Crew AI 的 A2A 協定範例。

處理代理 (Agent) 並提供所需工具。
"""

import base64
import logging
import os
import re

from collections.abc import AsyncIterable
from io import BytesIO
from typing import Any
from uuid import uuid4

from PIL import Image
from crewai import LLM, Agent, Crew, Task
from crewai.process import Process
from crewai.tools import tool
from dotenv import load_dotenv
from google import genai
from google.genai import types
from in_memory_cache import InMemoryCache
from pydantic import BaseModel


load_dotenv()

logger = logging.getLogger(__name__)


class Imagedata(BaseModel):
    """代表圖片資料。

    屬性:
      id: 圖片的唯一識別碼。
      name: 圖片的名稱。
      mime_type: 圖片的 MIME 類型。
      bytes: Base64 編碼的圖片資料。
      error: 如果圖片出現問題，則為錯誤訊息。
    """

    id: str | None = None
    name: str | None = None
    mime_type: str | None = None
    bytes: str | None = None
    error: str | None = None


@tool('ImageGenerationTool')
def generate_image_tool(
    prompt: str, session_id: str, artifact_file_id: str = None
) -> str:
    """圖片產生工具，可根據提示產生圖片或修改給定圖片。"""
    if not prompt:
        raise ValueError('提示不能為空')

    client = genai.Client()
    cache = InMemoryCache()

    text_input = (
        prompt,
        '如果輸入圖片與請求不符，請忽略。',
    )

    ref_image = None
    logger.info(f'Session id {session_id}')
    print(f'Session id {session_id}')

    # TODO (rvelicheti) - 將複雜的記憶體處理邏輯更改為更好的版本。
    # 從快取中取得圖片並將其傳回模型。
    # 假設產生的圖片的最新版本適用。
    # 轉換為 PIL 圖片，以免傳送給 LLM 的上下文 (Context) 過載
    try:
        ref_image_data = None
        # image_id = session_cache[session_id][-1]
        session_image_data = cache.get(session_id)
        if artifact_file_id:
            try:
                ref_image_data = session_image_data[artifact_file_id]
                logger.info('在提示輸入中找到參考圖片')
            except Exception:
                ref_image_data = None
        if not ref_image_data:
            # 從 python 3.7 開始維護插入順序
            latest_image_key = list(session_image_data.keys())[-1]
            ref_image_data = session_image_data[latest_image_key]

        ref_bytes = base64.b64decode(ref_image_data.bytes)
        ref_image = Image.open(BytesIO(ref_bytes))
    except Exception:
        ref_image = None

    if ref_image:
        contents = [text_input, ref_image]
    else:
        contents = text_input

    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash-exp',
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            ),
        )
    except Exception as e:
        logger.error(f'產生圖片時發生錯誤 {e}')
        print(f'Exception {e}')
        return -999999999

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            try:
                print('正在建立圖片資料')
                data = Imagedata(
                    bytes=base64.b64encode(part.inline_data.data).decode(
                        'utf-8'
                    ),
                    mime_type=part.inline_data.mime_type,
                    name='generated_image.png',
                    id=uuid4().hex,
                )
                session_data = cache.get(session_id)
                if session_data is None:
                    # 工作階段不存在，用新項目建立它
                    cache.set(session_id, {data.id: data})
                else:
                    # 工作階段已存在，直接更新現有的字典
                    session_data[data.id] = data

                return data.id
            except Exception as e:
                logger.error(f'解壓縮圖片時發生錯誤 {e}')
                print(f'Exception {e}')
    return -999999999


class ImageGenerationAgent:
    """根據使用者提示產生圖片的代理 (Agent)。"""

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain', 'image/png']

    def __init__(self):
        if os.getenv('GOOGLE_GENAI_USE_VERTEXAI'):
            self.model = LLM(model='vertex_ai/gemini-1.5-flash')
        elif os.getenv('GOOGLE_API_KEY'):
            self.model = LLM(
                model='gemini/gemini-1.5-flash',
                api_key=os.getenv('GOOGLE_API_KEY'),
            )

        self.image_creator_agent = Agent(
            role='圖片創作專家',
            goal=(
                "根據使用者的文字提示產生圖片。如果提示模糊，請提出澄清問題（儘管該工具目前在一次執行中不支援來回對話）。專注於解讀使用者的請求並有效地使用圖片產生器工具。"
            ),
            backstory=(
                '您是一位由 AI 驅動的數位藝術家。您專門將文字描述轉換為視覺呈現，使用強大的圖片產生工具。您的目標是根據提供的提示實現準確性和創造力。'
            ),
            verbose=False,
            allow_delegation=False,
            tools=[generate_image_tool],
            llm=self.model,
        )

        self.image_creation_task = Task(
            description=(
                "接收使用者提示：'{user_prompt}'。\n分析提示並確定您需要建立新圖片還是編輯現有圖片。在提示中尋找像 this、that 等代名詞，它們可能提供上下文，重寫提示以包含上下文。如果建立新圖片，請忽略作為輸入上下文提供的任何圖片。使用 'Image Generator' 工具進行圖片創作或修改。該工具將需要一個提示，即 {user_prompt}，以及一個 session_id，即 {session_id}。可選地，該工具還需要一個 artifact_file_id，它會作為 {artifact_file_id} 傳送給您。"
            ),
            expected_output='產生圖片的 ID',
            agent=self.image_creator_agent,
        )

        self.image_crew = Crew(
            agents=[self.image_creator_agent],
            tasks=[self.image_creation_task],
            process=Process.sequential,
            verbose=False,
        )

    def extract_artifact_file_id(self, query):
        try:
            pattern = r'(?:id|artifact-file-id)\s+([0-9a-f]{32})'
            match = re.search(pattern, query)

            if match:
                return match.group(1)
            return None
        except Exception:
            return None

    def invoke(self, query, session_id) -> str:
        """啟動 CrewAI 並傳回回應。"""
        artifact_file_id = self.extract_artifact_file_id(query)

        inputs = {
            'user_prompt': query,
            'session_id': session_id,
            'artifact_file_id': artifact_file_id,
        }
        logger.info(f'Inputs {inputs}')
        print(f'Inputs {inputs}')
        response = self.image_crew.kickoff(inputs)
        return response

    async def stream(self, query: str) -> AsyncIterable[dict[str, Any]]:
        """CrewAI 不支援串流。"""
        raise NotImplementedError('CrewAI 不支援串流。')

    def get_image_data(self, session_id: str, image_key: str) -> Imagedata:
        """根據金鑰傳回 Imagedata。這是代理 (Agent) 的一個輔助方法。"""
        cache = InMemoryCache()
        session_data = cache.get(session_id)
        try:
            cache.get(session_id)
            return session_data[image_key]
        except KeyError:
            logger.error('產生圖片時發生錯誤')
            return Imagedata(error='產生圖片時發生錯誤，請重試。')
