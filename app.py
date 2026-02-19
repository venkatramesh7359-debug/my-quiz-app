import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. పేజీ సెట్టింగ్స్
st.set_page_config(page_title="Venkat Quiz App", page_icon="📚", layout="centered")

# 2. JavaScript ఉపయోగించి Footerని ఫోర్స్ గా తీసేయడం
components.html(
    """
    <script>
    const removeElements = () => {
        const selectors = [
            'footer', 
            '[data-testid="stFooter"]', 
            'header', 
            '.stAppDeployButton', 
            '[data-testid="stHeader"]'
        ];
        selectors.forEach(selector => {
            const elements = window.parent.document.querySelectorAll(selector);
            elements.forEach(el => el.style.display = 'none');
        });
    };
    // యాప్ లోడ్ అయినప్పుడు మరియు ప్రతి 1 సెకనుకు ఒకసారి చెక్ చేస్తుంది
    setInterval(removeElements, 1000);
    </script>
    """,
    height=0,
)

# 3. పాత పద్ధతి CSS (Double Protection కోసం)
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {display: none !important;}
    header {display: none !important;}
    [data-testid="stFooter"] {display: none !important;}
    .stAppDeployButton {display: none !important;}
    </style>
    """
st.markdown(hide_style, unsafe_allow_html=True)

# --- ఇక్కడి నుండి నీ అసలు క్విజ్ కోడ్ ---

SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

st.title("📚 Venkat's Learning App")

if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False

try:
    df = pd.read_csv(SHEET_URL)
    
    if not st.session_state.quiz_started:
        name = st.text_input("మీ పేరు నమోదు చేయండి:")
        if st.button("Start Quiz"):
            if name:
                st.session_state.user_name = name
                st.session_state.quiz_started = True
                st.rerun()
            else:
                st.warning("దయచేసి పేరు టైప్ చేయండి.")
    else:
        st.success(f"హలో {st.session_state.user_name}! ఆల్ ది బెస్ట్.")
        if st.button("Reset Quiz"):
            st.session_state.quiz_started = False
            st.rerun()
            
        st.write("---")
        
        for index, row in df.iterrows():
            st.subheader(f"ప్రశ్న {index+1}:")
            st.write(f"**{row['Question']}**")
            
            options = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
            
            choice = st.radio(f"సమాధానం ఎంచుకోండి:", options, index=None, key=f"r_{index}")
            
            if st.button(f"Check Answer {index+1}", key=f"b_{index}"):
                if choice is None:
                    st.warning("ఆప్షన్‌ను ఎంచుకోండి!")
                elif str(choice).strip() == str(row['Correct_Answer']).strip():
                    st.success("సరైన సమాధానం! ✅")
                else:
                    st.error(f"తప్పు! సరైన సమాధానం: {row['Correct_Answer']} ❌")
            st.write("---")

except Exception as e:
    st.error("డేటా లోడ్ అవ్వలేదు.")
