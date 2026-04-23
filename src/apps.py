#from langgraph.graph import StateGraph, START
from langgraph.graph import StateGraph

from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState # Assuming state.py is in the same folder
from .nodes import assistant_node # Assuming nodes.py is in the same folder
from .tools import campus_db_tool, campus_rag_tool # Your mock tools

# 1. Initialize the Graph
workflow = StateGraph(AgentState)

# 2. Add Logic Nodes
workflow.add_node("assistant", assistant_node)
workflow.add_node("tools", ToolNode([campus_db_tool, campus_rag_tool]))

# 3. Define the Flow
#workflow.add_edge(START, "assistant")
workflow.set_entry_point("assistant")
workflow.add_conditional_edges("assistant", tools_condition)
workflow.add_edge("tools", "assistant")

# 4. Compile with Memory
# This allows the bot to remember the session context in the terminal
memory = MemorySaver()
# Change the variable name to 'graph'
graph = workflow.compile(checkpointer=memory)