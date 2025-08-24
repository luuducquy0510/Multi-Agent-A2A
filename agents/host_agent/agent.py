from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
import json
import os
from dotenv import load_dotenv
load_dotenv()


# AGENT_MODEL = os.getenv("AGENT_MODEL")
# if not AGENT_MODEL:
#     raise ValueError("AGENT_MODEL is not set in the environment variables.")
# API_KEY = os.environ["GOOGLE_API_KEY"]
# if not API_KEY:
#     raise ValueError("API_KEY is not set in the environment variables.")

AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_API_BASE= os.getenv("AZURE_API_BASE")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")

root_agent = Agent(
    name="host_agent",
    model=LiteLlm(model="azure/gpt-4o-mini"), # LiteLLM model string format
    description="Coordinates travel planning by calling flight, stay, and activity agents.",
    instruction="You are the host agent responsible for orchestrating trip planning tasks. "
                "You call external agents to gather flights, stays, and activities, then return a final result."
)
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="host_app",
    session_service=session_service
)
USER_ID = "user_host"
SESSION_ID = "session_host"


async def execute(request):
    # Ensure session exists
    session_service.create_session(
        app_name="host_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"Plan a trip to {request['destination']} from {request['start_date']} to {request['end_date']} "
        f"within a total budget of {request['budget']} in USD. Call the flights, stays, and activities agents for results."
        "You must answer in user-friendly format, including all relevant details."
    )
    
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                if "summary" in parsed and isinstance(parsed["summary"], list):
                    print(f"summary: {parsed['summary']}")
                    # return {"summary": parsed["summary"]}
                else:
                    print("'summary' key missing or not a list in response JSON")
                    # return {"summary": response_text}  # fallback to raw text
            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                # return {"summary": response_text}  # fallback to raw text