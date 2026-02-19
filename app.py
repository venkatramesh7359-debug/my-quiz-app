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

# 4. Session State
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

@st.cache_data(ttl=0)
def load_data(url):
    try:
        # డేటాను చదివి, కాలమ్ పేర్లను క్లీన్ చేయడం
        data = pd.read_csv(url)
        data.columns = [str(c).strip().lower().replace(' ', '_') for c in data.columns]
        return data
    except Exception as e:
        st.error(f"Error: {e}")
        return None

try:
    df = load_data(SHEET_URL)
    
    if df is not None:
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
                start_row = (l - 1) * rows_per_lesson
                
                # --- లెసన్ పేరును పక్కాగా కనిపెట్టే లాజిక్ ---
                display_name = f"Lesson {l}"
                if start_row < len(df):
                    # కాలమ్ పేర్లలో 'lesson' అని ఎక్కడ ఉన్నా అది తీసుకుంటుంది
                    lesson_cols = [c for c in df.columns if 'lesson' in c]
                    if lesson_cols:
                        val = df.iloc[start_row][lesson_cols[0]]
                        if pd.notna(val) and str(val).strip() != "":
                            display_name = str(val)
                        else:
                            # ఒకవేళ ఆ వరుస ఖాళీగా ఉంటే, పై వరుసల నుండి పేరు వెతుకుతుంది
                            temp_val = df.iloc[:start_row+1][lesson_cols[0]].dropna().iloc[-1]
                            display_name = str(temp_val)

                st.markdown(f"### 📘 {display_name}") 
                
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
            
            st.write("⏳ New tasks uploading daily...")

        else:
            # Quiz Section
            level = st.session_state.current_playing_level
            st.header(f"Task {level} ⚡")
            
            start_idx = (level - 1) * 10
            end_idx = min(start_idx + 10, len(df))
            level_df = df.iloc[start_idx:end_idx]
            
            score = 0
            answered_count = 0

            for i, row in level_df.iterrows():
                # కాలమ్ పేర్లు వెతకడం
                q_col = [c for c in df.columns if 'question' in c][0]
                st.markdown(f"**ప్రశ్న {i+1}:** {row[q_col]}")
                
                # ఆప్షన్స్
                opts = [
                    str(row[[c for c in df.columns if 'option_a' in c][0]]),
                    str(row[[c for c in df.columns if 'option_b' in c][0]]),
                    str(row[[c for c in df.columns if 'option_c' in c][0]]),
                    str(row[[c for c in df.columns if 'option_d' in c][0]])
                ]
                
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
                    ans_col = [c for c in df.columns if 'correct' in c][0]
                    correct_val = str(row[ans_col]).strip().lower()
                    if str(st.session_state[key]).strip().lower() == correct_val:
                        st.success("Correct! ✅")
                        score += 1
                    else:
                        st.error(f"Wrong! ❌ Correct: {row[ans_col]}")
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
    st.error(f"Error: {e}. గూగుల్ షీట్‌లో కాలమ్ పేర్లు సరిగ్గా ఉన్నాయో లేదో చెక్ చేయండి.")
