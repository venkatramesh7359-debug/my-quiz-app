import streamlit as st

st.set_page_config(page_title="https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/edit?pli=1&gid=0#gid=0", page_icon="📚")
st.title("📚 Venkat's Learning App")
st.write("హలో! ఇది మీ మొదటి వెబ్ యాప్.")

name = st.text_input("మీ పేరు:")
if st.button("Start"):
    st.balloons() # ఆకాశంలో బెలూన్లు వస్తాయి!
    st.success(f"వెల్కమ్ {name}!")
