"""
agent.py
--------
Entry point for running the CampusAware AI agent.
Provides the run_agent() function used by the Streamlit UI
to process user queries through the LangGraph workflow.

Fix CF1CT-42: thread_id now passed per session from app.py
instead of being a global shared across all users.

Fix CF1CT-44: Context window managed by trimming oldest messages
when token limit is exceeded. Recursion limit set to 50.
"""

import uuid
from src.apps import graph


def run_agent(user_input: str, thread_id: str) -> str:
    """
    Process a user query through the CampusAware LangGraph agent.

    Streams the agent response and returns the final text answer.
    Handles context length errors by resetting the conversation thread.

    CF1CT-42 Fix: thread_id passed per session from app.py —
    each browser session has its own isolated conversation history.

    CF1CT-44 Fix: Context length errors handled gracefully —
    thread is reset and user is prompted to ask again.

    Args:
        user_input (str): Natural language query from the user
        thread_id  (str): Unique session thread ID from Streamlit session_state

    Returns:
        str: Agent response as plain English text, or error message

    Example:
        >>> response = run_agent("Which room had the highest CO2?", "abc-123")
        >>> print(response)
        "Library-L3 had the highest CO2 levels at 1322.33 ppm."
    """
    # CF1CT-42 Fix: Use per-session thread_id passed from app.py
    # CF1CT-44 Fix: recursion_limit=50 for sequential multi-tool calls
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 50
    }

    input_state = {"messages": [("user", user_input)]}
    response = ""

    try:
        # Stream agent events and extract final text response
        for event in graph.stream(
            input_state,
            config,
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
        if "4097" in error_msg or "context length" in error_msg or "input_tokens" in error_msg:
            return "context_limit_exceeded"

        return f"Sorry, something went wrong: {error_msg}"

    return response if response else "Sorry, I couldn't process that request. Please try again."