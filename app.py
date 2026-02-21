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
        data.columns = [str(c).strip() for c in data.columns]
        if 'Subject' in data.columns:
            data['Subject'] = data['Subject'].astype(str).str.strip().str.title()
        return data
    except Exception as e:
        st.error(f"Error: {e}"); return None

df = load_data(SHEET_URL)

if df is not None:
    # --- 1. LOGIN ---
    if st.session_state.user_name == "":
        st.title("🎮 Venkat's Quiz Quest")
        name = st.text_input("మీ పేరు రాయండి:")
        if st.button("Start Game 🚀"):
            if name.strip() == "admin7997": st.session_state.user_name, st.session_state.is_admin = "Venkat", True
            elif name.strip(): st.session_state.user_name = name
            st.rerun()

    # --- 2. SUBJECT SELECTION ---
    elif st.session_state.selected_subject is None:
        st.title("📚 Select Subject")
        subjects = sorted(df['Subject'].unique())
        for sub in subjects:
            if st.button(f"📖 {sub}"):
                st.session_state.selected_subject = sub
                st.rerun()
        if st.button("Logout 🚪"): st.session_state.user_name = ""; st.rerun()

    # --- 3. MAP SECTION ---
    elif st.session_state.current_playing_level is None:
        sub = st.session_state.selected_subject
        st.title(f"🗺️ {sub} Map")
        if st.button("⬅️ Back to Subjects"): st.session_state.selected_subject = None; st.rerun()

        sub_df = df[df['Subject'] == sub]
        lessons = sorted(sub_df['lesson_name'].unique())
        global_task_counter = 1 

        for lesson in lessons:
            st.markdown(f"### 📘 {lesson}")
            l_df = sub_df[sub_df['lesson_name'] == lesson]
            num_tasks = (len(l_df) // 10) + (1 if len(l_df) % 10 > 0 else 0)
            cols = st.columns(5)
            for t in range(1, num_tasks + 1):
                unlocked = st.session_state.is_admin or global_task_counter <= st.session_state.unlocked
