# app.py
import streamlit as st
from agent import run_agent
# Page config
st.set_page_config(
    page_title="Campus-Aware AI Agent",
    page_icon="🎓",
    layout="centered"
)
st.title("🎓 Campus-Aware AI Agent")
st.caption(
    "Ask anything about La Trobe Bundoora campus"
)
# Sidebar with quick questions
with st.sidebar:
    st.header("💡 Try asking:")
    examples = [
    "Which room had high CO2?",
    "Find me a quiet room to study",
    "What is the average temperature in the library?",
    "How do I connect to eduroam WiFi?",
    "Which rooms are currently occupied?",
]
    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state["quick_q"] = example
    st.divider()
    if st.button("🗑️ Clear chat",
                  use_container_width=True):
        st.session_state["messages"] = []
# Initialise chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []
# Handle quick question from sidebar
if "quick_q" in st.session_state:
    prompt = st.session_state.pop("quick_q")
else:
    prompt = None
# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
# Chat input
user_input = st.chat_input(
    "Ask about the campus..."
) or prompt
if user_input:
    # Show user message
    st.session_state["messages"].append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.write(user_input)
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Searching campus data..."):
            import time
            start = time.time()
            response = run_agent(user_input)
            elapsed = time.time() - start
        st.write(response)
        st.caption(f"Response time: {elapsed:.1f}s")
    st.session_state["messages"].append(
        {"role": "assistant", "content": response}
    )