import logging  # Import the logging module

from uuid import uuid4

import asyncclick as click
import grpc
import httpx

from a2a.client import A2ACardResolver, A2AGrpcClient
from a2a.grpc import a2a_pb2, a2a_pb2_grpc
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    TextPart,
)
from a2a.utils import proto_utils


@click.command()
@click.option('--agent-card-url', 'agent_card_url', default='http://localhost:11000')
@click.option('--grpc-endpoint', 'grpc_endpoint', default=None)
async def main(agent_card_url: str, grpc_endpoint: str | None) -> None:
    # 設定日誌記錄以顯示 INFO 等級的訊息
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)  # Get a logger instance

    if grpc_endpoint is None:
        logger.info('未指定 gRPC 端點。正在從 HTTP 伺服器擷取公用代理 (Agent) 名片')
        # 如果未指定 grpc_url，請嘗試擷取公用代理 (Agent) 名片
        agent_card = await get_public_agent_card(agent_card_url)
        base_url = agent_card.url
    else:
        logger.info('已指定 gRPC 端點。跳過從 HTTP 伺服器擷取公用代理 (Agent) 名片')
        # 如果 gRPC 端點是特定的
        base_url = grpc_endpoint


    async with grpc.aio.insecure_channel(base_url) as channel:
        stub = a2a_pb2_grpc.A2AServiceStub(channel)

        # 使用 gRPC 通道取得經過驗證的代理 (Agent) 名片
        # 在實際應用程式中，agent_card.supports_authenticated_extended_card 旗標
        # 指定是否應擷取經過驗證的名片。
        # 如果提供了經過驗證的代理 (Agent) 名片，用戶端應使用它與 gRPC 服務互動
        try:
            logger.info(
                '正在嘗試從 grpc 端點擷取經過驗證的代理 (Agent) 名片'
            )
            proto_card = await stub.GetAgentCard(a2a_pb2.GetAgentCardRequest())
            logger.info('成功擷取代理 (Agent) 名片：')
            logger.info(proto_card)
            final_agent_card_to_use = proto_utils.FromProto.agent_card(
                proto_card
            )
        except Exception:
            logging.exception('無法取得經過驗證的代理 (Agent) 名片。正在結束。')
            return


        client = A2AGrpcClient(stub, agent_card=final_agent_card_to_use)
        logger.info('A2AClient 已初始化。')

        request = MessageSendParams(
            message=Message(
                role=Role.user,
                parts=[Part(root=TextPart(text='擲一個 5 面的骰子'))],
                message_id=str(uuid4()),
            )
        )

        response = await client.send_message(request)
        logging.info(response.model_dump(mode='json', exclude_none=True))

        stream_response = client.send_message_streaming(request)

        async for chunk in stream_response:
            logging.info(chunk.model_dump(mode='json', exclude_none=True))

async def get_public_agent_card(agent_card_url: str) -> AgentCard:
    agent_card: AgentCard | None = None
    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=agent_card_url,
        )
        # 擷取基本代理 (Agent) 名片
        agent_card = await resolver.get_agent_card()

    if not agent_card:
        raise ValueError('找不到公用代理 (Agent) 名片')

    return agent_card


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
