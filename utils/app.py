"""
EPT Pro System — Main Entry Point
Aplikasi latihan EPT berbasis Streamlit dengan Google Sheets sebagai database.

CARA MENJALANKAN:
  pip install -r requirements.txt
  streamlit run app.py
"""

import os
import streamlit as st
from utils.auth import login_page, logout
from utils.session import init_session

st.set_page_config(
    page_title="EPT Pro System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject global CSS — pakai path absolut agar tidak error
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()

# Routing berdasarkan login state
if not st.session_state.get("logged_in"):
    login_page()
else:
    role = st.session_state.get("role", "user")
    if role == "admin":
        st.switch_page("pages/2_Admin.py")
    else:
        st.switch_page("pages/1_Dashboard.py")
