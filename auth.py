"""utils/auth.py — Login, logout, dan validasi user."""

import streamlit as st
from utils.sheets import get_user_registry


def login_page():
    """Render halaman login."""
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("""
            <div class="login-header">
                <div class="login-icon">🎓</div>
                <h1 class="login-title">EPT Pro</h1>
                <p class="login-sub">English Proficiency Training System</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Masukkan username...")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("🚀 Masuk Sekarang", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("Username dan password wajib diisi.")
                return

            user_data = get_user_registry()
            if username in user_data:
                user = user_data[username]
                if user["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.name = user.get("name", username)
                    st.session_state.role = user.get("role", "user")
                    st.rerun()
                else:
                    st.error("❌ Password salah.")
            else:
                st.error("❌ Username tidak ditemukan.")

        st.markdown('</div>', unsafe_allow_html=True)


def logout():
    """Reset semua session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
