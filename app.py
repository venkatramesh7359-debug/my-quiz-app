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

# లెవల్ ని పూర్తిగా రీసెట్ చేసే ఫంక్షన్
def restart_level(level):
    # ఆ లెవల్ కి సంబంధించిన అన్ని ఆన్సర్లను Session State నుండి క్లియర్ చేయడం
    keys_to_delete = [k for k in st.session_state.keys() if f"_lvl_{level}" in k]
    for k in keys_to_delete:
        del st.session_state[k]
    st.session_state.level_failed = False
    st.rerun()

def reset_to_map():
    st.session_state.current_playing_level = None
    st.session_state.level_failed = False
    st.rerun()

st.title("🎮 Venkat's Learning Quest")

@st.cache_data(ttl=0)
def load_data(url):
    try:
        data = pd.read_csv(url)
        data.columns = [c.strip().lower().replace(' ', '_') for c in data.columns]
        return data
    except Exception as e:
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
            
            # అసలు ఎన్ని ప్రశ్నలు ఉన్నాయో దాన్ని బట్టి లెవల్స్ లెక్కింపు
            total_rows = len(df)
            total_levels = (total_rows // rows_per_task)
            total_lessons = (total_levels // tasks_per_lesson) + (1 if total_levels % tasks_per_lesson > 0 else 0)

            # మనం కనీసం 10 లెసన్స్ వరకు చూపిద్దాం (Coming Soon కోసం)
            display_lessons = max(total_lessons, 5)

            for l in range(1, display_lessons + 1):
                start_row = (l - 1) * rows_per_lesson
                
                # లెసన్ పేరు లాజిక్
                current_name = "Coming Soon..."
                if start_row < total_rows:
                    if 'lesson_name' in df.columns:
                        val = df.iloc[start_row]['lesson_name']
                        if pd.notna(val) and str(val).strip() != "":
                            current_name = str(val)
                        else:
                            current_name = f"Lesson {l}"
                
                st.markdown(f"### 📘 {current_name}") 
                
                # ఒకవేళ ఆ లెసన్ లో డేటా లేకపోతే బటన్లు చూపించదు
                if current_name == "Coming Soon...":
                    st.write("🛠️ Work in progress...")
                else:
                    cols = st.columns(tasks_per_lesson)
                    for t in range(1, tasks_per_lesson + 1):
                        level_num = ((l - 1) * tasks_per_lesson) + t
                        
                        # డేటా ఉన్న లెవల్స్ కి మాత్రమే బటన్లు
                        if level_num <= total_levels:
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
            # Quiz Section
            level = st.session_state.current_playing_level
            st.header(f"Task {level} ⚡")
            
            start_idx = (level - 1) * 10
            end_idx = min(start_idx + 10, len(df))
            level_df = df.iloc[start_idx:end_idx]
            
            score = 0
            answered_count = 0

            for i, row in level_df.iterrows():
                st.markdown(f"**ప్రశ్న {i+1}:** {row['question']}")
                opts = [str(row['option_a']), str(row['option_b']), str(row['option_c']), str(row['option_d'])]
                
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
                    correct_val = str(row['correct_answer']).strip().lower()
                    if str(st.session_state[key]).strip().lower() == correct_val:
                        st.success("Correct! ✅")
                        score += 1
                    else:
                        st.error(f"Wrong! ❌ Correct: {row['correct_answer']}")
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
                    st.error("Try Again! 10/10 వస్తేనే నెక్స్ట్ టాస్క్ ఓపెన్ అవుతుంది.")
                    if st.button("Retry Task 🔄"):
                        restart_level(level)
                    st.button("Map కి వెళ్ళు 🗺️", on_click=reset_to_map)

except Exception as e:
    st.error(f"System Error: {e}")
