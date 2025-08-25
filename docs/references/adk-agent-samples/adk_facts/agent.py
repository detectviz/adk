import os

from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import google_search


root_agent = Agent(
    name='facts_agent',
    model='gemini-2.5-flash-lite',
    description=('提供有趣事實的代理 (Agent)。'),
    instruction=('你是一個可以提供有趣事實的有用代理 (Agent)。'),
    tools=[google_search],
)

a2a_app = to_a2a(root_agent, port=int(os.getenv('PORT', '8001')))
