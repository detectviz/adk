"""
Common SubAgents File
Contains hotel_agent, sightseeing_agent, and trip_summary_agent
that can be used by dispatcher, parallel, and self_critic agents.
"""

from google.genai.types import Content, Part
from typing import AsyncGenerator
from google.adk.agents import  LlmAgent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flight Agent
flight_agent = LlmAgent(
    model=os.getenv('MODEL_NAME', 'gemini-2.0-flash'),
    name="FlightAgent",
    description="Flight booking agent",
    instruction="""You are a flight booking agent.
    - You take any flight booking or confirmation request
    - You check for available flights based on user preferences
    - You return a valid JSON with flight booking and confirmation details, including flight number, departure and arrival times, airline, price, and status based on user request.
    - If the user does not provide specific details, make reasonable assumptions about the flight and booking details.
    """
)

# Hotel Agent
hotel_agent = LlmAgent(
    model=os.getenv('MODEL_NAME', 'gemini-2.0-flash'),
    name="HotelAgent",
    description="Hotel booking agent",
    instruction="""You are a hotel booking agent.
    - You take any hotel booking or confirmation request
    - Always return a valid JSON with hotel booking and confirmation details, including hotel name, check-in and check-out dates, room type, price, and status based on user request.
    - If the user does not provide specific details, make reasonable assumptions about the hotel and booking details.
    """
)

# Sightseeing Agent
sightseeing_agent = LlmAgent(
    model=os.getenv('MODEL_NAME', 'gemini-2.0-flash'),
    name="SightseeingAgent",
    description="Sightseeing information agent",
    instruction="""You are a sightseeing information agent.
    - You take any sightseeing request and suggest only the top 2 best places to visit, timings, and any other relevant details.
    - Always return a valid JSON with sightseeing information, including places to visit, timings, and any other relevant details based on user request.
    - If the user does not provide specific details, make reasonable assumptions about the sightseeing options available.
    """
)

# Trip Summary Agent
trip_summary_agent = LlmAgent(
    model=os.getenv('MODEL_NAME', 'gemini-2.0-flash'),
    name="TripSummaryAgent",
    instruction="Summarize the trip details from the flight, hotel, and sightseeing agents. Summarise JSON responses into a single summary document with all trip information like a travel itinerary. The summary should be well-structured and clearly present all trip details in an organized manner using text format only like a travel itinerary.",
    output_key="trip_summary"
)

 