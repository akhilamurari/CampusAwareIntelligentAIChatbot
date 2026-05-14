"""
apps.py
-------
LangGraph workflow definition for CampusAware AI.
Builds the agent graph with:
    - Assistant node: LLM that processes queries and decides which tool to call
    - Tools node: Executes campus_db_tool (NL2SQL) or campus_rag_tool (RAG)
    - Memory: Maintains conversation history within a session

Graph Flow:
    START → assistant → tools (if tool call needed) → assistant → END
"""

from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from .state import AgentState
from .nodes import assistant_node
from .tools import campus_db_tool, campus_rag_tool
import os


# ── Build LangGraph Workflow ───────────────────────────────────────────────────
workflow = StateGraph(AgentState)

workflow.add_node("assistant", assistant_node)
workflow.add_node("tools", ToolNode([campus_db_tool, campus_rag_tool]))

workflow.add_edge(START, "assistant")
workflow.add_conditional_edges("assistant", tools_condition)
workflow.add_edge("tools", "assistant")

checkpoint_db = os.getenv("CHECKPOINT_DB_PATH", "data/checkpoints.db")
os.makedirs(os.path.dirname(checkpoint_db), exist_ok=True)

memory = SqliteSaver.from_conn_string(checkpoint_db)
graph = workflow.compile(checkpointer=memory)