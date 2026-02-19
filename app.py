import streamlit as st
import pandas as pd

# 1. పేజీ సెట్టింగ్స్ - ఇది అందరికంటే పైన ఉండాలి
st.set_page_config(page_title="Venkat Quiz App", page_icon="📚", layout="centered")

# 2. Footer మరియు అనవసరమైన లింక్స్ అన్నీ దాచేసే 'బ్రహ్మాస్త్రం' CSS
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {display: none !important;}
    header {display: none !important;}
    .stAppDeployButton {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    [data-testid="stFooter"] {display: none !important;}
    /* యాప్ క్లీన్‌గా కనిపించడానికి ప్యాడింగ్ సర్దుబాటు */
    .main .block-container {padding-top: 2rem; padding-bottom: 0rem;}
    </style>
    """
st.markdown(hide_style, unsafe_allow_html=True)

# 3. నీ Google Sheets CSV URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

# 4. సెషన్ స్టేట్ మేనేజ్‌మెంట్ (డేటా పోకుండా ఉండటానికి)
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'score' not in st.session_state:
    st.session_state.score = 0

# 5. యాప్ హెడర్
st.title("📚 Venkat's Interactive Quiz")
st.write(f"ప్రిపరేషన్: AP DSC / TET")
st.write("---")

try:
    # డేటాని లోడ్ చేయడం
    df = pd.read_csv(SHEET_URL)
    
    # ఎంట్రీ స్క్రీన్: పేరు అడగడం
    if not st.session_state.quiz_started:
        st.subheader("క్విజ్ ప్రారంభించండి")
        name = st.text_input("మీ పేరు నమోదు చేయండి:", placeholder="ఉదాహరణ: వెంకట్")
        
        if st.button("Start Quiz 🚀"):
            if name.strip():
                st.session_state.user_name = name
                st.session_state.quiz_started = True
                st.rerun()
            else:
                st.warning("దయచేసి మీ పేరును నమోదు చేయండి.")
    
    # క్విజ్ స్క్రీన్
    else:
        st.success(f"హలో {st.session_state.user_name}! ప్రశ్నలను జాగ్రత్తగా చదివి సమాధానం ఇవ్వండి.")
        
        if st.button("🔄 Reset Quiz (మొదటి నుండి)"):
            st.session_state.quiz_started = False
            st.session_state.score = 0
            st.rerun()
            
        st.write("---")
        
        # ప్రశ్నల లూప్
        for index, row in df.iterrows():
            st.markdown(f"#### ప్రశ్న {index+1}:")
            st.write(f"**{row['Question']}**")
            
            # ఆప్షన్స్ లోడ్ చేయడం
            options = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
            
            # రేడియో బటన్స్
            choice = st.radio(
                "సరైన సమాధానాన్ని ఎంచుకోండి:", 
                options, 
                index=None, 
                key=f"q_{index}"
            )
            
            # సమాధానం చెక్ చేసే బటన్
            if st.button(f"Check Answer {index+1} ✔️", key=f"btn_{index}"):
                if choice is None:
                    st.warning("ముందుగా ఒక ఆప్షన్‌ను ఎంచుకోండి!")
                else:
                    user_answer = str(choice).strip().lower()
                    correct_answer = str(row['Correct_Answer']).strip().lower()
                    
                    if user_answer == correct_answer:
                        st.success("సరైన సమాధానం! ✅")
                    else:
                        st.error(f"తప్పు! సరైన సమాధానం: {row['Correct_Answer']} ❌")
            st.write("---")

except Exception as e:
    st.error("డేటా లోడ్ అవ్వడంలో ఇబ్బంది ఉంది. దయచేసి ఇంటర్నెట్ లేదా షీట్ లింక్ చెక్ చేయండి.")
