"""
tools.py
--------
LangGraph tool definitions for CampusAware AI.
Provides two tools:
    - campus_db_tool: Executes SQL queries against the IoT SQLite database
    - campus_rag_tool: Searches campus PDF documents using FAISS vector store

Author: Jince, Akhila
"""

import os
import sqlite3
from langchain_core.tools import tool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import BaseModel, Field


# ── Database Configuration ─────────────────────────────────────────────────────
# SQLite database containing IoT sensor data for 17 campus rooms
# Default path: data/campus.db (override with SQLITE_DB_PATH env variable)
# ──────────────────────────────────────────────────────────────────────────────

DB_PATH = os.getenv("SQLITE_DB_PATH", "data/campus.db")
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}", sample_rows_in_table_info=3)


# ── SQL Query Schema ───────────────────────────────────────────────────────────

class SQLQuery(BaseModel):
    """Schema for validating SQL queries passed to campus_db_tool."""

    sql_query: str = Field(
        description=(
            "A valid SQL SELECT query to execute against the campus SQLite database. "
            "IMPORTANT: Use double-quotes for all string literals in WHERE clauses. "
            'Example: SELECT temperature_c FROM room_telemetry WHERE room_id = "Lab-101"'
        )
    )


# ── IoT Database Tool ──────────────────────────────────────────────────────────

@tool(args_schema=SQLQuery)
def campus_db_tool(sql_query: str) -> str:
    """
    Execute a SQL query against the campus IoT SQLite database.

    Use this tool for questions about room conditions including:
    temperature, humidity, CO2 levels, noise, light, occupancy and air quality.

    The database table 'room_telemetry' contains sensor readings for 17 rooms:
    Libraries (L1-L3), Labs (101-302), Lecture Halls (A-C),
    Study Rooms (1-3), Cafeteria, Meeting-Room-1, Student-Lounge.

    Args:
        sql_query (str): Valid SQL SELECT statement with double-quoted string literals

    Returns:
        str: Query results or error message
    """
    print(f"\n[DB Tool] Executing SQL: {repr(sql_query)}")

    try:
        result = db.run(sql_query)
        return f"Execution successful.\nSQL Executed: {sql_query}\nResult Data: {result}"
    except Exception as e:
        return f"Execution failed.\nSQL Executed: {sql_query}\nError: {str(e)}"


# ── RAG Document Search Tool ───────────────────────────────────────────────────

@tool
def campus_rag_tool(query: str) -> str:
    """
    Search La Trobe University campus documents using FAISS vector similarity search.

    Use this tool for ANY question about campus information including:
    - Phone numbers and emergency contacts
    - Library opening hours
    - Parking fees and permits
    - Campus WiFi (eduroam) connection
    - Master of ICT course details (CRICOS, credit points, coordinator)
    - Student residence rules and guest policies
    - Campus safety and security
    - Student charter, rights and responsibilities
    - Admissions requirements
    - Code of conduct

    Knowledge base contains 10 PDF documents with 246 indexed chunks.
    Uses sentence-transformers/all-MiniLM-L6-v2 for semantic search.

    Args:
        query (str): Natural language question to search for in campus documents

    Returns:
        str: Relevant document excerpts joined by separator, or error message
    """
    index_path = os.getenv("FAISS_INDEX_PATH", "data/campus_rag.index")

    if not os.path.exists(index_path):
        return "RAG index not found. Please run ingest_pdfs.py first."

    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_db = FAISS.load_local(
            index_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        # Retrieve top 5 most relevant document chunks
        docs = vector_db.similarity_search(query, k=5)
        context = "\n---\n".join([doc.page_content for doc in docs])
        return context
    except Exception as e:
        return f"RAG search error: {str(e)}"