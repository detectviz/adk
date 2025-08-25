from ... import config
from google.adk.agents import Agent
from .prompt import PROMPT
from ..tools.fetch_policy_tool import get_policy

image_generation_prompt_agent = Agent(
    name="image_generation_prompt_agent",
    model=config.GENAI_MODEL,
    description=("您是創建用於圖像生成的 imagen3 提示的專家"),
    instruction=(PROMPT),
    tools=[get_policy],
    output_key="imagen_prompt",  # gets stored in session.state
)
