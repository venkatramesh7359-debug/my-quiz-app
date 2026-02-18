import streamlit as st
import pandas as pd

st.set_page_config(page_title="Venkat Quiz App", page_icon="📚")
st.title("📚 Venkat's Learning App")

SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

# క్విజ్ స్టార్ట్ అయ్యిందో లేదో గుర్తుంచుకోవడానికి
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
        st.success(f"హలో {st.session_state.user_name}! క్విజ్ పూర్తి చేయండి.")
        if st.button("Reset Quiz (మళ్ళీ మొదటికి)"):
            st.session_state.quiz_started = False
            st.rerun()
            
        st.write("---")
        
        for index, row in df.iterrows():
            st.subheader(f"ప్రశ్న {index+1}:")
            st.write(f"**{row['Question']}**")
            
            options = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
            
            # ఇక్కడ 'key' ఇవ్వడం వల్ల ఒక ప్రశ్న సమాధానం ఇంకో దానికి అడ్డు రాదు
            choice = st.radio(f"సరైన సమాధానాన్ని ఎంచుకోండి:", options, key=f"radio_{index}")
            
            if st.button(f"Check Answer {index+1}", key=f"btn_{index}"):
                if str(choice).strip() == str(row['Correct_Answer']).strip():
                    st.success("సరైన సమాధానం! ✅")
                else:
                    st.error(f"తప్పు! సరైన సమాధానం: {row['Correct_Answer']} ❌")
            st.write("---")

except Exception as e:
    st.error("డేటా లోడ్ అవ్వలేదు.")
    st.write(f"Error: {e}")
