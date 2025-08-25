import logging

from typing import Any
from uuid import uuid4

import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
)
from a2a.utils.constants import (
    AGENT_CARD_WELL_KNOWN_PATH,
    EXTENDED_AGENT_CARD_PATH,
)


async def main() -> None:
    # 設定日誌記錄以顯示 INFO 等級的訊息
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)  # Get a logger instance

    # --8<-- [start:A2ACardResolver]

    base_url = 'http://localhost:9999'

    async with httpx.AsyncClient() as httpx_client:
        # 初始化 A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
            # agent_card_path 使用預設值，extended_agent_card_path 也使用預設值
        )
        # --8<-- [end:A2ACardResolver]

        # 擷取公用代理 (Agent) 名片並初始化用戶端
        final_agent_card_to_use: AgentCard | None = None

        try:
            logger.info(
                f'正在嘗試從以下位置擷取公用代理 (Agent) 名片：{base_url}{AGENT_CARD_WELL_KNOWN_PATH}'
            )
            _public_card = (
                await resolver.get_agent_card()
            )  # 從預設公用路徑擷取
            logger.info('成功擷取公用代理 (Agent) 名片：')
            logger.info(
                _public_card.model_dump_json(indent=2, exclude_none=True)
            )
            final_agent_card_to_use = _public_card
            logger.info(
                '\n使用公用代理 (Agent) 名片進行用戶端初始化（預設）。'
            )

            if _public_card.supports_authenticated_extended_card:
                try:
                    logger.info(
                        f'\n公用名片支援經過驗證的擴充名片。正在嘗試從以下位置擷取：{base_url}{EXTENDED_AGENT_CARD_PATH}'
                    )
                    auth_headers_dict = {
                        'Authorization': 'Bearer dummy-token-for-extended-card'
                    }
                    _extended_card = await resolver.get_agent_card(
                        relative_card_path=EXTENDED_AGENT_CARD_PATH,
                        http_kwargs={'headers': auth_headers_dict},
                    )
                    logger.info(
                        '成功擷取經過驗證的擴充代理 (Agent) 名片：'
                    )
                    logger.info(
                        _extended_card.model_dump_json(
                            indent=2, exclude_none=True
                        )
                    )
                    final_agent_card_to_use = (
                        _extended_card  # 更新為使用擴充名片
                    )
                    logger.info(
                        '\n使用經過驗證的擴充代理 (Agent) 名片進行用戶端初始化。'
                    )
                except Exception as e_extended:
                    logger.warning(
                        f'無法擷取擴充代理 (Agent) 名片：{e_extended}。將繼續使用公用名片。',
                        exc_info=True,
                    )
            elif (
                _public_card
            ):  # supports_authenticated_extended_card 為 False 或 None
                logger.info(
                    '\n公用名片未表示支援擴充名片。正在使用公用名片。'
                )

        except Exception as e:
            logger.error(
                f'擷取公用代理 (Agent) 名片時發生嚴重錯誤：{e}', exc_info=True
            )
            raise RuntimeError(
                '無法擷取公用代理 (Agent) 名片。無法繼續。'
            ) from e

        # --8<-- [start:send_message]
        client = A2AClient(
            httpx_client=httpx_client, agent_card=final_agent_card_to_use
        )
        logger.info('A2AClient 已初始化。')

        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': '10 美元等於多少印度盧比？'}
                ],
                'messageId': uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        response = await client.send_message(request)
        print(response.model_dump(mode='json', exclude_none=True))
        # --8<-- [end:send_message]

        # --8<-- [start:send_message_streaming]

        streaming_request = SendStreamingMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        stream_response = client.send_message_streaming(streaming_request)

        async for chunk in stream_response:
            print(chunk.model_dump(mode='json', exclude_none=True))
        # --8<-- [end:send_message_streaming]


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
