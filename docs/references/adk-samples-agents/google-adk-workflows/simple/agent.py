"""
Simple Agent
Basic trip planner coordinator that manages sub-agents.
"""

from google.adk.agents import LlmAgent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all agents from common subagent file
from subagent import flight_agent, hotel_agent, sightseeing_agent

# Root agent acting as a Trip Planner coordinator
root_agent = LlmAgent(
    model=os.getenv('MODEL_NAME', 'gemini-2.0-flash'),
    name="TripPlanner",
    instruction="""
    Acts as a comprehensive trip planner.
    - Use the FlightAgent to find and book flights
    - Use the HotelAgent to find and book accommodation
    - Use the SightseeingAgent to find information on places to visit
    - Coordinate between all agents to provide complete trip planning
    - Ensure all user requirements are met across flight, hotel, and sightseeing needs
    """,
    sub_agents=[flight_agent, hotel_agent, sightseeing_agent] # The coordinator manages these sub-agents
) 