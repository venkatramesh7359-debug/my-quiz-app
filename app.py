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

# 3. Google Sheets URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

# 4. Session State initialization
if 'unlocked_level' not in st.session_state: st.session_state.unlocked_level = 1
if 'current_playing_level' not in st.session_state: st.session_state.current_playing_level = None
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'level_failed' not in st.session_state: st.session_state.level_failed = False
if 'retry_count' not in st.session_state: st.session_state.retry_count = {}
if 'game_mode' not in st.session_state: st.session_state.game_mode = None
if 'start_time' not in st.session_state: st.session_state.start_time = None

# Reset function
def reset_to_map():
    st.session_state.current_playing_level = None
    st.session_state.level_failed = False
    st.session_state.game_mode = None
    st.session_state.start_time = None
    st.rerun()

# Retry function
def restart_level(level):
    if level not in st.session_state.retry_count:
        st.session_state.retry_count[level] = 1
    else:
        st.session_state.retry_count[level] += 1
    
    st.session_state.game_mode = None
    st.session_state.start_time = None
    
    keys_to_del = [k for k in st.session_state.keys() if f"_lvl_{level}" in k]
    for k in keys_to_del:
        del st.session_state[k]
        
    st.session_state.level_failed = False
    st.rerun()

st.title("🎮 Venkat's Learning Quest")

@st.cache_data(ttl=0)
def load_data(url):
    try:
        data = pd.read_csv(url)
        data.columns = [c.strip().lower().replace(' ', '_') for c in data.columns]
        return data
    except:
        return None

try:
    df = load_data(SHEET_URL)
    
    if df is not None:
        if st.session_state.user_name == "":
            name = st.text_input("Me peru rasivvandi:")
            if st.button("Start Game 🚀"):
                if name.strip():
                    st.session_state.user_name = name
                    st.rerun()
        
        elif st.session_state.current_playing_level is None:
            st.subheader(f"Player: {st.session_state.user_name}")
            
            tasks_per_lesson = 5
            rows_per_task = 10
            rows_per_lesson = tasks_per_lesson * rows_per_task
            total_rows = len(df)
            total_levels = (total_rows // rows_per_task)
            
            for l in range(1, 11):
                start_row = (l - 1) * rows_per_lesson
                current_name = "Coming Soon..."
                if start_row < total_rows:
                    if 'lesson_name' in df.columns:
                        val = df.iloc[start_row]['lesson_name']
                        if pd.notna(val) and str(val).strip() != "":
                            current_name = str(val)
                
                st.markdown(f"### 📘 {current_name}") 
                
                if current_name != "Coming Soon...":
                    cols = st.columns(tasks_per_lesson)
                    for t in range(1, tasks_per_lesson + 1):
                        level_num = ((l - 1) * tasks_per_lesson) + t
                        if level_num <= total_levels:
                            with cols[t-1]:
                                if level_num <= st.session_state.unlocked_level:
                                    if st.button(f"Task {t}\n⭐", key=f"btn_{level_num}"):
                                        st.session_state.current_playing_level = level_num
                                        st.rerun()
                                else:
                                    st.button(f"Task {t}\n🔒", key=f"btn_{level_num}", disabled=True)
                else:
                    st.info("Ee lesson inka tayaru avuthundi... 🛠️")
                st.write("---")

        else:
            level = st.session_state.current_playing_level
            attempt = st.session_state.retry_count.get(level, 0)
            
            # --- TIMER MODE SELECTION ---
            if st.session_state.game_mode is None:
                st.header(f"Task {level}: Mode Select Cheyandi")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Normal Mode 🧘"):
                        st.session_state.game_mode = "normal"
                        st.rerun()
                with col2:
                    if st.button("Speed Run (5 Mins) ⏱️"):
                        st.session_state.game_mode = "timer"
                        st.session_state.start_time = time.time()
                        st.rerun()
                if st.button("⬅️ Back to Map"):
                    reset_to_map()
                st.stop()

            # --- DYNAMIC REFRESH TIMER ---
            if st.session_state.game_mode == "timer":
                # Auto-refresh every 1 second
                st_autorefresh(interval=1000, key="quiz_timer")
                
                elapsed = time.time() - st.session_state.start_time
                remaining = max(0, 300 - int(elapsed))
                
                mins, secs = divmod(remaining, 60)
                # Sidebar lo live timer chupinchadam
                st.sidebar.markdown(f"## ⏳ Time: {mins:02d}:{secs:02d}")
                
                if remaining <= 0:
                    st.error("⏰ TIME UP! Task reset ayyindi.")
                    if st.button("Malli Modalu Pettu 🔄"):
                        restart_level(level)
                    st.stop()

            st.header(f"Task {level} {'⏱️' if st.session_state.game_mode == 'timer' else ''}")
            start_idx = (level - 1) * 10
            level_df = df.iloc[start_idx : start_idx + 10]
            
            score = 0
            answered_count = 0

            for i, row in level_df.iterrows():
                st.markdown(f"**Prasna {answered_count + 1}:** {row['question']}")
                opts = [str(row['option_a']), str(row['option_b']), str(row['option_c']), str(row['option_d'])]
                
                key = f"q_{i}_lvl_{level}_at_{attempt}"
                if key not in st.session_state:
                    st.session_state[key] = None

                choice = st.radio(
                    "Sariyna option enchukondi:", opts, 
                    index=None if st.session_state[key] is None else opts.index(st.session_state[key]),
                    key=f"radio_{key}",
                    disabled=st.session_state[key] is not None
                )

                if choice and st.session_state[key] is None:
                    st.session_state[key] = choice
                    st.rerun()

                if st.session_state[key]:
                    answered_count += 1
                    correct = str(row['correct_answer']).strip().lower()
                    if str(st.session_state[key]).strip().lower() == correct:
                        st.success("Correct! ✅")
                        score += 1
                    else:
                        st.error(f"Wrong! ❌ Correct: {row['correct_answer']}")
                        st.session_state.level_failed = True
                st.write("---")

            if answered_count == 10:
                st.subheader(f"📊 Result: {score}/10")
                if not st.session_state.level_failed and score == 10:
                    st.balloons()
                    st.success("Sabbash! Task Completed! 🎉")
                    if level == st.session_state.unlocked_level:
                        st.session_state.unlocked_level += 1
                    st.button("Map ki vellu 🗺️", on_click=reset_to_map)
                else:
                    st.error("10/10 vasthene next level open avthundi.")
                    if st.button("Retry Task 🔄"):
                        restart_level(level)
                    st.button("Map ki vellu 🗺️", on_click=reset_to_map)

except Exception as e:
    st.error(f"Error: {e}")
