import logging
import os

import click
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import QnAAgentExecutor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.starlette import StarletteInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


logger = logging.getLogger(__name__)
logging.basicConfig()


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10020)
def main(host: str, port: int):
    """A2A 遙測範例 GRPC 伺服器。"""
    if not os.getenv('GOOGLE_API_KEY'):
        raise ValueError('未設定 GOOGLE_API_KEY。')

    skill = AgentSkill(
        id='question_answer',
        name='Q&A Agent',
        description='一個可以回答問題的實用助理代理。',
        tags=['Question-Answer'],
        examples=[
            '誰在 2025 年 F1 積分榜上領先？',
            '我在哪裡可以找到活火山？',
        ],
    )

    agent_executor = QnAAgentExecutor()
    agent_card = AgentCard(
        name='Q&A Agent',
        description='一個可以回答問題的實用助理代理。',
        url=f'http://{host}:{port}/',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    logger.debug('遙測設定')
    # 設定服務名稱以便在 Jaeger 和 Grafana 中查詢
    resource = Resource(
        attributes={
            'service.name': 'a2a-telemetry-sample',
            'service.version': '1.0',
        }
    )
    # 建立一個 TracerProvider 並註冊它
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    tracer_provider = trace.get_tracer_provider()

    # 建立並設定 Jaeger 匯出器，UDP 傳輸。
    jaeger_exporter = OTLPSpanExporter(
        endpoint='http://localhost:4317', insecure=True
    )
    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

    server = A2AStarletteApplication(agent_card, request_handler)
    starlette_app = server.build()
    # 為 starlette 應用程式進行追蹤檢測
    StarletteInstrumentor().instrument_app(starlette_app)
    uvicorn.run(starlette_app, host=host, port=port)


if __name__ == '__main__':
    main()
