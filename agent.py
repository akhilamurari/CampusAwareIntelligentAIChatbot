"""
agent.py
--------
Entry point for running the CampusAware AI agent.
Provides the run_agent() function used by the Streamlit UI
to process user queries through the LangGraph workflow.
Fix CF1CT-42: thread_id now passed per session from app.py.
Fix CF1CT-44: On context limit, automatically retries with
fresh thread so user gets an answer without seeing an error.
Fix CF1CT-50: Filter too aggressive — was blocking valid responses.
Fix CF1CT-51: Debug logging added to trace tool call routing.
"""
import uuid
from src.apps import graph


def run_agent(user_input: str, thread_id: str) -> str:
    """
    Process a user query through the CampusAware LangGraph agent.
    On context length exceeded — automatically retries with a new
    thread_id so user gets an answer without manual intervention.

    Args:
        user_input (str): Natural language query from the user
        thread_id  (str): Unique session thread ID from Streamlit session_state

    Returns:
        str: Agent response as plain English text, or error message
    """
    def _invoke(tid: str) -> str:
        config = {
            "configurable": {"thread_id": tid},
            "recursion_limit": 10
        }
        input_state = {"messages": [("user", user_input)]}
        response = ""

        for event in graph.stream(input_state, config, stream_mode="values"):
            if event["messages"]:
                last_msg = event["messages"][-1]
                msg_type = type(last_msg).__name__

                # Debug logging — remove after fix confirmed
                print(f"[DEBUG] msg_type={msg_type}")
                print(f"[DEBUG] content={repr(last_msg.content)}")
                print(f"[DEBUG] tool_calls={getattr(last_msg, 'tool_calls', 'N/A')}")

                if msg_type == "AIMessage":
                    content = last_msg.content
                    if content and isinstance(content, str):
                        stripped = content.strip()
                        if (stripped
                                and not stripped.startswith('{"name"')
                                and not stripped.startswith('[{"name"')):
                            response = stripped

        return response

    try:
        response = _invoke(thread_id)
    except Exception as e:
        error_msg = str(e)

        if "4097" in error_msg or "context length" in error_msg or "input_tokens" in error_msg:
            try:
                new_thread = str(uuid.uuid4())
                response = _invoke(new_thread)
                return f"__new_thread__{new_thread}__{response}"
            except Exception:
                return "context_limit_exceeded"
        elif "401" in error_msg:
            return "API key error — check NIM configuration."
        elif "Connection" in error_msg:
            return "Connection error — check SSH tunnel is running."
        elif "timeout" in error_msg.lower():
            return "Request timed out — server may be busy."
        else:
            return f"Sorry, something went wrong: {error_msg}"

    return response if response else "Sorry, I couldn't process that request. Please try again."