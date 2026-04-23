<<<<<<< Updated upstream
=======
#<<<<<<< HEAD
def run_agent(user_input):
    graph.invoke(...)
#=======
>>>>>>> Stashed changes
# agent.py
import uuid
from src.apps import graph

_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

def run_agent(user_input: str) -> str:
    input_state = {"messages": [("user", user_input)]}
    response = ""
<<<<<<< Updated upstream
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
        return f"Sorry, something went wrong: {str(e)}"

    return response if response else "Sorry, I couldn't process that request. Please try again."
=======
    for event in graph.stream(input_state, _config, stream_mode="values"):
        if event["messages"]:
            last_message = event["messages"][-1]
            response = last_message.content
    
    return response
#>>>>>>> e0276af8f77df896b4a02c5678c1648c545f64b6
>>>>>>> Stashed changes
