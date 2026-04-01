from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Annotated with add_messages so history is appended, not overwritten
    messages: Annotated[list, add_messages]