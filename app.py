import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Venkat Quiz App", page_icon="📚")
st.title("📚 Venkat's Learning App")

# మీ షీట్ లింక్
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=SHEET_URL, worksheet="Sheet1")
    
    name = st.text_input("మీ పేరు నమోదు చేయండి:")
    
    if name:
        if st.button("Start Quiz"):
            st.balloons()
            st.success(f"హలో {name}! క్విజ్ ప్రారంభిద్దాం.")
            
            for index, row in df.iterrows():
                # మీ షీట్ కాలమ్ పేర్ల ప్రకారం ఇక్కడ మార్చాను
                st.subheader(f"ప్రశ్న {index+1} (Subject: {row['Subject']}):")
                st.write(f"**{row['Question']}**")
                
                # Option_A, Option_B... అని మీ షీట్ లో ఉన్న పేర్లు ఇక్కడ ఇచ్చాను
                options = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
                choice = st.radio(f"సరైన సమాధానాన్ని ఎంచుకోండి:", options, key=f"q{index}")
                
                if st.button(f"Check Answer {index+1}", key=f"btn{index}"):
                    # Correct_Answer అని మీ షీట్ లో ఉన్న పేరు ఇక్కడ ఇచ్చాను
                    if choice == str(row['Correct_Answer']):
                        st.success("సరైన సమాధానం! ✅")
                    else:
                        st.error(f"తప్పు! సరైన సమాధానం: {row['Correct_Answer']} ❌")
                st.write("---")
except Exception as e:
    st.error("షీట్ డేటా చదవడంలో సమస్య ఉంది. కాలమ్ పేర్లు సరిగ్గా ఉన్నాయో లేదో చూడండి.")
    st.write(f"Error Details: {e}")
