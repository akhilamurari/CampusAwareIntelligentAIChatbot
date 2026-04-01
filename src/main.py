import uuid
import sys
import os

# Ensure the root directory is in the path so we can find app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .apps import graph

def run_terminal_agent():
    print("\n" + "="*40)
    print(" BUNDOORA CAMPUSAWARE AI (TERMINAL) ")
    print("="*40)
    print("Type 'exit' to quit.\n")

    # A unique thread ID keeps the conversation 'memory' alive for this session
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    while True:
        user_input = input("Student > ")
        if user_input.lower() in ["exit", "quit", "q"]:
            break

        # Send input to the LangGraph
        input_state = {"messages": [("user", user_input)]}
        
        # We stream the values so you see the final processed response
        for event in graph.stream(input_state, config, stream_mode="values"):
            if event["messages"]:
                last_message = event["messages"][-1]
        
        print(f"Agent   > {last_message.content}\n")

if __name__ == "__main__":
    run_terminal_agent()