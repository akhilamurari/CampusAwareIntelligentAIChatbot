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
    model = os.getenv("NIM_MODEL", "/data/shared/nobackup/Qwen2.5-7B-Instruct")
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

    # ── Sprint 4 (CF1CT-26 — Harshitha): Updated for expanded DB ──
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
        "The campus knowledge base contains these documents:\n"
        "1. Melbourne Campus Map — building locations, room numbers, campus layout\n"
        "2. Library Opening Hours — library hours, PLA availability, Bundoora library schedule\n"
        "3. La Trobe Student Safety Guide — emergency contacts, after hours helpline (1800 758 360), campus security (03 9479 2222), personal safety, road safety\n"
        "4. Rules of Residence 2026 — student residence rules, guest policies, disciplinary procedures\n"
        "5. Fees and Permits, Car Parking — parking fees, permits, transport, daily maximum charges\n"
        "6. Master of ICT Handbook — CRICOS code (061684F), course structure, credit points (195), subject codes, course coordinator (Lydia Cui), career outcomes\n"
        "\n"
        "When asked about ANY of the following — ALWAYS call campus_rag_tool IMMEDIATELY:\n"
        "WiFi, eduroam, maps, buildings, library, opening hours, campus services, CRICOS codes,\n"
        "course handbooks, fees, parking, permits, transport, residence rules, guest rules,\n"
        "safety, emergency, after hours, helpline, phone numbers, security, ICT program,\n"
        "subject codes, credit points, course coordinators, career outcomes, accreditation,\n"
        "ACS, study options, course duration, electives, thesis, project management.\n"
        "\n"
        "CRITICAL RULES FOR DOCUMENTS:\n"
        "1. IMMEDIATELY call campus_rag_tool — do NOT answer from memory.\n"
        "2. Use ONLY the exact information returned by campus_rag_tool.\n"
        "3. NEVER use your own training knowledge for campus-specific facts.\n"
        "4. If the tool returns a phone number, address or fee — use THAT exact value.\n"
        "5. Give a plain English answer based ONLY on retrieved documents.\n"
        "6. NEVER ask the user if they want information — just search and answer directly.\n"
        "\n"
        "7. When multiple phone numbers appear in the retrieved text, identify the SPECIFIC number requested by the user — do not return a different number from the same document.\n"
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