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

"""FOMC 研究範例代理的 'fetch_transcript' 工具"""

import logging

from google.adk.tools import ToolContext
from google.genai.types import Part

from ..shared_libraries import file_utils

logger = logging.getLogger(__name__)


async def fetch_transcript_tool(tool_context: ToolContext) -> dict:
    """從聯準會網站擷取聯準會新聞發布會的記錄。

    Args:
      tool_context: ToolContext 物件。

    Returns:
      一個包含 "status" 和 (可選) "error_message" 鍵的字典。
    """
    fed_hostname = "https://www.federalreserve.gov"
    transcript_url = tool_context.state["transcript_url"]
    if not transcript_url.startswith("https"):
        transcript_url = fed_hostname + transcript_url
    pdf_path = await file_utils.download_file_from_url(
        transcript_url, "transcript.pdf", tool_context
    )
    if pdf_path is None:
        logger.error("從 URL 下載 PDF 失敗，中止")
        return {
            "status": "error",
            "error_message": "從 GCS 下載 PDF 失敗",
        }

    text = await file_utils.extract_text_from_pdf_artifact(pdf_path, tool_context)
    filename = "transcript_fulltext"
    version = await tool_context.save_artifact(
        filename=filename, artifact=Part(text=text)
    )
    logger.info("已儲存成品 %s，版本 %i", filename, version)
    return {"status": "ok"}
