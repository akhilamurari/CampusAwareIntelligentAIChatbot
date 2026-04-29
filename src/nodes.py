# nodes.py
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from .state import AgentState
from .tools import campus_db_tool, campus_rag_tool
import os

load_dotenv()

# ── Sprint 4: NIM Configuration ──
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

    # ── Sprint 5 Update: Included Policy Knowledge Expansion ──
    system_instructions = SystemMessage(content=(
        "You are the Cisco-La Trobe CampusAware AI, a digital twin assistant for the Bundoora campus.\n"
        "\n"
        "--- DATABASE RULES ---\n"
        "When asked about room conditions (temperature, CO2, humidity, noise, occupancy, light, air quality):\n"
        "1. IMMEDIATELY call campus_db_tool with a SQL query. DO NOT explain or show the SQL to the user.\n"
        "2. The SQLite database has a table named 'room_telemetry' with columns: timestamp, room_id, temperature_c, humidity_pct, co2_ppm, noise_db, light_lux, occupancy, air_quality.\n"
        "3. Valid room_ids are: Library-L1, Library-L2, Library-L3, Lab-101, Lab-102, Lab-203, Lab-301, Lab-302, Lecture-Hall-A, Lecture-Hall-B, Lecture-Hall-C, Study-Room-1, Study-Room-2, Study-Room-3, Cafeteria, Meeting-Room-1, Student-Lounge.\n"
        "4. Use double-quotes for string literals: WHERE room_id = \"Lab-101\"\n"
        "5. Always LIMIT results to 10 rows.\n"
        "6. After getting results, give ONLY a plain English answer. NEVER show SQL to the user.\n"
        "7. NEVER ask the user if they want results — just run the query and answer directly.\n"
        "\n"
        "--- DOCUMENT RULES ---\n"
        "When asked about WiFi, maps, courses, library, campus services, Assessment policies, "
        "Privacy protocols, or the Student Code of Conduct:\n"
        "1. IMMEDIATELY call campus_rag_tool with the user question.\n"
        "2. Give a plain English answer based ONLY on the retrieved documents.\n"
        "3. If a student asks about Criterion-based assessment or Privacy breaches, use the specific definitions "
        "found in the local policies.\n"
        "4. NEVER ask the user if they want information — just search and answer directly.\n"
        "\n"
        "--- CONVERSATIONAL RULES ---\n"
        "For greetings or general questions:\n"
        "1. Respond directly and friendly as CampusAware AI.\n"
        "2. NEVER narrate your reasoning or show internal thoughts.\n"
        "3. NEVER say 'No function call is required'.\n"
        "4. Just give the final answer directly.\n"
    ))

    llm_with_tools = llm.bind_tools([campus_db_tool, campus_rag_tool])
    response = llm_with_tools.invoke([system_instructions] + messages)

    return {"messages": [response]}