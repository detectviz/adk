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
    """A tool to write the test plan into file

    Args:
        prd_id: Product requirement document ID
        test_cases: List of test case dictionaries that should conform to these fields:
            - test_case_key: str
            - test_type: Literal["manual","automatic"]
            - summary: str
            - preconditions: str
            - test_steps: str
            - expected_result: str
            - associated_requirements: str

    Returns:
        A message indicating success or failure of the validation and writing process
    """
    validated_test_cases = []
    validation_errors = []

    # Validate each test case
    for i, test_case in enumerate(test_cases):
        try:
            validated_test_case = TestPlan(**test_case)
            validated_test_cases.append(validated_test_case)
        except Exception as e:
            validation_errors.append(f"Error in test case {i + 1}: {str(e)}")

    # If validation errors exist, return error message
    if validation_errors:
        return {
            "status": "error",
            "message": "Validation failed",
            "errors": validation_errors,
        }

    # Write validated test cases to CSV
    try:
        # Convert validated test cases to a pandas DataFrame
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

        # Create DataFrame from the test case data
        df = pd.DataFrame(data)

        if not df.empty:
            # Create a temporary file with .csv extension
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
                # Write DataFrame to the temporary CSV file
                df.to_csv(temp_file.name, index=False)
                temp_file_path = temp_file.name

            # Read the file bytes from the temporary file
            with open(temp_file_path, "rb") as f:
                file_bytes = f.read()

            # Create an artifact with the file bytes
            await tool_context.save_artifact(
                filename=f"{prd_id}_test_plan.csv",
                artifact=types.Part.from_bytes(data=file_bytes, mime_type="text/csv"),
            )

            # Clean up the temporary file
            os.unlink(temp_file_path)

            return {
                "status": "success",
                "message": (
                    f"Successfully wrote {len(validated_test_cases)} test cases to "
                    f"CSV file: {prd_id}_test_plan.csv"
                ),
            }
        else:
            return {"status": "warning", "message": "No test cases to write"}
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred while writing to CSV: {str(e)}",
        }


root_agent = Agent(
    model="gemini-2.5-flash",
    name="qa_test_planner_agent",
    description="You are an expert QA Test Planner and Product Manager assistant",
    instruction=f"""
Help user search any product requirement documents on Confluence. Furthermore you also can provide the following capabilities when asked:
- evaluate product requirement documents and assess it, then give expert input on what can be improved 
- create a comprehensive test plan following Jira Xray mandatory field formatting, result showed as markdown table. Each test plan must also have explicit mapping on 
    which user stories or requirements identifier it's associated to 

Here is the Confluence space ID with it's respective document grouping:

- "{os.getenv("CONFLUENCE_PRD_SPACE_ID")}" : space to store Product Requirements Documents

Do not making things up, Always stick to the fact based on data you retrieve via tools.
""",
    tools=[confluence_tool, write_test_tool],
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_budget=2048,
        )
    ),
)
