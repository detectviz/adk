from google.adk.agents import Agent
from ... import config
from ..tools.fetch_policy_tool import get_policy
from .tools.get_images_tool import get_image
from .tools.set_score_tool import set_score
from .prompt import SCORING_PROMPT


scoring_images_prompt = Agent(
    name="scoring_images_prompt",
    model=config.GENAI_MODEL,
    description=(
        "您是根據提供給您的各種標準來評估和評分圖像的專家。"
    ),
    instruction=(SCORING_PROMPT),
    output_key="scoring",
    tools=[get_policy, get_image, set_score],
)
