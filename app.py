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

# 5. Session State Initialization
for key, val in {
    'user_name': "", 'selected_subject': None, 'unlocked_level': 1,
    'current_playing_level': None, 'is_admin': False, 'retry_trigger': 0,
    'game_mode': None, 'start_time': None, 'final_submitted': False
}.items():
    if key not in st.session_state: st.session_state[key] = val

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
        # Headers ని క్లీన్ చేసే లాజిక్
        data.columns = [str(c).strip().capitalize() for c in data.columns]
        
        # 'Lesson_name' మ్యాపింగ్
        if 'Lesson_name' in data.columns:
            data.rename(columns={'Lesson_name': 'lesson_name'}, inplace=True)
            
        if 'Subject' in data.columns:
            data['Subject'] = data['Subject'].astype(str).str.strip().str.title()
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data(SHEET_URL)

if df is not None:
    # --- 1. LOGIN ---
    if st.session_state.user_name == "":
        st.title("🎮 Venkat's Quiz Quest")
        name = st.text_input("మీ పేరు రాయండి:")
        if st.button("Start Game 🚀"):
            if name.strip() == "admin7997": 
                st.session_state.user_name, st.session_state.is_admin = "Venkat", True
            elif name.strip(): 
                st.session_state.user_name = name
            st.rerun()

    # --- 2. SUBJECT SELECTION ---
    elif st.session_state.selected_subject is None:
        st.title("📚 Select Subject")
        if 'Subject' in df.columns:
            subjects = sorted(df['Subject'].unique())
            for sub in subjects:
                if st.button(f"📖 {sub}"):
                    st.session_state.selected_subject = sub
                    st.rerun()
        else:
            st.error("షీట్ లో 'Subject' కాలమ్ దొరకలేదు.")
        
        if st.button("Logout 🚪"): st.session_state.user_name = ""; st.rerun()

    # --- 3. MAP SECTION ---
    elif st.session_state.current_playing_level is None:
        sub = st.session_state.selected_subject
        st.title(f"🗺️ {sub} Map")
        if st.button("⬅️ Back to Subjects"): 
            st.session_state.selected_subject = None; st.rerun()

        sub_df = df[df['Subject'] == sub]
        lessons = sorted(sub_df['lesson_name'].unique())
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
                    else: st.button(f"T{t}\n🔒", key=f"b_{sub}_{lesson}_{t}", disabled=True)
                global_task_counter += 1
            st.divider()

    # --- 4. QUIZ SECTION ---
    else:
        sub, lesson, t_num = st.session_state.cur_sub, st.session_state.cur_lesson, st.session_state.cur_t_num
        
        if st.session_state.game_mode is None:
            st.header(f"Task {t_num}")
            if st.button("Normal Mode 🧘"): st.session_state.game_mode = "normal"; st.rerun()
            if st.button("Speed Run ⏱️"): 
                st.session_state.game_mode = "timer"
                st.session_state.start_time = time.time()
                st.rerun()
            if st.button("⬅️ Back to Map"): reset_to_map()
            st.stop()

        if st.session_state.game_mode == "timer" and not st.session_state.final_submitted:
            st_autorefresh(interval=1000, key="timer_refresh")
            rem = max(0, 300 - int(time.time() - st.session_state.start_time))
            st.markdown(f'<div class="sticky-timer">⏳ Time: {rem//60:02d}:{rem%60:02d}</div>', unsafe_allow_html=True)
            if rem <= 0: st.error("⏰ Time Up!"); st.button("Retry", on_click=reset_to_map); st.stop()

        f_df = df[(df['Subject'] == sub) & (df['lesson_name'] == lesson)]
        l_df = f_df.iloc[(t_num-1)*10 : t_num*10]
        score, answered = 0, 0
        st.write("<br><br>", unsafe_allow_html=True)

        for idx, (i, row) in enumerate(l_df.iterrows(), 1):
            st.write(f"**Q {idx}:** {row['Question']}")
            ans_key = f"ans_{i}_{st.session_state.retry_trigger}"
            sub_key = f"sub_{i}_{st.session_state.retry_trigger}"
            
            if sub_key not in st.session_state: st.session_state[sub_key] = False
            
            opts = [str(row['Option_a']), str(row['Option_b']), str(row['Option_c']), str(row['Option_d'])]
            
            choice = st.radio(f"Q_{i}", opts, key=f"r_{i}_{st.session_state.retry_trigger}", 
                              index=None if ans_key not in st.session_state else opts.index(st.session_state[ans_key]), 
                              disabled=st.session_state[sub_key] or st.session_state.final_submitted, 
                              label_visibility="collapsed")
            
            # --- SUBMIT / CHANGE TOGGLE ---
            if not st.session_state.final_submitted:
                if not st.session_state[sub_key]:
                    if st.button(f"Submit {idx} ✅", key=f"s_btn_{i}_{st.session_state.retry_trigger}"):
                        if choice: 
                            st.session_state[ans_key] = choice
                            st.session_state[sub_key] = True
                            st.rerun()
                else:
                    if st.button(f"Change {idx} ✏️", key=f"c_btn_{i}_{st.session_state.retry_trigger}"):
                        st.session_state[sub_key] = False
                        st.rerun()
            
            if st.session_state.get(sub_key):
                answered += 1
                if st.session_state.final_submitted:
                    if st.session_state.get(ans_key) == str(row['Correct_answer']).strip(): 
                        st.success("Correct! ✅"); score += 1
                    else: st.error(f"Wrong! ❌ Correct: {row['Correct_answer']}")
            st.divider()

        if answered == len(l_df) and not st.session_state.final_submitted:
            if st.button("🏁 Final Submit", type="primary"): 
                st.session_state.final_submitted = True; st.rerun()

        if st.session_state.final_submitted:
            st.subheader(f"📊 Score: {score}/{len(l_df)}")
            if score == 10:
                st.balloons()
                if st.session_state.g_id == st.session_state.unlocked_level:
                    st.session_state.unlocked_level += 1
                st.button("Next Level ➡️", on_click=reset_to_map)
            else:
                st.warning("10/10 వస్తేనే నెక్స్ట్ లెవెల్ ఓపెన్ అవుతుంది!")
                st.button("Retry Task 🔄", on_click=reset_to_map)
            
            st.button("Map 🗺️", key="map_btn", on_click=reset_to_map)
