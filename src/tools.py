# src/tools.py
import os
import sqlite3
from langchain_core.tools import tool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import BaseModel, Field

# Ensure path is relative to the project root
DB_PATH = os.getenv("SQLITE_DB_PATH", "data/campus.db")
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}", sample_rows_in_table_info=3)

# ─── DB Tool Schema ────────────────────────────────────
class SQLQuery(BaseModel):
    sql_query: str = Field(
        description=(
            "A valid SQL SELECT query to execute against the campus SQLite database. "
            "IMPORTANT: Use double-quotes for all string literals in WHERE clauses. "
            'Example: SELECT temperature_c FROM room_telemetry WHERE room_id = "Lab-101"'
        )
    )

# ─── IoT Database Tool ─────────────────────────────────
@tool(args_schema=SQLQuery)
def campus_db_tool(sql_query: str):
    """Execute a SQL query to get room occupancy and sensor data from the Bundoora digital twin database."""
    print(f"\n[Backend DB Log] Executing SQL: {repr(sql_query)}")
    
    try:
        result = db.run(sql_query)
        return f"Execution successful.\nSQL Executed: {sql_query}\nResult Data: {result}"
    except Exception as e:
        return f"Execution failed.\nSQL Executed: {sql_query}\nError: {str(e)}"

# ─── RAG Tool ──────────────────────────────────────────
@tool
def campus_rag_tool(query: str):
    """Search campus PDF documents for information about campus facilities, policies and guidelines."""
    
    # Matches the path used in your ingest_pdfs.py
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
        # Retrieve top 3 relevant chunks
        docs = vector_db.similarity_search(query, k=3)
        context = "\n---\n".join([doc.page_content for doc in docs])
        return context
    except Exception as e:
        return f"RAG search error: {str(e)}"