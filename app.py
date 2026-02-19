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
    # లెవల్ కి సంబంధించిన డేటా మొత్తం క్లియర్ చేయడం
    level = st.session_state.current_playing_level
    for k in list(st.session_state.keys()):
        if f"_lvl_{level}" in k:
            del st.session_state[k]
    st.session_state.current_playing_level = None
    st.session_state.level_failed = False
    st.rerun()

st.title("🎮 Venkat's Learning Quest")

try:
    df = pd.read_csv(SHEET_URL)
    
    if st.session_state.user_name == "":
        name = st.text_input("మీ పేరు నమోదు చేయండి:")
        if st.button("Start Game 🚀"):
            if name.strip():
                st.session_state.user_name = name
                st.rerun()
    
    elif st.session_state.current_playing_level is None:
        st.subheader(f"Player: {st.session_state.user_name}")
        
        tasks_per_lesson = 5
        total_levels = (len(df) // 10) + (1 if len(df) % 10 > 0 else 0)
        total_lessons = (total_levels // tasks_per_lesson) + (1 if total_levels % tasks_per_lesson > 0 else 0)

        for l in range(1, total_lessons + 1):
            # షీట్ లోని 'lesson_name' కాలమ్ నుండి పేరు తీసుకోవడం
            start_row_for_lesson = (l - 1) * tasks_per_lesson * 10
            if start_row_for_lesson < len(df):
                actual_lesson_name = df.iloc[start_row_for_lesson]['lesson_name']
            else:
                actual_lesson_name = "Upcoming Lesson"
                
            st.markdown(f"### 📘 Lesson {l}: {actual_lesson_name}") 
            
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

        # టాస్క్ చివరలో రిజల్ట్ చూపించడం
        if answered_count == len(level_df):
            st.subheader(f"📊 Your Score: {score}/{len(level_df)}")
            
            if not st.session_state.level_failed and score == len(level_df):
                st.balloons()
                st.success("Excellent! 10/10 సాధించారు. తర్వాతి టాస్క్ అన్‌లాక్ అయింది! 🎉")
                if level == st.session_state.unlocked_level:
                    st.session_state.unlocked_level += 1
                st.button("Map కి వెళ్ళు 🗺️", on_click=reset_to_map)
            else:
                st.error("పాస్ అవ్వడానికి 10/10 రావాలి. దయచేసి మళ్ళీ ప్రయత్నించండి.")
                if st.button("Retry Task 🔄"):
                    # Retry నొక్కినప్పుడు ఆన్సర్స్ క్లియర్ అయి మళ్ళీ అదే లెవల్ లో మొదటి ప్రశ్న వస్తుంది
                    for k in list(st.session_state.keys()):
                        if f"_lvl_{level}" in k: del st.session_state[k]
                    st.session_state.level_failed = False
                    st.rerun()
                st.button("Map కి వెళ్ళు 🗺️", on_click=reset_to_map)

except Exception as e:
    st.error("షీట్ లో 'lesson_name' కాలమ్ ఉందో లేదో ఒకసారి చెక్ చేయండి!")
