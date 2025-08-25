# type: ignore
import logging
import os

import google.generativeai as genai

from a2a_mcp.common.types import ServerConfig


logger = logging.getLogger(__name__)


def init_api_key():
    """初始化 Google Generative AI 的 API 金鑰。"""
    if not os.getenv('GOOGLE_API_KEY'):
        logger.error('未設定 GOOGLE_API_KEY')
        raise ValueError('未設定 GOOGLE_API_KEY')

    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))


def config_logging():
    """設定基本日誌記錄。"""
    log_level = (
        os.getenv('A2A_LOG_LEVEL') or os.getenv('FASTMCP_LOG_LEVEL') or 'INFO'
    ).upper()
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO))


def config_logger(logger):
    """日誌記錄器特定設定，避免在啟用所有日誌記錄時造成混亂。"""
    # TODO: 以 env 取代
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def get_mcp_server_config() -> ServerConfig:
    """取得 MCP 伺服器設定。"""
    return ServerConfig(
        host='localhost',
        port=10100,
        transport='sse',
        url='http://localhost:10100/sse',
    )
