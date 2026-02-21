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
        const selectors = ['footer', '[data-testid="stFooter"]', 'header', 'button[title="View fullscreen"]', '.stAppDeployButton'];
        selectors.forEach(s => {
            const els = window.parent.document.querySelectorAll(s);
            els.forEach(el => el.style.display = 'none');
        });
    };
    setInterval(removeElements, 500);
    </script>
    """, height=0,
)

# 3. Multiple Subjects Configuration
# ఇక్కడ నీ వేర్వేరు గూగుల్ షీట్ లింకులను పేస్ట్ చేయి
SUBJECT_SHEETS = {
    "Social Studies 🌍": "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv",
    "General Science 🧪": "YOUR_SCIENCE_SHEET_URL_HERE",
    "English Spoken 🗣️": "YOUR_ENGLISH_SHEET_URL_HERE"
}

# 4. Session State initialization
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'selected_subject' not in st.session_state: st.session_state.selected_subject = None
if 'unlocked_level' not in st.session_state: st.session_state.unlocked_level = 1
if 'current_playing_level' not in st.session_state: st.session_state.current_playing_level = None
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
        data.columns = [c.strip().lower().replace(' ', '_') for c in data.columns]
        return data
    except Exception: return None

# --- UI LOGIC ---

# 1. Login Section
if st.session_state.user_name == "":
    st.title("🎮 Venkat's Learning Quest")
    name = st.text_input("మీ పేరు రాయండి:") 
    if st.button("Start Game 🚀"):
        if name.strip() == "admin7997": 
            st.session_state.user_name = "Venkat"
            st.session_state.is_admin = True
        elif name.strip():
            st.session_state.user_name = name
            st.session_state.is_admin = False
        st.rerun()

# 2. Subject Selection Section
elif st.session_state.selected_subject is None:
    st.title("📚 Select Subject")
    st.subheader(f"Player: {st.session_state.user_name}")
    
    for sub in SUBJECT_SHEETS.keys():
        if st.button(sub, use_container_width=True):
            st.session_state.selected_subject = sub
            st.session_state.unlocked_level = 1 # సబ్జెక్ట్ మారినప్పుడు లెవల్ 1 నుండి రావాలి
            st.rerun()
    
    if st.button("Logout 🚪"):
        st.session_state.user_name = ""
        st.rerun()

# 3. Map Section
elif st.session_state.current_playing_level is None:
    st.title(f"🗺️ {st.session_state.selected_subject} Map")
    
    # Sidebar for navigation
    if st.sidebar.button("🔄 Change Subject"):
        st.session_state.selected_subject = None
        st.rerun()
    
    df = load_data(SUBJECT_SHEETS[st.session_state.selected_subject])
    
    if df is not None:
        lessons = df['lesson_name'].unique()
        global_task_counter = 1 

        for lesson in lessons:
            st.markdown(f"### 📘 {lesson}")
            lesson_df = df[df['lesson_name'] == lesson]
            num_tasks = (len(lesson_df) // 10) + (1 if len(lesson_df) % 10 > 0 else 0)
            
            cols = st.columns(5)
            for t in range(1, num_tasks + 1):
                is_unlocked = st.session_state.is_admin or global_task_counter <= st.session_state.unlocked_level
                
                with cols[(t-1)%5]:
                    if is_unlocked:
                        if st.button(f"Task {t}\n⭐", key=f"btn_{lesson}_{t}"):
                            st.session_state.current_playing_level = f"{lesson}_T{t}"
                            st.session_state.current_lesson = lesson
                            st.session_state.current_task_num = t
                            st.session_state.global_task_id = global_task_counter
                            st.rerun()
                    else:
                        st.button(f"Task {t}\n🔒", key=f"btn_{lesson}_{t}", disabled=True)
                
                global_task_counter += 1
            st.write("---")
    else:
        st.error("Sheet data load అవ్వలేదు. URL చెక్ చేయండి.")

# 4. Quiz Section
else:
    df = load_data(SUBJECT_SHEETS[st.session_state.selected_subject])
    lesson = st.session_state.current_lesson
    task_num = st.session_state.current_task_num
    level_id = st.session_state.current_playing_level
    attempt = st.session_state.retry_count.get(level_id, 0)
    
    if st.session_state.game_mode is None:
        st.header(f"Task {task_num}: Mode Select")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Normal Mode 🧘"):
                st.session_state.game_mode = "normal"; st.rerun()
        with c2:
            if st.button("Speed Run ⏱️"):
                st.session_state.game_mode = "timer"
                st.session_state.start_time = time.time()
                st.rerun()
        if st.button("⬅️ Back"): reset_to_map()
        st.stop()

    # Timer logic
    if st.session_state.game_mode == "timer" and not st.session_state.final_submitted:
        st_autorefresh(interval=1000, key="timer_ref")
        remaining = max(0, 300 - int(time.time() - st.session_state.start_time))
        mins, secs = divmod(remaining, 60)
        st.markdown(f"<div style='background-color: #ff4b4b; padding: 10px; border-radius: 10px; text-align: center; color: white;'><h2 style='margin:0; color: white;'>⏳ {mins:02d}:{secs:02d}</h2></div><br>", unsafe_allow_html=True)
        if remaining <= 0:
            st.error("⏰ TIME UP!"); st.button("Retry 🔄", on_click=restart_level, args=(level_id,)); st.stop()

    # Quiz Filtering
    lesson_full_df = df[df['lesson_name'] == lesson]
    start_row = (task_num - 1) * 10
    level_df = lesson_full_df.iloc[start_row : start_row + 10]
    
    score = 0
    answered_count = 0

    for idx, (i, row) in enumerate(level_df.iterrows(), 1):
        st.markdown(f"**ప్రశ్న {idx}:** {row['question']}")
        ans_key = f"ans_{i}_lvl_{level_id}_at_{attempt}"
        sub_key = f"sub_{i}_lvl_{level_id}_at_{attempt}"
        if sub_key not in st.session_state: st.session_state[sub_key] = False
        
        opts = [str(row['option_a']), str(row['option_b']), str(row['option_c']), str(row['option_d'])]
        correct_val = str(row['correct_answer']).strip()
        
        choice = st.radio(f"Opt_{i}", opts, key=f"radio_{i}", 
                          index=None if ans_key not in st.session_state else opts.index(st.session_state[ans_key]), 
                          disabled=st.session_state[sub_key] or st.session_state.final_submitted, 
                          label_visibility="collapsed")
        
        if not st.session_state.final_submitted:
            c1, c2 = st.columns([1, 2])
            with c1:
                if not st.session_state[sub_key]:
                    if st.button(f"Submit {idx} ✅", key=f"s_{i}"):
                        if choice:
                            st.session_state[ans_key] = choice
                            st.session_state[sub_key] = True
                            st.rerun()
                else:
                    if st.button(f"Edit {idx} ✏️", key=f"e_{i}"):
                        st.session_state[sub_key] = False
                        st.rerun()
        
        if st.session_state[sub_key]:
            answered_count += 1
            if st.session_state.final_submitted:
                user_ans = st.session_state.get(ans_key)
                if user_ans == correct_val:
                    st.success(f"Correct! ✅"); score += 1
                else:
                    st.error(f"మీరు పెట్టింది: {user_ans} ❌ | సరైనది: {correct_val}")
        st.divider()

    if answered_count == len(level_df) and not st.session_state.final_submitted:
        if st.button("🏁 Final Submit", type="primary", use_container_width=True):
            st.session_state.final_submitted = True
            st.rerun()

    if st.session_state.final_submitted:
        st.subheader(f"📊 Score: {score}/{len(level_df)}")
        if score == len(level_df):
            st.balloons()
            if st.session_state.global_task_id == st.session_state.unlocked_level:
                st.session_state.unlocked_level += 1
        st.button("Map 🗺️", on_click=reset_to_map)
