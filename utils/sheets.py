"""
utils/sheets.py — Semua interaksi dengan Google Sheets.

STRUKTUR SPREADSHEET:
  Sheet 1: "Users"      → username | password | name | role | phone
  Sheet 2: "Questions"  → date | no | type | question | option_a | option_b | option_c | option_d | correct | script | passage
  Sheet 3: "Scores"     → username | name | date | listening | structure | reading | total | accuracy | timestamp
  Sheet 4: "AnswerLog"  → username | date | question_date | section | q_no | is_correct | user_answer | correct_answer | timestamp
"""

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
def get_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    return gspread.authorize(creds)


def _get_sheet(sheet_name):
    client = get_client()
    spreadsheet_id = st.secrets["spreadsheet"]["id"]
    return client.open_by_key(spreadsheet_id).worksheet(sheet_name)

def sanitize(value):
    if pd.isna(value):
        return ""
    return value


# ── Users ───────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def get_user_registry() -> dict:
    ws = _get_sheet("Users")
    records = ws.get_all_records()
    return {
        row["username"]: {
            "password": str(row["password"]),
            "name": row["name"],
            "role": row.get("role", "user"),
            "phone": str(row.get("phone", "")),
        }
        for row in records if row.get("username")
    }


def add_user(username: str, password: str, name: str, role: str = "user", phone: str = ""):
    ws = _get_sheet("Users")
    ws.append_row([username, password, name, role, phone])
    get_user_registry.clear()


def delete_user(username: str):
    ws = _get_sheet("Users")
    records = ws.get_all_records()
    for i, row in enumerate(records, start=2):
        if row["username"] == username:
            ws.delete_rows(i)
            break
    get_user_registry.clear()


def get_all_user_phones() -> list:
    users = get_user_registry()
    return [
        {"username": u, "name": d["name"], "phone": d["phone"]}
        for u, d in users.items()
        if d.get("phone") and d["role"] == "user"
    ]


# ── Questions ───────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_questions_for_date(target_date: str = None) -> dict:
    if target_date is None:
        target_date = date.today().isoformat()

    ws = _get_sheet("Questions")
    records = ws.get_all_records()

    result = {"listening": [], "structure": [], "reading": []}
    for row in records:
        if str(row.get("date", "")).strip() == target_date:
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
                    "correct": int(row.get("correct", 0)),
                    "script": row.get("script", ""),
                    "passage": row.get("passage", ""),
                })
    return result


def add_question(row_data):
    ws = _get_sheet("Questions")

    try:
        values = [
            sanitize(row_data.get("date", date.today().isoformat())),
            sanitize(row_data.get("pool_id", "")),   # ✅ NEW
            sanitize(row_data.get("no", "")),
            sanitize(row_data.get("type", "")),
            sanitize(row_data.get("question", "")),
            sanitize(row_data.get("option_a", "")),
            sanitize(row_data.get("option_b", "")),
            sanitize(row_data.get("option_c", "")),
            sanitize(row_data.get("option_d", "")),
            sanitize(row_data.get("correct", "")),
            sanitize(row_data.get("script", "")),
            sanitize(row_data.get("passage", "")),
            sanitize(row_data.get("difficulty", "")),  # ✅ NEW
        ]

        ws.append_row(values)

    except Exception as e:
        raise Exception(f"Gagal insert ke sheet: {e}")


def delete_questions_for_date(target_date: str):
    ws = _get_sheet("Questions")
    records = ws.get_all_records()
    rows_to_delete = [i for i, r in enumerate(records, start=2)
                      if str(r.get("date", "")).strip() == target_date]
    for row_idx in sorted(rows_to_delete, reverse=True):
        ws.delete_rows(row_idx)
    get_questions_for_date.clear()


# ── Scores ──────────────────────────────────────────────────────────────────

def save_score(username: str, name: str, listening: int, structure: int, reading: int):
    total = listening + structure + reading
    accuracy = round((total / 45) * 100, 1)
    today = date.today().isoformat()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ws = _get_sheet("Scores")
    ws.append_row([username, name, today, listening, structure, reading, total, f"{accuracy}%", timestamp])
    get_user_scores.clear()
    get_all_scores.clear()


@st.cache_data(ttl=60)
def get_user_scores(username: str) -> pd.DataFrame:
    ws = _get_sheet("Scores")
    records = ws.get_all_records()
    rows = [r for r in records if r.get("username") == username]
    if not rows:
        return pd.DataFrame(columns=["date","listening","structure","reading","total","accuracy","timestamp"])
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date", ascending=False).reset_index(drop=True)


@st.cache_data(ttl=60)
def get_all_scores() -> pd.DataFrame:
    ws = _get_sheet("Scores")
    records = ws.get_all_records()
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date", ascending=False).reset_index(drop=True)


def has_done_test_today(username: str) -> bool:
    df = get_user_scores(username)
    if df.empty:
        return False
    today = date.today().isoformat()
    return today in df["date"].dt.strftime("%Y-%m-%d").tolist()
