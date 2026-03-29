"""
utils/question_pool.py — Sistem random shuffle dari bank soal besar.

CARA KERJA:
  1. Admin upload BANK_SOAL_EPT_LENGKAP.csv ke sheet "QuestionPool"
  2. Setiap pagi admin klik "Draw Soal Harian" di halaman Bank Soal
     (atau sistem auto-draw saat user pertama buka dashboard)
  3. 45 soal terpilih disimpan di sheet "DailyDraw" → semua user dapat soal SAMA
  4. Soal yang sudah dipakai 7 hari terakhir tidak akan dipilih lagi (anti-repeat)

SHEET YANG DIBUTUHKAN:
  "QuestionPool" → pool_id | type | question | option_a–d | correct | script | passage | difficulty
  "DailyDraw"   → date | pool_id | no | type
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.sheets import _get_sheet


# ── Baca QuestionPool ─────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def get_question_pool() -> pd.DataFrame:
    """Ambil semua soal dari sheet QuestionPool."""
    try:
        ws      = _get_sheet("QuestionPool")
        records = ws.get_all_records()
        if not records:
            return pd.DataFrame()
        df = pd.DataFrame(records)
        df["correct"] = pd.to_numeric(df["correct"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"Gagal membaca QuestionPool: {e}")
        return pd.DataFrame()


# ── Baca / Tulis DailyDraw ────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def get_daily_draw(target_date: str = None) -> list:
    """
    Ambil daftar pool_id yang terpilih untuk tanggal tertentu.
    Return: list of pool_id strings (urut sesuai disimpan).
    """
    if target_date is None:
        target_date = date.today().isoformat()
    try:
        ws      = _get_sheet("DailyDraw")
        records = ws.get_all_records()
        rows    = [r for r in records if str(r.get("date", "")).strip() == target_date]
        # Urutkan berdasarkan kolom 'no' agar urutan konsisten
        rows.sort(key=lambda r: int(r.get("no", 0)))
        return [r["pool_id"] for r in rows]
    except Exception:
        return []


def save_daily_draw(pool_ids_by_section: dict, target_date: str = None) -> None:
    """
    Simpan soal terpilih ke sheet DailyDraw.
    FIX: simpan kolom 'type' agar urutan per-section bisa dipulihkan.

    pool_ids_by_section: { 'listening': ['L001',...], 'structure': [...], 'reading': [...] }
    """
    if target_date is None:
        target_date = date.today().isoformat()
    try:
        ws  = _get_sheet("DailyDraw")
        no  = 1
        rows = []
        for section in ["listening", "structure", "reading"]:
            for pid in pool_ids_by_section.get(section, []):
                rows.append([target_date, pid, no, section])
                no += 1
        if rows:
            ws.append_rows(rows)
        get_daily_draw.clear()
    except Exception as e:
        st.error(f"Gagal menyimpan daily draw: {e}")


def delete_daily_draw(target_date: str) -> None:
    """Hapus semua draw untuk tanggal tertentu (untuk reset)."""
    try:
        ws      = _get_sheet("DailyDraw")
        records = ws.get_all_records()
        to_del  = [
            i for i, r in enumerate(records, start=2)
            if str(r.get("date", "")).strip() == target_date
        ]
        for row_idx in sorted(to_del, reverse=True):
            ws.delete_rows(row_idx)
        get_daily_draw.clear()
    except Exception as e:
        st.error(f"Gagal menghapus draw: {e}")


def get_recently_used_ids(days: int = 7) -> set:
    """
    Ambil pool_id yang sudah dipakai dalam N hari terakhir (TIDAK termasuk hari ini).
    FIX: filter yang benar — exclude hari ini agar draw hari ini tidak conflict.
    """
    try:
        ws      = _get_sheet("DailyDraw")
        records = ws.get_all_records()
        today   = date.today().isoformat()
        cutoff  = (date.today() - timedelta(days=days)).isoformat()
        # Ambil yang: tanggalnya > cutoff DAN < hari ini
        recent  = [
            r["pool_id"] for r in records
            if cutoff < str(r.get("date", "")).strip() < today
        ]
        return set(recent)
    except Exception:
        return set()


# ── Core: draw soal acak ──────────────────────────────────────────────────────

def draw_questions_for_today(
    per_section: int = 15,
    difficulty_mix: dict = None,
    avoid_recent_days: int = 7,
) -> dict:
    """
    Pilih soal secara acak untuk hari ini dan simpan ke DailyDraw.

    difficulty_mix : { 'easy': N, 'medium': N, 'hard': N }
                     jumlah harus = per_section
    Return         : { 'listening': [...], 'structure': [...], 'reading': [...] }
    """
    if difficulty_mix is None:
        difficulty_mix = {"easy": 5, "medium": 5, "hard": 5}

    pool_df = get_question_pool()
    if pool_df.empty:
        st.error("QuestionPool kosong. Upload bank soal terlebih dahulu.")
        return {"listening": [], "structure": [], "reading": []}

    recent_ids = get_recently_used_ids(days=avoid_recent_days)

    result: dict             = {}
    pool_ids_by_section: dict = {}

    for section in ["listening", "structure", "reading"]:
        section_pool = pool_df[pool_df["type"] == section].copy()

        # Soal segar (belum dipakai N hari terakhir)
        fresh_pool = section_pool[~section_pool["pool_id"].isin(recent_ids)]

        # Fallback: kalau segar tidak cukup, pakai semua
        if len(fresh_pool) < per_section:
            fresh_pool = section_pool

        chosen_frames = []
        for diff, count in difficulty_mix.items():
            diff_pool = fresh_pool[fresh_pool["difficulty"] == diff]
            # Fallback level: kalau segar tidak cukup untuk level ini
            if len(diff_pool) < count:
                diff_pool = section_pool[section_pool["difficulty"] == diff]
            n       = min(count, len(diff_pool))
            sampled = diff_pool.sample(n=n, random_state=None)
            chosen_frames.append(sampled)

        if not chosen_frames:
            result[section] = []
            pool_ids_by_section[section] = []
            continue

        section_df = (
            pd.concat(chosen_frames)
            .drop_duplicates(subset="pool_id")
            .sample(frac=1)           # acak urutan
            .reset_index(drop=True)
        )

        questions = []
        pids      = []
        for _, row in section_df.iterrows():
            questions.append({
                "pool_id":    str(row["pool_id"]),
                "no":         len(questions) + 1,
                "question":   str(row["question"]),
                "options": [
                    str(row["option_a"]),
                    str(row["option_b"]),
                    str(row["option_c"]),
                    str(row["option_d"]),
                ],
                "correct":    int(row["correct"]),
                "script":     str(row.get("script",  "")),
                "passage":    str(row.get("passage", "")),
                "difficulty": str(row.get("difficulty", "")),
            })
            pids.append(str(row["pool_id"]))

        result[section]              = questions
        pool_ids_by_section[section] = pids

    # Simpan ke DailyDraw
    save_daily_draw(pool_ids_by_section)
    return result


def get_or_create_todays_questions(per_section: int = 15) -> dict:
    """
    Ambil soal hari ini.
    Jika sudah di-draw → ambil dari pool berdasarkan ID yang tersimpan.
    Jika belum → draw baru otomatis.
    """
    today       = date.today().isoformat()
    existing_ids = get_daily_draw(today)

    if len(existing_ids) >= per_section * 3:
        # Draw sudah ada — rebuild dari QuestionPool berdasarkan ID
        pool_df = get_question_pool()
        if pool_df.empty:
            return {"listening": [], "structure": [], "reading": []}

        id_order = {pid: i for i, pid in enumerate(existing_ids)}
        matched  = (
            pool_df[pool_df["pool_id"].isin(existing_ids)]
            .copy()
        )
        matched["_order"] = matched["pool_id"].map(id_order)
        matched = matched.sort_values("_order").drop(columns=["_order"])

        result: dict = {"listening": [], "structure": [], "reading": []}
        for section in ["listening", "structure", "reading"]:
            sec_df = matched[matched["type"] == section].reset_index(drop=True)
            for _, row in sec_df.iterrows():
                result[section].append({
                    "pool_id":    str(row["pool_id"]),
                    "no":         len(result[section]) + 1,
                    "question":   str(row["question"]),
                    "options": [
                        str(row["option_a"]),
                        str(row["option_b"]),
                        str(row["option_c"]),
                        str(row["option_d"]),
                    ],
                    "correct":    int(row["correct"]),
                    "script":     str(row.get("script",  "")),
                    "passage":    str(row.get("passage", "")),
                    "difficulty": str(row.get("difficulty", "")),
                })
        return result
    else:
        # Belum ada draw hari ini → buat baru
        return draw_questions_for_today(per_section=per_section)


# ── Import dari CSV ───────────────────────────────────────────────────────────

def import_pool_from_df(df: pd.DataFrame) -> int:
    """
    Import soal dari DataFrame ke sheet QuestionPool (mengganti semua data lama).
    Return: jumlah baris yang diimport.
    """
    required = ["pool_id", "type", "question",
                "option_a", "option_b", "option_c", "option_d",
                "correct", "difficulty"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom wajib tidak ada: {missing}")

    ws = _get_sheet("QuestionPool")
    ws.clear()
    ws.append_row(list(df.columns))
    rows = df.fillna("").values.tolist()
    ws.append_rows(rows)
    get_question_pool.clear()
    return len(rows)


def get_pool_stats() -> dict:
    """Statistik bank soal untuk admin panel."""
    pool_df = get_question_pool()
    if pool_df.empty:
        return {}

    stats: dict = {"total": len(pool_df)}
    for section in ["listening", "structure", "reading"]:
        sec = pool_df[pool_df["type"] == section]
        stats[section] = {
            "total":  len(sec),
            "easy":   len(sec[sec["difficulty"] == "easy"]),
            "medium": len(sec[sec["difficulty"] == "medium"]),
            "hard":   len(sec[sec["difficulty"] == "hard"]),
        }
    return stats
