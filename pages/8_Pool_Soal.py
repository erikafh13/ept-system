"""pages/8_Pool_Soal.py — Admin: kelola bank soal & shuffle harian."""

import os
import streamlit as st
import pandas as pd
from datetime import date
from utils.session import init_session
from utils.auth import logout
from utils.sheets import _get_sheet
from utils.question_pool import (
    get_question_pool,
    get_pool_stats,
    import_pool_from_df,
    get_or_create_todays_questions,
    draw_questions_for_today,
    get_daily_draw,
    delete_daily_draw,
    get_recently_used_ids,
)

st.set_page_config(page_title="Bank Soal — EPT Pro", page_icon="🎲", layout="wide")

css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()
if not st.session_state.get("logged_in") or st.session_state.get("role") != "admin":
    st.error("⛔ Akses ditolak. Halaman ini khusus admin.")
    st.stop()

c1, _, c3 = st.columns([1, 4, 1])
with c1:
    st.markdown('<span class="nav-logo">🎲 Bank Soal</span>', unsafe_allow_html=True)
with c3:
    if st.button("Keluar", key="nav_logout"):
        logout()
st.markdown("---")
st.markdown("## 🎲 Kelola Bank Soal & Shuffle Harian")

tab_stats, tab_import, tab_draw, tab_preview = st.tabs(
    ["📊 Statistik Pool", "📤 Import Soal", "🎯 Konfigurasi Draw", "🔍 Preview Hari Ini"]
)


