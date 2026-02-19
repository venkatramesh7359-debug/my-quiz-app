import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. Page Config
st.set_page_config(page_title="Venkat's Learning Quest", page_icon="🎮", layout="centered")

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
    st.session_state.current_playing_level = None
    st.session_state.level_failed = False
    st.rerun()

st.title("🎮 Venkat's Learning Quest")

try:
    df = pd.read_csv(SHEET_URL)
    
    # --- లెసన్ పేర్ల లిస్ట్ (నువ్వు ఇక్కడ పేర్లు మార్చుకోవచ్చు) ---
    # నీ దగ్గర ఎన్ని లెసన్స్ ఉంటే అన్ని పేర్లు ఇక్కడ ఇవ్వు
    lesson_names = {
        1: "తెలుగు వ్యాకరణం",
        2: "English Grammar",
        3: "Social Studies",
        4: "Mathematics",
        5: "General Science"
    }

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
            # ఇక్కడ లెసన్ పేరు కనిపిస్తుంది
            name_of_lesson = lesson_names.get(l, "మరిన్ని పాఠాలు")
            st.markdown(f"### 📘 Lesson {l}: {name_of_lesson}") 
            
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

    else:
        # క్విజ్ కోడ్ (మునుపటి లాగే ఉంటుంది)
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
                if str(st.session_state[key]).strip() == str(row['Correct_Answer']).strip():
                    st.success("Correct! ✅")
                    score += 1
                else:
                    st.error(f"Wrong! ❌ Correct: {row['Correct_Answer']}")
                    st.session_state.level_failed = True
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
                st.error("తప్పులు దొర్లాయి! 10/10 వస్తేనే నెక్స్ట్ లెవల్ ఓపెన్ అవుతుంది.")
                if st.button("Restart Task 🔄"):
                    for k in list(st.session_state.keys()):
                        if f"_lvl_{level}" in k: del st.session_state[k]
                    st.session_state.level_failed = False
                    st.rerun()

except Exception as e:
    st.error("డేటా లోడ్ అవ్వలేదు!")
