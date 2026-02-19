import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. పేజీ సెట్టింగ్స్
st.set_page_config(page_title="Venkat Quiz App", page_icon="📚", layout="centered")

# 2. 'Fullscreen' మరియు 'Built with Streamlit' ని శాశ్వతంగా తీసేసే కోడ్
components.html(
    """
    <script>
    const removeElements = () => {
        // ఈ కింద ఉన్నవన్నీ వెతికి డిలీట్ చేస్తుంది
        const selectors = [
            'footer', 
            '[data-testid="stFooter"]', 
            'header', 
            '.stAppDeployButton', 
            'button[title="View fullscreen"]',
            '[data-testid="styled-link-icon"]',
            '.stStatusWidget',
            '#MainMenu'
        ];
        
        selectors.forEach(selector => {
            const elements = window.parent.document.querySelectorAll(selector);
            elements.forEach(el => {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
            });
        });
        
        // కింద ఉండే ఆ వైట్ బార్ గ్యాప్ ని కూడా తీసేస్తుంది
        const app = window.parent.document.querySelector('.stApp');
        if (app) {
            app.style.paddingBottom = '0px';
        }
    };

    // యాప్ ఓపెన్ అయినప్పుడు మరియు ప్రతి సెకనుకు ఒకసారి చెక్ చేస్తూనే ఉంటుంది
    setInterval(removeElements, 500);
    </script>
    """,
    height=0,
)

# 3. పాత CSS కూడా ఉంచుదాం (Double Safety)
st.markdown("""
    <style>
    footer, header, [data-testid="stFooter"], .stAppDeployButton, button[title="View fullscreen"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ఇక్కడ నుండి నీ క్విజ్ కోడ్ మొదలవుతుంది ---
st.title("📚 Venkat's Learning App")
# ... నీ పాత క్విజ్ కోడ్ అంతా ఇక్కడ పేస్ట్ చేయి ...
