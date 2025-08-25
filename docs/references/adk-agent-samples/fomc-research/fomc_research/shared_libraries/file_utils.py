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

"""fed_research_agent 的檔案相關公用程式函式。"""

import base64
import binascii
import io
import logging
import mimetypes
from collections.abc import Sequence

import diff_match_patch as dmp
import pdfplumber
import requests
from absl import app
from google.adk.tools import ToolContext
from google.genai.types import Blob, Part

logger = logging.getLogger(__name__)


async def download_file_from_url(
    url: str, output_filename: str, tool_context: ToolContext
) -> str:
    """從 URL 下載檔案並將其儲存在成品 (artifact) 中。

    Args:
      url: 要從中擷取檔案的 URL。
      output_filename: 要儲存檔案的成品名稱。
      tool_context: 工具上下文 (Tool Context)。

    Returns:
      成品名稱。
    """
    logger.info("正在從 %s 下載至 %s", url, output_filename)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        file_bytes = base64.b64encode(response.content)
        mime_type = response.headers.get(
            "Content-Type", mimetypes.guess_type(url)
        )
        artifact = Part(inline_data=Blob(data=file_bytes, mime_type=mime_type))
        await tool_context.save_artifact(filename=output_filename, artifact=artifact)
        logger.info("已從 %s 下載至成品 %s", url, output_filename)
        return output_filename

    except requests.exceptions.RequestException as e:
        logger.error("從 URL 下載檔案時發生錯誤：%s", e)
        return ""


async def extract_text_from_pdf_artifact(
    pdf_path: str, tool_context: ToolContext
) -> str:
    """從儲存在成品中的 PDF 檔案擷取文字"""
    try:
        pdf_artifact = await tool_context.load_artifact(pdf_path)
        if pdf_artifact and pdf_artifact.inline_data:
            logger.info("正在從 PDF 成品 %s 擷取文字", pdf_path)
            with io.BytesIO(
                base64.b64decode(pdf_artifact.inline_data.data)
            ) as pdf_file_obj:
                pdf_text = ""
                with pdfplumber.open(pdf_file_obj) as pdf:
                    for page in pdf.pages:
                        pdf_text += page.extract_text()
            return pdf_text
    except ValueError as e:
        logger.error("載入 PDF 成品時發生錯誤：%s", e)
        return ""


def create_html_redline(text1: str, text2: str) -> str:
    """建立 text1 和 text2 之間差異的 HTML 紅線文件。"""
    d = dmp.diff_match_patch()
    diffs = d.diff_main(text2, text1)
    d.diff_cleanupSemantic(diffs)

    html_output = ""
    for op, text in diffs:
        if op == -1:  # 刪除
            html_output += (
                f'<del style="background-color: #ffcccc;">{text}</del>'
            )
        elif op == 1:  # 插入
            html_output += (
                f'<ins style="background-color: #ccffcc;">{text}</ins>'
            )
        else:  # 未變更
            html_output += text

    return html_output


async def save_html_to_artifact(
    html_content: str, output_filename: str, tool_context: ToolContext
) -> str:
    """將 HTML 內容以 UTF-8 編碼儲存至成品。

    Args:
      html_content: 要儲存的 HTML 內容。
      output_filename: 要儲存 HTML 的成品名稱。

    Returns:
      成品名稱。
    """
    artifact = Part(text=html_content)
    await tool_context.save_artifact(filename=output_filename, artifact=artifact)
    logger.info("HTML 內容已成功儲存至 %s", output_filename)
    return output_filename


def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("過多的命令列引數。")


if __name__ == "__main__":
    app.run(main)
