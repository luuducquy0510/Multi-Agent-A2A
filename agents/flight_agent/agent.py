from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent_tools import web_search_tool
import os
from dotenv import load_dotenv
load_dotenv()


AGENT_MODEL = os.getenv("AGENT_MODEL")
if not AGENT_MODEL:
    raise ValueError("AGENT_MODEL is not set in the environment variables.")
API_KEY = os.environ["GOOGLE_API_KEY"]
if not API_KEY:
    raise ValueError("API_KEY is not set in the environment variables.")

flight_agent = Agent(
    name="flight_agent",
    model=AGENT_MODEL,
    description="Suggests flight options for a destination.",
    instruction=(
        "Given a destination, travel dates, and budget, suggest 1-2 realistic flight options. "
        "Include airline name, price, and departure time. Ensure flights fit within the budget."
        "You must use the web search tool to find real-time flight information."
        "You must provide sources to support the suggestions about flight (links, urls,...)"
    ),
    tools=[web_search_tool]
)

session_service = InMemorySessionService()
runner = Runner(
    agent=flight_agent,
    app_name="flight_app",
    session_service=session_service
)

USER_ID = "user_1"
SESSION_ID = "session_001"

async def execute(request):
    # 🔧 Ensure session is created before running the agent
    session_service.create_session(
        app_name="flight_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )

 
    prompt = (
    f"User is flying from {request['origin']} to {request['destination']} "
    f"from {request['start_date']} to {request['end_date']}, with a budget of {request['budget']} in USD. "
    "Suggest 2-3 realistic flight options. For each option, include airline, departure time, return time, "
    "price, and mention if it's direct or has layovers."
    )


    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            return {"flights": event.content.parts[0].text}