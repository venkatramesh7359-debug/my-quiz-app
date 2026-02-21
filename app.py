import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="Venkat's Quiz Quest", page_icon="🎮", layout="centered")

# 2. JavaScript to hide Footer & Header
components.html(
    """
    <script>
    const removeElements = () => {
        const selectors = ['footer', '[data-testid="stFooter"]', 'header', '.stAppDeployButton'];
        selectors.forEach(s => {
            const els = window.parent.document.querySelectorAll(s);
            els.forEach(el => el.style.display = 'none');
        });
    };
    setInterval(removeElements, 500);
    </script>
    """, height=0,
)

# 3. Google Sheets URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

# 4. Session State initialization
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'unlocked_level' not in st.session_state: st.session_state.unlocked_level = 1
if 'current_playing_level' not in st.session_state: st.session_state.current_playing_level = None
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'retry_count' not in st.session_state: st.session_state.retry_count = {}
if 'game_mode' not in st.session_state: st.session_state.game_mode = None
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'final_submitted' not in st.session_state: st.session_state.final_submitted = False

# Helper Functions
def reset_to_map():
    st.session_state.current_playing_level = None
    st.session_state.game_mode = None
    st.session_state.start_time = None
    st.session_state.final_submitted = False
    st.rerun()

def restart_level(level_id):
    st.session_state.retry_count[level_id] = st.session_state.retry_count.get(level_id, 0) + 1
    st.session_state.game_mode = None
    st.session_state.start_time = None
    st.session_state.final_submitted = False
    keys_to_del = [k for k in st.session_state.keys() if f"_lvl_{level_id}" in k]
    for k in keys_to_del: del st.session_state[k]
    st.rerun()

@st.cache_data(show_spinner=False)
def load_data(url):
    try:
        data = pd.read_csv(url)
        # ఇక్కడ పాత హెడర్స్ లో స్పేస్ లు ఉన్నా సరిచేస్తుంది
        data.columns = [c.strip() for c in data.columns]
        return data
    except Exception as e:
        st.error(f"డేటా లోడ్ అవ్వలేదు: {e}")
        return None

df = load_data(SHEET_URL)

if df is not None:
    # --- LOGIN SECTION ---
    if st.session_state.user_name == "":
        st.title("🎮 Venkat's Learning Quest")
        name = st.text_input("మీ పేరు రాయండి:") 
        if st.button("Start Game 🚀
