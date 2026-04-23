# app.py
import streamlit as st
from agent import run_agent
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Campus-Aware AI Agent",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Campus-Aware AI Agent")
st.caption("Ask anything about La Trobe Bundoora campus")

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:

    # ── Connection Status (CF1CT-25 — Tarun) ──
    nim_mode = os.getenv("NIM_MODE", "cloud")
    if nim_mode == "onprem":
        st.success("🖥️ On-Premises NIM (aiotcentre-03)")
    else:
        st.info("☁️ NVIDIA Cloud API")

    st.divider()

    st.header("💡 Try asking:")
    examples = [
        "Which room had high CO2?",
        "Find me a quiet room to study",
        "What is the average temperature in the library?",
        "How do I connect to eduroam WiFi?",
        "Which rooms are currently occupied?",
        "What is the noise level in the cafeteria?",
        "Which room has the best air quality?",
    ]
    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state["quick_q"] = example

    st.divider()

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

    st.divider()

    # ── Session stats ──
    if "messages" in st.session_state:
        total = len([m for m in st.session_state["messages"] if m["role"] == "user"])
        st.caption(f"💬 Questions asked: {total}")

# ── Initialise chat history ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ── Handle quick question from sidebar ────────────────────────────
if "quick_q" in st.session_state:
    prompt = st.session_state.pop("quick_q")
else:
    prompt = None

# ── Display chat history ───────────────────────────────────────────
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        # Show timestamp if available
        if "time" in msg:
            st.caption(f"🕐 {msg['time']}")
        # Show response time for assistant messages
        if msg["role"] == "assistant" and "elapsed" in msg:
            st.caption(f"⚡ Response time: {msg['elapsed']:.1f}s")

# ── Chat input ─────────────────────────────────────────────────────
user_input = st.chat_input("Ask about the campus...") or prompt

if user_input:
    # Timestamp
    now = time.strftime("%H:%M:%S")

    # Show user message
    st.session_state["messages"].append({
        "role": "user",
        "content": user_input,
        "time": now
    })
    with st.chat_message("user"):
        st.write(user_input)
        st.caption(f"🕐 {now}")

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking... querying campus data..."):
            start = time.time()
            try:
                response = run_agent(user_input)
                elapsed = time.time() - start
                st.write(response)
                st.caption(f"⚡ Response time: {elapsed:.1f}s")

                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": response,
                    "elapsed": elapsed,
                    "time": time.strftime("%H:%M:%S")
                })

            except Exception as e:
                elapsed = time.time() - start
                error_msg = str(e)

                if "401" in error_msg:
                    st.error("🔑 API key error — please check your NIM configuration")
                elif "Connection" in error_msg:
                    st.error("🔌 Connection error — please check SSH tunnel is running")
                elif "timeout" in error_msg.lower():
                    st.error("⏱️ Request timed out — server may be busy, please try again")
                else:
                    st.error(f"❌ Something went wrong: {error_msg}")

                st.caption(f"⚡ Response time: {elapsed:.1f}s")