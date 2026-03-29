"""
utils/analytics.py — Analitik soal & performa user.

Sheet 4: "AnswerLog" — log jawaban per soal untuk analisis.
Kolom: username | date | question_date | section | q_no | is_correct | user_answer | correct_answer
"""

import streamlit as st
import pandas as pd
from utils.sheets import _get_sheet
import gspread


@st.cache_data(ttl=120)
def get_answer_log() -> pd.DataFrame:
    """Ambil semua log jawaban dari sheet AnswerLog."""
    try:
        ws = _get_sheet("AnswerLog")
        records = ws.get_all_records()
        if not records:
            return pd.DataFrame()
        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame()


def save_answer_log(username: str, question_date: str, answers: dict, questions: dict):
    """
    Simpan log jawaban detail ke sheet AnswerLog.
    answers: { 'listening_0': 2, 'structure_1': 0, ... }
    questions: { 'listening': [...], 'structure': [...], 'reading': [...] }
    """
    try:
        ws = _get_sheet("AnswerLog")
        from datetime import date, datetime
        today = date.today().isoformat()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        rows = []
        for section, q_list in questions.items():
            for i, q in enumerate(q_list):
                key = f"{section}_{i}"
                user_ans = answers.get(key, -1)
                correct_ans = int(q.get("correct", 0))
                is_correct = 1 if user_ans == correct_ans else 0
                rows.append([
                    username, today, question_date,
                    section, i + 1,
                    is_correct, user_ans, correct_ans,
                    timestamp
                ])

        if rows:
            ws.append_rows(rows)
        get_answer_log.clear()
    except Exception as e:
        print(f"[AnswerLog Error] {e}")


# ── Analisis ────────────────────────────────────────────────────────────────

def get_hardest_questions(df: pd.DataFrame, section: str = None, top_n: int = 10) -> pd.DataFrame:
    """
    Soal dengan tingkat kesalahan tertinggi.
    Return DataFrame: section | q_no | total_attempts | wrong | error_rate%
    """
    if df.empty:
        return pd.DataFrame()

    filtered = df.copy()
    if section:
        filtered = filtered[filtered["section"] == section]

    grouped = filtered.groupby(["question_date", "section", "q_no"]).agg(
        total=("is_correct", "count"),
        correct=("is_correct", "sum"),
    ).reset_index()
    grouped["wrong"] = grouped["total"] - grouped["correct"]
    grouped["error_rate"] = ((grouped["wrong"] / grouped["total"]) * 100).round(1)
    grouped = grouped.sort_values("error_rate", ascending=False).head(top_n)
    return grouped


def get_user_weak_sections(username: str, df: pd.DataFrame) -> dict:
    """
    Analisis bagian lemah seorang user.
    Return: { 'listening': 72.5, 'structure': 55.0, 'reading': 80.0 }  (akurasi %)
    """
    if df.empty:
        return {}
    user_df = df[df["username"] == username]
    if user_df.empty:
        return {}

    result = {}
    for sec in ["listening", "structure", "reading"]:
        sec_df = user_df[user_df["section"] == sec]
        if not sec_df.empty:
            acc = (sec_df["is_correct"].sum() / len(sec_df)) * 100
            result[sec] = round(acc, 1)
    return result


def get_section_difficulty(df: pd.DataFrame) -> pd.DataFrame:
    """Rata-rata akurasi per section seluruh user."""
    if df.empty:
        return pd.DataFrame()
    grouped = df.groupby("section").agg(
        total=("is_correct", "count"),
        correct=("is_correct", "sum"),
    ).reset_index()
    grouped["accuracy"] = ((grouped["correct"] / grouped["total"]) * 100).round(1)
    return grouped


def get_user_trend(username: str, df: pd.DataFrame) -> pd.DataFrame:
    """Tren akurasi harian seorang user per section."""
    if df.empty:
        return pd.DataFrame()
    user_df = df[df["username"] == username].copy()
    if user_df.empty:
        return pd.DataFrame()

    trend = user_df.groupby(["date", "section"]).agg(
        total=("is_correct", "count"),
        correct=("is_correct", "sum"),
    ).reset_index()
    trend["accuracy"] = ((trend["correct"] / trend["total"]) * 100).round(1)
    return trend
