"""
EPT Pro System — Main Entry Point
"""

import os
import streamlit as st
from utils.auth import login_page
from utils.session import init_session

st.set_page_config(
    page_title="EPT Pro System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# FIX: pakai os.path agar tidak error di semua environment
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()

if not st.session_state.get("logged_in"):
    login_page()
    st.stop()

if st.session_state.get("role") == "admin":
    st.switch_page("pages/2_Admin.py")
else:
    st.switch_page("pages/1_Dashboard.py")
