import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Venkat Quiz App", page_icon="📚")
st.title("📚 Venkat's Learning App")

SHEET_URL = ""

try:
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=SHEET_URL, worksheet="Sheet1")

except Exception as e:
st.error("షీట్ కనెక్ట్ కాలేదు. Secrets మరియు Requirements ఫైల్స్ చెక్ చేయండి.")
