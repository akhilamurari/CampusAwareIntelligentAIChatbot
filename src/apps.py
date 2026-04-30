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

Author: Jince, Akhila
"""

from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes import assistant_node
from .tools import campus_db_tool, campus_rag_tool


# ── Build LangGraph Workflow ───────────────────────────────────────────────────

# Initialise state graph with AgentState schema
workflow = StateGraph(AgentState)

# Add agent nodes
workflow.add_node("assistant", assistant_node)  # LLM decision node
workflow.add_node("tools", ToolNode([campus_db_tool, campus_rag_tool]))  # Tool execution node

# Define graph edges and flow
workflow.add_edge(START, "assistant")  # Start with assistant
workflow.add_conditional_edges("assistant", tools_condition)  # Route to tools if needed
workflow.add_edge("tools", "assistant")  # Return to assistant after tool execution

# ── Compile Graph with Memory ──────────────────────────────────────────────────
# MemorySaver maintains conversation history within a session
# Allows multi-turn conversations with context awareness
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)