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

"""FOMC 研究範例代理的 'compute_rate_move_probability' 工具。"""

import logging

from google.adk.tools import ToolContext

from ..shared_libraries import price_utils

logger = logging.getLogger(__name__)


def compute_rate_move_probability_tool(
    tool_context: ToolContext,
) -> dict[str, str]:
    """計算所要求會議日期的利率變動機率。

    Args:
      tool_context: ToolContext 物件。

    Returns:
      一個包含 "status" 和 (可選) "error_message" 鍵的字典。
    """
    meeting_date = tool_context.state["requested_meeting_date"]
    logger.debug("正在計算 %s 的利率變動機率", meeting_date)
    prob_result = price_utils.compute_probabilities(meeting_date)
    if prob_result["status"] != "OK":
        return {"status": "ERROR", "message": prob_result["message"]}
    probs = prob_result["output"]
    logger.debug("利率變動機率：%s", probs)
    tool_context.state.update({"rate_move_probabilities": probs})
    return {"status": "OK"}
