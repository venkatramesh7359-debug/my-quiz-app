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
if 'final_submitted' not in st.session_state: st.session_state.final_submitted = False

# Reset function
def reset_to_map():
    st.session_state.current_playing_level = None
    st.session_state.level_failed = False
    st.session_state.game_mode = None
    st.session_state.start_time = None
    st.session_state.final_submitted = False
    st.rerun()

# Retry function
def restart_level(level):
    if level not in st.session_state.retry_count:
        st.session_state.retry_count[level] = 1
    else:
        st.session_state.retry_count[level] += 1
    st.session_state.game_mode = None
    st.session_state.start_time = None
    st.session_state.final_submitted = False
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
                st.write("---")

        else:
            level = st.session_state.current_playing_level
            attempt = st.session_state.retry_count.get(level, 0)
            
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

            # --- TIMER SECTION (MAIN SCREEN LO UNTUNDI) ---
            if st.session_state.game_mode == "timer" and not st.session_state.final_submitted:
                st_autorefresh(interval=1000, key="quiz_timer")
                elapsed = time.time() - st.session_state.start_time
                remaining = max(0, 300 - int(elapsed))
                mins, secs = divmod(remaining, 60)
                
                # Highlighted Timer Box for Mobile visibility
                st.markdown(
                    f"""
                    <div style="background-color: #ff4b4b; padding: 10px; border-radius: 10px; text-align: center; color: white;">
                        <h2 style="margin:0;">⏳ Time Left: {mins:02d}:{secs:02d}</h2>
                    </div>
                    """, unsafe_header_custom=True, unsafe_allow_html=True
                )
                
                if remaining <= 0:
                    st.error("⏰ TIME UP!")
                    if st.button("Malli Modalu Pettu 🔄"):
                        restart_level(level)
                    st.stop()
            # ----------------------------------------------

            st.header(f"Task {level}")
            start_idx = (level - 1) * 10
            level_df = df.iloc[start_idx : start_idx + 10]
            
            score = 0
            answered_count = 0

            for q_num, (i, row) in enumerate(level_df.iterrows(), 1):
                st.markdown(f"### ప్రశ్న {q_num}")
                st.write(row['question'])
                opts = [str(row['option_a']), str(row['option_b']), str(row['option_c']), str(row['option_d'])]
                
                ans_key = f"ans_{i}_lvl_{level}_at_{attempt}"
                sub_key = f"sub_{i}_lvl_{level}_at_{attempt}"
                
                if sub_key not in st.session_state: st.session_state[sub_key] = False

                choice = st.radio(
                    "సరైన ఆప్షన్ ఎంచుకోండి:", opts, 
                    key=f"radio_{ans_key}",
                    index=None if ans_key not in st.session_state else opts.index(st.session_state[ans_key]),
                    disabled=st.session_state[sub_key] or st.session_state.final_submitted
                )
                
                if not st.session_state.final_submitted:
                    c1, c2 = st.columns(2)
                    with c1:
                        if not st.session_state[sub_key]:
                            if st.button(f"Submit {q_num} ✅", key=f"btn_sub_{i}"):
                                if choice:
                                    st.session_state[ans_key] = choice
                                    st.session_state[sub_key] = True
                                    st.rerun()
                                else:
                                    st.warning("Select option!")
                    with c2:
                        if st.session_state[sub_key]:
                            if st.button(f"Change Answer {q_num} ✏️", key=f"btn_edit_{i}"):
                                st.session_state[sub_key] = False
                                st.rerun()

                if st.session_state.final_submitted:
                    user_ans = st.session_state.get(ans_key)
                    correct = str(row['correct_answer']).strip()
                    if user_ans == correct:
                        st.success(f"మీరు పెట్టిన సమాధానం: {user_ans} ✅")
                        score += 1
                    else:
                        st.error(f"మీరు పెట్టిన సమాధానం: {user_ans} ❌")
                        st.info(f"సరైన సమాధానం: {correct}")
                        st.session_state.level_failed = True
                
                if st.session_state[sub_key]:
                    answered_count += 1
                st.write("---")

            if answered_count == 10 and not st.session_state.final_submitted:
                if st.button("🏁 Final Submit Task", type="primary", use_container_width=True):
                    st.session_state.final_submitted = True
                    st.rerun()

            if st.session_state.final_submitted:
                st.subheader(f"📊 మొత్తం స్కోరు: {score}/10")
                if score == 10:
                    st.balloons()
                    st.success("శభాష్! అన్ని ప్రశ్నలకు సరిగ్గా సమాధానం ఇచ్చారు. 🎉")
                    if level == st.session_state.unlocked_level:
                        st.session_state.unlocked_level += 1
                    st.button("మ్యాప్ కి వెళ్ళు 🗺️", on_click=reset_to_map)
                else:
                    st.error("10/10 వస్తేనే తదుపరి టాస్క్ ఓపెన్ అవుతుంది.")
                    if st.button("Retry Task 🔄"):
                        restart_level(level)
                    st.button("మ్యాప్ కి వెళ్ళు 🗺️", on_click=reset_to_map)

except Exception as e:
    st.error(f"Error: {e}")
