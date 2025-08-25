from google.adk.agents import Agent
from . import config
from .prompt import CHECKER_PROMPT
from .tools.loop_condition_tool import check_tool_condition


# 此代理負責檢查條件並驗證評分過程
# 它使用 check_tool_condition 工具來評估評分過程是否應繼續
# 代理的輸出儲存在 "checker_output" 鍵中
checker_agent_instance = Agent(
    name="checker_agent",
    model=config.GENAI_MODEL,
    instruction=CHECKER_PROMPT,
    tools=[check_tool_condition],
    output_key="checker_output",
)
