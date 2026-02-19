import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. పేజీ సెట్టింగ్స్ - ఇది అందరికంటే పైన ఉండాలి
st.set_page_config(
    page_title="Venkat Quiz App", 
    page_icon="📚", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. JavaScript & CSS బ్రహ్మాస్త్రం (Footer మరియు Toolbar ని దాచడానికి)
# ఇది యాప్ రన్ అవుతున్నంత సేపు బ్యాక్‌గ్రౌండ్‌లో ఫుటర్ ని వెతికి తీసేస్తూనే ఉంటుంది
components.html(
    """
    <script>
    const hideElements = () => {
        const selectors = [
            'footer', 
            '[data-testid="stFooter"]', 
            'header', 
            '.stAppDeployButton', 
            '[data-testid="stHeader"]',
            '#MainMenu'
        ];
        selectors.forEach(selector => {
            const elements = window.parent.document.querySelectorAll(selector);
            elements.forEach(el => el.style.display = 'none');
        });
    };
    setInterval(hideElements, 500); // ప్రతి అర సెకనుకు ఒకసారి చెక్ చేస్తుంది
    </script>
    """,
    height=0,
)

# CSS ద్వారా అదనపు రక్షణ
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {display: none !important;}
    header {display: none !important;}
    [data-testid="stFooter"] {display: none !important;}
    .stAppDeployButton {display: none !important;}
    .main .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    </style>
    """, unsafe_allow_html=True)

# 3. డేటా లోడింగ్ (Google Sheet URL)
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

# 4. సెషన్ స్టేట్ (యాప్ రిఫ్రెష్ అయినా డేటా పోకుండా ఉండటానికి)
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# 5. యాప్ హెడర్
st.title("📚 Venkat's Learning App")
st.write("---")

try:
    # Google Sheet నుండి డేటా రీడ్ చేయడం
    df = pd.read_csv(SHEET_URL)
    
    # ఎంట్రీ స్క్రీన్: పేరు అడగడం
    if not st.session_state.quiz_started:
        st.subheader("క్విజ్ ప్రారంభించండి")
        name = st.text_input("మీ పేరు నమోదు చేయండి:", placeholder="ఇక్కడ టైప్ చేయండి...")
        
        if st.button("Start Quiz 🚀"):
            if name.strip():
                st.session_state.user_name = name
                st.session_state.quiz_started = True
                st.rerun()
            else:
                st.warning("ముందుగా మీ పేరును ఎంటర్ చేయండి.")
    
    # క్విజ్ స్క్రీన్
    else:
        st.success(f"హలో {st.session_state.user_name}! ఆల్ ది బెస్ట్.")
        
        if st.button("🔄 Reset Quiz (మొదటి నుండి)"):
            st.session_state.quiz_started = False
            st.rerun()
            
        st.write("---")
        
        # ప్రశ్నలను లూప్ ద్వారా చూపించడం
        for index, row in df.iterrows():
            st.markdown(f"#### ప్రశ్న {index+1}:")
            st.write(f"**{row['Question']}**")
            
            # ఆప్షన్స్
            options = [
                str(row['Option_A']), 
                str(row['Option_B']), 
                str(row['Option_C']), 
                str(row['Option_D'])
            ]
            
            # రేడియో బటన్స్ ద్వారా ఆప్షన్స్ సెలక్షన్
            choice = st.radio(
                "సమాధానాన్ని ఎంచుకోండి:", 
                options, 
                index=None, 
                key=f"q_{index}"
            )
            
            # చెక్ బటన్
            if st.button(f"Check Answer {index+1} ✔️", key=f"btn_{index}"):
                if choice is None:
                    st.warning("ఒక ఆప్షన్‌ను ఎంచుకోండి!")
                else:
                    user_answer = str(choice).strip()
                    correct_answer = str(row['Correct_Answer']).strip()
                    
                    if user_answer == correct_answer:
                        st.success("సరైన సమాధానం! ✅")
                    else:
                        st.error(f"తప్పు! సరైన సమాధానం: {row['Correct_Answer']} ❌")
            st.write("---")

except Exception as e:
    st.error("డేటా లోడ్ అవ్వలేదు. దయచేసి ఇంటర్నెట్ లేదా షీట్ పర్మిషన్స్ చెక్ చేయండి.")
