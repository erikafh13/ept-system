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
        "test_section": "listening",   # listening | structure | reading
        "test_idx": 0,
        "answers": {},                  # { "listening_0": 2, ... }
        "questions_today": {},          # { listening: [], structure: [], reading: [] }
        "test_done": False,
        "last_score": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
