from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioConnectionParams,
    StdioServerParameters,
)
from google.adk.planners import BuiltInPlanner
from google.genai import types
from dotenv import load_dotenv
import os
from pathlib import Path
from pydantic import BaseModel
from typing import Literal
import tempfile
import pandas as pd
from google.adk.tools import ToolContext


load_dotenv(dotenv_path=Path(__file__).parent / ".env")

confluence_tool = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uvx",
            args=[
                "mcp-atlassian",
                f"--confluence-url={os.getenv('CONFLUENCE_URL')}",
                f"--confluence-username={os.getenv('CONFLUENCE_USERNAME')}",
                f"--confluence-token={os.getenv('CONFLUENCE_TOKEN')}",
                "--enabled-tools=confluence_search,confluence_get_page,confluence_get_page_children",
            ],
            env={},
        ),
        timeout=60,
    ),
)


class TestPlan(BaseModel):
    test_case_key: str
    test_type: Literal["manual", "automatic"]
    summary: str
    preconditions: str
    test_steps: str
    expected_result: str
    associated_requirements: str


async def write_test_tool(
    prd_id: str, test_cases: list[dict], tool_context: ToolContext
):
    """一個將測試計畫寫入檔案的工具

    參數：
        prd_id：產品需求文件 ID
        test_cases：應符合以下欄位的測試案例字典清單：
            - test_case_key：字串
            - test_type：文字 ["manual","automatic"]
            - summary：字串
            - preconditions：字串
            - test_steps：字串
            - expected_result：字串
            - associated_requirements：字串

    傳回：
        一則訊息，指出驗證和寫入程序的成功或失敗
    """
    validated_test_cases = []
    validation_errors = []

    # 驗證每個測試案例
    for i, test_case in enumerate(test_cases):
        try:
            validated_test_case = TestPlan(**test_case)
            validated_test_cases.append(validated_test_case)
        except Exception as e:
            validation_errors.append(f"測試案例 {i + 1} 中發生錯誤：{str(e)}")

    # 如果存在驗證錯誤，則傳回錯誤訊息
    if validation_errors:
        return {
            "status": "error",
            "message": "驗證失敗",
            "errors": validation_errors,
        }

    # 將已驗證的測試案例寫入 CSV
    try:
        # 將已驗證的測試案例轉換為 pandas DataFrame
        data = []
        for tc in validated_test_cases:
            data.append(
                {
                    "Test Case ID": tc.test_case_key,
                    "Type": tc.test_type,
                    "Summary": tc.summary,
                    "Preconditions": tc.preconditions,
                    "Test Steps": tc.test_steps,
                    "Expected Result": tc.expected_result,
                    "Associated Requirements": tc.associated_requirements,
                }
            )

        # 從測試案例資料建立 DataFrame
        df = pd.DataFrame(data)

        if not df.empty:
            # 建立一個副檔名為 .csv 的暫存檔案
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
                # 將 DataFrame 寫入暫存 CSV 檔案
                df.to_csv(temp_file.name, index=False)
                temp_file_path = temp_file.name

            # 從暫存檔案讀取檔案位元組
            with open(temp_file_path, "rb") as f:
                file_bytes = f.read()

            # 使用檔案位元組建立成品
            await tool_context.save_artifact(
                filename=f"{prd_id}_test_plan.csv",
                artifact=types.Part.from_bytes(data=file_bytes, mime_type="text/csv"),
            )

            # 清除暫存檔案
            os.unlink(temp_file_path)

            return {
                "status": "success",
                "message": (
                    f"已成功將 {len(validated_test_cases)} 個測試案例寫入 "
                    f"CSV 檔案：{prd_id}_test_plan.csv"
                ),
            }
        else:
            return {"status": "warning", "message": "沒有要寫入的測試案例"}
    except Exception as e:
        return {
            "status": "error",
            "message": f"寫入 CSV 時發生錯誤：{str(e)}",
        }


root_agent = Agent(
    model="gemini-2.5-flash",
    name="qa_test_planner_agent",
    description="您是一位專業的 QA 測試計畫員和產品經理助理",
    instruction=f"""
協助使用者在 Confluence 上搜尋任何產品需求文件。此外，當被問及時，您還可以提供以下功能：
- 評估產品需求文件並對其進行評估，然後提供專家意見以說明可以改進之處
- 遵循 Jira Xray 強制性欄位格式建立全面的測試計畫，結果以 markdown 表格顯示。每個測試計畫還必須明確對應
    其關聯的使用者案例或需求識別碼

以下是 Confluence 空間 ID 及其各自的文件分組：

- "{os.getenv("CONFLUENCE_PRD_SPACE_ID")}"：用於儲存產品需求文件的空間

不要憑空捏造，始終根據您透過工具擷取的資料堅持事實。
""",
    tools=[confluence_tool, write_test_tool],
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_budget=2048,
        )
    ),
)
