"""
app.py
"""

import streamlit as st
from agent import run_agent
import os
import sqlite3
import pandas as pd
import uuid
import time
import base64
import pathlib
from dotenv import load_dotenv
from auth import (init_auth_table, login_student, register_student,
                  create_session_token, validate_session_token,
                  delete_session_token)

load_dotenv()

st.set_page_config(
    page_title="CampusAware AI",
    page_icon="🎓",
    layout="centered"
)

# ── Initialise auth table on startup ──────────────────────────────────────────
init_auth_table()

# ── Session State Init ─────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "student_id" not in st.session_state:
    st.session_state["student_id"] = ""
if "full_name" not in st.session_state:
    st.session_state["full_name"] = ""
if "session_token" not in st.session_state:
    st.session_state["session_token"] = ""
if "last_active" not in st.session_state:
    st.session_state["last_active"] = 0.0

# ── Restore session from URL token on refresh ──────────────────────────────────
if not st.session_state["authenticated"]:
    url_token = st.query_params.get("token", "")
    if url_token:
        student_id, full_name = validate_session_token(url_token)
        if student_id:
            st.session_state["authenticated"] = True
            st.session_state["student_id"]    = student_id
            st.session_state["full_name"]      = full_name
            st.session_state["session_token"]  = url_token
            st.session_state["last_active"]    = time.time()
            if "thread_id" not in st.session_state:
                st.session_state["thread_id"] = str(uuid.uuid4())
            if "messages" not in st.session_state:
                st.session_state["messages"] = []