# ═══════════════════════════════════════════════════════════════════
#  TAB 1: STATISTIK POOL
# ═══════════════════════════════════════════════════════════════════
with tab_stats:
    st.markdown("### 📊 Statistik Bank Soal")
    stats = get_pool_stats()

    if not stats:
        st.warning("Bank soal masih kosong. Upload soal di tab 'Import Soal'.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"""<div class="stat-card blue">
            <div class="stat-num">{stats.get('total', 0)}</div>
            <div class="stat-label">Total Soal</div>
        </div>""", unsafe_allow_html=True)
        for col, sec, color in zip(
            [c2, c3, c4],
            ["listening", "structure", "reading"],
            ["purple", "orange", "green"],
        ):
            col.markdown(f"""<div class="stat-card {color}">
                <div class="stat-num">{stats.get(sec, {}).get('total', 0)}</div>
                <div class="stat-label">{sec.capitalize()}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Distribusi Level per Section")
        rows_table = []
        for sec in ["listening", "structure", "reading"]:
            s = stats.get(sec, {})
            rows_table.append({
                "Section":         sec.capitalize(),
                "Mudah":           s.get("easy",   0),
                "Sedang":          s.get("medium", 0),
                "Sulit":           s.get("hard",   0),
                "Total":           s.get("total",  0),
                "Maks Rotasi": s.get("total", 0) // 15,
            })
        st.dataframe(pd.DataFrame(rows_table), use_container_width=True, hide_index=True)

        min_rot = min(
            stats.get(s, {}).get("total", 0) // 15
            for s in ["listening", "structure", "reading"]
        )
        st.info(f"💡 Dengan {stats['total']} soal, sistem bisa rotasi ~**{min_rot} hari** tanpa mengulang soal yang sama.")

        recent_ids = get_recently_used_ids(days=7)
        st.caption(f"Soal dipakai 7 hari terakhir: {len(recent_ids)} soal (tidak akan muncul hari ini)")

        pool_df = get_question_pool()
        if not pool_df.empty:
            with st.expander("📋 Lihat Semua Soal di Pool"):
                col_ft, col_fd = st.columns(2)
                with col_ft:
                    ft = st.selectbox("Filter tipe", ["Semua", "listening", "structure", "reading"])
                with col_fd:
                    fd = st.selectbox("Filter level", ["Semua", "easy", "medium", "hard"])
                view_df = pool_df.copy()
                if ft != "Semua": view_df = view_df[view_df["type"]       == ft]
                if fd != "Semua": view_df = view_df[view_df["difficulty"] == fd]
                st.dataframe(
                    view_df[["pool_id", "type", "difficulty", "question"]].rename(
                        columns={"pool_id": "ID", "type": "Tipe",
                                 "difficulty": "Level", "question": "Pertanyaan"}
                    ),
                    use_container_width=True, hide_index=True,
                )


# ═══════════════════════════════════════════════════════════════════
#  TAB 2: IMPORT SOAL
# ═══════════════════════════════════════════════════════════════════
with tab_import:
    st.markdown("### 📤 Import Bank Soal dari CSV")
    st.markdown("""
    Upload file **BANK_SOAL_EPT_LENGKAP.csv** yang sudah disertakan, atau buat sendiri:

    | pool_id | type | question | option_a | option_b | option_c | option_d | correct | script | passage | difficulty |
    |---------|------|----------|----------|----------|----------|----------|---------|--------|---------|------------|
    | L001 | listening | What... | Go home | Buy food | Study | Sleep | 0 | Man: ... | | easy |

    - `type` → `listening` / `structure` / `reading`
    - `correct` → 0=A, 1=B, 2=C, 3=D
    - `difficulty` → `easy` / `medium` / `hard`
    """)

    uploaded = st.file_uploader("Upload CSV Bank Soal", type=["csv"])
    if uploaded:
        df_upload = pd.read_csv(uploaded)
        st.markdown(f"**{len(df_upload)} soal** ditemukan di file.")

        if "type" in df_upload.columns:
            st.dataframe(
                df_upload["type"].value_counts().rename_axis("Tipe").reset_index(name="Jumlah"),
                use_container_width=True, hide_index=True,
            )
        st.dataframe(df_upload.head(3), use_container_width=True)

        if st.button("⬆️ Import ke Bank Soal (mengganti semua data lama)", type="primary"):
            with st.spinner("Mengimport soal ke Google Sheets..."):
                try:
                    count = import_pool_from_df(df_upload)
                    st.success(f"✅ {count} soal berhasil diimport!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Format CSV tidak sesuai: {e}")
                except Exception as e:
                    st.error(f"Gagal import: {e}")

    st.markdown("---")
    # Template CSV
    tmpl = pd.DataFrame([{
        "pool_id": "L001", "type": "listening",
        "question": "What does the man say?",
        "option_a": "He is tired", "option_b": "He is hungry",
        "option_c": "He is happy", "option_d": "He is busy",
        "correct": 0, "script": "Man: I'm really tired today.",
        "passage": "", "difficulty": "easy",
    }, {
        "pool_id": "S001", "type": "structure",
        "question": "She ___ to school every day.",
        "option_a": "go", "option_b": "goes",
        "option_c": "going", "option_d": "gone",
        "correct": 1, "script": "", "passage": "", "difficulty": "easy",
    }, {
        "pool_id": "R001", "type": "reading",
        "question": "What is the main idea?",
        "option_a": "Topic A", "option_b": "Topic B",
        "option_c": "Topic C", "option_d": "Topic D",
        "correct": 0, "script": "",
        "passage": "The article discusses...", "difficulty": "medium",
    }])
    st.download_button(
        "📥 Download Template CSV",
        data=tmpl.to_csv(index=False).encode("utf-8"),
        file_name="template_bank_soal.csv",
        mime="text/csv",
    )


# ═══════════════════════════════════════════════════════════════════
#  TAB 3: KONFIGURASI DRAW
# ═══════════════════════════════════════════════════════════════════
with tab_draw:
    st.markdown("### 🎯 Konfigurasi Random Draw Harian")

    today_str  = date.today().isoformat()
    today_ids  = get_daily_draw(today_str)
    draw_ready = len(today_ids) >= 45

    if draw_ready:
        st.success(f"✅ Draw hari ini sudah ada ({len(today_ids)} soal terpilih)")
    else:
        st.warning("❌ Draw hari ini belum dibuat. Klik tombol di bawah untuk memilih soal secara acak.")

    st.markdown("---")
    st.markdown("#### ⚙️ Pengaturan Soal Harian")
    col1, col2 = st.columns(2)
    with col1:
        per_section = st.number_input("Soal per section", min_value=5, max_value=20, value=15)
        avoid_days  = st.number_input("Hindari soal N hari terakhir", 1, 30, 7)
    with col2:
        st.markdown("**Komposisi Level (harus total = soal per section):**")
        easy_n   = st.slider("Mudah (Easy)",    0, int(per_section), 5)
        medium_n = st.slider("Sedang (Medium)", 0, int(per_section), 5)
        hard_n   = st.slider("Sulit (Hard)",    0, int(per_section), 5)

    total_cfg = easy_n + medium_n + hard_n
    if total_cfg != per_section:
        st.warning(f"⚠️ Total level ({total_cfg}) ≠ soal per section ({per_section})")
    else:
        st.success(f"✅ Konfigurasi valid: {easy_n} mudah + {medium_n} sedang + {hard_n} sulit = {per_section}")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button(
            "🎲 Buat Draw Baru untuk Hari Ini",
            type="primary",
            disabled=(total_cfg != per_section),
            use_container_width=True,
        ):
            with st.spinner("Memilih soal secara acak..."):
                qs    = draw_questions_for_today(
                    per_section=int(per_section),
                    difficulty_mix={"easy": easy_n, "medium": medium_n, "hard": hard_n},
                    avoid_recent_days=int(avoid_days),
                )
                total = sum(len(v) for v in qs.values())
            st.success(f"✅ {total} soal berhasil dipilih untuk hari ini!")
            st.rerun()

    with col_btn2:
        if st.button("🔄 Reset Draw Hari Ini", type="secondary", use_container_width=True):
            # FIX: gunakan fungsi delete_daily_draw yang bersih, bukan __import__ hack
            delete_daily_draw(today_str)
            st.success("Draw hari ini dihapus. Klik 'Buat Draw Baru' untuk membuat ulang.")
            st.rerun()

    st.markdown("---")
    st.markdown("#### 📅 Riwayat Draw 7 Hari Terakhir")
    try:
        ws      = _get_sheet("DailyDraw")
        records = ws.get_all_records()
        if records:
            draw_df = pd.DataFrame(records)
            draw_df["date"] = pd.to_datetime(draw_df["date"])
            summary = (
                draw_df.groupby("date")
                .size()
                .reset_index(name="Jumlah Soal")
            )
            summary["date"] = summary["date"].dt.strftime("%d %b %Y")
            summary.columns = ["Tanggal", "Jumlah Soal Dipilih"]
            st.dataframe(summary.tail(7), use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada riwayat draw.")
    except Exception:
        st.info("Belum ada riwayat draw.")


# ═══════════════════════════════════════════════════════════════════
#  TAB 4: PREVIEW SOAL HARI INI
# ═══════════════════════════════════════════════════════════════════
with tab_preview:
    st.markdown(f"### 🔍 Preview Soal Hari Ini ({date.today().strftime('%d %B %Y')})")
    qs    = get_or_create_todays_questions()
    total = sum(len(v) for v in qs.values())

    if total == 0:
        st.warning("Soal belum di-draw. Pergi ke tab 'Konfigurasi Draw' dan buat draw dulu.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total",     total)
        c2.metric("Listening", len(qs["listening"]))
        c3.metric("Structure", len(qs["structure"]))
        c4.metric("Reading",   len(qs["reading"]))

        for section, icon in [("listening", "🎧"), ("structure", "📐"), ("reading", "📖")]:
            with st.expander(f"{icon} {section.capitalize()} — {len(qs[section])} soal"):
                for q in qs[section]:
                    diff_icon = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(
                        q.get("difficulty", ""), "⚪"
                    )
                    st.markdown(
                        f"**{q['no']}. {q['question']}** {diff_icon} `{q.get('pool_id','')}`"
                    )
                    for i, opt in enumerate(q["options"]):
                        marker = "✅" if i == q["correct"] else "○"
                        st.markdown(f"  {marker} **{'ABCD'[i]}.** {opt}")
                    if q.get("script"):
                        st.caption(f"Script: _{q['script'][:100]}_")
                    if q.get("passage"):
                        st.caption(f"Passage: _{q['passage'][:80]}..._")
                    st.divider()
