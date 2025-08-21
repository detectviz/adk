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

"""FOMC 研究代理的回呼函式。"""

import logging
import time

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from typing import Any, Dict, Optional, Tuple
from google.adk.tools import BaseTool
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions.state import State
from google.adk.tools.tool_context import ToolContext
from jsonschema import ValidationError
from customer_service.entities.customer import Customer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

RATE_LIMIT_SECS = 60
RPM_QUOTA = 10


def rate_limit_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    """實作查詢速率限制的回呼函式。

    Args:
      callback_context: 代表作用中回呼上下文的 CallbackContext 物件。
      llm_request: 代表作用中 LLM 請求的 LlmRequest 物件。
    """
    for content in llm_request.contents:
        for part in content.parts:
            if part.text=="":
                part.text=" "

    
    

    now = time.time()
    if "timer_start" not in callback_context.state:

        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
        logger.debug(
            "rate_limit_callback [timestamp: %i, "
            "req_count: 1, elapsed_secs: 0]",
            now,
        )
        return

    request_count = callback_context.state["request_count"] + 1
    elapsed_secs = now - callback_context.state["timer_start"]
    logger.debug(
        "rate_limit_callback [timestamp: %i, request_count: %i,"
        " elapsed_secs: %i]",
        now,
        request_count,
        elapsed_secs,
    )

    if request_count > RPM_QUOTA:
        delay = RATE_LIMIT_SECS - elapsed_secs + 1
        if delay > 0:
            logger.debug("正在休眠 %i 秒", delay)
            time.sleep(delay)
        callback_context.state["timer_start"] = now
        callback_context.state["request_count"] = 1
    else:
        callback_context.state["request_count"] = request_count

    return

def validate_customer_id(customer_id: str, session_state: State) -> Tuple[bool, str]:
    """
        根據會話狀態中的客戶個人資料驗證客戶 ID。
        
        Args:
            customer_id (str): 要驗證的客戶 ID。
            session_state (State): 包含客戶個人資料的會話狀態。
        
        Returns:
            一個包含布林值 (True/False) 和字串的元組。
            當為 False 時，字串中包含錯誤訊息，以傳遞給模型決定
            要採取何種補救措施。
    """
    if 'customer_profile' not in session_state:
        return False, "未選取客戶個人資料。請選取一個個人資料。"

    try:
        # 我們從狀態中讀取個人資料，該狀態在會話開始時
        # 就已確定性地設定。
        c = Customer.model_validate_json(session_state['customer_profile'])
        if customer_id == c.customer_id:
            return True, None
        else:
            return False, "您不能使用客戶 ID " +customer_id+" 的工具，只能使用 "+c.customer_id+" 的工具。"
    except ValidationError as e:
        return False, "無法解析客戶個人資料。請重新載入客戶資料。"

def lowercase_value(value):
    """將字典轉換為小寫"""
    if isinstance(value, dict):
        return (dict(k, lowercase_value(v)) for k, v in value.items())
    elif isinstance(value, str):
        return value.lower()
    elif isinstance(value, (list, set, tuple)):
        tp = type(value)
        return tp(lowercase_value(i) for i in value)
    else:
        return value


# 回呼方法
def before_tool(
    tool: BaseTool, args: Dict[str, Any], tool_context: CallbackContext
):

    # 我確保代理傳送給工具的所有值都是小寫
    lowercase_value(args)

    # 有幾個工具需要 customer_id 作為輸入。我們不希望
    # 單獨依賴模型選擇正確的客戶 ID。我們對其進行驗證。
    # 替代方案：工具可以直接從狀態中擷取 customer_id。
    if 'customer_id' in args:
        valid, err = validate_customer_id(args['customer_id'], tool_context.state)
        if not valid:
            return err

    # 檢查下一個工具呼叫，然後採取相應的行動。
    # 根據被呼叫的工具的範例邏輯。
    if tool.name == "sync_ask_for_approval":
        amount = args.get("value", None)
        if amount <= 10:  # 範例業務規則
            return {
                "status": "approved",
                "message": "您可以批准此折扣；不需要經理。"
            }
        # 根據需要在此處新增更多邏輯檢查。

    if tool.name == "modify_cart":
        if (
            args.get("items_added") is True
            and args.get("items_removed") is True
        ):
            return {"result": "我已新增和移除所要求的商品。"}
    return None

def after_tool(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:

  # 批准後，我們在回呼中確定性地執行操作
  # 以在購物車中套用折扣。
  if tool.name == "sync_ask_for_approval":
    if tool_response['status'] == "approved":
        logger.debug("正在將折扣應用於購物車")
        # 實際對購物車進行變更

  if tool.name == "approve_discount":
    if tool_response['status'] == "ok":
        logger.debug("正在將折扣應用於購物車")
        # 實際對購物車進行變更

  return None

# 檢查客戶個人資料是否已載入為狀態。
def before_agent(callback_context: InvocationContext):
    # 在生產環境的代理中，這是在為代理建立
    # 會話時設定的。
    if "customer_profile" not in callback_context.state:
        callback_context.state["customer_profile"] = Customer.get_customer(
            "123"
        ).to_json()

    # logger.info(callback_context.state["customer_profile"])
