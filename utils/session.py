"""utils/session.py — Inisialisasi session state global."""

import streamlit as st


def init_session():
    """Set default session state jika belum ada."""
    defaults = {
        "logged_in": False,
        "username": "",
        "name": "",
        "role": "user",
        "test_active": False,
        "test_section": "listening",
        "test_idx": 0,
        "answers": {},
        "questions_today": {},
        "test_done": False,
        "last_score": None,
        "wa_result_sent": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
