# Multi-Agent-A2A

# 🤖 Multi-Agent A2A Project (Google ADK)

This project demonstrates a multi-agent system using Google's Agent Development Kit (ADK). Each agent serves a different purpose (e.g., host planning, flight booking, activity suggestions) and communicates via a common A2A protocol.

---

## 🚀 Getting Started

### 1. Clone the Repo

git clone https://github.com/luuducquy0510/Multi-Agent-A2A.git
cd Multi-Agent-A2A

### 2. Setup environment

python3 -m venv adk_demo
source adk_demo/bin/activate
pip install -r requirements.txt

### 3. Add your API key

GOOGLE_API_KEY="your-key"
AGENT_MODEL="your-model"

### 4. Run the Agent and UI

uvicorn agents.host_agent.__main__:app --port 8080 &
uvicorn agents.flight_agent.__main__:app --port 8081 &
uvicorn agents.stay_agent.__main__:app --port 8082 &
uvicorn agents.activities_agent.__main__:app --port 8083 &


streamlit run streamlit_app.py
