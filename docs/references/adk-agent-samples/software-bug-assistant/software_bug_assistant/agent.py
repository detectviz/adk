# Copyright 2025 Google LLC
#
# 根據 Apache 授權條款 2.0 版 (「授權」) 授權；
# 除非遵守授權，否則您不得使用此檔案。
# 您可以在以下網址取得授權副本：
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# 除非適用法律要求或書面同意，否則根據授權散佈的軟體
# 是以「現狀」為基礎散佈的，
# 不附帶任何明示或暗示的保證或條件。
# 請參閱授權以了解特定語言下的權限和
# 限制。

# 此檔案定義了主要的「軟體助理」代理 (Agent)。
# 它匯入了代理所需的指令、所有可用的工具，並將它們組合在一起以建立一個 Agent 實例。

from google.adk.agents import Agent

from .prompt import agent_instruction
from .tools.tools import get_current_date, langchain_tool, mcp_tools, search_tool, toolbox_tools


root_agent = Agent(
    model="gemini-2.5-flash",
    name="software_assistant",
    instruction=agent_instruction,
    tools=[get_current_date, search_tool, langchain_tool, *toolbox_tools, mcp_tools],
)
