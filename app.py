import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. Page Config
st.set_page_config(page_title="Venkat's Learning Quest", page_icon="🎮", layout="centered")

# 2. JavaScript to hide Footer & Fullscreen
components.html(
    """
    <script>
    const removeElements = () => {
        const selectors = ['footer', '[data-testid="stFooter"]', 'header', 'button[title="View fullscreen"]', '.stAppDeployButton'];
        selectors.forEach(s => {
            const els = window.parent.document.querySelectorAll(s);
            els.forEach(el => el.style.display = 'none');
        });
    };
    setInterval(removeElements, 500);
    </script>
    """, height=0,
)

# 3. Google Sheets URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/17ErdXLapXbTPCFpitqZErZIV32nE0vcYTqcFO7Ip-Lg/export?format=csv"

# 4. Session State Management
if 'unlocked_level' not in st.session_state: st.session_state.unlocked_level = 1
if 'current_playing_level' not in st.session_state: st.session_state.current_playing_level = None
if 'user_name' not in st.session_state: st.session_state.user_name = ""

def reset_to_map():
    st.session_state.current_playing_level = None
    st.rerun()

# 5. UI Setup
st.title("🎮 Venkat's Learning Quest")

try:
    df = pd.read_csv(SHEET_URL)
    total_q = len(df)
    total_levels = (total_q // 10) + (1 if total_q % 10 > 0 else 0)

    # Step 1: Login
    if st.session_state.user_name == "":
        st.subheader("Welcome! Please Login")
        name = st.text_input("మీ పేరు నమోదు చేయండి:", placeholder="Ex: Venkat")
        if st.button("Start Game 🚀"):
            if name.strip():
                st.session_state.user_name = name
                st.rerun()
            else:
                st.warning("దయచేసి పేరు నమోదు చేయండి.")
    
    # Step 2: Level Selection (Candy Crush Map with Scroll Effect)
    elif st.session_state.current_playing_level is None:
        st.write(f"Player: **{st.session_state.user_name}** | Unlocked: **Level {st.session_state.unlocked_level}**")
        st.subheader("📍 Select a Level to Play")
        
        # లెవల్స్ ప్రదర్శన
        for i in range(1, total_levels + 1):
            cols = st.columns([1, 4])
            with cols[0]:
                if i <= st.session_state.unlocked_level:
                    st.write(f"⭐ **L{i}**")
                else:
                    st.write(f"🔒 **L{i}**")
            with cols[1]:
                if i <= st.session_state.unlocked_level:
                    if st.button(f"Level {i} ఆడండి", key=f"btn_{i}", use_container_width=True):
                        st.session_state.current_playing_level = i
                        st.rerun()
                else:
                    st.button(f"Level {i} (Locked)", key=f"btn_{i}", disabled=True, use_container_width=True)
        
        # --- ఇక్కడ నువ్వు అడిగిన "Uploading" ఫీచర్ ---
        st.write("---")
        st.markdown("<h3 style='text-align: center; color: gray;'>⏳ Uploading more lessons...</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>ప్రతిరోజూ కొత్త లెవల్స్ అప్‌లోడ్ చేయబడతాయి. వేచి ఉండండి!</p>", unsafe_allow_html=True)
        st.progress(85) # ఒక చిన్న లోడింగ్ బార్ లాంటిది
        
    # Step 3: Quiz Screen (Instant Feedback Logic)
    else:
        level = st.session_state.current_playing_level
        st.header(f"Level {level} ⚡")
        
        start_idx = (level - 1) * 10
        end_idx = min(start_idx + 10, total_q)
        level_df = df.iloc[start_idx:end_idx]
        
        correct_in_this_run = 0
        
        for i, row in level_df.iterrows():
            st.markdown(f"**ప్రశ్న {i+1}:** {row['Question']}")
            opts = [str(row['Option_A']), str(row['Option_B']), str(row['Option_C']), str(row['Option_D'])]
            
            # యూజర్ ఆప్షన్ ఎంచుకోగానే వెంటనే రిజల్ట్
            ans = st.radio(f"సమాధానం (Q{i+1}):", opts, index=None, key=f"radio_{i}")
            
            if ans:
                if str(ans).strip() == str(row['Correct_Answer']).strip():
                    st.success("Correct! ✅")
                    correct_in_this_run += 1
                else:
                    st.error(f"Wrong! ❌ Correct Answer: {row['Correct_Answer']}")
            st.write("---")

        if st.button("Finish Level 🏁"):
            if correct_in_this_run == len(level_df):
                st.balloons()
                st.success(f"అద్భుతం! లెవల్ {level} లో 10/10 సాధించారు! 🎉")
                if level == st.session_state.unlocked_level:
                    st.session_state.unlocked_level += 1
                st.button("Map కి వెళ్ళు 🗺️", on_click=reset_to_map)
            else:
                st.error(f"స్కోర్: {correct_in_this_run}/10. లెవల్ పాస్ అవ్వడానికి 10/10 రావాలి.")
                st.button("మళ్ళీ ప్రయత్నించు 🔄", on_click=reset_to_map)

except Exception as e:
    st.error("Sheet Error: డేటా లోడ్ అవ్వలేదు లేదా షీట్ ఖాళీగా ఉంది.")
