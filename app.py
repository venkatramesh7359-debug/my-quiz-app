import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. Page Config
st.set_page_config(page_title="Venkat's Learning Quest", page_icon="🎮", layout="centered")

# 2. Footer & Fullscreen Hiding (JavaScript)
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
    st.session_state.current_playing_level = None
    st.session_state.level_failed = False
    st.rerun()

st.title("🎮 Venkat's Learning Quest")

try:
    df = pd.read_csv(SHEET_URL)
    
    # Step 1: Login
    if st.session_state.user_name == "":
        name = st.text_input("మీ పేరు నమోదు చేయండి:")
        if st.button("Start Game 🚀"):
            if name.strip():
                st.session_state.user_name = name
                st.rerun()
    
    # Step 2: Lesson & Tasks (Levels) View
    elif st.session_state.current_playing_level is None:
        st.subheader(f"Player: {st.session_state.user_name}")
        
        # ఉదాహరణకి ఒక్కో లెసన్ లో 5 టాస్క్ లు (Levels)
        tasks_per_lesson = 5
        total_levels = (len(df) // 10) + (1 if len(df) % 10 > 0 else 0)
        total_lessons = (total_levels // tasks_per_lesson) + (1 if total_levels % tasks_per_lesson > 0 else 0)

        for l in range(1, total_lessons + 1):
            st.markdown(f"### 📘 Lesson {l}") # Lesson Heading
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
        
        st.write("⏳ Uploading more lessons soon...")

    # Step 3: Quiz Screen
    else:
        level = st.session_state.current_playing_level
        st.header(f"Task {level} ⚡")
        
        start_idx = (level - 1) * 10
        end_idx = min(start_idx + 10, len(df))
        level_df = df.iloc[start_idx:end_idx]
        
        score = 0
        all_answered = True

        for i, row in level_df.iterrows():
            st.markdown(f"**ప్రశ్న {i+1}:** {row['Question']}")
            opts = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
            
            # ఒకసారి ఆన్సర్ ఇస్తే మార్చకుండా ఉండటానికి 'disabled' వాడుతున్నాం
            key = f"q_{i}_lvl_{level}"
            if key not in st.session_state:
                st.session_state[key] = None

            choice = st.radio(
                "సమాధానం ఎంచుకోండి:", opts, 
                index=None if st.session_state[key] is None else opts.index(st.session_state[key]),
                key=f"radio_{i}",
                disabled=st.session_state[key] is not None # ఆన్సర్ ఇచ్చాక Lock అయిపోతుంది
            )

            if choice and st.session_state[key] is None:
                st.session_state[key] = choice
                st.rerun()

            if st.session_state[key]:
                if str(st.session_state[key]).strip() == str(row['Correct_Answer']).strip():
                    st.success("Correct! ✅")
                    score += 1
                else:
                    st.error(f"Wrong! ❌ Correct: {row['Correct_Answer']}")
                    st.session_state.level_failed = True # ఒకటి తప్పు అయినా ఫెయిల్ కింద లెక్క
            else:
                all_answered = False
            st.write("---")

        if all_answered:
            if st.session_state.level_failed == False and score == len(level_df):
                st.balloons()
                st.success("అద్భుతం! టాస్క్ పూర్తి చేసారు! 🔓")
                if level == st.session_state.unlocked_level:
                    st.session_state.unlocked_level += 1
                st.button("Map కి వెళ్ళు 🗺️", on_click=reset_to_map)
            else:
                st.error(f"ఈ టాస్క్ లో తప్పులు ఉన్నాయి. పాస్ అవ్వడానికి 10/10 రావాలి!")
                if st.button("Restart Task 🔄"):
                    # ఆ లెవల్ కి సంబంధించిన ఆన్సర్స్ అన్నీ క్లియర్ చేయడం
                    for k in list(st.session_state.keys()):
                        if f"_lvl_{level}" in k: del st.session_state[k]
                    st.session_state.level_failed = False
                    st.rerun()

except Exception as e:
    st.error("Sheet Error!")
