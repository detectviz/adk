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

"""FOMC 研究範例代理的 'store_state' 工具"""

import logging
import typing

from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)


def store_state_tool(
    state: dict[str, typing.Any], tool_context: ToolContext
) -> dict[str, str]:
    """將新的狀態值儲存在 ToolContext 中。

    Args:
      state: 新狀態值的字典。
      tool_context: ToolContext 物件。

    Returns:
      一個包含 "status" 和 (可選) "error_message" 鍵的字典。
    """
    logger.info("store_state_tool(): %s", state)
    tool_context.state.update(state)
    return {"status": "ok"}
