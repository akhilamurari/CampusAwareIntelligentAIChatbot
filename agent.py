<<<<<<< HEAD
def run_agent(user_input):
    graph.invoke(...)
=======
# agent.py
import uuid
from src.apps import graph

# Keep the same thread ID for the whole session
# so the agent remembers the conversation
_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

def run_agent(user_input: str) -> str:
    """
    Takes user input and returns the agent's response.
    This is called by Tarun's app.py (Streamlit UI).
    """
    input_state = {"messages": [("user", user_input)]}
    
    response = ""
    for event in graph.stream(input_state, _config, stream_mode="values"):
        if event["messages"]:
            last_message = event["messages"][-1]
            response = last_message.content
    
    return response
>>>>>>> e0276af8f77df896b4a02c5678c1648c545f64b6
