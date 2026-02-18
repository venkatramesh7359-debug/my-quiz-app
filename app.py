import streamlit as st
import pandas as pd

st.set_page_config(page_title="Venkat Quiz App", page_icon="📚")
st.title("📚 Venkat's Learning App")

# మీ గూగుల్ షీట్ URL ఇక్కడ ఇవ్వండి
# Share -> Anyone with the link -> Viewer అని మార్చడం మర్చిపోకండి!
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/edit?pli=1&gid=0#gid=0"

def load_data(url):
    try:
        # URL ని CSV డౌన్‌లోడ్ లింక్‌గా మారుస్తుంది
        if "edit" in url:
            csv_url = url.split('/edit')[0] + '/export?format=csv'
        else:
            csv_url = url
        return pd.read_csv(csv_url)
    except:
        return None

df = load_data(SHEET_URL)

if df is not None:
    name = st.text_input("మీ పేరు టైప్ చేయండి:")
    if name:
        st.success(f"హలో {name}! క్విజ్ మొదలు పెడదాం.")
        for index, row in df.iterrows():
            st.subheader(f"ప్రశ్న {index+1}: {row['Question']}")
            options = [str(row['A']), str(row['B']), str(row['C']), str(row['D'])]
            choice = st.radio(f"సమాధానం ఎంచుకోండి:", options, key=f"q{index}")
            if st.button(f"Check Answer {index+1}", key=f"btn{index}"):
                if str(choice).strip() == str(row['Answer']).strip():
                    st.success("సరైన సమాధానం! ✅")
                else:
                    st.error(f"తప్పు! సరైన సమాధానం: {row['Answer']} ❌")
            st.write("---")
else:
    st.warning("షీట్ కనెక్ట్ అవ్వలేదు. URL మరియు పర్మిషన్స్ చెక్ చేయండి.")
