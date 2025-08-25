import json
import logging

import azure.functions as func
import httpx


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.generic_trigger(
    arg_name='context',
    type='mcpToolTrigger',
    toolName='hello_mcp',
    description='哈囉世界。',
    toolProperties='[]',
)
def hello_mcp(context) -> None:
    """一個傳回問候訊息的簡單函式。

    Args:
        context: 觸發器上下文（此函式中未使用）。

    Returns:
        str: 一則問候訊息。
    """
    return '哈囉，我是 MCPTool！'


@app.generic_trigger(
    arg_name='context',
    type='mcpToolTrigger',
    tool_name='get_exchange_rate',
    description='一個利用 Frankfurter 取得匯率的簡單貨幣函式',
    toolProperties="""[
        {
            "propertyName": "currency_from",
            "propertyType": "string",
            "description": "要換算的貨幣代碼，例如 USD"
        },
        {
            "propertyName": "currency_to",
            "propertyType": "string",
            "description": "要換算成的貨幣代碼，例如 EUR 或 INR"
        }
    ]""",
)
def get_exchange_rate(context) -> str:
    try:
        content = json.loads(context)
        arguments = content.get('arguments', {})

        currency_from = arguments.get('currency_from')
        currency_to = arguments.get('currency_to')
        logging.info(
            f'貨幣換算從 {currency_from} 到 {currency_to}'
        )
        response = httpx.get(
            'https://api.frankfurter.app/latest',
            params={'from': currency_from, 'to': currency_to},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
        if 'rates' not in data or currency_to not in data['rates']:
            return (
                f'無法擷取 {currency_from} 到 {currency_to} 的匯率'
            )
        rate = data['rates'][currency_to]
        return f'1 {currency_from} = {rate} {currency_to}'
    except Exception as e:
        return f'貨幣 API 呼叫失敗：{e!s}'
