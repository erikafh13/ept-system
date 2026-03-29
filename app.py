"""
EPT Pro System — Main Entry Point
Aplikasi latihan EPT berbasis Streamlit dengan Google Sheets sebagai database.
"""

import streamlit as st
from utils.auth import login_page, logout
from utils.session import init_session

st.set_page_config(
    page_title="EPT Pro System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject global CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()

# Routing berdasarkan login state
if not st.session_state.get("logged_in"):
    login_page()
    st.stop()

# setelah login → redirect SEKALI saja
if st.session_state.get("role") == "admin":
    st.switch_page("pages/2_Admin.py")
else:
    st.switch_page("pages/1_Dashboard.py")
