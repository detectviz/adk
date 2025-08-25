import base64
import logging

from collections.abc import AsyncIterable
from io import BytesIO
from typing import Any
from uuid import uuid4

import matplotlib.pyplot as plt
import pandas as pd

from crewai import Agent, Crew, Task
from crewai.process import Process
from crewai.tools import tool
from dotenv import load_dotenv
from pydantic import BaseModel
from utils import cache


load_dotenv()

logger = logging.getLogger(__name__)


class Imagedata(BaseModel):
    id: str | None = None
    name: str | None = None
    mime_type: str | None = None
    bytes: str | None = None
    error: str | None = None


@tool('ChartGenerationTool')
def generate_chart_tool(prompt: str, session_id: str) -> str:
    """使用 matplotlib 從類 CSV 輸入產生長條圖圖片。"""
    logger.info(f'>>>圖表工具以提示呼叫：{prompt}')

    if not prompt:
        raise ValueError('提示不能為空')

    try:
        # 解析類 CSV 輸入
        from io import StringIO

        df = pd.read_csv(StringIO(prompt))
        if df.shape[1] != 2:
            raise ValueError(
                '輸入必須剛好有兩欄：類別和值'
            )
        df.columns = ['類別', '值']
        df['值'] = pd.to_numeric(df['值'], errors='coerce')
        if df['值'].isnull().any():
            raise ValueError('所有值都必須是數字')

        # 產生長條圖
        fig, ax = plt.subplots()
        ax.bar(df['類別'], df['值'])
        ax.set_xlabel('類別')
        ax.set_ylabel('值')
        ax.set_title('長條圖')

        # 儲存到緩衝區
        buf = BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        image_bytes = buf.read()

        # 編碼圖片
        data = Imagedata(
            bytes=base64.b64encode(image_bytes).decode('utf-8'),
            mime_type='image/png',
            name='generated_chart.png',
            id=uuid4().hex,
        )

        logger.info(
            f'正在快取圖片，ID 為：{data.id}，工作階段為：{session_id}'
        )

        # 快取圖片
        session_data = cache.get(session_id) or {}
        session_data[data.id] = data
        cache.set(session_id, session_data)

        return data.id

    except Exception as e:
        logger.error(f'產生圖表時發生錯誤：{e}')
        return -999999999


class ChartGenerationAgent:
    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain', 'image/png']

    def __init__(self):
        self.chart_creator_agent = Agent(
            role='圖表建立專家',
            goal='根據結構化 CSV 輸入產生長條圖圖片。',
            backstory='你是一位將結構化資料轉換為視覺化圖表的資料視覺化專家。',
            verbose=False,
            allow_delegation=False,
            tools=[generate_chart_tool],
        )

        self.chart_creation_task = Task(
            description=(
                "你收到一個提示：'{user_prompt}'。\n"
                "如果提示包含以逗號分隔的鍵值對（例如 'a:100, b:200'），"
                "請將其重新格式化為帶有標頭 'Category,Value' 的 CSV。\n"
                "確保它成為兩欄的 CSV，然後將其傳遞給 'ChartGenerationTool'。\n"
                "呼叫工具時使用工作階段 ID：'{session_id}'。"
            ),
            expected_output='產生的圖表圖片 ID',
            agent=self.chart_creator_agent,
        )

        self.chart_crew = Crew(
            agents=[self.chart_creator_agent],
            tasks=[self.chart_creation_task],
            process=Process.sequential,
            verbose=False,
        )

    import uuid

    def invoke(self, query, session_id: str | None = None) -> str:
        # 正規化或產生 session_id
        session_id = session_id or f'session-{uuid.uuid4().hex}'
        logger.info(
            f'[invoke] 正在為查詢使用 session_id：{session_id}：{query}'
        )

        inputs = {
            'user_prompt': query,
            'session_id': session_id,
        }

        response = self.chart_crew.kickoff(inputs)
        logger.info(f'[invoke] 圖表工具傳回的圖片 ID：{response}')
        return response

    async def stream(self, query: str) -> AsyncIterable[dict[str, Any]]:
        raise NotImplementedError('不支援串流。')

    def get_image_data(self, session_id: str, image_key: str) -> Imagedata:
        session_data = cache.get(session_id)

        if not session_data:
            logger.error(
                f'[get_image_data] 找不到工作階段 ID 的工作階段資料：{session_id}'
            )
            return Imagedata(
                error=f'找不到工作階段 ID 的工作階段資料：{session_id}'
            )

        if image_key not in session_data:
            logger.error(
                f'[get_image_data] 在工作階段資料中找不到圖片金鑰 {image_key}'
            )
            return Imagedata(
                error=f'在工作階段 {session_id} 中找不到圖片 ID {image_key}'
            )

        return session_data[image_key]
