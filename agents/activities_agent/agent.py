from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent_tools import web_search_tool
import json
import os
from dotenv import load_dotenv
load_dotenv()


AGENT_MODEL = os.getenv("AGENT_MODEL")
if not AGENT_MODEL:
    raise ValueError("AGENT_MODEL is not set in the environment variables.")
API_KEY = os.environ["GOOGLE_API_KEY"]
if not API_KEY:
    raise ValueError("API_KEY is not set in the environment variables.")

activities_agent = Agent(
    name="activities_agent",
    model=AGENT_MODEL,
    description="Suggests interesting activities for the user at a destination.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 engaging tourist or cultural activities. "
        "For each activity, provide a name, a short description, price estimate, and duration in hours. "
        "Respond in plain English. Keep it concise and well-formatted."
        "Use the web search tool to find real-time activity information."
    ),
    tools=[web_search_tool]
)


session_service = InMemorySessionService()
runner = Runner(
    agent=activities_agent,
    app_name="activities_app",
    session_service=session_service
)
USER_ID = "user_activities"
SESSION_ID = "session_activities"


async def execute(request):
    session_service.create_session(
        app_name="activities_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"User is flying to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']} in USD. Suggest 2-3 activities, each with name, description, price estimate, and duration. "
        # f"Respond in JSON format using the key 'activities' with a list of activity objects."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                if "activities" in parsed and isinstance(parsed["activities"], list):
                    return {"activities": parsed["activities"]}
                else:
                    print("'activities' key missing or not a list in response JSON")
                    return {"activities": response_text}  # fallback to raw text
            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"activities": response_text}  # fallback to raw text