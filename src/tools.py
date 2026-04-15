# src/tools.py
import os
import sqlite3
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import BaseModel, Field

# ─── DB Tool Schema ────────────────────────────────────
class SQLQuery(BaseModel):
    sql_query: str = Field(
        description=(
            "The raw SQL SELECT query to execute. "
            "CRITICAL: You MUST complete the entire query and ensure string literals are properly escaped in your JSON. "
            "Example: SELECT temperature FROM room_telemetry WHERE room_id = 'Library-L1';"
        )
    )

# ─── IoT Database Tool ─────────────────────────────────
@tool(args_schema=SQLQuery)
def campus_db_tool(sql_query: str):
    """Execute an SQL query to get room occupancy and sensor data from the Bundoora digital twin database."""
    print(f"\n[Backend DB Log] Executing SQL: {sql_query}")
    
    db_path = os.getenv("SQLITE_DB_PATH", "data/campus.db")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "No data found for this query."
        
        results = [dict(row) for row in rows]
        return f"SQL Executed: {sql_query}\nResult Data: {results}"
    except Exception as e:
        return f"Database error: {str(e)}"

# ─── RAG Tool ──────────────────────────────────────────
@tool
def campus_rag_tool(query: str):
    """Search campus PDF documents for information about campus facilities, policies and guidelines."""
    
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
        docs = vector_db.similarity_search(query, k=3)
        context = "\n---\n".join([doc.page_content for doc in docs])
        return context
    except Exception as e:
        return f"RAG search error: {str(e)}"