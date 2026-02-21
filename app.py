import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="Venkat's Quiz Quest", page_icon="🎮", layout="centered")

# 2. UI Styling
st.markdown("""
    <style>
    .sticky-timer {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #ff4b4b; color: white; text-align: center;
        padding: 12px; z-index: 9999; font-size: 20px; font-weight: bold;
    }
    .stButton > button { width: 100%; border-radius: 12px; height: 50px; font-size: 16px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Hide Header
components.html("<script>const removeElements = () => { const selectors = ['header', '.stAppDeployButton']; selectors.forEach(s => { const els = window.parent.document.querySelectorAll(s); els.forEach(el => el.style.display = 'none'); }); }; setInterval(removeElements, 500);</script>", height=0)

# 4. Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

# 5. Session State Init
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'selected_subject' not in st.session_state: st.session_state.selected_subject = None
if 'unlocked_level' not in st.session_state: st.session_state.unlocked_level = 1
if 'current_playing_level' not in st.session_state: st.session_state.current_playing_level = None
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'retry_trigger' not in st.session_state: st.session_state.retry_trigger = 0
if 'game_mode' not in st.session_state: st.session_state.game_mode = None
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'final_submitted' not in st.session_state: st.session_state.final_submitted = False

def reset_to_map():
    st.session_state.retry_trigger += 1
    st.session_state.current_playing_level = None
    st.session_state.game_mode = None
    st.session_state.final_submitted = False
    st.rerun()

@st.cache_data(show_spinner=False)
def load_data(url):
    try:
        data = pd.read_csv(url)
        # --- కాలమ్ పేర్లని శుభ్రం చేసే లాజిక్ ---
        # అన్ని కాలమ్ పేర్ల చివర స్పేస్ లు తీసేసి, కేవలం మొదటి అక్షరం Capital చేస్తుంది
        data.columns = [str(c).strip().capitalize() for c in data.columns]
        
        # 'Lesson_name' ని మనం చిన్న అక్షరాల్లో వాడుతున్న
