import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time
from streamlit_autorefresh import st_autorefresh

# 1. Page Config
st.set_page_config(page_title="Venkat's Quiz Quest", page_icon="🎮", layout="centered")

# 2. CSS for Sticky Timer & UI
st.markdown("""
    <style>
    .sticky-timer {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #ff4b4b; color: white; text-align: center;
        padding: 12px; z-index: 9999; font-size: 20px; font-weight: bold;
    }
    .stButton > button { width: 100%; border-radius: 12px; height: 55px; font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. JS to Hide Header
components.html("<script>const removeElements = () => { const selectors = ['header', '.stAppDeployButton']; selectors.forEach(s => { const els = window.parent.document.querySelectorAll(s); els.forEach(el => el.style.display = 'none'); }); }; setInterval(removeElements, 500);</script>", height=0)

# 4. Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

# 5. State Init
state_keys = {
    'user_name': "", 'selected_subject': None, 'unlocked_level': 1,
    'current_playing_level': None, 'is_admin': False, 'retry_count': {},
    'game_mode': None, 'start_time': None, 'final_submitted': False
}
for key, val in state_keys.items():
    if key not in st.session_state: st.session_state[key] = val

def reset_to_map():
    st.session_state.current_playing_level = None
    st.session_state.game_mode = None
    st.session_state.final_submitted = False
    st.rerun()

@st.cache_data(show_spinner=False)
def load_data(url):
    try:
        data = pd.read_csv(url)
        data.columns = [c.strip() for c in data.columns]
        # Subject grouping fix: spaces remove chesi, first letter capital chestundi
        if 'Subject' in data.columns:
            data['Subject'] = data['Subject'].astype(str).str.strip().str.title()
        return data
    except Exception as e:
        st.error(f"Error: {e}"); return None

df = load_data(SHEET_URL)

if df is not None:
    # --- 1. LOGIN ---
    if st.session_state.user_name == "":
        st.title("🎮 Venkat's Learning Quest")
        name = st.text_input("Meeru Peru Rayandi:")
        if st.button("Start Game 🚀"):
            if name.strip() == "admin7997": 
                st.session_state.user_name, st.session_state.is_admin = "Venkat", True
            elif name.strip(): 
                st.session_state.user_name = name
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
        
        # --- BACK OPTION ---
        if st.button("⬅️ Back to Subjects"):
            st.session_state.selected_subject = None
            st.rerun()

        sub_df = df[df['Subject'] == sub]
        lessons = sub_df['lesson_name'].unique()
        global_task_counter = 1 

        for lesson in lessons:
            st.markdown(f"### 📘 {lesson}")
            l_df = sub_df[sub_df['lesson_name'] == lesson]
            num_tasks = (len(l_df) // 10) + (1 if len(l_df) % 10 > 0 else 0)
            cols = st.columns(5)
            for t in range(1, num_tasks + 1):
                unlocked = st.session_state.is_admin or global_task_counter <= st.session_state.unlocked_level
                with cols[(t-1)%5]:
                    if unlocked:
                        if st.button(f"T{t}\n⭐", key=f"b_{sub}_{lesson}_{t}"):
                            st.session_state.current_playing_level = f"{sub}_{lesson}_T{t}"
                            st.session_state.cur_sub, st.session_state.cur_lesson, st.session_state.cur_t_num, st.session_state.g_id = sub, lesson, t, global_task_counter
                            st.rerun()
                    else: 
                        st.button(f"T{t}\n🔒", key=f"b_{sub}_{lesson}_{t}", disabled=True)
                global_task_counter += 1
            st.divider()

    # --- 4. QUIZ SECTION ---
    else:
        if 'cur_sub' not in st.session_state: reset_to_map(); st.stop()
        sub, lesson, t_num = st.session_state.cur_sub, st.session_state.cur_lesson, st.session_state.cur_t_num
        level_id, attempt = st.session_state.current_playing_level, st.session_state.retry_count.get(st.session_state.current_playing_level, 0)
        
        if st.session_state.game_mode is None:
            st.header(f"Task {t_num}")
            if st.button("Normal Mode 🧘"): st.session_state.game_mode = "normal"; st.rerun()
            if st.button("Speed Run ⏱️"): 
                st.session_state.game_mode = "timer"; st.session_state.start_time = time.time(); st.rerun()
            if st.button("⬅️ Back to Map"): reset_to_map()
            st.stop()

        if st.session_state.game_mode == "timer" and not st.session_state.final_submitted:
            st_autorefresh(interval=1000, key="timer_refresh")
            rem = max(0, 300 - int(time.time() - st.session_state.start_time))
            st.markdown(f'<div class="sticky-timer">⏳ Time: {rem//60:02d}:{rem%60:02d}</div>', unsafe_allow_html=True)
            if rem <= 0: st.error("⏰ Time Up!"); st.button("Retry", on_click=reset_to_map); st.stop()

        f_df = df[(df['Subject'] == sub) & (df['lesson_name'] == lesson)]
