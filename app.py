import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. Page Config
st.set_page_config(page_title="Venkat's Quiz Quest", page_icon="🎮", layout="centered")

# 2. JavaScript to hide Footer & Fullscreen
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

def reset_to_map():
    level = st.session_state.current_playing_level
    for k in list(st.session_state.keys()):
        if f"_lvl_{level}" in k:
            del st.session_state[k]
    st.session_state.current_playing_level = None
    st.session_state.level_failed = False
    st.rerun()

st.title("🎮 Venkat's Learning Quest")

# Cache clear check - ఎప్పటికప్పుడు కొత్త డేటా కోసం
@st.cache_data(ttl=0)
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(SHEET_URL)
    # కాలమ్ పేర్లలో ఖాళీలు ఉంటే తీసేయడం
    df.columns = df.columns.str.strip()
    
    if st.session_state.user_name == "":
        name = st.text_input("మీ పేరు నమోదు చేయండి:")
        if st.button("Start Game 🚀"):
            if name.strip():
                st.session_state.user_name = name
                st.rerun()
    
    elif st.session_state.current_playing_level is None:
        st.subheader(f"Player: {st.session_state.user_name}")
        
        tasks_per_lesson = 5
        rows_per_task = 10
        rows_per_lesson = tasks_per_lesson * rows_per_task
        
        total_levels = (len(df) // rows_per_task) + (1 if len(df) % rows_per_task > 0 else 0)
        total_lessons = (total_levels // tasks_per_lesson) + (1 if total_levels % tasks_per_lesson > 0 else 0)

        for l in range(1, total_lessons + 1):
            # షీట్ లో ప్రతి లెసన్ కి మొదటి రో (Row) నుండి పేరు తీసుకోవడం
            start_row = (l - 1) * rows_per_lesson
            if start_row < len(df):
                # ఇక్కడ 'lesson_name' అనేది నీ షీట్ లో ఉన్న కాలమ్ పేరుకు సరిపోవాలి
                try:
                    actual_lesson_name = df.iloc[start_row]['lesson_name']
                except:
                    actual_lesson_name = f"Lesson {l}"
            else:
                actual_lesson_name = "Coming Soon..."
                
            st.markdown(f"### 📘 {actual_lesson_name}") 
            
            cols = st.columns(tasks_per_lesson)
            for t in range(1, tasks_per_lesson + 1):
                level_num = ((l - 1) * tasks_per_lesson) + t
                if level_num > total_levels: break
                
                with cols[t-1]:
                    if level_num <= st.session_state.unlocked_level:
                        if st.button(f"Task {t}\n⭐", key=f"lvl_{level_num}"):
                            st.session_state.current_playing_level = level_num
                            st.rerun()
                    else:
                        st.button(f"Task {t}\n🔒", key=f"lvl_{level_num}", disabled=True)
            st.write("---")
        
        st.write("⏳ New content uploading daily...")

    else:
        # Quiz Section (No changes here)
        level = st.session_state.current_playing_level
        st.header(f"Task {level} ⚡")
        
        start_idx = (level - 1) * 10
        end_idx = min(start_idx + 10, len(df))
        level_df = df.iloc[start_idx:end_idx]
        
        score = 0
        answered_count = 0

        for i, row in level_df.iterrows():
            st.markdown(f"**ప్రశ్న {i+1}:** {row['Question']}")
            opts = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
            
            key = f"q_{i}_lvl_{level}"
            if key not in st.session_state: st.session_state[key] = None

            choice = st.radio(
                "సమాధానం ఎంచుకోండి:", opts, 
                index=None if st.session_state[key] is None else opts.index(st.session_state[key]),
                key=f"radio_{i}",
                disabled=st.session_state[key] is not None
            )

            if choice and st.session_state[key] is None:
                st.session_state[key] = choice
                st.rerun()

            if st.session_state[key]:
                answered_count += 1
                if str(st.session_state[key]).strip() == str(row['Correct_Answer']).strip():
                    st.success("Correct! ✅")
                    score += 1
                else:
                    st.error(f"Wrong! ❌ Correct: {row['Correct_Answer']}")
                    st.session_state.level_failed = True
            st.write("---")

        if answered_count == len(level_df):
            st.subheader(f"📊 Result: {score}/{len(level_df)}")
            if not st.session_state.level_failed and score == len(level_df):
                st.balloons()
                st.success("10/10! Next Task Unlocked! 🎉")
                if level == st.session_state.unlocked_level:
                    st.session_state.unlocked_level += 1
                st.button("Map కి వెళ్ళు 🗺️", on_click=reset_to_map)
            else:
                st.error("Try Again for 10/10!")
                if st.button("Retry Task 🔄"):
                    for k in list(st.session_state.keys()):
                        if f"_lvl_{level}" in k: del st.session_state[k]
                    st.session_state.level_failed = False
                    st.rerun()
                st.button("Map కి వెళ్ళు 🗺️", on_click=reset_to_map)

except Exception as e:
    st.error(f"Error: {e}")
