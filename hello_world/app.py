import streamlit as st

st.set_page_config(
    page_title="Agent Launcher",
    page_icon="🚀",
    layout="centered",
)

# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .launch-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.25rem;
    }
    .launch-sub {
        font-size: 1rem;
        color: #9ca3af;
        text-align: center;
        margin-bottom: 2.5rem;
    }
    div.stButton > button {
        width: 100%;
        height: 90px;
        font-size: 1.2rem;
        font-weight: 600;
        border-radius: 12px;
        border: 2px solid #FF3621;
        background-color: #FF3621;
        color: #ffffff;
        transition: background-color 0.2s ease, transform 0.1s ease;
    }
    div.stButton > button:hover {
        background-color: #cc2a18;
        transform: translateY(-2px);
    }
    div.stButton > button:active {
        transform: translateY(0px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="launch-title">Agent Launcher</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="launch-sub">Select an agent to launch</p>',
    unsafe_allow_html=True,
)

# ── Buttons ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    if st.button("STTM Agent", key="sttm"):
        st.info("Launching STTM Agent...")

with col2:
    if st.button("DQ Agent", key="dq"):
        st.info("Launching DQ Agent...")
