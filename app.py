import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. పేజీ సెట్టింగ్స్ - బ్రౌజర్ ట్యాబ్ పేరు మరియు ఐకాన్
st.set_page_config(
    page_title="Venkat Quiz App", 
    page_icon="📚", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. ఆ కింద ఉన్న 'Fullscreen' మరియు 'Built with Streamlit' ని తీసేసే కోడ్
hide_elements = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {display: none !important;}
    header {display: none !important;}
    [data-testid="stFooter"] {display: none !important;}
    .stAppDeployButton {display: none !important;}
    /* Fullscreen బటన్ ని దాచడానికి */
    [data-testid="styled-link-icon"] {display: none !important;}
    button[title="View fullscreen"] {display: none !important;}
    /* కింది వైట్ బార్ ని పూర్తిగా క్లోజ్ చేయడానికి */
    .stApp > header {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    </style>
    """
st.markdown(hide_elements, unsafe_allow_html=True)

# JavaScript ద్వారా అదనపు క్లీనప్
components.html(
    """
    <script>
    const removeOverlay = () => {
        const arr = window.parent.document.querySelectorAll('footer, [data-testid="stFooter"], .stAppDeployButton');
        arr.forEach(el => el.style.display = 'none');
    };
    setInterval(removeOverlay, 300);
    </script>
    """,
    height=0,
)

# 3. నీ Google Sheets URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

# 4. సెషన్ స్టేట్ మెనేజ్మెంట్
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# 5. యాప్ టైటిల్
st.title("📚 Venkat's Learning App")
st.write("---")

try:
    # డేటాని లోడ్ చేయడం
    df = pd.read_csv(SHEET_URL)
    
    # లాగిన్ స్క్రీన్
    if not st.session_state.quiz_started:
        st.subheader("క్విజ్ ప్రారంభించండి")
        name = st.text_input("మీ పేరు నమోదు చేయండి:", placeholder="ఇక్కడ టైప్ చేయండి...")
        
        if st.button("Start Quiz 🚀"):
            if name.strip():
                st.session_state.user_name = name
                st.session_state.quiz_started = True
                st.rerun()
            else:
                st.warning("ముందుగా పేరు నమోదు చేయండి.")
    
    # క్విజ్ స్క్రీన్
    else:
        st.success(f"హలో {st.session_state.user_name}! ఆల్ ది బెస్ట్.")
        
        if st.button("🔄 Reset Quiz (మళ్ళీ మొదటికి)"):
            st.session_state.quiz_started = False
            st.rerun()
            
        st.write("---")
        
        # ప్రశ్నలు మరియు ఆన్సర్లు
        for index, row in df.iterrows():
            st.markdown(f"#### ప్రశ్న {index+1}:")
            st.write(f"**{row['Question']}**")
            
            options = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
            
            choice = st.radio(
                "సమాధానాన్ని ఎంచుకోండి:", 
                options, 
                index=None, 
                key=f"q_{index}"
            )
            
            if st.button(f"Check Answer {index+1} ✔️", key=f"btn_{index}"):
                if choice is None:
                    st.warning("ఒక ఆప్షన్‌ను సెలెక్ట్ చేయండి!")
                else:
                    user_ans = str(choice).strip().lower()
                    correct_ans = str(row['Correct_Answer']).strip().lower()
                    
                    if user_ans == correct_ans:
                        st.success("సరైన సమాధానం! ✅")
                    else:
                        st.error(f"తప్పు! సరైన సమాధానం: {row['Correct_Answer']} ❌")
            st.write("---")

except Exception as e:
    st.error("డేటా లోడ్ అవ్వడంలో సమస్య ఉంది.")
