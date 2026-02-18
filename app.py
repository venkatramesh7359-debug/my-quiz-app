import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Venkat Quiz App", page_icon="📚")
st.title("📚 Venkat's Learning App")

# మీ షీట్ లింక్
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=SHEET_URL, worksheet="Sheet1")
    
    name = st.text_input("మీ పేరు టైప్ చేయండి:")
    
    if name:
        if st.button("Start Quiz"):
            st.balloons()
            st.success(f"హలో {name}! క్విజ్ మొదలు పెడదాం.")
            
            for index, row in df.iterrows():
                # ఇక్కడ మీ షీట్ లోని పేర్లను వాడుతున్నాం
                st.subheader(f"ప్రశ్న {index+1}:")
                # ఒకవేళ మీ షీట్ లో కాలమ్ పేరు 'Question' కాకపోతే, ఆ పేరు ఇక్కడ మార్చాలి
                st.write(f"Subject: {row['subject']} | Task ID: {row['task id']}")
                
                # ఇక్కడ మీ ఆప్షన్ కాలమ్ పేర్లు (A, B, C, D) ఉండాలి
                options = [str(row['A']), str(row['B']), str(row['C']), str(row['D'])]
                choice = st.radio(f"సమాధానం ఎంచుకోండి:", options, key=f"q{index}")
                
                if st.button(f"Check Answer {index+1}", key=f"btn{index}"):
                    if choice == str(row['Answer']):
                        st.success("సరైన సమాధానం! ✅")
                    else:
                        st.error(f"తప్పు! సరైన సమాధానం: {row['Answer']} ❌")
                st.write("---")
except Exception as e:
    st.error("షీట్ లోని డేటాను చదవడంలో సమస్య ఉంది.")
    st.write(f"చిన్న సలహా: మీ షీట్ లో మొదటి వరుసలో class, subject, task id, Question, A, B, C, D, Answer అనే పేర్లు ఉన్నాయో లేదో చూడండి.")
