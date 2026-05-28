"""
agent.py
--------
Entry point for running the CampusAware AI agent.
Provides the run_agent() function used by the Streamlit UI
to process user queries through the LangGraph workflow.
"""
import uuid
from src.apps import graph


def run_agent(user_input: str, thread_id: str):
    """
    Process a user query through the CampusAware LangGraph agent.

    Args:
        user_input (str): Natural language query from the user
        thread_id  (str): Unique session thread ID from Streamlit session_state

    Yields:
        str: Accumulated agent response chunks or special status tokens
    """
    def _stream(tid: str):
        config = {
            "configurable": {"thread_id": tid},
            "recursion_limit": 10
        }
        input_state = {"messages": [("user", user_input)]}
        
        current_msg_id = None
        current_content = ""
        final_response = ""

        for msg, metadata in graph.stream(input_state, config, stream_mode="messages"):
            msg_type = type(msg).__name__
            if msg_type in ["AIMessageChunk", "AIMessage"]:
                if msg.id != current_msg_id:
                    current_msg_id = msg.id
                    current_content = ""
                
                if msg.content and isinstance(msg.content, str):
                    current_content += msg.content
                    stripped = current_content.strip()
                    
                    # Block all tool call JSON formats
                    if (stripped
                            and not stripped.startswith('{"name"')
                            and not stripped.startswith('[{"name"')
                            and not stripped.startswith('<tool_call>')
                            and '"campus_db_tool"' not in stripped
                            and '"campus_rag_tool"' not in stripped):
                        final_response = stripped
                        yield final_response
                    else:
                        yield "" # Clear text, indicates a tool call is being formulated

        if not final_response:
             yield "Sorry, I couldn't process that request. Please try again."

    try:
        yield from _stream(thread_id)
    except Exception as e:
        error_msg = str(e)

        if "4097" in error_msg or "context length" in error_msg or "input_tokens" in error_msg:
            try:
                new_thread = str(uuid.uuid4())
                yield f"__new_thread__{new_thread}"
                yield from _stream(new_thread)
            except Exception:
                yield "context_limit_exceeded"
        elif "401" in error_msg:
            yield "__error__API key error — check NIM configuration."
        elif "Connection" in error_msg:
            yield "__error__Connection error — check SSH tunnel is running."
        elif "timeout" in error_msg.lower():
            yield "__error__Request timed out — server may be busy."
        else:
            yield f"__error__Sorry, something went wrong: {error_msg}"