"""
tools.py
--------
LangGraph tool definitions for CampusAware AI.
Provides two tools:
    - campus_db_tool: Executes SQL queries against the IoT SQLite database
    - campus_rag_tool: Searches campus PDF documents using FAISS vector store

Fix CF1CT-49: NL2SQL module divergence fixed — SQL never shown to user,
consistent result formatting, error messages unified.

Fix CF1CT-45: FAISS index and embeddings now loaded once at module startup
and cached in memory — no longer reloaded on every query call.

Author: Jince, Akhila
"""

import os
from langchain_core.tools import tool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import BaseModel, Field


# ── Database Configuration ─────────────────────────────────────────────────────
DB_PATH = os.getenv("SQLITE_DB_PATH", "data/campus.db")
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}", sample_rows_in_table_info=3)


# ── CF1CT-45 Fix: Load FAISS index ONCE at startup, cache in memory ────────────
# Previously loaded on every call — now loaded once when tools.py is imported.
# This avoids repeated disk reads and embedding model initialisation.
# ──────────────────────────────────────────────────────────────────────────────
_embeddings = None
_vector_db = None

def _get_vector_db():
    """
    Load and cache the FAISS vector store and embeddings model.
    Only loads from disk on first call — subsequent calls use cached instance.

    Returns:
        FAISS: Cached vector store instance, or None if index not found
    """
    global _embeddings, _vector_db

    if _vector_db is not None:
        return _vector_db

    index_path = os.getenv("FAISS_INDEX_PATH", "data/campus_rag.index")

    if not os.path.exists(index_path):
        print(f"[RAG Tool] WARNING: FAISS index not found at {index_path}")
        return None

    try:
        print("[RAG Tool] Loading FAISS index into memory (first call only)...")
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        _vector_db = FAISS.load_local(
            index_path,
            _embeddings,
            allow_dangerous_deserialization=True
        )
        print("[RAG Tool] FAISS index loaded and cached successfully.")
        return _vector_db
    except Exception as e:
        print(f"[RAG Tool] ERROR loading FAISS index: {str(e)}")
        return None


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
        str: Query results as plain data — SQL is never exposed to the user
    """
    print(f"\n[DB Tool] Executing SQL: {repr(sql_query)}")

    # CF1CT-47 Fix: SQL Injection Prevention
    # Strip dangerous characters and keywords before execution
    import re
    dangerous_patterns = [
        r";\s*(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|TRUNCATE|REPLACE)",
        r"--",           # SQL comment injection
        r"/\*.*?\*/",   # Block comment injection
        r"xp_",          # Extended stored procedures
        r"EXEC\s*\(",    # Execute injection
        r"UNION\s+SELECT", # Union-based injection
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, sql_query, re.IGNORECASE):
            print(f"[DB Tool] BLOCKED suspicious query: {repr(sql_query)}")
            return "Error: Query contains forbidden patterns and was blocked for security."

    # CF1CT-49 Fix: Validate query is SELECT only — prevent any write operations
    cleaned = sql_query.strip().upper()
    if not cleaned.startswith("SELECT"):
        return "Error: Only SELECT queries are permitted."

    try:
        result = db.run(sql_query)

        # CF1CT-49 Fix: Return only the result data — never return raw SQL to user
        # Previously returned SQL in response which caused it to sometimes show to user
        if not result or result == "[]" or result == "":
            return "No data found for that query."

        return f"Query result: {result}"

    except Exception as e:
        error_msg = str(e)
        print(f"[DB Tool] ERROR: {error_msg}")

        # CF1CT-49 Fix: Unified consistent error messages
        if "no such table" in error_msg.lower():
            return "Database error: room_telemetry table not found. Check database setup."
        elif "no such column" in error_msg.lower():
            return f"Database error: invalid column name used. {error_msg}"
        else:
            return f"Database error: {error_msg}"


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

    Knowledge base contains 10 PDF documents indexed with FAISS.
    Uses sentence-transformers/all-MiniLM-L6-v2 for semantic search.
    Filters low-relevance chunks using L2 distance threshold.

    Args:
        query (str): Natural language question to search for in campus documents

    Returns:
        str: Relevant document excerpts with source metadata, or error message
    """
    # CF1CT-45 Fix: Use cached vector DB instead of reloading every call
    vector_db = _get_vector_db()

    if vector_db is None:
        return "RAG index not found. Please run ingest_pdfs.py first."

    try:
        # Retrieve top 8 chunks with scores — filter poor matches (L2 distance >= 1.5)
        l2_threshold = float(os.getenv("FAISS_L2_THRESHOLD", "1.5"))
        docs_with_scores = vector_db.similarity_search_with_score(query, k=8)
        docs = [doc for doc, score in docs_with_scores if score < l2_threshold]

        if not docs:
            return "No relevant campus documents found for that query."

        # Include source document name in each chunk for citation
        context = "\n---\n".join([
            f"[Source: {doc.metadata.get('source_doc', doc.metadata.get('source', '?'))}]\n{doc.page_content}"
            for doc in docs
        ])
        return context

    except Exception as e:
        error_msg = str(e)
        print(f"[RAG Tool] ERROR: {error_msg}")
        return f"RAG search error: {str(e)}"