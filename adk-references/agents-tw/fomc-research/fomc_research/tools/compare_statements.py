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

"""FOMC 研究範例代理的 'compare_statements' 工具。"""

import logging

from google.adk.tools import ToolContext
from google.genai.types import Part

from ..shared_libraries import file_utils

logger = logging.getLogger(__name__)


async def compare_statements_tool(tool_context: ToolContext) -> dict[str, str]:
    """比較要求的和先前的聲明並產生 HTML 紅線。

    Args:
      tool_context: ToolContext 物件。

    Returns:
      一個包含 "status" 和 (可選) "error_message" 鍵的字典。
    """
    fed_hostname = "https://www.federalreserve.gov"

    reqd_statement_url = tool_context.state[
        "requested_meeting_statement_pdf_url"
    ]
    if not reqd_statement_url.startswith("https"):
        reqd_statement_url = fed_hostname + reqd_statement_url
    prev_statement_url = tool_context.state[
        "previous_meeting_statement_pdf_url"
    ]
    if not prev_statement_url.startswith("https"):
        prev_statement_url = fed_hostname + prev_statement_url

    # 從 URL 下載 PDF 至成品 (artifacts)
    reqd_pdf_path = await file_utils.download_file_from_url(
        reqd_statement_url, "curr.pdf", tool_context
    )
    prev_pdf_path = await file_utils.download_file_from_url(
        prev_statement_url, "prev.pdf", tool_context
    )

    if reqd_pdf_path is None or reqd_pdf_path is None:
        logger.error("下載檔案失敗，中止")
        return {
            "status": "error",
            "error_message": "下載聲明檔案失敗",
        }

    reqd_pdf_text = await file_utils.extract_text_from_pdf_artifact(
        reqd_pdf_path, tool_context
    )
    prev_pdf_text = await file_utils.extract_text_from_pdf_artifact(
        prev_pdf_path, tool_context
    )

    if reqd_pdf_text is None or prev_pdf_text is None:
        logger.error("從 PDF 擷取文字失敗，中止")
        return {
            "status": "error",
            "error_message": "從 PDF 擷取文字失敗",
        }

    await tool_context.save_artifact(
        filename="requested_statement_fulltext",
        artifact=Part(text=reqd_pdf_text),
    )
    await tool_context.save_artifact(
        filename="previous_statement_fulltext",
        artifact=Part(text=prev_pdf_text),
    )

    redline_html = file_utils.create_html_redline(reqd_pdf_text, prev_pdf_text)
    await file_utils.save_html_to_artifact(
        redline_html, "statement_redline", tool_context
    )

    return {"status": "ok"}
