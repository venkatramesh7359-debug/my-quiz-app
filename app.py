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
if 'selected_subject' not in st.session_state: st.session_state.selected_subject = None
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

@st.cache_data(show_spinner=False)
def load_data(url):
    try:
        data = pd.read_csv(url)
        data.columns = [c.strip() for c in data.columns]
        return data
    except Exception as e:
        st.error(f"డేటా లోడ్ అవ్వలేదు: {e}")
        return None

df = load_data(SHEET_URL)

if df is not None:
    # --- 1. LOGIN SECTION ---
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

    # --- 2. SUBJECT SELECTION SECTION ---
    elif st.session_state.selected_subject is None:
        st.title("📚 సబ్జెక్టును ఎంచుకోండి")
        st.subheader(f"హలో {st.session_state.user_name}, ఈరోజు ఏం నేర్చుకుందాం?")
        
        subjects = df['Subject'].unique()
        
        # సబ్జెక్టులను బటన్ల రూపంలో చూపిస్తున్నాం
        for sub in subjects:
            if st.button(f"📖 {sub}", use_container_width=True):
                st.session_state.selected_subject = sub
                st.rerun()
        
        if st.button("Logout 🚪", type="secondary"):
            st.session_state.user_name = ""
            st.rerun()

    # --- 3. MAP SECTION (Selected Subject Only) ---
    elif st.session_state.current_playing_level is None:
        sub = st.session_state.selected_subject
        st.title(f"🗺️ {sub} Map")
        
        # Sidebar to Change Subject
        if st.sidebar.button("🔄 Change Subject"):
            st.session_state.selected_subject = None
            st.rerun()

        sub_df = df[df['Subject'] == sub]
        lessons = sub_df['lesson_name'].unique()
        global_task_counter = 1 

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

    # --- 4. QUIZ SECTION ---
    else:
        sub = st.session_state.current_sub
        lesson = st.session_state.current_lesson
        task_num = st.session_state.current_task_num
        level_id = st.session_state.current_playing_level
        attempt = st.session_state.retry_count.get(level_id, 0)
        
        if st.session_state.game_mode is None:
            st.header(f"{sub}: {lesson} - Task {task_num}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Normal Mode 🧘"): st.session_state.game_mode = "normal"; st.rerun()
            with c2:
                if st.button("Speed Run ⏱️"): 
                    st.session_state.game_mode = "timer"
                    st.session_state.start_time = time.time()
                    st.rerun()
            if st.button("⬅️ Back to Map"): reset_to_map()
            st.stop()

        # Filtering logic
        full_df = df[(df['Subject'] == sub) & (df['lesson_name'] == lesson)]
        level_df = full_df.iloc[(task_num-1)*10 : task_num*10]
        
        score = 0
        answered_count = 0

        for idx, (i, row) in enumerate(level_df.iterrows(), 1):
            st.write(f"**Q{idx}:** {row['Question']}")
            ans_key = f"a_{i}_{attempt}"
            sub_key = f"s_{i}_{attempt}"
            
            opts = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
            correct_val = str(row['Correct_Answer']).strip()
            
            if sub_key not in st.session_state: st.session_state[sub_key] = False
            
            choice = st.radio(f"R_{i}", opts, key=f"radio_{i}", 
                              index=None if ans_key not in st.session_state else opts.index(st.session_state[ans_key]), 
                              disabled=st.session_state[sub_key] or st.session_state.final_submitted,
                              label_visibility="collapsed")
            
            if not st.session_state.final_submitted:
                if not st.session_state[sub_key] and st.button(f"Submit {idx}", key=f"btn_s_{i}"):
                    if choice: st.session_state[ans_key] = choice; st.session_state[sub_key] = True; st.rerun()
            
            if st.session_state[sub_key]:
                answered_count += 1
                if st.session_state.final_submitted:
                    if st.session_state.get(ans_key) == correct_val:
                        st.success("Correct! ✅"); score += 1
                    else:
                        st.error(f"Wrong! ❌ Correct: {correct_val}")
            st.divider()

        if answered_count == len(level_df) and not st.session_state.final_submitted:
            if st.button("🏁 Final Submit", type="primary", use_container_width=True): 
                st.session_state.final_submitted = True; st.rerun()

        if st.session_state.final_submitted:
            st.subheader(f"📊 Score: {score}/{len(level_df)}")
            if score == len(level_df):
                st.balloons()
                if st.session_state.global_id == st.session_state.unlocked_level:
                    st.session_state.unlocked_level += 1
            st.button("Map 🗺️", on_click=reset_to_map)
