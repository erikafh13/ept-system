"""pages/8_Pool_Soal.py — Admin: kelola bank soal & konfigurasi shuffle harian."""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.session import init_session
from utils.auth import logout
from utils.question_pool import (
    get_question_pool, get_pool_stats, import_pool_from_df,
    get_or_create_todays_questions, draw_questions_for_today,
    get_daily_draw, get_recently_used_ids,
)

st.set_page_config(page_title="Bank Soal — EPT Pro", page_icon="🎲", layout="wide")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()
if not st.session_state.get("logged_in") or st.session_state.get("role") != "admin":
    st.error("Akses ditolak."); st.stop()

c1, _, c3 = st.columns([1, 4, 1])
with c1: st.markdown('<span class="nav-logo">🎲 Bank Soal</span>', unsafe_allow_html=True)
with c3:
    if st.button("Keluar"): logout()
st.markdown("---")

st.markdown("## 🎲 Kelola Bank Soal & Shuffle Harian")

tab_stats, tab_import, tab_draw, tab_preview = st.tabs(
    ["📊 Statistik Pool", "📤 Import Soal", "🎯 Konfigurasi Draw", "🔍 Preview Soal Hari Ini"])


# ═══════════════════════════════════════════════════════════════════
#  TAB 1: STATISTIK POOL
# ═══════════════════════════════════════════════════════════════════
with tab_stats:
    st.markdown("### 📊 Statistik Bank Soal")
    stats = get_pool_stats()

    if not stats:
        st.warning("Bank soal masih kosong. Upload soal di tab 'Import Soal'.")
    else:
        # Summary cards
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"""<div class="stat-card blue">
            <div class="stat-num">{stats.get('total', 0)}</div>
            <div class="stat-label">Total Soal</div>
        </div>""", unsafe_allow_html=True)
        for col, sec, color in zip([c2, c3, c4], ["listening","structure","reading"], ["purple","orange","green"]):
            col.markdown(f"""<div class="stat-card {color}">
                <div class="stat-num">{stats.get(sec, {}).get('total', 0)}</div>
                <div class="stat-label">{sec.capitalize()}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Distribusi Level per Section")
        rows_table = []
        for sec in ["listening","structure","reading"]:
            s = stats.get(sec, {})
            rows_table.append({
                "Section": sec.capitalize(),
                "Mudah (Easy)": s.get("easy", 0),
                "Sedang (Medium)": s.get("medium", 0),
                "Sulit (Hard)": s.get("hard", 0),
                "Total": s.get("total", 0),
                "Rotasi Maksimum": s.get("total", 0) // 15,
            })
        st.dataframe(pd.DataFrame(rows_table), use_container_width=True, hide_index=True)

        st.info(f"""
        💡 **Rotasi** = berapa kali soal bisa diputar sebelum mengulang.
        Dengan {stats.get('total', 0)} soal, sistem bisa berjalan ~{min(s.get('total',0)//15 for s in [stats.get(k,{}) for k in ['listening','structure','reading']] if s)} hari tanpa mengulang soal yang sama.
        """)

        # Anti-repeat info
        recent_ids = get_recently_used_ids(days=7)
        st.markdown(f"**Soal digunakan 7 hari terakhir:** {len(recent_ids)} soal (tidak akan muncul lagi hari ini)")

        # Full pool table
        pool_df = get_question_pool()
        if not pool_df.empty:
            with st.expander("📋 Lihat Semua Soal di Pool"):
                filter_type = st.selectbox("Filter tipe", ["Semua","listening","structure","reading"], key="pool_filter")
                filter_diff = st.selectbox("Filter level", ["Semua","easy","medium","hard"], key="diff_filter")
                view_df = pool_df.copy()
                if filter_type != "Semua": view_df = view_df[view_df["type"] == filter_type]
                if filter_diff != "Semua": view_df = view_df[view_df["difficulty"] == filter_diff]
                st.dataframe(view_df[["pool_id","type","difficulty","question"]].rename(
                    columns={"pool_id":"ID","type":"Tipe","difficulty":"Level","question":"Pertanyaan"}
                ), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════
#  TAB 2: IMPORT SOAL
# ═══════════════════════════════════════════════════════════════════
with tab_import:
    st.markdown("### 📤 Import Bank Soal dari CSV")
    st.markdown("""
    Upload file **BANK_SOAL_EPT_LENGKAP.csv** yang sudah disertakan bersama proyek ini,
    atau buat sendiri dengan format kolom berikut:

    | pool_id | type | question | option_a | option_b | option_c | option_d | correct | script | passage | difficulty |
    |---------|------|----------|----------|----------|----------|----------|---------|--------|---------|------------|
    | L001 | listening | What does... | Go home | Buy food | Study | Sleep | 0 | Man: ... | | easy |

    - `type` → `listening` / `structure` / `reading`
    - `correct` → 0=A, 1=B, 2=C, 3=D
    - `difficulty` → `easy` / `medium` / `hard`
    - `pool_id` → ID unik tiap soal (L001, S001, R001, dst.)
    """)

    uploaded = st.file_uploader("Upload CSV Bank Soal", type=["csv"])
    if uploaded:
        df_upload = pd.read_csv(uploaded)
        st.markdown(f"**Preview:** {len(df_upload)} soal ditemukan")

        type_counts = df_upload["type"].value_counts().to_dict() if "type" in df_upload.columns else {}
        diff_counts = df_upload["difficulty"].value_counts().to_dict() if "difficulty" in df_upload.columns else {}

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Per Tipe:**")
            for t, n in type_counts.items(): st.markdown(f"- {t}: {n}")
        with col2:
            st.markdown("**Per Level:**")
            for d, n in diff_counts.items(): st.markdown(f"- {d}: {n}")

        st.dataframe(df_upload.head(5), use_container_width=True)

        if st.button("⬆️ Import ke Bank Soal (mengganti data lama)", type="primary"):
            with st.spinner("Mengimport soal ke Google Sheets..."):
                try:
                    count = import_pool_from_df(df_upload)
                    st.success(f"✅ {count} soal berhasil diimport ke QuestionPool!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Format CSV tidak sesuai: {e}")
                except Exception as e:
                    st.error(f"Gagal import: {e}")

    st.markdown("---")
    st.markdown("### ⬇️ Download Template & Bank Soal Bawaan")
    st.markdown("Bank soal sudah berisi **180 soal** (60 Listening + 60 Structure + 60 Reading, 3 level).")

    # Buat template CSV
    template = pd.DataFrame([
        {"pool_id":"L001","type":"listening","question":"What does the man say?",
         "option_a":"He is tired","option_b":"He is hungry","option_c":"He is happy","option_d":"He is busy",
         "correct":0,"script":"Man: I'm really tired today.","passage":"","difficulty":"easy"},
        {"pool_id":"S001","type":"structure","question":"She ___ to school every day.",
         "option_a":"go","option_b":"goes","option_c":"going","option_d":"gone",
         "correct":1,"script":"","passage":"","difficulty":"easy"},
    ])
    st.download_button("📥 Download Template CSV",
        data=template.to_csv(index=False).encode("utf-8"),
        file_name="template_bank_soal.csv", mime="text/csv")


# ═══════════════════════════════════════════════════════════════════
#  TAB 3: KONFIGURASI DRAW
# ═══════════════════════════════════════════════════════════════════
with tab_draw:
    st.markdown("### 🎯 Konfigurasi Random Draw")

    today_ids = get_daily_draw()
    st.markdown(f"**Status Draw Hari Ini ({date.today()}):** "
                f"{'✅ Sudah ada (' + str(len(today_ids)) + ' soal)' if today_ids else '❌ Belum ada'}")

    st.markdown("---")
    st.markdown("#### ⚙️ Pengaturan Soal Harian")

    col1, col2 = st.columns(2)
    with col1:
        per_section = st.number_input("Soal per section", min_value=5, max_value=20, value=15)
        avoid_days  = st.number_input("Hindari soal N hari terakhir (anti-repeat)", 1, 30, 7)
    with col2:
        st.markdown("**Komposisi Level:**")
        easy_n   = st.slider("Mudah (Easy)",   0, per_section, 5)
        medium_n = st.slider("Sedang (Medium)", 0, per_section, 5)
        hard_n   = st.slider("Sulit (Hard)",   0, per_section, 5)

    total_configured = easy_n + medium_n + hard_n
    if total_configured != per_section:
        st.warning(f"⚠️ Total level ({total_configured}) harus sama dengan soal per section ({per_section})")
    else:
        st.success(f"✅ Konfigurasi valid: {easy_n} mudah + {medium_n} sedang + {hard_n} sulit = {per_section}")

    diff_mix = {"easy": easy_n, "medium": medium_n, "hard": hard_n}

    col_draw1, col_draw2 = st.columns(2)
    with col_draw1:
        if st.button("🎲 Buat Draw Baru untuk Hari Ini", type="primary",
                     disabled=(total_configured != per_section)):
            with st.spinner("Memilih soal secara acak..."):
                qs = draw_questions_for_today(
                    per_section=per_section,
                    difficulty_mix=diff_mix,
                    avoid_recent_days=avoid_days,
                )
                total = sum(len(v) for v in qs.values())
                st.success(f"✅ {total} soal berhasil dipilih untuk hari ini!")
                st.rerun()

    with col_draw2:
        if st.button("🔄 Reset & Buat Ulang Draw Hari Ini", type="secondary"):
            # Hapus draw hari ini dari sheet DailyDraw
            try:
                ws_draw = __import__('utils.sheets', fromlist=['_get_sheet'])._get_sheet("DailyDraw")
                records = ws_draw.get_all_records()
                today_str = date.today().isoformat()
                rows_del = [i for i, r in enumerate(records, 2) if str(r.get("date","")) == today_str]
                for r in sorted(rows_del, reverse=True):
                    ws_draw.delete_rows(r)
                get_daily_draw.clear()
                st.success("Draw hari ini dihapus. Klik 'Buat Draw Baru' untuk membuat ulang.")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal reset: {e}")

    st.markdown("---")
    st.markdown("#### 📅 Riwayat Draw 7 Hari Terakhir")
    try:
        ws = __import__('utils.sheets', fromlist=['_get_sheet'])._get_sheet("DailyDraw")
        records = ws.get_all_records()
        if records:
            draw_df = pd.DataFrame(records)
            draw_df["date"] = pd.to_datetime(draw_df["date"])
            summary = draw_df.groupby("date").size().reset_index(name="jumlah_soal")
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
    st.markdown(f"### 🔍 Preview Soal yang Akan Dikerjakan Hari Ini ({date.today()})")

    qs = get_or_create_todays_questions()
    total = sum(len(v) for v in qs.values())

    if total == 0:
        st.warning("Soal belum di-draw. Pergi ke tab 'Konfigurasi Draw' dan buat draw dulu.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", total)
        c2.metric("Listening", len(qs["listening"]))
        c3.metric("Structure", len(qs["structure"]))
        c4.metric("Reading", len(qs["reading"]))

        for section, icon in [("listening","🎧"),("structure","📐"),("reading","📖")]:
            with st.expander(f"{icon} {section.capitalize()} — {len(qs[section])} soal"):
                for q in qs[section]:
                    diff_badge = {"easy":"🟢","medium":"🟡","hard":"🔴"}.get(q.get("difficulty",""),"⚪")
                    st.markdown(f"**{q['no']}. {q['question']}** {diff_badge} `{q.get('pool_id','')}`")
                    opts = q["options"]
                    labels = "ABCD"
                    for i, opt in enumerate(opts):
                        marker = "✅" if i == q["correct"] else "○"
                        st.markdown(f"  {marker} **{labels[i]}.** {opt}")
                    if q.get("script"):
                        st.caption(f"Script: _{q['script'][:80]}..._")
                    st.divider()
