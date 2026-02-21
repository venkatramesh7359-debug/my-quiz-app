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
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        text-align: center;
        padding: 12px;
        z-index: 9999;
        font-size: 20px;
        font-weight: bold;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.3);
    }
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 55px;
        font-size: 18px !important;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. JS to Hide Header
components.html("<script>const removeElements = () => { const selectors = ['header', '.stAppDeployButton']; selectors.forEach(s => { const els = window.parent.document.querySelectorAll(s); els.forEach(el => el.style.display = 'none'); }); }; setInterval(removeElements, 500);</script>", height=0)

# 4. Sheet URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

# 5. State Init
for key, val in {'user_name': "", 'selected_subject': None, 'unlocked_level': 1, 'current_playing_level': None, 'is_admin': False, 'retry_count': {}, 'game_mode': None, 'start_time': None, 'final_submitted': False}.items():
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
        # కాలమ్ పేర్లలో స్పేస్‌లు ఉంటే తీసేస్తుంది
        data.columns = [c.strip() for c in data.columns]
        return data
    except Exception as e:
        st.error(f"Error: {e}"); return None

df = load_data(SHEET_URL)

if df is not None:
    # --- 1. LOGIN ---
    if st.session_state.user_name == "":
        st.title("🎮 Venkat's Learning Quest")
        name = st.text_input("మీ పేరు రాయండి:")
        if st.button("Start Game 🚀"):
            if name.strip() == "admin7997": st.session_state.user_name, st.session_state.is_admin = "Venkat", True
            elif name.strip(): st.session_state.user_name = name
            st.rerun()

    # --- 2. SUBJECT SELECTION ---
    elif st.session_state.selected_subject is None:
        st.title("📚 Select Subject")
        
        # ఇక్కడ 'Subject' (చిన్న 's' లేదు) అని మార్చాను
        if 'Subject' in df.columns:
            sub_list = sorted(df['Subject'].unique())
            for sub in sub_list:
                if st.button(f"📖 {sub}"):
                    st.session_state.selected_subject = sub
                    st.rerun()
        else:
            st.error(f"Sheet లో 'Subject' కాలమ్ దొరకలేదు! ఉన్న కాలమ్స్: {list(df.columns)}")
        
        if st.button("Logout 🚪"): st.session_state.user_name = ""; st.rerun()

    # --- 3. MAP SECTION ---
    elif st.session_state.current_playing_level is None:
        sub = st.session_state.selected_subject
        st.title(f"🗺️ {sub}")
        if st.sidebar.button("🔄 Change Subject"): st.session_state.selected_subject = None; st.rerun()

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
                    else: st.button(f"T{t}\n🔒", key=f"b_{sub}_{lesson}_{t}", disabled=True)
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
            if st.button("Speed Run ⏱️"): st.session_state.game_mode = "timer"; st.session_state.start_time = time.time(); st.rerun()
            if st.button("⬅️ Back"): reset_to_map()
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
            st.write(f"**ప్రశ్న {idx}:** {row['Question']}")
            ans_key, sub_key = f"a_{i}_{attempt}", f"s_{i}_{attempt}"
            opts = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
            
            if sub_key not in st.session_state: st.session_state[sub_key] = False
            choice = st.radio(f"Q_{i}", opts, key=f"r_{i}", index=None if ans_key not in st.session_state else opts.index(st.session_state[ans_key]), disabled=st.session_state[sub_key] or st.session_state.final_submitted, label_visibility="collapsed")
            
            if not st.session_state.final_submitted:
                if not st.session_state[sub_key] and st.button(f"Submit {idx} ✅", key=f"btn_s_{i}"):
                    if choice: st.session_state[ans_key] = choice; st.session_state[sub_key] = True; st.rerun()
            
            if st.session_state[sub_key]:
                answered += 1
                if st.session_state.final_submitted:
                    if st.session_state[ans_key] == str(row['Correct_Answer']).strip(): st.success("Correct! ✅"); score += 1
                    else: st.error(f"Wrong! ❌ Correct: {row['Correct_Answer']}")
            st.divider()

        if answered == len(l_df) and not st.session_state.final_submitted:
            if st.button("🏁 Final Submit", type="primary"): st.session_state.final_submitted = True; st.rerun()

        if st.session_state.final_submitted:
            st.subheader(f"📊 Score: {score}/{len(l_df)}")
            if score == len(l_df): st.balloons()
            if score >= 8 and st.session_state.g_id == st.session_state.unlocked_level: st.session_state.unlocked_level += 1
            st.button("Map 🗺️", on_click=reset_to_map)
