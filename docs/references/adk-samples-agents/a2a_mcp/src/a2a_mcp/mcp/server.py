# type: ignore
import json
import os
import sqlite3
import traceback

from pathlib import Path

import google.generativeai as genai
import numpy as np
import pandas as pd
import requests

from a2a_mcp.common.utils import init_api_key
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger


logger = get_logger(__name__)
AGENT_CARDS_DIR = 'agent_cards'
MODEL = 'models/embedding-001'
SQLLITE_DB = 'travel_agency.db'
PLACES_API_URL = 'https://places.googleapis.com/v1/places:searchText'


def generate_embeddings(text):
    """使用 Google Generative AI 為給定文字產生嵌入。

    Args:
        text: 要為其產生嵌入的輸入字串。

    Returns:
        代表輸入文字的嵌入列表。
    """
    return genai.embed_content(
        model=MODEL,
        content=text,
        task_type='retrieval_document',
    )['embedding']


def load_agent_cards():
    """從指定目錄中的 JSON 檔案載入代理卡資料。

    Returns:
        一個列表，其中包含在指定目錄中找到的代理卡檔案中的 JSON 資料。
        如果目錄為空、不包含 '.json' 檔案，
        或如果在處理過程中所有 '.json' 檔案都遇到錯誤，則返回一個空列表。
    """
    card_uris = []
    agent_cards = []
    dir_path = Path(AGENT_CARDS_DIR)
    if not dir_path.is_dir():
        logger.error(
            f'找不到代理卡目錄或該路徑不是一個目錄：{AGENT_CARDS_DIR}'
        )
        return agent_cards

    logger.info(f'正在從卡片庫載入代理卡：{AGENT_CARDS_DIR}')

    for filename in os.listdir(AGENT_CARDS_DIR):
        if filename.lower().endswith('.json'):
            file_path = dir_path / filename

            if file_path.is_file():
                logger.info(f'正在讀取檔案：{filename}')
                try:
                    with file_path.open('r', encoding='utf-8') as f:
                        data = json.load(f)
                        card_uris.append(
                            f'resource://agent_cards/{Path(filename).stem}'
                        )
                        agent_cards.append(data)
                except json.JSONDecodeError as jde:
                    logger.error(f'JSON 解碼器錯誤 {jde}')
                except OSError as e:
                    logger.error(f'讀取檔案 {filename} 時出錯：{e}。')
                except Exception as e:
                    logger.error(
                        f'處理 {filename} 時發生未預期的錯誤：{e}',
                        exc_info=True,
                    )
    logger.info(
        f'代理卡載入完成。共找到 {len(agent_cards)} 張卡片。'
    )
    return card_uris, agent_cards


def build_agent_card_embeddings() -> pd.DataFrame:
    """載入代理卡，為其產生嵌入，並傳回一個 DataFrame。

    Returns:
        Optional[pd.DataFrame]: 一個 Pandas DataFrame，包含原始的
        'agent_card' 資料及其對應的 'Embeddings'。如果最初沒有載入代理卡，
        或在嵌入生成過程中發生例外，則返回 None。
    """
    card_uris, agent_cards = load_agent_cards()
    logger.info('正在為代理卡產生嵌入')
    try:
        if agent_cards:
            df = pd.DataFrame(
                {'card_uri': card_uris, 'agent_card': agent_cards}
            )
            df['card_embeddings'] = df.apply(
                lambda row: generate_embeddings(json.dumps(row['agent_card'])),
                axis=1,
            )
            return df
        logger.info('代理卡嵌入產生完成')
    except Exception as e:
        logger.error(f'發生未預期的錯誤：{e}。', exc_info=True)
        return None


