"""
app.py
------
CampusAware AI — Mobile-friendly version.
IoT stats moved from sidebar to collapsible expander above chat
so mobile users can see everything without needing the sidebar.

Fix CF1CT-42: Unique thread_id per browser session.
Fix CF1CT-44: Context window reset handled gracefully.

Author: Tarun, Akhila
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from agent import run_agent
import os
import sqlite3
import pandas as pd
import uuid
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="CampusAware AI",
    page_icon="🎓",
    layout="centered"
)

# Auto-refresh every 30 seconds
st_autorefresh(interval=30000, limit=None, key="iot_refresh")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

* { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

/* User bubble */
.user-bubble-wrapper { display:flex; justify-content:flex-end; margin:6px 0; }
.user-bubble {
    background: #4B2E83; color: #fff;
    padding: 10px 16px;
    border-radius: 20px 20px 4px 20px;
    max-width: 75%; font-size: 0.9rem; line-height: 1.5; word-wrap: break-word;
}

/* Bot bubble */
.bot-bubble-wrapper { display:flex; justify-content:flex-start; align-items:flex-end; gap:8px; margin:6px 0; }
.bot-avatar {
    width:32px; height:32px; background:#4B2E83;
    border-radius:50%; display:flex; align-items:center;
    justify-content:center; font-size:1rem; flex-shrink:0;
}
.bot-bubble {
    background: #f0f2f6; color: #1a1a1a;
    padding: 10px 16px;
    border-radius: 20px 20px 20px 4px;
    max-width: 75%; font-size: 0.9rem; line-height: 1.5; word-wrap: break-word;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: #f0f2f6 !important; color: #1a1a1a !important;
    border: 1px solid #e0e0e0 !important; border-radius: 8px !important;
    font-size: 0.82rem !important; text-align: left !important;
    padding: 8px 12px !important; margin-bottom: 4px; transition: all 0.15s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #EDE9FE !important; border-color: #4B2E83 !important; color: #4B2E83 !important;
}

/* Chat input */
[data-testid="stChatInput"] > div { border-color: #4B2E83 !important; }
[data-testid="stChatInput"] > div:focus-within {
    border-color: #4B2E83 !important;
    box-shadow: 0 0 0 2px rgba(75,46,131,0.2) !important;
}
[data-testid="stChatInput"] textarea { caret-color: #4B2E83 !important; }
button[data-testid="stChatInputSubmitButton"] svg {
    fill: #4B2E83 !important; stroke: #4B2E83 !important;
}

/* IoT cards */
.iot-card {
    background: #f8f9fa; border: 1px solid #e0e0e0;
    border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;
    display: flex; align-items: center; justify-content: space-between;
}
.iot-card-label { font-size: 11px; color: #6b7280; font-weight: 500; }
.iot-card-value { font-size: 18px; font-weight: 700; font-family: monospace; }
.iot-card-sub   { font-size: 9px; color: #9ca3af; }

/* Quick action chips */
.stButton > button[kind="secondary"] {
    background: #EDE9FE !important; color: #4B2E83 !important;
    border: 1px solid rgba(75,46,131,0.3) !important;
    border-radius: 20px !important; font-size: 0.8rem !important;
    padding: 4px 12px !important; margin: 2px !important;
    transition: all 0.15s !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #4B2E83 !important; color: #fff !important;
}

/* App header */
.app-header { text-align:center; margin-bottom:0.8rem; }
.app-header h2 { color:#1a1a1a; font-weight:600; font-size:1.4rem; margin:0; }
.app-header p  { color:#6b7280; font-size:0.82rem; margin:4px 0 0 0; }
</style>
""", unsafe_allow_html=True)


