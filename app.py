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
if 'retry_count' not in st.session_state: st.session_state.retry_count = {}
if 'game_mode' not in st.session_state: st.session_state.game_mode = None
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'final_submitted' not in st.session_state: st.session_state.final_submitted = False

# Reset function
def reset_to_map():
    st.session_state.current_playing_level = None
    st.session_state.game_mode = None
    st.session_state.start_time = None
    st.session_state.final_submitted = False
    st.rerun()

# Retry function
def restart_level(level):
    st.session_state.retry_count[level] = st.session_state.retry_count.get(level, 0) + 1
    st.session_state.game_mode = None
    st.session_state.start_time = None
    st.session_state.final_submitted = False
    # Specific keys matrame delete chesthunnam
    keys_to_del = [k for k in st.session_state.keys() if f"_lvl_{level}" in k]
    for k in keys_to_del: del st.session_state[k]
    st.rerun()

@st.cache_data(show_spinner=False)
def load_data(url):
    try:
        data = pd.read_csv(url)
        data.columns = [c.strip().lower().replace(' ', '_') for c in data.columns]
        return data
    except: return None

df = load_data(SHEET_URL)

if df is not None:
    if st.session_state.user_name == "":
        name = st.text_input("Me peru rasivvandi:")
        if st.button("Start Game 🚀"):
            if name.strip():
                st.session_state.user_name = name
                st.rerun()
    
    elif st.session_state.current_playing_level is None:
        st.title("🎮 Venkat's Learning Quest")
        st.subheader(f"Player: {st.session_state.user_name}")
        tasks_per_lesson = 5
        rows_per_task = 10
        total_levels = len(df) // rows_per_task
        
        for l in range(1, 11):
            start_row = (l - 1) * 50
            current_name = "Coming Soon..."
            if start_row < len(df):
                val = df.iloc[start_row]['lesson_name']
                if pd.notna(val): current_name = str(val)
            
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
            st.header(f"Task {level}: Mode Select")
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

        # --- SMART TIMER SECTION ---
        if st.session_state.game_mode == "timer" and not st.session_state.final_submitted:
            # Refresh limited to 1 second
            st_autorefresh(interval=1000, key="timer_ref", limit=None)
            remaining = max(0, 300 - int(time.time() - st.session_state.start_time))
            mins, secs = divmod(remaining, 60)
            
            st.markdown(f"""
                <div style="background-color: #ff4b4b; padding: 10px; border-radius: 10px; text-align: center; color: white;">
                    <h2 style="margin:0;">⏳ {mins:02d}:{secs:02d}</h2>
                </div><br>""", unsafe_allow_html=True)
            
            if remaining <= 0:
                st.error("⏰ TIME UP!"); st.button("Retry 🔄", on_click=restart_level, args=(level,)); st.stop()

        # Questions Display
        level_df = df.iloc[(level-1)*10 : level*10]
        score = 0
        answered_count = 0

        for idx, (i, row) in enumerate(level_df.iterrows(), 1):
            st.markdown(f"**ప్రశ్న {idx}:** {row['question']}")
            ans_key = f"ans_{i}_lvl_{level}_at_{attempt}"
            sub_key = f"sub_{i}_lvl_{level}_at_{attempt}"
            
            if sub_key not in st.session_state: st.session_state[sub_key] = False
            
            opts = [str(row['option_a']), str(row['option_b']), str(row['option_c']), str(row['option_d'])]
            
            # Selection
            current_choice = st.radio("Options:", opts, key=f"radio_{i}", index=None if ans_key not in st.session_state else opts.index(st.session_state[ans_key]), disabled=st.session_state[sub_key] or st.session_state.final_submitted, label_visibility="collapsed")
            
            if not st.session_state.final_submitted:
                c1, c2 = st.columns([1, 2])
                with c1:
                    if not st.session_state[sub_key]:
                        if st.button(f"Submit {idx}", key=f"s_{i}"):
                            if current_choice:
                                st.session_state[ans_key] = current_choice
                                st.session_state[sub_key] = True
                                st.rerun()
                    else:
                        if st.button(f"Edit {idx}", key=f"e_{i}"):
                            st.session_state[sub_key] = False
                            st.rerun()
            
            if st.session_state[sub_key]:
                answered_count += 1
                if st.session_state.final_submitted:
                    if st.session_state[ans_key] == str(row['correct_answer']).strip():
                        st.success(f"Correct! ✅"); score += 1
                    else:
                        st.error(f"Wrong ❌ (Ans: {row['correct_answer']})")
            st.divider()

        if answered_count == 10 and not st.session_state.final_submitted:
            if st.button("🏁 Final Submit", type="primary", use_container_width=True):
                st.session_state.final_submitted = True
                st.rerun()

        if st.session_state.final_submitted:
            st.subheader(f"Score: {score}/10")
            if score == 10:
                st.balloons(); st.success("Task Complete! 🎉")
                if level == st.session_state.unlocked_level: st.session_state.unlocked_level += 1
            else: st.error("10/10 వస్తేనే నెక్స్ట్ లెవెల్ అన్లాక్ అవుతుంది.")
            st.button("Map 🗺️", on_click=reset_to_map)