# ── Login / Register Page ──────────────────────────────────────────────────────
if not st.session_state["authenticated"]:
    # Load logo for the login page branding
    _login_logo_path = pathlib.Path(__file__).parent / "assets" / "latrobe_logo.png"
    _login_logo_b64 = base64.b64encode(_login_logo_path.read_bytes()).decode()

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * {{ font-family: 'Inter', sans-serif; }}
    #MainMenu, footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    [data-testid="stDecoration"] {{ display: none; }}
    .stDeployButton, .stAppDeployButton, [data-testid="stToolbarActionButton"] {{ display: none !important; }}

    /* Hide Streamlit header anchor links */
    .stMarkdown a.header-anchor,
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a,
    div[data-testid="stMarkdownContainer"] a.header-anchor,
    div[data-testid="stMarkdownContainer"] h1 a,
    div[data-testid="stMarkdownContainer"] h2 a,
    div[data-testid="stMarkdownContainer"] h3 a {{
        display: none !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }}

    /* ── Animated background ───────────────────────────────────── */
    .stApp {{
        background: linear-gradient(135deg, #fafafa 0%, #f0f0f0 30%, #fef2f2 60%, #fafafa 100%) !important;
        background-size: 400% 400% !important;
        animation: authBgShift 12s ease-in-out infinite !important;
    }}
    @keyframes authBgShift {{
        0%   {{ background-position: 0% 50%; }}
        50%  {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* ── Floating geometric accents ────────────────────────────── */
    .stApp::before {{
        content: '';
        position: fixed;
        top: -120px; right: -120px;
        width: 340px; height: 340px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(218,41,28,0.07) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
        animation: floatOrb1 8s ease-in-out infinite;
    }}
    .stApp::after {{
        content: '';
        position: fixed;
        bottom: -100px; left: -80px;
        width: 280px; height: 280px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(26,26,26,0.04) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
        animation: floatOrb2 10s ease-in-out infinite;
    }}
    @keyframes floatOrb1 {{
        0%, 100% {{ transform: translate(0, 0) scale(1); }}
        50%      {{ transform: translate(-20px, 30px) scale(1.08); }}
    }}
    @keyframes floatOrb2 {{
        0%, 100% {{ transform: translate(0, 0) scale(1); }}
        50%      {{ transform: translate(20px, -25px) scale(1.05); }}
    }}

    /* ── Main block centering ──────────────────────────────────── */
    .stMainBlockContainer {{
        max-width: 440px !important;
        margin: 0 auto !important;
        padding-top: 36px !important;
    }}

    /* ── Input field styling ────────────────────────────────────── */
    [data-testid="stTextInput"] div[data-baseweb] {{
        background-color: rgba(255,255,255,0.8) !important;
        border: none !important;
        border-radius: 12px !important;
    }}
    [data-testid="stTextInput"] > div > div {{
        background-color: rgba(255,255,255,0.8) !important;
        border: 1.5px solid rgba(0,0,0,0.08) !important;
        border-radius: 12px !important;
        overflow: hidden;
        transition: all 0.25s cubic-bezier(.4,0,.2,1) !important;
        backdrop-filter: blur(8px);
    }}
    [data-testid="stTextInput"] > div > div:focus-within {{
        border-color: #DA291C !important;
        box-shadow: 0 0 0 3px rgba(218,41,28,0.1) !important;
        background-color: #FFFFFF !important;
    }}
    [data-testid="stTextInput"] input {{
        color: #1A1A1A !important;
        background-color: transparent !important;
        font-size: 0.92rem !important;
        padding: 12px 14px !important;
    }}
    [data-testid="stTextInput"] input::placeholder {{
        color: #9CA3AF !important;
        font-weight: 400 !important;
    }}
    [data-testid="stTextInput"] label {{
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        color: #374151 !important;
        letter-spacing: 0.2px !important;
        text-transform: uppercase !important;
    }}

    /* Password eye-toggle button */
    [data-testid="stTextInput"] button {{
        background-color: transparent !important;
        border: none !important;
        color: #9CA3AF !important;
        padding: 0 12px !important;
        transition: color 0.2s ease !important;
    }}
    [data-testid="stTextInput"] button:hover {{
        color: #DA291C !important;
    }}
    [data-testid="stTextInput"] button svg {{
        fill: currentColor !important;
        stroke: currentColor !important;
    }}

    /* Hide "Press Enter to submit form" text */
    .stTextInput [data-testid="InputInstructions"],
    .stTextInput div[class*="InputInstructions"] {{
        display: none !important;
    }}

    /* ── Tab Styling ───────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0 !important;
        background: rgba(0,0,0,0.03) !important;
        border-radius: 14px !important;
        padding: 4px !important;
        border: 1px solid rgba(0,0,0,0.04) !important;
        margin-bottom: 8px !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        flex: 1 !important;
        justify-content: center !important;
        border-radius: 11px !important;
        padding: 10px 0 !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        color: #6B7280 !important;
        background: transparent !important;
        border: none !important;
        transition: all 0.25s cubic-bezier(.4,0,.2,1) !important;
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background: #FFFFFF !important;
        color: #1A1A1A !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.04) !important;
    }}
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {{
        color: #DA291C !important;
        background: rgba(218,41,28,0.04) !important;
    }}
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
    }}

    /* ── Submit button styling ─────────────────────────────────── */
    .stFormSubmitButton button {{
        background: linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.3px !important;
        transition: all 0.3s cubic-bezier(.4,0,.2,1) !important;
        box-shadow: 0 4px 14px rgba(26,26,26,0.2) !important;
        position: relative;
        overflow: hidden;
    }}
    .stFormSubmitButton button::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, #DA291C 0%, #FF6B5A 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
        border-radius: 12px;
    }}
    .stFormSubmitButton button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(218,41,28,0.3) !important;
        background: linear-gradient(135deg, #DA291C 0%, #FF6B5A 100%) !important;
    }}
    .stFormSubmitButton button:active {{
        transform: translateY(0) scale(0.98) !important;
        box-shadow: 0 2px 8px rgba(218,41,28,0.2) !important;
    }}

    /* ── Card entrance animation ───────────────────────────────── */
    @keyframes authCardIn {{
        from {{ opacity: 0; transform: translateY(24px) scale(0.97); }}
        to   {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    @keyframes authLogoIn {{
        from {{ opacity: 0; transform: scale(0.6) rotate(-8deg); }}
        to   {{ opacity: 1; transform: scale(1) rotate(0deg); }}
    }}
    @keyframes authTextIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .auth-card {{
        animation: authCardIn 0.6s cubic-bezier(.4,0,.2,1) both;
    }}
    .auth-logo {{
        animation: authLogoIn 0.5s cubic-bezier(.34,1.56,.64,1) 0.15s both;
    }}
    .auth-title {{
        animation: authTextIn 0.5s ease-out 0.3s both;
    }}
    .auth-subtitle {{
        animation: authTextIn 0.5s ease-out 0.4s both;
    }}
    .auth-badges {{
        animation: authTextIn 0.5s ease-out 0.5s both;
    }}

    /* ── Subtle logo glow ──────────────────────────────────────── */
    @keyframes logoGlow {{
        0%, 100% {{ box-shadow: 0 4px 20px rgba(218,41,28,0.12); }}
        50%      {{ box-shadow: 0 4px 28px rgba(218,41,28,0.25); }}
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="auth-card" style="text-align:center; padding: 0 0 8px 0;">
        <div class="auth-logo" style="margin-bottom: 16px;">
            <img src="data:image/png;base64,{_login_logo_b64}"
                 alt="La Trobe University"
                 style="width: 88px; height: 88px; border-radius: 18px;
                        object-fit: cover;
                        border: 3px solid rgba(218,41,28,0.12);
                        animation: logoGlow 3s ease-in-out infinite;" />
        </div>
        <div class="auth-title" style="margin: 0;">
            <span style="font-size: 1.8rem; font-weight: 800; color: #1A1A1A;
                         letter-spacing: -0.8px; line-height: 1.2;">
                CampusAware AI
            </span>
        </div>
        <div class="auth-subtitle">
            <p style="color: #6B7280; font-size: 0.9rem; margin: 8px 0 0 0;
                       font-weight: 500; letter-spacing: 0.1px;">
                Your intelligent campus companion
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑  Login", "📝  Sign Up"])

    with tab_login:
        with st.form("login_form"):
            st.markdown("""
            <div style="text-align:center; margin-bottom: 4px;">
                <p style="color:#6B7280; font-size:0.84rem; font-weight:500; margin:0;">
                    Sign in with your La Trobe student credentials
                </p>
            </div>
            """, unsafe_allow_html=True)
            student_id = st.text_input("Student ID", placeholder="e.g. 20012345",
                                       help="8-digit La Trobe student ID")
            password   = st.text_input("Password", type="password",
                                       placeholder="Enter your password")
            submitted  = st.form_submit_button("Sign In →", use_container_width=True,
                                               type="primary")
            if submitted:
                if not student_id or not password:
                    st.error("Please fill in all fields.")
                else:
                    success, result = login_student(student_id.strip(), password)
                    if success:
                        token = create_session_token(student_id.strip())
                        st.session_state["authenticated"] = True
                        st.session_state["student_id"]    = student_id.strip()
                        st.session_state["full_name"]      = result
                        st.session_state["session_token"]  = token
                        st.session_state["thread_id"]      = str(uuid.uuid4())
                        st.session_state["messages"]       = []
                        st.session_state["last_active"]    = time.time()
                        st.query_params["token"]           = token
                        st.rerun()
                    else:
                        st.error(result)

    with tab_register:
        with st.form("register_form"):
            st.markdown("""
            <div style="text-align:center; margin-bottom: 4px;">
                <p style="color:#6B7280; font-size:0.84rem; font-weight:500; margin:0;">
                    Create your CampusAware account to get started
                </p>
            </div>
            """, unsafe_allow_html=True)
            reg_id       = st.text_input("Student ID", placeholder="e.g. 20012345",
                                         help="8-digit La Trobe student ID starting with 2")
            reg_name     = st.text_input("Full Name", placeholder="e.g. Akhila Murari")
            reg_password = st.text_input("Password", type="password",
                                         placeholder="8+ chars, upper, lower, num, special",
                                         help="Must be at least 8 characters long, and include at least one uppercase letter, one lowercase letter, one number, and one special character.")
            reg_confirm  = st.text_input("Confirm Password", type="password",
                                         placeholder="Re-enter your password")
            reg_submit   = st.form_submit_button("Create Account →", use_container_width=True,
                                                  type="primary")
            if reg_submit:
                if not reg_id or not reg_name or not reg_password or not reg_confirm:
                    st.error("Please fill in all fields.")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match.")
                else:
                    success, msg = register_student(reg_id.strip(), reg_password,
                                                    reg_name.strip())
                    if success:
                        st.success(msg + " Switch to the Login tab to sign in.")
                    else:
                        st.error(msg)

    # ── Footer branding on auth page ──────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding: 28px 0 16px 0; opacity: 0;
                animation: authTextIn 0.5s ease-out 0.7s both;">
        <p style="color:#C0C0C0; font-size:0.72rem; margin:0; font-weight:500;
                  letter-spacing: 0.4px;">
            © 2026 CampusAware AI · La Trobe University · Bundoora Campus
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ── Handle logout via query param ─────────────────────────────────────────────
if st.query_params.get("logout") == "true":
    delete_session_token(st.session_state.get("session_token", ""))
    st.query_params.clear()
    st.session_state["authenticated"] = False
    st.session_state["student_id"]    = ""
    st.session_state["full_name"]      = ""
    st.session_state["session_token"]  = ""
    st.session_state["messages"]       = []
    st.session_state["thread_id"]      = str(uuid.uuid4())
    st.session_state["last_active"]    = 0.0
    st.rerun()


# ── Main App CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

* { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stDecoration"] { display: none; }
.stDeployButton, .stAppDeployButton, [data-testid="stToolbarActionButton"] { display: none !important; }

/* Hide Streamlit header anchor links */
.stMarkdown a.header-anchor,
.stMarkdown h1 a,
.stMarkdown h2 a,
.stMarkdown h3 a,
div[data-testid="stMarkdownContainer"] a.header-anchor,
div[data-testid="stMarkdownContainer"] h1 a,
div[data-testid="stMarkdownContainer"] h2 a,
div[data-testid="stMarkdownContainer"] h3 a,
.app-header a {
    display: none !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

.user-bubble-wrapper { display:flex; justify-content:flex-end; margin:6px 0; }
.user-bubble {
    background: #DA291C; color: #fff; padding: 10px 16px;
    border-radius: 20px 20px 4px 20px;
    max-width: 65%; font-size: 0.9rem; line-height: 1.5; word-wrap: break-word;
}
.bot-bubble-wrapper { display:flex; justify-content:flex-start; align-items:flex-end; gap:8px; margin:6px 0; }
.bot-avatar {
    width:38px; height:38px; background:#DA291C;
    border-radius:50%; display:flex; align-items:center;
    justify-content:center; font-size:1.3rem; flex-shrink:0;
    box-shadow: 0 2px 8px rgba(218,41,28,0.35);
    border: 2px solid white;
}
.bot-bubble {
    background: #F5F5F5; border: 1px solid #E5E7EB; color: #1a1a1a; padding: 10px 16px;
    border-radius: 20px 20px 20px 4px;
    max-width: 65%; font-size: 0.9rem; line-height: 1.5; word-wrap: break-word;
}
[data-testid="stSidebar"] .stButton > button {
    background: #FFFFFF; border: 1px solid #1a1a1a !important; color: #1a1a1a !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important; text-align: left !important;
    padding: 8px 12px !important; margin-bottom: 4px; transition: all 0.15s;
}
[data-testid="stSidebar"] [data-testid="stExpander"] details summary {
    background-color: #1A1A1A !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] details summary p {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] details summary svg,
[data-testid="stSidebar"] [data-testid="stExpander"] details summary svg path,
[data-testid="stSidebar"] [data-testid="stExpander"] details summary span {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stCaptionContainer"] * {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background-color: #1A1A1A !important;
    border: 1px solid #1A1A1A !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] details,
[data-testid="stSidebar"] [data-testid="stExpander"] details > div {
    background-color: #1A1A1A !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #DA291C !important; border-color: #DA291C !important;
    color: #FFFFFF !important;
}
[data-testid="stChatInput"] * { background-color: transparent !important; }
[data-testid="stChatInput"] > div { background-color: #FFFFFF !important; border-color: #1A1A1A !important; }
[data-testid="stChatInput"] > div:focus-within {
    border-color: #1A1A1A !important;
    box-shadow: 0 0 0 2px rgba(26,26,26,0.2) !important;
}
[data-testid="stChatInput"] textarea { color: #1a1a1a !important; caret-color: #DA291C !important; }
button[data-testid="stChatInputSubmitButton"] {
    transition: all 0.2s ease !important;
    border-radius: 50% !important;
    width: 38px !important;
    min-width: 38px !important;
    height: 38px !important;
    min-height: 38px !important;
    flex: 0 0 38px !important;
    padding: 0 !important;
    margin: auto 6px auto 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border: none !important;
    background: linear-gradient(135deg, #1a1a1a, #3d3d3d) !important;
    box-shadow: 0 4px 10px rgba(26, 26, 26, 0.25) !important;
    overflow: hidden !important;
}
button[data-testid="stChatInputSubmitButton"] * {
    color: #FFFFFF !important;
    background-color: transparent !important;
}
button[data-testid="stChatInputSubmitButton"]:hover {
    transform: scale(1.08) translateY(-1px) !important;
    box-shadow: 0 6px 14px rgba(218, 41, 28, 0.4) !important;
    background: linear-gradient(135deg, #DA291C, #FF6B5A) !important;
}
button[data-testid="stChatInputSubmitButton"]:active {
    transform: scale(0.95) !important;
    box-shadow: 0 2px 5px rgba(218, 41, 28, 0.2) !important;
}
button[data-testid="stChatInputSubmitButton"] svg {
    width: 18px !important;
    height: 18px !important;
    transition: all 0.2s ease !important;
    margin-left: 2px !important; /* Visual centering for a send arrow */
}
.app-header {
    text-align: center; margin-bottom: 1.5rem; padding-top: 12px;
    position: relative;
}
.app-header-accent {
    width: 48px; height: 4px; border-radius: 2px;
    background: linear-gradient(90deg, #DA291C, #FF6B5A);
    margin: 0 auto 14px auto;
}
.app-header h1 {
    font-weight: 900; font-size: 2.4rem; margin: 0; letter-spacing: -1px;
    color: #000000;
    background-clip: text;
    line-height: 1.2;
}
.app-header .header-tagline {
    color: #6B7280; font-size: 0.92rem; margin: 8px 0 0 0;
    font-weight: 500; letter-spacing: 0.2px;
}
.header-iot-status {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 0.8rem; color: #6B7280; margin: 12px 0 0 0;
    padding: 6px 16px; border-radius: 20px;
    background: rgba(218,41,28,0.04);
    border: 1px solid rgba(218,41,28,0.12);
}
.header-iot-status .live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #10B981;
    animation: pulse 1.4s ease-in-out infinite;
}
.header-badges {
    display: flex; justify-content: center; gap: 10px;
    margin-top: 14px; flex-wrap: wrap;
}
.header-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 5px 14px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.3px; text-transform: uppercase;
}
.badge-latrobe {
    background: rgba(218, 41, 28, 0.08); color: #DA291C;
    border: 1px solid rgba(218, 41, 28, 0.2);
}
.badge-cisco {
    background: rgba(75, 85, 99, 0.08); color: #4B5563;
    border: 1px solid rgba(75, 85, 99, 0.2);
}
.iot-card {
    background:#FFFFFF; border:1px solid #1a1a1a; border-radius:10px;
    padding:10px 14px; margin-bottom:8px;
    display:flex; align-items:center; justify-content:space-between;
}
.iot-card-label { font-size:11px; color:#6b7280; font-weight:500; }
.iot-card-value { font-size:18px; font-weight:700; font-family:monospace; }
.iot-card-sub   { font-size:9px; color:#9ca3af; }
/* Branded Thinking Indicator */
.thinking-container {
    display: flex; align-items: center; gap: 10px;
    animation: thinkFadeIn 0.35s ease-out both;
}
@keyframes thinkFadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: translateY(0); }
}
.thinking-dots {
    display: flex; align-items: center; gap: 4px;
}
.typing-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #DA291C;
    display: inline-block;
    animation: pulse 1.4s ease-in-out infinite both;
}
@keyframes pulse {
    0%, 80%, 100% { opacity: 0.25; transform: scale(0.85); }
    40% { opacity: 1; transform: scale(1.15); }
}
.thinking-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: #6B7280;
    background: linear-gradient(90deg, #6B7280 0%, #DA291C 50%, #6B7280 100%);
    background-size: 200% 100%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 2.4s ease-in-out infinite;
}
@keyframes shimmer {
    0%   { background-position: 100% 0; }
    100% { background-position: -100% 0; }
}

/* Quick Pills Styling – main area only (card-style) */
.stMainBlockContainer .quick-pill-card {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 16px;
    padding: 20px 16px 18px 16px;
    cursor: pointer;
    transition: all 0.32s cubic-bezier(.4,0,.2,1);
    position: relative;
    overflow: hidden;
    text-align: center;
    min-height: 120px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
}
/* Animated gradient border effect on hover */
.quick-pill-card::before {
    content: '';
    position: absolute; inset: 0;
    border-radius: 16px;
    padding: 1.5px;
    background: linear-gradient(135deg, #2D2D2D, #4A4A4A, #2D2D2D);
    background-size: 200% 200%;
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    opacity: 0;
    transition: opacity 0.32s ease;
}
.quick-pill-card:hover::before {
    opacity: 1;
    animation: pillBorderShift 2.5s ease infinite;
}
@keyframes pillBorderShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
/* Subtle background shimmer on hover */
.quick-pill-card::after {
    content: '';
    position: absolute; inset: 0;
    border-radius: 16px;
    background: radial-gradient(circle at 30% 30%, rgba(45,45,45,0.06) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.32s ease;
}
.quick-pill-card:hover::after { opacity: 1; }
.quick-pill-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(45,45,45,0.15), 0 4px 12px rgba(0,0,0,0.06);
    border-color: transparent;
}
.quick-pill-card:active {
    transform: translateY(-1px) scale(0.98);
    box-shadow: 0 4px 12px rgba(45,45,45,0.12);
}
/* Icon area */
.pill-icon-wrapper {
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.35rem;
    transition: all 0.32s cubic-bezier(.4,0,.2,1);
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}
.pill-icon-wrapper.pill-iot    { background: linear-gradient(135deg, #FEE2E2, #FECACA); }
.pill-icon-wrapper.pill-rules  { background: linear-gradient(135deg, #FEF3C7, #FDE68A); }
.pill-icon-wrapper.pill-library { background: linear-gradient(135deg, #DBEAFE, #BFDBFE); }
.quick-pill-card:hover .pill-icon-wrapper {
    transform: scale(1.1);
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}
/* Title */
.pill-title {
    font-size: 0.88rem; font-weight: 700; color: #1A1A1A;
    letter-spacing: -0.2px;
    position: relative; z-index: 1;
    margin: 0;
    line-height: 1.3;
}
.quick-pill-card:hover .pill-title { color: #2D2D2D; }
/* Subtitle */
.pill-subtitle {
    font-size: 0.72rem; color: #9CA3AF;
    font-weight: 500;
    position: relative; z-index: 1;
    margin: 0;
    line-height: 1.35;
}
/* Staggered entrance animation */
@keyframes pillSlideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.pill-anim-1 { animation: pillSlideUp 0.5s ease-out 0.25s both; }
.pill-anim-2 { animation: pillSlideUp 0.5s ease-out 0.40s both; }
.pill-anim-3 { animation: pillSlideUp 0.5s ease-out 0.55s both; }
/* Hide actual Streamlit buttons under pill cards */
.stMainBlockContainer .stColumn:has(.quick-pill-card) .stButton {
    position: absolute !important;
    inset: 0 !important;
    z-index: 5 !important;
    overflow: hidden !important;
}
.stMainBlockContainer .stColumn:has(.quick-pill-card) .stButton button {
    position: absolute !important;
    inset: 0 !important;
    width: 100% !important;
    height: 100% !important;
    opacity: 0 !important;
    cursor: pointer !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    background: transparent !important;
}
.stMainBlockContainer .stColumn:has(.quick-pill-card) {
    position: relative;
}
</style>
""", unsafe_allow_html=True)


# ── Fixed top-right avatar ────────────────────────────────────────────────────
full_name  = st.session_state.get("full_name", st.session_state.get("student_id", "Student"))
student_id = st.session_state.get("student_id", "")
initials   = "".join([w[0].upper() for w in full_name.split()[:2]]) if full_name else "?"

st.markdown(f"""
<style>
/* ── Avatar Keyframes ───────────────────────────────────────────── */

@keyframes avatarGlow {{
    0%, 100% {{ box-shadow: 0 0 0 0 rgba(218,41,28,0.0); }}
    50%      {{ box-shadow: 0 0 14px 3px rgba(218,41,28,0.18); }}
}}
@keyframes dropdownSlideIn {{
    from {{ opacity: 0; transform: translateY(-8px) scale(0.97); }}
    to   {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
@keyframes statusPulse {{
    0%, 100% {{ box-shadow: 0 0 0 0 rgba(16,185,129,0.45); }}
    50%      {{ box-shadow: 0 0 0 5px rgba(16,185,129,0); }}
}}

/* ── Avatar Wrapper ─────────────────────────────────────────────── */
.avatar-wrapper {{
    position: fixed;
    top: 12px;
    right: 20px;
    z-index: 999999;
    font-family: 'Inter', sans-serif;
    padding-bottom: 24px;
}}

/* ── Gradient Ring (outer) ──────────────────────────────────────── */
.avatar-ring {{
    width: 44px; height: 44px;
    border-radius: 50%;
    padding: 2.5px;
    background: conic-gradient(from 0deg, #DA291C, #FF6B5A, #DA291C);
    cursor: pointer;
    margin-left: auto;
    transition: transform 0.25s cubic-bezier(.4,0,.2,1);
}}
.avatar-wrapper:hover .avatar-ring {{
    transform: scale(1.08);
}}

/* ── Inner Circle ───────────────────────────────────────────────── */
.avatar-circle {{
    width: 100%; height: 100%;
    background: linear-gradient(145deg, #DA291C 0%, #a01a12 100%);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: 700; font-size: 14px;
    letter-spacing: 0.5px;
    border: 2.5px solid #fff;
    animation: avatarGlow 3s ease-in-out infinite;
    text-shadow: 0 1px 3px rgba(0,0,0,0.18);
    user-select: none;
}}

/* ── Status dot (online) ────────────────────────────────────────── */
.avatar-status {{
    position: absolute;
    bottom: 22px; right: -1px;
    width: 12px; height: 12px;
    background: #10B981;
    border: 2.5px solid #fff;
    border-radius: 50%;
    animation: statusPulse 2s ease-in-out infinite;
    z-index: 2;
}}

/* ── Dropdown Panel ─────────────────────────────────────────────── */
.avatar-dropdown {{
    visibility: hidden;
    opacity: 0;
    position: absolute;
    top: 52px;
    right: 0;
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 16px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06);
    min-width: 240px;
    padding: 0;
    z-index: 99999;
    transform: translateY(-8px) scale(0.97);
    transition: opacity 0.22s ease, transform 0.22s cubic-bezier(.4,0,.2,1), visibility 0.22s;
    overflow: hidden;
}}
.avatar-wrapper:hover .avatar-dropdown {{
    visibility: visible;
    opacity: 1;
    transform: translateY(0) scale(1);
}}

/* ── Dropdown Header ────────────────────────────────────────────── */
.dropdown-header {{
    padding: 18px 20px 14px 20px;
    background: linear-gradient(135deg, rgba(218,41,28,0.06) 0%, rgba(255,107,90,0.04) 100%);
    border-bottom: 1px solid rgba(0,0,0,0.05);
    display: flex;
    align-items: center;
    gap: 12px;
}}
.dropdown-avatar-sm {{
    width: 40px; height: 40px;
    border-radius: 50%;
    background: linear-gradient(145deg, #DA291C, #a01a12);
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: 700; font-size: 14px;
    flex-shrink: 0;
    border: 2px solid rgba(218,41,28,0.15);
    letter-spacing: 0.5px;
}}
.dropdown-info {{
    flex: 1;
    min-width: 0;
}}
.dropdown-name {{
    font-weight: 700; font-size: 14px; color: #111827;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    line-height: 1.3;
}}
.dropdown-id {{
    font-size: 11.5px; color: #6B7280; margin-top: 2px;
    font-family: 'SF Mono', 'Fira Code', monospace;
    letter-spacing: 0.3px;
}}

/* ── Role badge ─────────────────────────────────────────────────── */
.dropdown-role {{
    padding: 10px 20px;
    border-bottom: 1px solid rgba(0,0,0,0.04);
}}
.role-badge {{
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px; font-weight: 600;
    background: rgba(16,185,129,0.08);
    color: #059669;
    border: 1px solid rgba(16,185,129,0.15);
    letter-spacing: 0.3px;
}}
.role-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: #10B981;
}}

/* ── Dropdown Items ─────────────────────────────────────────────── */
.dropdown-item {{
    padding: 11px 20px;
    font-size: 13px;
    font-weight: 500;
    color: #374151;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    transition: all 0.15s ease;
}}
.dropdown-item:hover {{
    background: rgba(218,41,28,0.05);
    color: #DA291C;
}}
.dropdown-item-icon {{
    font-size: 15px;
    width: 20px;
    text-align: center;
    flex-shrink: 0;
}}

/* ── Logout Button ──────────────────────────────────────────────── */
.dropdown-logout {{
    margin: 6px 12px 12px 12px;
    padding: 10px 16px;
    border-radius: 10px;
    background: #1A1A1A !important;
    color: #FFFFFF !important;
    font-weight: 600;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    text-decoration: none;
    transition: all 0.2s ease;
    border: none;
}}
.dropdown-logout:hover {{
    background: #DA291C !important;
    color: #FFFFFF !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(218,41,28,0.3);
}}
</style>

<div class="avatar-wrapper">
    <div class="avatar-ring">
        <div class="avatar-circle">{initials}</div>
    </div>
    <div class="avatar-status"></div>
    <div class="avatar-dropdown">
        <div class="dropdown-header">
            <div class="dropdown-avatar-sm">{initials}</div>
            <div class="dropdown-info">
                <div class="dropdown-name">{full_name}</div>
                <div class="dropdown-id">{student_id}</div>
            </div>
        </div>
        <div class="dropdown-role">
            <span class="role-badge"><span class="role-dot"></span> Student — Active</span>
        </div>
        <a class="dropdown-logout" href="?logout=true" target="_top">
            <span>🚪</span> Sign Out
        </a>
    </div>
</div>
""", unsafe_allow_html=True)


# ── App Header ────────────────────────────────────────────────────────────────
header_placeholder = st.empty()
if not st.session_state.get("messages"):
    header_placeholder.markdown("""
    <div class="app-header">
        <h1>🎓 CampusAware AI</h1>
        <p class="header-tagline">Your intelligent campus companion</p>
        <div class="header-iot-status"><span class="live-dot"></span> Powered by live IoT sensor data</div>
    </div>
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

df = get_room_data()

EXAMPLES = [
    "Find me a quiet room to study",
    "Which room has high CO2?",
    "What are parking fees for different bays?",
    "How do I connect to eduroam WiFi?",
    "What is the after hours helpline?",
]

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── Premium Sidebar Branding ──────────────────────────────────────────────
    st.markdown("""
    <style>
    /* ── Sidebar Brand Block ─────────────────────────────────────────────── */
    .sidebar-brand {
        text-align: center;
        padding: 16px 12px 12px 12px;
        position: relative;
    }
    .sidebar-brand-logo {
        width: 76px; height: 76px;
        border-radius: 14px;
        object-fit: cover;
        margin-bottom: 10px;
        box-shadow: 0 4px 16px rgba(255, 255, 255, 0.25);
        border: 2px solid rgba(255, 255, 255, 0.35);
    }
    .sidebar-brand-title {
        font-size: 1.22rem;
        font-weight: 800;
        letter-spacing: -0.4px;
        margin: 0;
        line-height: 1.3;
        color: #F5F5F5;
    }
    @keyframes sidebarPulse {
        0%, 100% { opacity: 0.5; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
        50%      { opacity: 1;   box-shadow: 0 0 0 4px rgba(16, 185, 129, 0); }
    }
    .sidebar-brand-divider {
        height: 2px;
        margin: 0 auto;
        width: 60%;
        border-radius: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.25), transparent);
    }
    /* Collapse Streamlit's built-in sidebar header gap */
    [data-testid="stSidebarHeader"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _logo_path = pathlib.Path(__file__).parent / "assets" / "latrobe_logo.png"
    _logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()

    st.markdown(f"""
    <div class="sidebar-brand-wrapper">
        <div class="sidebar-brand">
            <img class="sidebar-brand-logo" src="data:image/png;base64,{_logo_b64}" alt="La Trobe University" />
            <div class="sidebar-brand-title">CampusAware AI</div>
        </div>
        <div class="sidebar-brand-divider"></div>
    </div>
    """, unsafe_allow_html=True)


    # ── JS to pin brand block at top (via iframe component) ──────────────
    import streamlit.components.v1 as components
    components.html("""
    <script>
    (function() {
        const doc = window.parent.document;

        function fixSidebarBrand() {
            const wrapper = doc.querySelector('.sidebar-brand-wrapper');
            const sidebarContent = doc.querySelector('[data-testid="stSidebarContent"]');
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (!wrapper || !sidebarContent || !sidebar) return false;

            // Prevent running twice
            if (doc.querySelector('.sidebar-brand-pinned')) return true;

            // Create pinned header
            const pinned = document.createElement('div');
            pinned.className = 'sidebar-brand-pinned';
            pinned.innerHTML = wrapper.innerHTML;

            // Style it fixed at top of sidebar
            // Walk up DOM to find actual opaque background color
            function getOpaqueBackground(el) {
                while (el) {
                    const bg = window.getComputedStyle(el).backgroundColor;
                    if (bg && bg !== 'transparent' && bg !== 'rgba(0, 0, 0, 0)') return bg;
                    el = el.parentElement;
                }
                return 'rgb(240, 242, 246)';
            }
            const bgColor = getOpaqueBackground(sidebarContent);
            Object.assign(pinned.style, {
                position: 'sticky',
                top: '0',
                zIndex: '999',
                backgroundColor: bgColor || 'rgb(240, 242, 246)',
                paddingBottom: '0',
                width: '100%',
                boxSizing: 'border-box'
            });

            // Insert pinned header as first child of sidebarContent
            sidebarContent.insertBefore(pinned, sidebarContent.firstChild);

            // Hide original wrapper
            wrapper.style.display = 'none';

            // Override overflow on all ancestors between sidebarContent and wrapper
            // to allow sticky to work
            let el = pinned.parentElement;
            while (el && el !== sidebarContent) {
                el.style.overflow = 'visible';
                el = el.parentElement;
            }

            return true;
        }

        // Retry until it works
        let attempts = 0;
        const interval = setInterval(function() {
            if (fixSidebarBrand() || attempts > 30) {
                clearInterval(interval);
            }
            attempts++;
        }, 200);
    })();
    </script>
    """, height=0)

    with st.expander("💡 Try asking", expanded=True):
        for example in EXAMPLES:
            if st.button(example, use_container_width=True, key=f"ex_{example}"):
                st.session_state["quick_q"] = example

    with st.expander("📡 Live Room Stats", expanded=False):
        if not df.empty:
            occupied       = int(df["occupancy"].sum())
            total          = len(df)
            vacant         = total - occupied
            avg_co2        = int(df["co2_ppm"].mean())
            avg_temp       = round(df["temperature_c"].mean(), 1)
            quietest       = df.loc[df["noise_db"].idxmin(), "room_id"]
            worst_co2_room = df.loc[df["co2_ppm"].idxmax(), "room_id"]
            worst_co2_val  = int(df["co2_ppm"].max())

            st.markdown(f"""
            <div class="iot-card">
                <div><div class="iot-card-label">🏢 Rooms Occupied</div><div class="iot-card-sub">of {total} total</div></div>
                <div class="iot-card-value" style="color:#EF4444">{occupied}</div>
            </div>
            <div class="iot-card">
                <div><div class="iot-card-label">✅ Rooms Available</div><div class="iot-card-sub">vacant now</div></div>
                <div class="iot-card-value" style="color:#10B981">{vacant}</div>
            </div>
            <div class="iot-card">
                <div><div class="iot-card-label">💨 Avg CO₂</div><div class="iot-card-sub">campus-wide</div></div>
                <div class="iot-card-value" style="color:#F59E0B">{avg_co2} ppm</div>
            </div>
            <div class="iot-card">
                <div><div class="iot-card-label">🌡 Avg Temp</div><div class="iot-card-sub">campus-wide</div></div>
                <div class="iot-card-value" style="color:#3B82F6">{avg_temp}°C</div>
            </div>
            <div class="iot-card">
                <div><div class="iot-card-label">🔇 Quietest Room</div><div class="iot-card-sub">best for studying</div></div>
                <div class="iot-card-value" style="color:#DA291C;font-size:13px">{quietest}</div>
            </div>
            <div class="iot-card">
                <div><div class="iot-card-label">⚠️ High CO₂ Room</div><div class="iot-card-sub">{worst_co2_val} ppm</div></div>
                <div class="iot-card-value" style="color:#EF4444;font-size:13px">{worst_co2_room}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔄 Refresh stats", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        else:
            st.warning("No sensor data available")

    with st.expander("⚙️ Session", expanded=False):
        total_q = len([m for m in st.session_state["messages"] if m["role"] == "user"])
        st.caption(f"Questions asked: {total_q}")
        if st.button("🗑 Clear chat", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["thread_id"] = str(uuid.uuid4())
            st.rerun()


# ── Resolve quick question ────────────────────────────────────────────────────
if st.session_state["quick_q"]:
    prompt = st.session_state.pop("quick_q")
else:
    prompt = None


# ── Chat History / Welcome Screen ─────────────────────────────────────────────
welcome_placeholder = st.empty()
pills_placeholder = st.empty()

if not st.session_state["messages"]:
    first_name = full_name.split()[0] if full_name else "there"

    # --- Welcome CSS ---
    st.markdown("""
    <style>
    @keyframes welcomeFadeIn {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes glowPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(218,41,28,0.15), 0 0 40px rgba(218,41,28,0.05); }
        50%      { box-shadow: 0 0 28px rgba(218,41,28,0.30), 0 0 56px rgba(218,41,28,0.10); }
    }
    .welcome-container {
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; padding: 40px 20px 10px 20px;
        animation: welcomeFadeIn 0.7s ease-out both;
    }
    .welcome-brand {
        font-size: 1.6rem; font-weight: 900; letter-spacing: -0.5px;
        background: linear-gradient(135deg, #DA291C, #A31B1B);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 4px 0; text-align: center;
        animation: welcomeFadeIn 0.7s ease-out 0.15s both;
    }
    .welcome-heading {
        font-size: 1.35rem; font-weight: 600; color: #000000;
        margin: 0 0 10px 0; text-align: center;
        animation: welcomeFadeIn 0.7s ease-out 0.25s both;
    }

    .welcome-hint {
        font-size: 0.78rem; color: #9CA3AF; margin: 0;
        text-align: center;
        animation: welcomeFadeIn 0.7s ease-out 0.45s both;
    }
    </style>
    """, unsafe_allow_html=True)

    welcome_placeholder.markdown(f"""
    <div class="welcome-container">
        <div class="welcome-heading">Hi {first_name}, how can I help you today?</div>
    </div>
    """, unsafe_allow_html=True)

    with pills_placeholder.container():
        col1, col2, col3 = st.columns(3)

        # ── Pill 1: Room conditions ─────────────────────────────────
        with col1:
            st.markdown("""
            <div class="quick-pill-card pill-anim-1">
                <div class="pill-icon-wrapper pill-iot">🌡️</div>
                <div class="pill-title">Room Conditions</div>
                <div class="pill-subtitle">Live IoT sensor data</div>
            </div>
            """, unsafe_allow_html=True)
            room_btn = st.button("ㅤ", use_container_width=True, key="pill_room")

        # ── Pill 2: Residence rules ─────────────────────────────────
        with col2:
            st.markdown("""
            <div class="quick-pill-card pill-anim-2">
                <div class="pill-icon-wrapper pill-rules">📜</div>
                <div class="pill-title">Residence Rules</div>
                <div class="pill-subtitle">Policies &amp; guidelines</div>
            </div>
            """, unsafe_allow_html=True)
            events_btn = st.button("ㅤ", use_container_width=True, key="pill_rules")

        # ── Pill 3: Library info ────────────────────────────────────
        with col3:
            st.markdown("""
            <div class="quick-pill-card pill-anim-3">
                <div class="pill-icon-wrapper pill-library">📚</div>
                <div class="pill-title">Library Info</div>
                <div class="pill-subtitle">Hours, services &amp; more</div>
            </div>
            """, unsafe_allow_html=True)
            policies_btn = st.button("ㅤ", use_container_width=True, key="pill_library")

        if room_btn or events_btn or policies_btn:
            if room_btn:
                user_text = "Room conditions"
                bot_text = "What kind of room conditions are you looking for?"
            elif events_btn:
                user_text = "Residence rules"
                bot_text = "What kind of residence rules do you want to know more about?"
            elif policies_btn:
                user_text = "Library information"
                bot_text = "What kind of information about libraries are you looking for?"
                
            st.session_state["messages"].append({"role": "user", "content": user_text})
            st.session_state["messages"].append({"role": "assistant", "content": bot_text})
            st.rerun()

        # ── JS to wire pill card clicks to Streamlit buttons ──────────
        import streamlit.components.v1 as components
        components.html("""
        <script>
        (function() {
            const doc = window.parent.document;
            function wirePills() {
                const cards = doc.querySelectorAll('.quick-pill-card');
                if (!cards.length) return false;
                cards.forEach(function(card) {
                    if (card.dataset.wired) return;
                    card.dataset.wired = '1';
                    card.style.cursor = 'pointer';
                    card.addEventListener('click', function() {
                        // Find the Streamlit button in the same column
                        const col = card.closest('[data-testid="stColumn"], [data-testid="column"]') ||
                                    card.parentElement;
                        const btn = col ? col.querySelector('button') : null;
                        if (btn) btn.click();
                    });
                });
                return true;
            }
            let attempts = 0;
            const interval = setInterval(function() {
                if (wirePills() || attempts > 30) clearInterval(interval);
                attempts++;
            }, 200);
        })();
        </script>
        """, height=0)

else:
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
    header_placeholder.empty()
    if 'welcome_placeholder' in locals():
        welcome_placeholder.empty()
    if 'pills_placeholder' in locals():
        pills_placeholder.empty()
        
    st.markdown(f"""
    <div class="user-bubble-wrapper">
        <div class="user-bubble">{user_input}</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state["messages"].append({"role": "user", "content": user_input})

    typing_indicator = st.empty()
    typing_indicator.markdown('''
    <div class="bot-bubble-wrapper">
        <div class="bot-avatar">🎓</div>
        <div class="bot-bubble" style="display: flex; align-items: center; padding: 14px 16px;">
            <div class="thinking-container">
                <div class="thinking-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot" style="animation-delay: 0.2s;"></div>
                    <div class="typing-dot" style="animation-delay: 0.4s;"></div>
                </div>
                <span class="thinking-label">CampusAware is thinking…</span>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    try:
        response = ""
        for chunk_text in run_agent(user_input, st.session_state["thread_id"]):
            if chunk_text.startswith("__new_thread__"):
                parts = chunk_text.split("__")
                if len(parts) >= 3:
                    st.session_state["thread_id"] = parts[2]
                continue
            elif chunk_text == "context_limit_exceeded":
                st.session_state["thread_id"] = str(uuid.uuid4())
                st.session_state["messages"] = []
                response = "Our conversation got too long and I've reset the memory. Please ask your question again!"
                break
            elif chunk_text.startswith("__error__"):
                response = chunk_text.replace("__error__", "")
                break
            else:
                response = chunk_text
                if response:
                    content = response.replace('\n', '<br>')
                    typing_indicator.markdown(f"""
                    <div class="bot-bubble-wrapper">
                        <div class="bot-avatar">🎓</div>
                        <div class="bot-bubble">{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    typing_indicator.markdown('''
                    <div class="bot-bubble-wrapper">
                        <div class="bot-avatar">🎓</div>
                        <div class="bot-bubble" style="display: flex; align-items: center; padding: 14px 16px;">
                            <div class="thinking-container">
                                <div class="thinking-dots">
                                    <div class="typing-dot"></div>
                                    <div class="typing-dot" style="animation-delay: 0.2s;"></div>
                                    <div class="typing-dot" style="animation-delay: 0.4s;"></div>
                                </div>
                                <span class="thinking-label">CampusAware is thinking…</span>
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

    except Exception as e:
        err = str(e)
        if "401" in err:
            response = "API key error — check NIM configuration."
        elif "Connection" in err:
            response = "Connection error — check SSH tunnel is running."
        elif "timeout" in err.lower():
            response = "Request timed out — server may be busy."
        else:
            response = f"Something went wrong: {err}"
            
    typing_indicator.empty()

    content = response.replace('\n', '<br>')
    st.markdown(f"""
    <div class="bot-bubble-wrapper">
        <div class="bot-avatar">🎓</div>
        <div class="bot-bubble">{content}</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state["messages"].append({"role": "assistant", "content": response})
    st.rerun()