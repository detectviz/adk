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

"""資料科學代理 V2：產生 nl2py 並使用程式碼直譯器 (Code Interpreter) 執行程式碼。"""
import os
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.callback_context import CallbackContext


from data_science.sub_agents.bqml.tools import (
    check_bq_models,
    execute_bqml_code,
    rag_response,
)
from .prompts import return_instructions_bqml


from data_science.sub_agents.bigquery.agent import database_agent as bq_db_agent
from data_science.sub_agents.bigquery.tools import (
    get_database_settings as get_bq_database_settings,
)


def setup_before_agent_call(callback_context: CallbackContext):
    """設定代理。"""

    # 在 session.state 中設定資料庫設定
    if "database_settings" not in callback_context.state:
        db_settings = dict()
        db_settings["use_database"] = "BigQuery"
        callback_context.state["all_db_settings"] = db_settings

    # 在指令中設定結構 (schema)
    if callback_context.state["all_db_settings"]["use_database"] == "BigQuery":
        callback_context.state["database_settings"] = get_bq_database_settings()
        schema = callback_context.state["database_settings"]["bq_ddl_schema"]

        callback_context._invocation_context.agent.instruction = (
            return_instructions_bqml()
            + f"""

   </此查詢的 BQML 參考>
    
    <相關資料的 BigQuery 結構 (schema) 及幾筆範例資料列>
    {schema}
    </相關資料的 BigQuery 結構 (schema) 及幾筆範例資料列>
    """
        )


async def call_db_agent(
    question: str,
    tool_context: ToolContext,
):
    """呼叫資料庫 (nl2sql) 代理的工具。"""
    print(
        "\n call_db_agent.use_database:"
        f' {tool_context.state["all_db_settings"]["use_database"]}'
    )
    database_agent = (
        bq_db_agent
        if tool_context.state["all_db_settings"]["use_database"] == "BigQuery"
        # else pg_db_agent
        else None
    )
    agent_tool = AgentTool(agent=database_agent)
    db_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )
    tool_context.state["db_agent_output"] = db_agent_output
    return db_agent_output


root_agent = Agent(
    model=os.getenv("BQML_AGENT_MODEL"),
    name="bq_ml_agent",
    instruction=return_instructions_bqml(),
    before_agent_callback=setup_before_agent_call,
    tools=[execute_bqml_code, check_bq_models, call_db_agent, rag_response],
)