# ── Load IoT Data ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_room_data():
    try:
        db_path = os.getenv("SQLITE_DB_PATH", "data/campus.db")
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("""
            SELECT room_id, temperature_c, humidity_pct, co2_ppm, noise_db, occupancy
            FROM room_telemetry
            WHERE timestamp=(SELECT MAX(timestamp) FROM room_telemetry)
            ORDER BY room_id
        """, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


# ── Session State ─────────────────────────────────────────────────────────────
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "quick_q" not in st.session_state:
    st.session_state["quick_q"] = None


# ── Sidebar — kept for desktop ────────────────────────────────────────────────
with st.sidebar:
    nim_mode = os.getenv("NIM_MODE", "cloud")
    if nim_mode == "onprem":
        st.success("● On-Premises — aiotcentre-03")
    else:
        st.info("● NVIDIA Cloud API")

    st.divider()
    st.markdown("**Try asking:**")
    examples = [
        "Find me a quiet room to study",
        "Which room has high CO2?",
        "What are parking fees?",
        "How do I connect to eduroam WiFi?",
        "What is the after hours helpline?",
    ]
    for example in examples:
        if st.button(example, use_container_width=True, key=f"sidebar_{example}"):
            st.session_state["quick_q"] = example

    st.divider()
    if st.button("🗑 Clear chat", use_container_width=True, key="sidebar_clear"):
        st.session_state["messages"] = []
        st.session_state["thread_id"] = str(uuid.uuid4())
        st.rerun()

    total_q = len([m for m in st.session_state["messages"] if m["role"] == "user"])
    st.caption(f"Questions asked: {total_q}")


# ── Main Page ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h2>🎓 CampusAware AI</h2>
    <p>La Trobe Bundoora Campus Assistant</p>
</div>
""", unsafe_allow_html=True)

# ── Live IoT Stats — collapsible expander (visible on mobile too) ─────────────
df = get_room_data()

with st.expander("📡 Live Room Stats — tap to view", expanded=False):
    if not df.empty:
        occupied       = int(df["occupancy"].sum())
        total          = len(df)
        vacant         = total - occupied
        avg_co2        = int(df["co2_ppm"].mean())
        avg_temp       = round(df["temperature_c"].mean(), 1)
        quietest       = df.loc[df["noise_db"].idxmin(), "room_id"]
        worst_co2_room = df.loc[df["co2_ppm"].idxmax(), "room_id"]
        worst_co2_val  = int(df["co2_ppm"].max())

        # 2-column grid for stats
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="iot-card">
                <div><div class="iot-card-label">🏢 Occupied</div><div class="iot-card-sub">of {total} rooms</div></div>
                <div class="iot-card-value" style="color:#EF4444">{occupied}</div>
            </div>
            <div class="iot-card">
                <div><div class="iot-card-label">💨 Avg CO₂</div><div class="iot-card-sub">campus-wide</div></div>
                <div class="iot-card-value" style="color:#F59E0B">{avg_co2} ppm</div>
            </div>
            <div class="iot-card">
                <div><div class="iot-card-label">🔇 Quietest Room</div><div class="iot-card-sub">best for studying</div></div>
                <div class="iot-card-value" style="color:#4B2E83;font-size:13px">{quietest}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="iot-card">
                <div><div class="iot-card-label">✅ Vacant</div><div class="iot-card-sub">available now</div></div>
                <div class="iot-card-value" style="color:#10B981">{vacant}</div>
            </div>
            <div class="iot-card">
                <div><div class="iot-card-label">🌡 Avg Temp</div><div class="iot-card-sub">campus-wide</div></div>
                <div class="iot-card-value" style="color:#3B82F6">{avg_temp}°C</div>
            </div>
            <div class="iot-card">
                <div><div class="iot-card-label">⚠️ High CO₂ Room</div><div class="iot-card-sub">{worst_co2_val} ppm</div></div>
                <div class="iot-card-value" style="color:#EF4444;font-size:13px">{worst_co2_room}</div>
            </div>
            """, unsafe_allow_html=True)
        st.caption("🔄 Auto-refreshes every 30s")
    else:
        st.warning("No sensor data available")

# ── Quick action chips — visible on mobile ────────────────────────────────────
st.markdown("**💬 Quick questions:**")
chip_cols = st.columns(2)
chip_examples = [
    ("🔇 Quiet room", "Find me a quiet room to study"),
    ("💨 High CO2", "Which room has high CO2?"),
    ("🅿️ Parking fees", "What are parking fees?"),
    ("📶 WiFi help", "How do I connect to eduroam WiFi?"),
    ("🚨 After hours", "What is the after hours helpline?"),
    ("📚 Library hours", "What are the library hours?"),
]
for i, (label, query) in enumerate(chip_examples):
    with chip_cols[i % 2]:
        if st.button(label, key=f"chip_{i}", use_container_width=True):
            st.session_state["quick_q"] = query

# Clear chat button on main page for mobile
if st.button("🗑 Clear chat", key="main_clear"):
    st.session_state["messages"] = []
    st.session_state["thread_id"] = str(uuid.uuid4())
    st.rerun()

st.divider()

# ── Resolve quick question ────────────────────────────────────────────────────
if st.session_state["quick_q"]:
    prompt = st.session_state.pop("quick_q")
else:
    prompt = None

# ── Chat History ──────────────────────────────────────────────────────────────
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

# ── Chat Input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask about the campus...") or prompt

if user_input:
    st.markdown(f"""
    <div class="user-bubble-wrapper">
        <div class="user-bubble">{user_input}</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state["messages"].append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        try:
            response = run_agent(user_input, st.session_state["thread_id"])

            if response == "context_limit_exceeded":
                st.session_state["thread_id"] = str(uuid.uuid4())
                st.session_state["messages"] = []
                response = "Our conversation got too long and I've reset the memory. Please ask your question again!"

        except Exception as e:
            err = str(e)
            if "401"          in err:        response = "API key error — check NIM configuration."
            elif "Connection" in err:         response = "Connection error — check SSH tunnel is running."
            elif "timeout"    in err.lower(): response = "Request timed out — server may be busy."
            else:                             response = f"Something went wrong: {err}"

    content = response.replace('\n', '<br>')
    st.markdown(f"""
    <div class="bot-bubble-wrapper">
        <div class="bot-avatar">🎓</div>
        <div class="bot-bubble">{content}</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state["messages"].append({"role": "assistant", "content": response})
    st.rerun()