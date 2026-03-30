"""
utils/sheets.py — Semua interaksi dengan Google Sheets.

STRUKTUR SPREADSHEET (6 sheet):
  Sheet 1: "Users"        → username | password | name | role | phone
  Sheet 2: "Questions"    → date | no | type | question | option_a | option_b | option_c | option_d | correct | script | passage
  Sheet 3: "Scores"       → username | name | date | listening | structure | reading | total | accuracy | timestamp
  Sheet 4: "AnswerLog"    → username | date | question_date | section | q_no | is_correct | user_answer | correct_answer | timestamp
  Sheet 5: "QuestionPool" → pool_id | type | question | option_a | option_b | option_c | option_d | correct | script | passage | difficulty
  Sheet 6: "DailyDraw"    → date | pool_id | no
"""

import os
import streamlit as st
import gspread
import pandas as pd
from datetime import date, datetime
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource(ttl=300)
def _get_client() -> gspread.Client:
    """
    Buat Google Sheets client.
    FIX: gspread v6+ tidak pakai gspread.authorize() lagi,
    melainkan gspread.Client() dengan credentials langsung.
    """
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.Client(auth=creds)


@st.cache_resource
def get_sheet(sheet_name):
    client = get_client()
    spreadsheet_id = st.secrets["spreadsheet"]["id"]
    return client.open_by_key(spreadsheet_id).worksheet(sheet_name)

# ── Users ────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def get_user_registry() -> dict:
    """
    Ambil semua user dari sheet Users.
    Return: { username: { password, name, role, phone } }
    """
    ws = _get_sheet("Users")
    records = ws.get_all_records()
    return {
        row["username"]: {
            "password": str(row["password"]),
            "name":     str(row["name"]),
            "role":     str(row.get("role", "user")),
            "phone":    str(row.get("phone", "")),
        }
        for row in records
        if row.get("username")
    }


def add_user(username: str, password: str, name: str,
             role: str = "user", phone: str = "") -> None:
    """Tambah user baru ke sheet Users."""
    ws = _get_sheet("Users")
    ws.append_row([username, password, name, role, phone])
    get_user_registry.clear()


def delete_user(username: str) -> None:
    """Hapus user dari sheet Users berdasarkan username."""
    ws = _get_sheet("Users")
    records = ws.get_all_records()
    for i, row in enumerate(records, start=2):  # baris 1 = header
        if row.get("username") == username:
            ws.delete_rows(i)
            break
    get_user_registry.clear()


def get_all_user_phones() -> list:
    """Return list { username, name, phone } untuk semua user yang punya nomor WA."""
    users = get_user_registry()
    return [
        {"username": u, "name": d["name"], "phone": d["phone"]}
        for u, d in users.items()
        if d.get("phone") and d.get("role") == "user"
    ]


# ── Questions (manual per tanggal) ───────────────────────────────────────────

@st.cache_data(ttl=300)
def get_questions_for_date(target_date: str = None) -> dict:
    """
    Ambil soal manual untuk tanggal tertentu dari sheet Questions.
    Return: { 'listening': [...], 'structure': [...], 'reading': [...] }
    """
    if target_date is None:
        target_date = date.today().isoformat()

    ws = _get_sheet("Questions")
    records = ws.get_all_records()

    result: dict = {"listening": [], "structure": [], "reading": []}
    for row in records:
        if str(row.get("date", "")).strip() != target_date:
            continue
        q_type = str(row.get("type", "")).lower().strip()
        if q_type not in result:
            continue
        result[q_type].append({
            "no":       row.get("no", ""),
            "question": str(row.get("question", "")),
            "options": [
                str(row.get("option_a", "")),
                str(row.get("option_b", "")),
                str(row.get("option_c", "")),
                str(row.get("option_d", "")),
            ],
            "correct": int(row.get("correct", 0)),
            "script":  str(row.get("script", "")),
            "passage": str(row.get("passage", "")),
        })
    return result


def add_question(row_data: dict) -> None:
    """Tambah satu soal manual ke sheet Questions."""
    ws = _get_sheet("Questions")
    ws.append_row([
        row_data.get("date",     date.today().isoformat()),
        row_data.get("no",       ""),
        row_data.get("type",     ""),
        row_data.get("question", ""),
        row_data.get("option_a", ""),
        row_data.get("option_b", ""),
        row_data.get("option_c", ""),
        row_data.get("option_d", ""),
        row_data.get("correct",  0),
        row_data.get("script",   ""),
        row_data.get("passage",  ""),
    ])
    get_questions_for_date.clear()


def delete_questions_for_date(target_date: str) -> None:
    """Hapus semua soal manual untuk tanggal tertentu."""
    ws = _get_sheet("Questions")
    records = ws.get_all_records()
    rows_to_delete = [
        i for i, r in enumerate(records, start=2)
        if str(r.get("date", "")).strip() == target_date
    ]
    for row_idx in sorted(rows_to_delete, reverse=True):
        ws.delete_rows(row_idx)
    get_questions_for_date.clear()


# ── Scores ───────────────────────────────────────────────────────────────────

def save_score(username: str, name: str,
               listening: int, structure: int, reading: int) -> None:
    """Simpan skor hasil simulasi ke sheet Scores."""
    total    = listening + structure + reading
    accuracy = round((total / 45) * 100, 1)
    today    = date.today().isoformat()
    ts       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ws = _get_sheet("Scores")
    ws.append_row([
        username, name, today,
        listening, structure, reading,
        total, f"{accuracy}%", ts,
    ])
    # Clear cache agar data terbaru langsung muncul
    get_user_scores.clear()
    get_all_scores.clear()


@st.cache_data(ttl=60)
def get_user_scores(username: str) -> pd.DataFrame:
    """Ambil riwayat skor seorang user sebagai DataFrame."""
    ws      = _get_sheet("Scores")
    records = ws.get_all_records()
    rows    = [r for r in records if r.get("username") == username]
    if not rows:
        return pd.DataFrame(columns=[
            "date", "listening", "structure", "reading",
            "total", "accuracy", "timestamp",
        ])
    df         = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0).astype(int)
    return df.sort_values("date", ascending=False).reset_index(drop=True)


@st.cache_data(ttl=60)
def get_all_scores() -> pd.DataFrame:
    """Ambil semua skor (untuk admin & leaderboard)."""
    ws      = _get_sheet("Scores")
    records = ws.get_all_records()
    if not records:
        return pd.DataFrame()
    df         = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0).astype(int)
    return df.sort_values("date", ascending=False).reset_index(drop=True)


def has_done_test_today(username: str) -> bool:
    """Cek apakah user sudah mengerjakan tes hari ini."""
    df = get_user_scores(username)
    if df.empty:
        return False
    today = date.today().isoformat()
    return today in df["date"].dt.strftime("%Y-%m-%d").tolist()
