"""
utils/question_pool.py
──────────────────────
Sistem random shuffle dari bank soal besar.

CARA KERJA:
  - Admin upload BANK_SOAL_EPT_LENGKAP.csv ke sheet "QuestionPool"
  - Setiap hari, sistem otomatis memilih 15 soal per section secara acak
  - Pilihan soal disimpan di sheet "DailyDraw" agar konsisten sepanjang hari
  - Soal yang sudah dipakai dalam 7 hari terakhir tidak akan muncul lagi (anti-repeat)

SHEET YANG DIBUTUHKAN:
  - "QuestionPool"  → semua soal (pool_id, type, question, ..., difficulty)
  - "DailyDraw"     → soal terpilih per hari (date, pool_id, type, no)
"""

import streamlit as st
import pandas as pd
import random
from datetime import date, timedelta
from utils.sheets import _get_sheet


# ── Ambil semua soal dari pool ──────────────────────────────────────────────

@st.cache_data(ttl=600)
def get_question_pool() -> pd.DataFrame:
    """Ambil semua soal dari sheet QuestionPool."""
    try:
        ws = _get_sheet("QuestionPool")
        records = ws.get_all_records()
        return pd.DataFrame(records) if records else pd.DataFrame()
    except Exception as e:
        st.error(f"Gagal membaca QuestionPool: {e}")
        return pd.DataFrame()


# ── Ambil draw hari ini ─────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_daily_draw(target_date: str = None) -> list:
    """
    Ambil daftar pool_id yang terpilih untuk hari ini dari sheet DailyDraw.
    Return: list of pool_id strings.
    """
    if target_date is None:
        target_date = date.today().isoformat()
    try:
        ws = _get_sheet("DailyDraw")
        records = ws.get_all_records()
        today_rows = [r for r in records if str(r.get("date", "")).strip() == target_date]
        return [r["pool_id"] for r in today_rows]
    except Exception:
        return []


def save_daily_draw(pool_ids: list, target_date: str = None):
    """Simpan daftar pool_id yang terpilih untuk hari ini ke sheet DailyDraw."""
    if target_date is None:
        target_date = date.today().isoformat()
    try:
        ws = _get_sheet("DailyDraw")
        for i, pid in enumerate(pool_ids):
            ws.append_row([target_date, pid, i + 1])
        get_daily_draw.clear()
    except Exception as e:
        st.error(f"Gagal menyimpan daily draw: {e}")


def get_recently_used_ids(days: int = 7) -> set:
    """
    Ambil pool_id yang sudah dipakai dalam N hari terakhir.
    Digunakan untuk anti-repeat logic.
    """
    try:
        ws = _get_sheet("DailyDraw")
        records = ws.get_all_records()
        cutoff = (date.today() - timedelta(days=days)).isoformat()
        recent = [r["pool_id"] for r in records
                  if str(r.get("date", "")) > cutoff
                  and str(r.get("date", "")) < date.today().isoformat()]
        return set(recent)
    except Exception:
        return set()


# ── Core: Pilih soal acak & bangun set hari ini ─────────────────────────────

