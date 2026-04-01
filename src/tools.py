# tools.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class SQLQuery(BaseModel):
    sql_query: str = Field(
        description=(
            "The raw SQL SELECT query to execute. "
            "CRITICAL: You MUST complete the entire query and ensure string literals are properly escaped in your JSON. "
            "Example: SELECT temperature FROM room_telemetry WHERE room_id = 'PW-202';"
        )
    )

@tool(args_schema=SQLQuery)
def campus_db_tool(sql_query: str):
    """Execute an SQL query to get room occupancy and sensor data from the Bundoora digital twin database."""
    
    # In a real implementation, you would use SQLAlchemy or psycopg2 here:
    # engine = create_engine("postgresql://user:pass@localhost/campus_db")
    # df = pd.read_sql(sql_query, engine)
    # return df.to_string()

    # MOCK DB EXECUTION:
    print(f"\n[Backend DB Log] Executing SQL: {sql_query}")
    
    if "PW-202" in sql_query.upper() or "PW202" in sql_query.upper():
        mock_data = "room_id: PW-202 | temperature: 22.5 | co2_ppm: 450 | occupancy: 12"
    else:
        mock_data = "0 rows returned."

    # We return both the SQL and the data so the LLM has context for its final response
    return f"Execution successful.\nSQL Executed: {sql_query}\nResult Data: {mock_data}"

@tool
def campus_rag_tool(query: str):
    """Search campus manuals for safety and comfort guidelines."""
    return "Campus Comfort Policy: Rooms are considered 'stuffy' if CO2 exceeds 1000 ppm."