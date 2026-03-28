"""
utils/sheets.py — Semua interaksi dengan Google Sheets.

STRUKTUR SPREADSHEET:
  Sheet 1: "Users"          → username | password | name | role
  Sheet 2: "Questions"      → date | no | type | question | option_a | option_b | option_c | option_d | correct | script | passage
  Sheet 3: "Scores"         → username | name | date | listening | structure | reading | total | accuracy
"""

import streamlit as st
import gspread
import pandas as pd
from datetime import date, datetime
from google.oauth2.service_account import Credentials

# ── Google Sheets Auth ──────────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource(ttl=300)
def _get_client():
    """Buat Google Sheets client dari st.secrets."""
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def _get_sheet(sheet_name: str):
    """Ambil worksheet berdasarkan nama."""
    client = _get_client()
    spreadsheet_id = st.secrets["spreadsheet"]["id"]
    spreadsheet = client.open_by_key(spreadsheet_id)
    return spreadsheet.worksheet(sheet_name)


# ── Users ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_user_registry() -> dict:
    """
    Ambil daftar user dari sheet 'Users'.
    Return: { username: { password, name, role } }
    """
    ws = _get_sheet("Users")
    records = ws.get_all_records()
    return {
        row["username"]: {
            "password": str(row["password"]),
            "name": row["name"],
            "role": row.get("role", "user"),
        }
        for row in records
        if row.get("username")
    }


def add_user(username: str, password: str, name: str, role: str = "user"):
    """Tambah user baru ke sheet Users."""
    ws = _get_sheet("Users")
    ws.append_row([username, password, name, role])
    get_user_registry.clear()


def delete_user(username: str):
    """Hapus user dari sheet Users."""
    ws = _get_sheet("Users")
    records = ws.get_all_records()
    for i, row in enumerate(records, start=2):  # baris 1 = header
        if row["username"] == username:
            ws.delete_rows(i)
            break
    get_user_registry.clear()


# ── Questions ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_questions_for_date(target_date: str = None) -> dict:
    """
    Ambil soal untuk tanggal tertentu dari sheet 'Questions'.
    target_date: format 'YYYY-MM-DD'. Default = hari ini.
    Return: { 'listening': [...], 'structure': [...], 'reading': [...] }
    """
    if target_date is None:
        target_date = date.today().isoformat()

    ws = _get_sheet("Questions")
    records = ws.get_all_records()

    result = {"listening": [], "structure": [], "reading": []}
    for row in records:
        row_date = str(row.get("date", "")).strip()
        if row_date == target_date:
            q_type = str(row.get("type", "")).lower().strip()
            if q_type in result:
                result[q_type].append({
                    "no": row.get("no"),
                    "question": row.get("question", ""),
                    "options": [
                        row.get("option_a", ""),
                        row.get("option_b", ""),
                        row.get("option_c", ""),
                        row.get("option_d", ""),
                    ],
                    "correct": int(row.get("correct", 0)),  # 0=A, 1=B, 2=C, 3=D
                    "script": row.get("script", ""),        # untuk listening TTS
                    "passage": row.get("passage", ""),      # untuk reading
                })
    return result


def add_question(row_data: dict):
    """
    Tambah soal baru ke sheet Questions.
    row_data keys: date, no, type, question, option_a..d, correct, script, passage
    """
    ws = _get_sheet("Questions")
    ws.append_row([
        row_data.get("date", date.today().isoformat()),
        row_data.get("no", ""),
        row_data.get("type", ""),
        row_data.get("question", ""),
        row_data.get("option_a", ""),
        row_data.get("option_b", ""),
        row_data.get("option_c", ""),
        row_data.get("option_d", ""),
        row_data.get("correct", 0),
        row_data.get("script", ""),
        row_data.get("passage", ""),
    ])
    get_questions_for_date.clear()


def delete_questions_for_date(target_date: str):
    """Hapus semua soal untuk tanggal tertentu."""
    ws = _get_sheet("Questions")
    records = ws.get_all_records()
    rows_to_delete = []
    for i, row in enumerate(records, start=2):
        if str(row.get("date", "")).strip() == target_date:
            rows_to_delete.append(i)
    # Hapus dari bawah agar indeks tidak bergeser
    for row_idx in sorted(rows_to_delete, reverse=True):
        ws.delete_rows(row_idx)
    get_questions_for_date.clear()


# ── Scores ──────────────────────────────────────────────────────────────────
def save_score(username: str, name: str, listening: int, structure: int, reading: int):
    """Simpan skor hasil simulasi ke sheet Scores."""
    total = listening + structure + reading
    # Total maksimum soal per section bergantung pada jumlah soal hari ini
    # Akurasi dihitung dari 45 soal
    accuracy = round((total / 45) * 100, 1)
    today = date.today().isoformat()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ws = _get_sheet("Scores")
    ws.append_row([
        username, name, today,
        listening, structure, reading,
        total, f"{accuracy}%", timestamp
    ])
    get_user_scores.clear()
    get_all_scores.clear()


@st.cache_data(ttl=60)
def get_user_scores(username: str) -> pd.DataFrame:
    """Ambil riwayat skor seorang user sebagai DataFrame."""
    ws = _get_sheet("Scores")
    records = ws.get_all_records()
    rows = [r for r in records if r.get("username") == username]
    if not rows:
        return pd.DataFrame(columns=["date", "listening", "structure", "reading", "total", "accuracy", "timestamp"])
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date", ascending=False).reset_index(drop=True)
    return df


@st.cache_data(ttl=60)
def get_all_scores() -> pd.DataFrame:
    """Ambil semua skor (untuk halaman admin)."""
    ws = _get_sheet("Scores")
    records = ws.get_all_records()
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date", ascending=False).reset_index(drop=True)
    return df


def has_done_test_today(username: str) -> bool:
    """Cek apakah user sudah mengerjakan test hari ini."""
    df = get_user_scores(username)
    if df.empty:
        return False
    today = date.today().isoformat()
    done_dates = df["date"].dt.strftime("%Y-%m-%d").tolist()
    return today in done_dates
