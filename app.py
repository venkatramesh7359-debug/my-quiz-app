import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. పేజీ సెట్టింగ్స్
st.set_page_config(page_title="Venkat Quiz App", page_icon="📚", layout="centered")

# 2. ఆ 'Fullscreen' మరియు Footer ని ఫోర్స్ గా తీసేసే JavaScript
components.html(
    """
    <script>
    const removeElements = () => {
        const selectors = [
            'footer', '[data-testid="stFooter"]', 'header', 
            '.stAppDeployButton', 'button[title="View fullscreen"]',
            '[data-testid="styled-link-icon"]', '.stStatusWidget', '#MainMenu'
        ];
        selectors.forEach(selector => {
            const elements = window.parent.document.querySelectorAll(selector);
            elements.forEach(el => {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
            });
        });
    };
    setInterval(removeElements, 500);
    </script>
    """,
    height=0,
)

# 3. CSS అదనపు రక్షణ
st.markdown("<style>footer {display: none !important;} [data-testid='stFooter'] {display: none !important;}</style>", unsafe_allow_html=True)

# 4. Google Sheets URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

# 5. సెషన్ స్టేట్ రీసెట్ ఆప్షన్ (పేరు మళ్ళీ అడగడానికి)
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

st.title("📚 Venkat's Learning App")

try:
    df = pd.read_csv(SHEET_URL)
    
    # ఒకవేళ క్విజ్ ఇంకా స్టార్ట్ అవ్వకపోతే పేరు అడుగుతుంది
    if not st.session_state.quiz_started:
        st.subheader("క్విజ్ ప్రారంభించండి")
        name = st.text_input("మీ పేరు నమోదు చేయండి:", key="name_input")
        if st.button("Start Quiz 🚀"):
            if name.strip():
                st.session_state.user_name = name
                st.session_state.quiz_started = True
                st.rerun() # ఇది పేజీని రిఫ్రెష్ చేసి క్విజ్ చూపిస్తుంది
            else:
                st.warning("దయచేసి మీ పేరును నమోదు చేయండి.")
    
    # క్విజ్ స్క్రీన్
    else:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"హలో {st.session_state.user_name}!")
        with col2:
            if st.button("Exit/Reset"): # ఈ బటన్ నొక్కితే మళ్ళీ పేరు అడుగుతుంది
                st.session_state.quiz_started = False
                st.session_state.user_name = ""
                st.rerun()
            
        st.write("---")
        
        # ప్రశ్నల లూప్
        for index, row in df.iterrows():
            st.markdown(f"#### ప్రశ్న {index+1}:")
            st.write(f"**{row['Question']}**")
            options = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
            
            choice = st.radio("సమాధానం ఎంచుకోండి:", options, index=None, key=f"q_{index}")
            
            if st.button(f"Check Answer {index+1}", key=f"btn_{index}"):
                if choice is None:
                    st.warning("ఒక ఆప్షన్‌ను సెలెక్ట్ చేయండి!")
                elif str(choice).strip() == str(row['Correct_Answer']).strip():
                    st.success("సరైన సమాధానం! ✅")
                else:
                    st.error(f"తప్పు! సరైన సమాధానం: {row['Correct_Answer']} ❌")
            st.write("---")

except Exception as e:
    st.error("డేటా లోడ్ అవ్వలేదు.")
