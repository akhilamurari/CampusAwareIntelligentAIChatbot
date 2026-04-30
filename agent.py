"""
agent.py
--------
Entry point for running the CampusAware AI agent.
Provides the run_agent() function used by the Streamlit UI
to process user queries through the LangGraph workflow.

Author: Jince, Akhila
"""

import uuid
from src.apps import graph


# ── Session Configuration ──────────────────────────────────────────────────────
# Each session gets a unique thread_id for conversation memory isolation.
# This allows multiple users to have independent conversations.
# ──────────────────────────────────────────────────────────────────────────────

_config = {"configurable": {"thread_id": str(uuid.uuid4())}}


def run_agent(user_input: str) -> str:
    """
    Process a user query through the CampusAware LangGraph agent.

    Streams the agent response and returns the final text answer.
    Handles context length errors by resetting the conversation thread.

    Args:
        user_input (str): Natural language query from the user

    Returns:
        str: Agent response as plain English text, or error message

    Example:
        >>> response = run_agent("Which room had the highest CO2?")
        >>> print(response)
        "Library-L3 had the highest CO2 levels at 1322.33 ppm."
    """
    input_state = {"messages": [("user", user_input)]}
    response = ""

    try:
        # Stream agent events and extract final text response
        for event in graph.stream(
            input_state,
            _config,
            stream_mode="values"
        ):
            if event["messages"]:
                last_msg = event["messages"][-1]
                # Filter out tool call messages (start with JSON)
                if hasattr(last_msg, 'content') and isinstance(last_msg.content, str):
                    if last_msg.content and not last_msg.content.startswith('{"name"'):
                        response = last_msg.content

    except Exception as e:
        error_msg = str(e)

        # Reset thread if context length exceeded (4096 token limit for on-premises model)
        if "4097" in error_msg or "context length" in error_msg or "input_tokens" in error_msg:
            _config["configurable"]["thread_id"] = str(uuid.uuid4())
            return "I've reset our conversation to free up memory. Please ask your question again."

        return f"Sorry, something went wrong: {error_msg}"

    return response if response else "Sorry, I couldn't process that request. Please try again."