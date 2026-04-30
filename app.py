"""
app.py
------
Streamlit web interface for CampusAware AI chatbot.
Provides a chat UI with:
    - Custom styled chat bubbles (user right, bot left)
    - Sidebar with quick example questions
    - Connection status indicator (cloud/on-premises)
    - Question counter
    - Error handling for common connection issues

Author: Tarun, Akhila
"""

import streamlit as st
from agent import run_agent
import os
from dotenv import load_dotenv

load_dotenv()

# ── Page Configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CampusAware AI",
    page_icon="🎓",
    layout="centered"
)

# ── Custom CSS Styling ─────────────────────────────────────────────────────────
# Applies Inter font, chat bubble styles, sidebar button styles
# and chat input styling with La Trobe blue (#1f6feb) theme
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

* { font-family: 'Inter', sans-serif; }

#MainMenu, footer, header { visibility: hidden; }

/* User bubble — right aligned, blue */
.user-bubble-wrapper {
    display: flex;
    justify-content: flex-end;
    margin: 6px 0;
}
.user-bubble {
    background: #1f6feb;
    color: #ffffff;
    padding: 10px 16px;
    border-radius: 20px 20px 4px 20px;
    max-width: 65%;
    font-size: 0.9rem;
    line-height: 1.5;
    word-wrap: break-word;
}

/* Bot bubble — left aligned, light grey */
.bot-bubble-wrapper {
    display: flex;
    justify-content: flex-start;
    align-items: flex-end;
    gap: 8px;
    margin: 6px 0;
}
.bot-avatar {
    width: 32px;
    height: 32px;
    background: #1f6feb;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}
.bot-bubble {
    background: #f0f2f6;
    color: #1a1a1a;
    padding: 10px 16px;
    border-radius: 20px 20px 20px 4px;
    max-width: 65%;
    font-size: 0.9rem;
    line-height: 1.5;
    word-wrap: break-word;
}

/* Sidebar example question buttons */
[data-testid="stSidebar"] .stButton > button {
    background: #f0f2f6 !important;
    color: #1a1a1a !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    text-align: left !important;
    padding: 8px 12px !important;
    margin-bottom: 4px;
    transition: all 0.15s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #e8f0fe !important;
    border-color: #1f6feb !important;
    color: #1f6feb !important;
}

/* Chat input — blue border and caret */
[data-testid="stChatInput"] > div {
    border-color: #1f6feb !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #1f6feb !important;
    box-shadow: 0 0 0 2px #1f6feb33 !important;
}
[data-testid="stChatInput"] textarea {
    outline: none !important;
    box-shadow: none !important;
    caret-color: #1f6feb !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #1f6feb !important;
    box-shadow: none !important;
    outline: none !important;
}
button[data-testid="stChatInputSubmitButton"] {
    color: #1f6feb !important;
}
button[data-testid="stChatInputSubmitButton"]:hover {
    color: #1f6feb !important;
    background: #e8f0fe !important;
}
button[data-testid="stChatInputSubmitButton"] svg {
    fill: #1f6feb !important;
    stroke: #1f6feb !important;
}

/* Page header */
.app-header {
    text-align: center;
    margin-bottom: 1.5rem;
}
.app-header h2 {
    color: #1a1a1a;
    font-weight: 600;
    font-size: 1.4rem;
    margin: 0;
}
.app-header p {
    color: #6b7280;
    font-size: 0.82rem;
    margin: 4px 0 0 0;
}
</style>
""", unsafe_allow_html=True)

# ── Page Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h2>🎓 CampusAware AI</h2>
    <p>La Trobe Bundoora Campus Assistant</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:

    # Show connection status — cloud or on-premises
    nim_mode = os.getenv("NIM_MODE", "cloud")
    if nim_mode == "onprem":
        st.success("On-Premises — aiotcentre-03")
    else:
        st.info("NVIDIA Cloud API")

    st.divider()
    st.markdown("**Try asking:**")

    # Example questions for quick access
    examples = [
        "Which room had high CO2?",
        "Find me a quiet room to study",
        "What are my rights as a student?",
        "How do I connect to eduroam WiFi?",
        "What is the Code of Conduct?",
        "What are parking fees?",
        "Which rooms are currently occupied?",
        "What do I wear to graduation?",
    ]
    for example in examples:
        if st.button(example, use_container_width=True, key=f"ex_{example}"):
            st.session_state["quick_q"] = example

    st.divider()

    # Clear chat history
    if st.button("Clear chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

    # Display total questions asked this session
    if "messages" in st.session_state:
        total = len([m for m in st.session_state["messages"] if m["role"] == "user"])
        st.caption(f"Questions asked: {total}")

# ── Session State Initialisation ───────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Handle quick question selected from sidebar
if "quick_q" in st.session_state:
    prompt = st.session_state.pop("quick_q")
else:
    prompt = None

# ── Chat History Display ───────────────────────────────────────────────────────
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="user-bubble-wrapper">
            <div class="user-bubble">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        content = msg["content"].replace('\n', '<br>')
        st.markdown(f"""
        <div class="bot-bubble-wrapper">
            <div class="bot-avatar">🎓</div>
            <div class="bot-bubble">{content}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Chat Input & Response ──────────────────────────────────────────────────────
user_input = st.chat_input("Ask about the campus...") or prompt

if user_input:
    # Display user message
    st.markdown(f"""
    <div class="user-bubble-wrapper">
        <div class="user-bubble">{user_input}</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Get agent response with error handling
    with st.spinner("Thinking..."):
        try:
            response = run_agent(user_input)
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg:
                response = "API key error — please check your NIM configuration."
            elif "Connection" in error_msg:
                response = "Connection error — please check the SSH tunnel is running."
            elif "timeout" in error_msg.lower():
                response = "Request timed out — server may be busy, please try again."
            else:
                response = f"Something went wrong: {error_msg}"

    # Display bot response
    content = response.replace('\n', '<br>')
    st.markdown(f"""
    <div class="bot-bubble-wrapper">
        <div class="bot-avatar">🎓</div>
        <div class="bot-bubble">{content}</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state["messages"].append({"role": "assistant", "content": response})
    st.rerun()