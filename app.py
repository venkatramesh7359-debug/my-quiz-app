import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. పేజీ సెట్టింగ్స్
st.set_page_config(page_title="Venkat Quiz Levels", page_icon="🎮", layout="centered")

# 2. Footer & Fullscreen తీసేసే JavaScript
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

# 4. సెషన్ స్టేట్ (లెవల్స్ మేనేజ్మెంట్)
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'current_level' not in st.session_state: st.session_state.current_level = 1
if 'answers' not in st.session_state: st.session_state.answers = {}
if 'quiz_submitted' not in st.session_state: st.session_state.quiz_submitted = False

st.title("🎮 Venkat's Candy Crush Quiz")

try:
    df = pd.read_csv(SHEET_URL)
    total_questions = len(df)
    total_levels = (total_questions // 10) + (1 if total_questions % 10 > 0 else 0)

    # పేరు అడగడం
    if st.session_state.user_name == "":
        name = st.text_input("మీ పేరు నమోదు చేయండి:")
        if st.button("Start Game 🚀"):
            if name:
                st.session_state.user_name = name
                st.rerun()
    else:
        st.sidebar.write(f"👤 Player: **{st.session_state.user_name}**")
        st.sidebar.write(f"⭐ Current Level: **{st.session_state.current_level}**")

        # లెవల్ సెలక్షన్
        level = st.session_state.current_level
        start_idx = (level - 1) * 10
        end_idx = start_idx + 10
        level_df = df.iloc[start_idx:end_idx]

        st.header(f"Level {level}")
        st.write(f"ఈ లెవల్ పాస్ అవ్వాలంటే 10/10 కరెక్ట్ అవ్వాలి!")

        # ప్రశ్నలు చూపించడం
        for i, row in level_df.iterrows():
            st.markdown(f"**Q{i+1}: {row['Question']}**")
            options = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
            
            # యూజర్ ఆన్సర్ సెలెక్ట్ చేయడం
            st.session_state.answers[i] = st.radio(f"సమాధానం ఎంచుకోండి (Q{i+1}):", options, index=None, key=f"q_{i}")
            st.write("---")

        # Submit బటన్
        if st.button("Submit Level ✅"):
            correct_count = 0
            wrong_questions = []

            for i, row in level_df.iterrows():
                user_ans = st.session_state.answers.get(i)
                if user_ans and str(user_ans).strip() == str(row['Correct_Answer']).strip():
                    correct_count += 1
                else:
                    wrong_questions.append(i + 1)

            # Candy Crush Logic
            if correct_count == len(level_df):
                st.balloons()
                st.success(f"అద్భుతం! లెవల్ {level} కంప్లీట్ అయింది! 🎉")
                if level < total_levels:
                    if st.button("Next Level ➡️"):
                        st.session_state.current_level += 1
                        st.session_state.answers = {}
                        st.rerun()
                else:
                    st.write("అన్ని లెవల్స్ పూర్తి చేశారు! మీరు విజేత! 🏆")
            else:
                st.error(f"లెవల్ ఫెయిల్! స్కోర్: {correct_count}/10")
                st.warning(f"ప్రశ్నలు {wrong_questions} తప్పుగా ఇచ్చారు. మళ్ళీ ప్రయత్నించండి!")
                if st.button("Try Level Again 🔄"):
                    st.session_state.answers = {}
                    st.rerun()

except Exception as e:
    st.error("డేటా లోడ్ అవ్వలేదు. షీట్ చెక్ చేయండి.")
