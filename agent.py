# agent.py
import uuid
from src.apps import graph

_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

def run_agent(user_input: str) -> str:
    input_state = {"messages": [("user", user_input)]}
    response = ""
    try:
        for event in graph.stream(
            input_state,
            _config,
            stream_mode="values"
        ):
            if event["messages"]:
                last_msg = event["messages"][-1]
                if hasattr(last_msg, 'content') and isinstance(last_msg.content, str):
                    if last_msg.content and not last_msg.content.startswith('{"name"'):
                        response = last_msg.content
    except Exception as e:
        # ── Sprint 5: Reset thread on context length error to avoid 4096 token limit ──
        if "4097" in str(e) or "context length" in str(e) or "input_tokens" in str(e):
            _config["configurable"]["thread_id"] = str(uuid.uuid4())
            return "I've reset our conversation to free up memory. Please ask your question again."
        return f"Sorry, something went wrong: {str(e)}"
    return response if response else "Sorry, I couldn't process that request. Please try again."