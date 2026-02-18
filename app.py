import streamlit as st
from streamlit_gsheets import GSheetsConnection

# పేజీ సెటప్
st.set_page_config(page_title="Venkat Quiz App", page_icon="📚")
st.title("📚 Venkat's Learning App")

# మీ Google Sheet URL ఇక్కడ ఇవ్వండి
SHEET_URL = "YOUR_GOOGLE_SHEET_URL_HERE"

try:
    # Indentation ఇక్కడ నుండి మారుతుంది
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=SHEET_URL, worksheet="Sheet1")
    
    name = st.text_input("మీ పేరు టైప్ చేయండి:")
    
    if name:
        if st.button("Start Quiz"):
            st.balloons()
            st.success(f"హలో {name}! క్విజ్ మొదలు పెడదాం.")
            
        # ప్రశ్నలను ప్రదర్శించడం
        for index, row in df.iterrows():
            st.subheader(f"ప్రశ్న {index+1}: {row['Question']}")
            
            options = [str(row['A']), str(row['B']), str(row['C']), str(row['D'])]
            choice = st.radio(f"సమాధానం ఎంచుకోండి:", options, key=f"q{index}")
            
            if st.button(f"Check Answer {index+1}", key=f"btn{index}"):
                if choice == str(row['Answer']):
                    st.success("సరైన సమాధానం! ✅")
                else:
                    st.error(f"తప్పు! సరైన సమాధానం: {row['Answer']} ❌")
            st.write("---")

except Exception as e:
    st.error("షీట్ కనెక్ట్ కాలేదు. Secrets మరియు Requirements ఫైల్స్ చెక్ చేయండి.")
    st.write(e) # అసలు సమస్య ఏంటో తెలియడానికి ఇది ఉపయోగపడుతుంది