def serve(host, port, transport):  # noqa: PLR0915
    """初始化並執行代理卡 MCP 伺服器。

    Args:
        host: 要綁定伺服器的主機名稱或 IP 位址。
        port: 要綁定伺服器的埠號。
        transport: MCP 伺服器的傳輸機制（例如，'stdio'、'sse'）。

    Raises:
        ValueError: 如果未設定 'GOOGLE_API_KEY' 環境變數。
    """
    init_api_key()
    logger.info('正在啟動代理卡 MCP 伺服器')
    mcp = FastMCP('agent-cards', host=host, port=port)

    df = build_agent_card_embeddings()

    @mcp.tool(
        name='find_agent',
        description='根據自然語言查詢字串尋找最相關的代理卡。',
    )
    def find_agent(query: str) -> str:
        """根據查詢字串尋找最相關的代理卡。

        此函式接受使用者查詢（通常是自然語言問題或代理產生的任務），
        產生其嵌入，並將其與已載入代理卡的預先計算嵌入進行比較。
        它使用點積來測量相似度，並識別具有最高相似度分數的代理卡。

        Args:
            query: 用於搜尋相關代理的自然語言查詢字串。

        Returns:
            代表根據嵌入相似度被認為與輸入查詢最相關的代理卡的 json。
        """
        query_embedding = genai.embed_content(
            model=MODEL, content=query, task_type='retrieval_query'
        )
        dot_products = np.dot(
            np.stack(df['card_embeddings']), query_embedding['embedding']
        )
        best_match_index = np.argmax(dot_products)
        logger.debug(
            f'在索引 {best_match_index} 找到最佳匹配，分數為 {dot_products[best_match_index]}'
        )
        return df.iloc[best_match_index]['agent_card']

    @mcp.tool()
    def query_places_data(query: str):
        """查詢 Google Places。"""
        logger.info(f'搜尋地點：{query}')
        api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        if not api_key:
            logger.info('未設定 GOOGLE_PLACES_API_KEY')
            return {'places': []}

        headers = {
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress',
            'Content-Type': 'application/json',
        }
        payload = {
            'textQuery': query,
            'languageCode': 'en',
            'maxResultCount': 10,
        }

        try:
            response = requests.post(
                PLACES_API_URL, headers=headers, json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.info(f'發生 HTTP 錯誤：{http_err}')
            logger.info(f'回應內容：{response.text}')
        except requests.exceptions.ConnectionError as conn_err:
            logger.info(f'發生連線錯誤：{conn_err}')
        except requests.exceptions.Timeout as timeout_err:
            logger.info(f'發生逾時錯誤：{timeout_err}')
        except requests.exceptions.RequestException as req_err:
            logger.info(
                f'請求發生未預期的錯誤：{req_err}'
            )
        except json.JSONDecodeError:
            logger.info(
                f'解碼 JSON 回應失敗。原始回應：{response.text}'
            )

        return {'places': []}

    @mcp.tool()
    def query_travel_data(query: str) -> dict:
        """ "name": "query_travel_data",
        "description": "擷取最新的航空公司、飯店和租車可用性。協助預訂。
        當使用者要求預訂機票、飯店或住宿，或租車時，應使用此工具。",
        "parameters": {
            "type": "object",
            "properties": {
            "query": {
                "type": "string",
                "description": "針對旅遊資料庫執行的 SQL。"
            }
            },
            "required": ["query"]
        }
        """
        # 以上是為了影響 gemini 選擇此工具。
        logger.info(f'查詢 sqllite：{query}')

        if not query or not query.strip().upper().startswith('SELECT'):
            raise ValueError(f'不正確的查詢 {query}')

        try:
            with sqlite3.connect(SQLLITE_DB) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                result = {'results': [dict(row) for row in rows]}
                return json.dumps(result)
        except Exception as e:
            logger.error(f'執行查詢時發生例外狀況 {e}')
            logger.error(traceback.format_exc())
            if 'no such column' in str(e):
                return {
                    'error': f'請檢查您的查詢，{e}。使用資料表結構重新產生查詢'
                }
            return {'error': str(e)}

    @mcp.resource('resource://agent_cards/list', mime_type='application/json')
    def get_agent_cards() -> dict:
        """擷取所有已載入的代理卡，作為 MCP 資源端點的 json / 字典。

        此函式作為由 URI 'resource://agent_cards/list' 識別的 MCP 資源的處理常式。

        Returns:
            一個結構為 {'agent_cards': [...]} 的 json / 字典，其中值是
            包含所有已載入代理卡字典的列表。如果無法擷取資料，
            則返回 {'agent_cards': []}。
        """
        resources = {}
        logger.info('開始讀取資源')
        resources['agent_cards'] = df['card_uri'].to_list()
        return resources

    @mcp.resource(
        'resource://agent_cards/{card_name}', mime_type='application/json'
    )
    def get_agent_card(card_name: str) -> dict:
        """擷取一個代理卡，作為 MCP 資源端點的 json / 字典。

        此函式作為由 URI 'resource://agent_cards/{card_name}' 識別的 MCP 資源的處理常式。

        Returns:
            一個 json / 字典
        """
        resources = {}
        logger.info(
            f'開始讀取資源 resource://agent_cards/{card_name}'
        )
        resources['agent_card'] = (
            df.loc[
                df['card_uri'] == f'resource://agent_cards/{card_name}',
                'agent_card',
            ]
        ).to_list()

        return resources

    logger.info(
        f'代理卡 MCP 伺服器位於 {host}:{port}，傳輸方式為 {transport}'
    )
    mcp.run(transport=transport)
