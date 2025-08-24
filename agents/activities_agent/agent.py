from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import StdioServerParameters
import json
import os
from dotenv import load_dotenv


load_dotenv()

USER_ID = "user_activities"
SESSION_ID = "session_activities"

# AGENT_MODEL = os.getenv("AGENT_MODEL")
# if not AGENT_MODEL:
#     raise ValueError("AGENT_MODEL is not set in the environment variables.")
# API_KEY = os.environ["GOOGLE_API_KEY"]
# if not API_KEY:
#     raise ValueError("API_KEY is not set in the environment variables.")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_API_BASE= os.getenv("AZURE_API_BASE")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")

SCRIPT_PATH = os.path.abspath("mcp_tools.py")

activities_agent = Agent(
    name="activities_agent",
    model=LiteLlm(model="azure/gpt-4o-mini"), # LiteLLM model string format
    description="Suggests interesting activities for the user at a destination.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 engaging tourist or cultural activities. "
        "For each activity, provide a name, a short description, price estimate, and duration in hours. "
        "You must use the tool to find real-time activity information."
        "You must provide sources to support the suggestions about activities (links, urls,...)"
    ),
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="python3",
                    args=[SCRIPT_PATH],
                ),
                timeout=60  # tăng lên 60s để tránh timeout 5s mặc định
            )
        )
    ]
)


session_service = InMemorySessionService()
runner = Runner(
    agent=activities_agent,
    app_name="activities_app",
    session_service=session_service
)


async def execute(request):
    
    await session_service.create_session(
        app_name="activities_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"User is flying to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']} in USD. Suggest 2-3 activities, each with name, description, price estimate, and duration. "
        f"Respond in JSON format using the key 'activities' with friendly format content."
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