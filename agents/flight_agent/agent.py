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

USER_ID = "user_flight"
SESSION_ID = "session_flight"

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


flight_agent = Agent(
    name="flight_agent",
    model=LiteLlm(model="azure/gpt-4o-mini"), # LiteLLM model string format
    description="Suggests flight options for a destination.",
    instruction=(
        "Given a destination, travel dates, and budget, suggest 1-2 realistic flight options. "
        "Include airline name, price, and departure time. Ensure flights fit within the budget."
        "You must use the tool to find real-time flight information."
        "You must provide sources to support the suggestions about flight (links, urls,...)"
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
    agent=flight_agent,
    app_name="flight_app",
    session_service=session_service
)

async def execute(request):
    # 🔧 Ensure session is created before running the agent
    await session_service.create_session(
        app_name="flight_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    prompt = (
    f"User is flying from {request['origin']} to {request['destination']} "
    f"from {request['start_date']} to {request['end_date']}, with a budget of {request['budget']} in USD. "
    "Suggest 2-3 realistic flight options. For each option, include airline, departure time, return time, "
    "price, and mention if it's direct or has layovers."
    "Respond in JSON format using the key 'flights' with the content."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                if "flights" in parsed and isinstance(parsed["flights"], list):
                    return {"flights": parsed["flights"]}
                else:
                    print("'flights' key missing or not a list in response JSON")
                    return {"flights": response_text}  # fallback to raw text
            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"flights": response_text}  # fallback to raw text