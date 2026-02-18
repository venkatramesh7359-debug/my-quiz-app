import streamlit as st
import pandas as pd

st.set_page_config(page_title="Venkat Quiz App", page_icon="📚")
st.title("📚 Venkat's Learning App")

# మీ షీట్ లింక్ ఇక్కడ నేరుగా ఇచ్చేశాను
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

try:
    # డేటాని చదవడం
    df = pd.read_csv(SHEET_URL)
    
    name = st.text_input("మీ పేరు నమోదు చేయండి:")
    
    if name:
        if st.button("Start Quiz"):
            st.balloons()
            st.success(f"హలో {name}! క్విజ్ ప్రారంభిద్దాం.")
            
            for index, row in df.iterrows():
                st.subheader(f"ప్రశ్న {index+1}:")
                st.write(f"**{row['Question']}**")
                
                # ఆప్షన్లు
                options = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
                choice = st.radio(f"సరైన సమాధానాన్ని ఎంచుకోండి:", options, key=f"q{index}")
                
                if st.button(f"Check Answer {index+1}", key=f"btn{index}"):
                    if str(choice).strip() == str(row['Correct_Answer']).strip():
                        st.success("సరైన సమాధానం! ✅")
                    else:
                        st.error(f"తప్పు! సరైన సమాధానం: {row['Correct_Answer']} ❌")
                st.write("---")
except Exception as e:
    st.error("డేటా లోడ్ అవ్వలేదు. షీట్ పర్మిషన్లు మరియు హెడర్స్ చెక్ చేయండి.")
    st.write(f"Error: {e}")
