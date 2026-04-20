# nodes.py
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from .state import AgentState
from .tools import campus_db_tool, campus_rag_tool
import os

load_dotenv()

# ── Sprint 4 (CF1CT-24 — Akhila): On-Premises NIM via OpenAI-compatible API ──
NIM_MODE = os.getenv("NIM_MODE", "cloud")

if NIM_MODE == "onprem":
    base_url = os.getenv("NIM_BASE_URL_ONPREM", "http://localhost:8000/v1")
    api_key = "not-required"
    model = os.getenv("NIM_MODEL", "/data/shared/nobackup/Qwen2_5-VL-7B-Instruct")
    print(f"🖥️  Agent using On-Premises NIM: {base_url}")
else:
    base_url = os.getenv("NIM_BASE_URL_CLOUD", "https://integrate.api.nvidia.com/v1")
    api_key = os.getenv("NIM_API_KEY", os.getenv("NVIDIA_API_KEY", ""))
    model = os.getenv("NIM_MODEL", "meta/llama-3.1-70b-instruct")
    print(f"☁️  Agent using Cloud API: {base_url}")

llm = ChatOpenAI(
    model=model,
    base_url=base_url,
    api_key=api_key,
    temperature=0
)

def assistant_node(state: AgentState):
    messages = state["messages"]

    system_instructions = SystemMessage(content=(
    "You are the Cisco-La Trobe CampusAware AI, a digital twin assistant for the Bundoora campus.\n"
    "When asked about room conditions, you MUST act as a Text-to-SQL agent.\n"
    "The SQLite database has a table named 'room_telemetry' with columns: timestamp, room_id, temperature_c, humidity_pct, co2_ppm, noise_db, light_lux, occupancy.\n"
    "Valid room_ids are: Library-L1, Library-L2, Library-L3, Lab-101, Lab-102, Lab-203, Lecture-Hall-A, Lecture-Hall-B, Cafeteria, Study-Room-1, Study-Room-2.\n"
    "Generate a complete, valid SQL SELECT statement and pass it to campus_db_tool. Map natural room names (e.g., 'study room 2') to the exact valid room_id.\n"
    'CRITICAL FORMATTING: Use double-quotes for all string literals in SQL. Example: SELECT temperature_c FROM room_telemetry WHERE room_id = "Lab-101"\n'
    "Always LIMIT results to 10 rows unless the user asks for more.\n"
    "In your final response to the user, provide ONLY the helpful plain English answer. Do not show the SQL query to the user.\n"
    "\n"
    "--- CONVERSATIONAL RULES ---\n"
    "If the user sends a casual greeting or asks a non-database question:\n"
    "1. Respond directly in character as the friendly, professional CampusAware AI.\n"
    "2. CRITICAL: DO NOT narrate your internal reasoning. DO NOT say 'No function call is required'. DO NOT explain your instructions to the user.\n"
    "3. Just output the final conversational response directly."
    ))

    llm_with_tools = llm.bind_tools([campus_db_tool, campus_rag_tool])
    response = llm_with_tools.invoke([system_instructions] + messages)
    
    return {"messages": [response]}