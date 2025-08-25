from .prompt import IMAGEGEN_PROMPT
from google.adk.agents import Agent
from .tools.image_generation_tool import generate_images


image_generation_agent = Agent(
    name="image_generation_agent",
    model="gemini-2.0-flash",
    description=("您是使用 imagen 3 創作圖像的專家"),
    instruction=(IMAGEGEN_PROMPT),
    tools=[generate_images],
    output_key="output_image",
)
