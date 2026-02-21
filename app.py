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
        # Headers క్లీన్ చేయడం (ముఖ్యంగా పాత Headers)
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
        if st.button("Start Game 🚀"):
            if name.strip() == "admin7997": 
                st.session_state.user_name = "Venkat"
                st.session_state.is_admin = True
            elif name.strip():
                st.session_state.user_name = name
            st.rerun()

    # --- MAP SECTION ---
    elif st.session_state.current_playing_level is None:
        st.title("🗺️ Quiz Map")
        st.subheader(f"Player: {st.session_state.user_name}")
        
        # 'Subject' మరియు 'lesson_name' అనే పాత హెడర్స్ ని వాడుతున్నాం
        subjects = df['Subject'].unique()
        global_task_counter = 1 

        for sub in subjects:
            st.markdown(f"## 📚 Subject: {sub}")
            sub_df = df[df['Subject'] == sub]
            lessons = sub_df['lesson_name'].unique()
            
            for lesson in lessons:
                st.markdown(f"### 📘 {lesson}")
                lesson_df = sub_df[sub_df['lesson_name'] == lesson]
                num_tasks = (len(lesson_df) // 10) + (1 if len(lesson_df) % 10 > 0 else 0)
                
                cols = st.columns(5)
                for t in range(1, num_tasks + 1):
                    is_unlocked = st.session_state.is_admin or global_task_counter <= st.session_state.unlocked_level
                    
                    with cols[(t-1)%5]:
                        if is_unlocked:
                            if st.button(f"Task {t}\n⭐", key=f"btn_{sub}_{lesson}_{t}"):
                                st.session_state.current_playing_level = f"{sub}_{lesson}_T{t}"
                                st.session_state.current_sub = sub
                                st.session_state.current_lesson = lesson
                                st.session_state.current_task_num = t
                                st.session_state.global_id = global_task_counter
                                st.rerun()
                        else:
                            st.button(f"Task {t}\n🔒", key=f"btn_{sub}_{lesson}_{t}", disabled=True)
                    
                    global_task_counter += 1
                st.divider()

    # --- QUIZ SECTION ---
    else:
        sub = st.session_state.current_sub
        lesson = st.session_state.current_lesson
        task_num = st.session_state.current_task_num
        level_id = st.session_state.current_playing_level
        attempt = st.session_state.retry_count.get(level_id, 0)
        
        if st.session_state.game_mode is None:
            st.header(f"Task {task_num}: Mode Select")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Normal Mode 🧘"): st.session_state.game_mode = "normal"; st.rerun()
            with c2:
                if st.button("Speed Run ⏱️"): 
                    st.session_state.game_mode = "timer"
                    st.session_state.start_time = time.time()
                    st.rerun()
            if st.button("⬅️ Back"): reset_to_map()
            st.stop()

        # Filtering logic for Task
        full_df = df[(df['Subject'] == sub) & (df['lesson_name'] == lesson)]
        level_df = full_df.iloc[(task_num-1)*10 : task_num*10]
        
        score = 0