def draw_questions_for_today(
    per_section: int = 15,
    difficulty_mix: dict = None,
    avoid_recent_days: int = 7,
) -> dict:
    """
    Pilih soal secara acak untuk hari ini.

    Parameters:
        per_section      : jumlah soal per section (default 15)
        difficulty_mix   : { 'easy': N, 'medium': N, 'hard': N }
                           default: { easy:5, medium:5, hard:5 }
        avoid_recent_days: hindari soal yang dipakai N hari terakhir

    Return:
        { 'listening': [...], 'structure': [...], 'reading': [...] }
        masing-masing list berisi dict soal lengkap.
    """
    if difficulty_mix is None:
        difficulty_mix = {"easy": 5, "medium": 5, "hard": 5}

    pool_df = get_question_pool()
    if pool_df.empty:
        return {"listening": [], "structure": [], "reading": []}

    # Soal yang sudah dipakai belakangan (anti-repeat)
    recent_ids = get_recently_used_ids(days=avoid_recent_days)

    result = {}
    selected_pool_ids = []

    for section in ["listening", "structure", "reading"]:
        section_pool = pool_df[pool_df["type"] == section].copy()

        # Filter soal yang belum dipakai belakangan
        fresh_pool = section_pool[~section_pool["pool_id"].isin(recent_ids)]

        # Jika pool segar tidak cukup, fallback ke semua soal
        if len(fresh_pool) < per_section:
            fresh_pool = section_pool

        chosen = []
        for diff, count in difficulty_mix.items():
            diff_pool = fresh_pool[fresh_pool["difficulty"] == diff]
            if len(diff_pool) < count:
                diff_pool = section_pool[section_pool["difficulty"] == diff]

            sampled = diff_pool.sample(min(count, len(diff_pool)), random_state=None)
            chosen.append(sampled)

        section_df = pd.concat(chosen).sample(frac=1).reset_index(drop=True)  # shuffle urutan

        questions = []
        for _, row in section_df.iterrows():
            questions.append({
                "pool_id": row["pool_id"],
                "no": len(questions) + 1,
                "question": row["question"],
                "options": [row["option_a"], row["option_b"], row["option_c"], row["option_d"]],
                "correct": int(row["correct"]),
                "script": row.get("script", ""),
                "passage": row.get("passage", ""),
                "difficulty": row.get("difficulty", ""),
            })
            selected_pool_ids.append(row["pool_id"])

        result[section] = questions

    # Simpan ke DailyDraw
    save_daily_draw(selected_pool_ids)

    return result


def get_or_create_todays_questions(per_section: int = 15) -> dict:
    """
    Ambil soal hari ini. Jika belum di-draw, buat dulu.
    Fungsi utama yang dipanggil dari Dashboard/Test.
    """
    today = date.today().isoformat()
    existing_ids = get_daily_draw(today)

    if len(existing_ids) >= per_section * 3:
        # Sudah ada draw hari ini — ambil dari pool berdasarkan ID
        pool_df = get_question_pool()
        if pool_df.empty:
            return {"listening": [], "structure": [], "reading": []}

        result = {"listening": [], "structure": [], "reading": []}
        id_order = {pid: i for i, pid in enumerate(existing_ids)}
        matched = pool_df[pool_df["pool_id"].isin(existing_ids)].copy()
        matched["sort_order"] = matched["pool_id"].map(id_order)
        matched = matched.sort_values("sort_order")

        for section in ["listening", "structure", "reading"]:
            sec_df = matched[matched["type"] == section].reset_index(drop=True)
            for _, row in sec_df.iterrows():
                result[section].append({
                    "pool_id": row["pool_id"],
                    "no": len(result[section]) + 1,
                    "question": row["question"],
                    "options": [row["option_a"], row["option_b"], row["option_c"], row["option_d"]],
                    "correct": int(row["correct"]),
                    "script": row.get("script", ""),
                    "passage": row.get("passage", ""),
                    "difficulty": row.get("difficulty", ""),
                })
        return result
    else:
        # Belum ada draw hari ini — buat baru
        return draw_questions_for_today(per_section=per_section)


# ── Admin: Import pool dari CSV ─────────────────────────────────────────────

def import_pool_from_df(df: pd.DataFrame) -> int:
    """
    Import soal dari DataFrame ke sheet QuestionPool.
    Return: jumlah soal yang berhasil diimport.
    """
    required_cols = ["pool_id", "type", "question", "option_a", "option_b",
                     "option_c", "option_d", "correct", "difficulty"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom hilang: {missing}")

    ws = _get_sheet("QuestionPool")
    # Hapus data lama
    ws.clear()
    # Tulis header
    ws.append_row(list(df.columns))
    # Tulis data
    rows = df.fillna("").values.tolist()
    ws.append_rows(rows)
    get_question_pool.clear()
    return len(rows)


def get_pool_stats() -> dict:
    """Statistik bank soal untuk ditampilkan di admin panel."""
    pool_df = get_question_pool()
    if pool_df.empty:
        return {}

    stats = {}
    for section in ["listening", "structure", "reading"]:
        sec = pool_df[pool_df["type"] == section]
        stats[section] = {
            "total": len(sec),
            "easy":   len(sec[sec["difficulty"] == "easy"]),
            "medium": len(sec[sec["difficulty"] == "medium"]),
            "hard":   len(sec[sec["difficulty"] == "hard"]),
        }
    stats["total"] = len(pool_df)
    return stats
