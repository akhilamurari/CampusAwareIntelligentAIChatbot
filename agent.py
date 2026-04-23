# agent.py
import uuid
from src.apps import graph

_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

def run_agent(user_input: str) -> str:
    input_state = {"messages": [("user", user_input)]}
    response = ""

    try:
        for event in graph.stream(input_state, _config, stream_mode="values"):
            if event.get("messages"):
                last_msg = event["messages"][-1]

                # Ensure valid content
                if hasattr(last_msg, "content") and isinstance(last_msg.content, str):
                    if last_msg.content and not last_msg.content.startswith('{"name"'):
                        response = last_msg.content

    except Exception as e:
        return f"⚠️ Sorry, something went wrong: {str(e)}"

    return response if response else "Sorry, I couldn't process that request. Please try again."