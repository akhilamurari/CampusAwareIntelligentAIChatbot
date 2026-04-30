"""
state.py
--------
State schema definition for CampusAware AI LangGraph agent.
Defines the AgentState TypedDict that holds conversation history
across all nodes in the graph.

Author: Jince, Akhila
"""

from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    State schema for the CampusAware AI agent.

    Attributes:
        messages (list): Conversation history containing all user and
                        assistant messages. Uses add_messages reducer
                        to append new messages instead of overwriting.

    Example:
        >>> state = AgentState(messages=[])
        >>> state["messages"].append(HumanMessage(content="Hello"))
    """

    # add_messages reducer ensures messages are appended not overwritten
    # This enables multi-turn conversation memory
    messages: Annotated[list, add_messages]