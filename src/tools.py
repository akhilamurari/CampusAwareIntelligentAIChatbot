# tools.py
from langchain_core.tools import tool
from langchain_community.utilities.sql_database import SQLDatabase
from pydantic import BaseModel, Field
import os

DB_PATH = os.getenv("SQLITE_DB_PATH", "data/campus.db")
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}", sample_rows_in_table_info=3)

class SQLQuery(BaseModel):
    sql_query: str = Field(
        description=(
            "A valid SQL SELECT query to execute against the campus SQLite database. "
            "IMPORTANT: Use double-quotes for all string literals in WHERE clauses. "
            'Example: SELECT temperature_c FROM room_telemetry WHERE room_id = "Lab-101"'
        )
    )

@tool(args_schema=SQLQuery)
def campus_db_tool(sql_query: str):
    """Execute a SQL query to get room occupancy and sensor data from the Bundoora digital twin database."""
    print(f"\n[Backend DB Log] Executing SQL: {repr(sql_query)}")
    
    try:
        result = db.run(sql_query)
        return f"Execution successful.\nSQL Executed: {sql_query}\nResult Data: {result}"
    except Exception as e:
        return f"Execution failed.\nSQL Executed: {sql_query}\nError: {str(e)}"

@tool
def campus_rag_tool(query: str):
    """Search campus manuals for safety and comfort guidelines."""
    return "Campus Comfort Policy: Rooms are considered 'stuffy' if CO2 exceeds 1000 ppm."