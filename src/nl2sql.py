# src/nl2sql.py
import sqlite3
import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

# ─── Config ────────────────────────────────────────────
DB_PATH = os.getenv("SQLITE_DB_PATH", "data/campus.db")

# ─── Database Schema ───────────────────────────────────
DB_SCHEMA = """
Table: room_telemetry
Columns:
  - timestamp (DATETIME): when the reading was taken
  - room_id (TEXT): room identifier e.g. 'Library-L1', 'Lab-101'
  - temperature_c (REAL): temperature in celsius
  - humidity_pct (REAL): humidity percentage
  - co2_ppm (REAL): CO2 level in parts per million
  - noise_db (REAL): noise level in decibels
  - light_lux (REAL): light intensity in lux
  - occupancy (INTEGER): 1 if occupied, 0 if not
  - air_quality (TEXT): air quality category — 'Good', 'Moderate', or 'Poor'

Available room_ids:
  Library-L1, Library-L2, Library-L3,
  Lab-101, Lab-102, Lab-203, Lab-301, Lab-302,
  Lecture-Hall-A, Lecture-Hall-B, Lecture-Hall-C,
  Cafeteria, Study-Room-1, Study-Room-2, Study-Room-3,
  Meeting-Room-1, Student-Lounge
"""

# ─── LLM Setup ─────────────────────────────────────────
llm = ChatNVIDIA(
    model="meta/llama-3.1-70b-instruct",
    temperature=0
)

# ─── Generate SQL ──────────────────────────────────────
def generate_sql(user_question: str) -> str:
    system_prompt = f"""You are an expert SQL generator for a campus IoT database.
Given a natural language question, generate a valid SQLite SQL query.

Database Schema:
{DB_SCHEMA}

Rules:
- Only generate SELECT statements
- Use DATE(timestamp) for date comparisons
- For "this morning" use: TIME(timestamp) >= '06:00:00' AND TIME(timestamp) <= '12:00:00' AND DATE(timestamp) = DATE('now')
- For "yesterday" use: DATE(timestamp) = DATE('now', '-1 day')
- For time comparisons NEVER use 'now' with commas — always use DATE() or TIME() functions
- Always LIMIT results to 10 unless asked for more
- Return ONLY the SQL query, nothing else
- Do not include markdown or backticks
- For comfort queries (cool, quiet) use relaxed thresholds:
  temperature_c < 24 for cool
  noise_db < 50 for quiet
  occupancy = 0 for empty
"""
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_question)
    ]
    response = llm.invoke(messages)
    return response.content.strip()

# ─── Execute SQL ───────────────────────────────────────
def execute_sql(sql_query: str) -> list:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        return [{"error": str(e)}]

# ─── Format Results ────────────────────────────────────
def format_results(results: list, question: str) -> str:
    if not results:
        return "No data found for your query."
    if "error" in results[0]:
        return f"Database error: {results[0]['error']}"

    system_prompt = """You are a helpful campus assistant.
Convert the database query results into a clear friendly 
plain English response. Be concise and informative."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""
Question: {question}
Database Results: {results}
Please provide a clear answer based on these results.
""")
    ]
    response = llm.invoke(messages)
    return response.content.strip()

# ─── Main Pipeline ─────────────────────────────────────
def nl2sql(user_question: str) -> dict:
    """
    Full pipeline: natural language → SQL → results → plain English

    Args:
        user_question: Natural language question about campus data

    Returns:
        dict with sql_query, raw_results, and answer
    """
    # Step 1: Generate SQL
    sql_query = generate_sql(user_question)
    print(f"\n[NL2SQL] Generated SQL: {sql_query}")

    # Step 2: Execute SQL
    raw_results = execute_sql(sql_query)
    print(f"[NL2SQL] Raw Results: {raw_results}")

    # Step 3: Format to plain English
    answer = format_results(raw_results, user_question)

    return {
        "sql_query": sql_query,
        "raw_results": raw_results,
        "answer": answer
    }

# ─── Test ──────────────────────────────────────────────
if __name__ == "__main__":
    test_questions = [
        "Which room had the highest CO2 levels?",
        "What is the average temperature in the library?",
        "Which rooms were occupied this morning?",
        "Find me a cool quiet room to study in",
    ]

    print("=" * 60)
    print("NL2SQL PIPELINE TEST")
    print("=" * 60)

    for question in test_questions:
        print(f"\n❓ Question: {question}")
        result = nl2sql(question)
        print(f"🔍 SQL: {result['sql_query']}")
        print(f"✅ Answer: {result['answer']}")
        print("-" * 60)