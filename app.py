import streamlit as st
import pandas as pd

# 1. పేజీ సెట్టింగ్స్ - ఇది అందరికంటే పైన ఉండాలి
st.set_page_config(page_title="Venkat Quiz App", page_icon="📚", layout="centered")

# 2. Footer, Toolbar మరియు Streamlit లింక్స్ అన్నీ దాచేసే పక్కా CSS కోడ్
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stFooter"] {display: none;}
    [data-testid="stHeader"] {display: none;}
    .stApp [data-testid="stToolbar"] {display: none;}
    </style>
    """
st.markdown(hide_style, unsafe_allow_html=True)

# 3. Google Sheets URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

# 4. యాప్ టైటిల్
st.title("📚 Venkat's Learning App")
st.write("---")

# 5. క్విజ్ లాజిక్
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False

try:
    # డేటాని లోడ్ చేయడం
    df = pd.read_csv(SHEET_URL)
    
    if not st.session_state.quiz_started:
        # స్టార్టింగ్ స్క్రీన్
        name = st.text_input("మీ పేరు నమోదు చేయండి:", placeholder="ఇక్కడ టైప్ చేయండి...")
        if st.button("Start Quiz 🚀"):
            if name.strip():
                st.session_state.user_name = name
                st.session_state.quiz_started = True
                st.rerun()
            else:
                st.warning("దయచేసి మీ పేరును నమోదు చేయండి.")
    else:
        # క్విజ్ స్క్రీన్
        st.subheader(f"ఆల్ ది బెస్ట్, {st.session_state.user_name}! 👍")
        
        if st.button("🔄 Reset Quiz (మొదటి నుండి ప్రారంభించు)"):
            st.session_state.quiz_started = False
            st.rerun()
            
        st.write("---")
        
        # ప్రశ్నలను చూపించడం
        for index, row in df.iterrows():
            st.markdown(f"### ప్రశ్న {index+1}:")
            st.markdown(f"**{row['Question']}**")
            
            # ఆప్షన్స్
            options = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
            
            choice = st.radio(
                "సరైన సమాధానాన్ని ఎంచుకోండి:", 
                options, 
                index=None, 
                key=f"q_{index}"
            )
            
            # చెక్ బటన్
            if st.button(f"Check Answer {index+1} ✔️", key=f"btn_{index}"):
                if choice is None:
                    st.warning("దయచేసి ఒక ఆప్షన్‌ను ఎంచుకోండి!")
                elif str(choice).strip() == str(row['Correct_Answer']).strip():
                    st.success("సరైన సమాధానం! ✅")
                else:
                    st.error(f"తప్పు! సరైన సమాధానం: {row['Correct_Answer']} ❌")
            st.write("---")

except Exception as e:
    st.error("క్షమించండి! డేటా లోడ్ చేయడంలో సమస్య వచ్చింది.")
    # st.write(f"Error details: {e}") # డెవలప్‌మెంట్ కోసం ఇది వాడుకోవచ్చు
