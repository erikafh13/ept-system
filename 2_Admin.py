"""pages/2_Admin.py — Panel kontrol untuk admin."""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.session import init_session
from utils.auth import logout
from utils.sheets import (
    get_questions_for_date,
    get_all_scores,
    get_user_registry,
    add_question,
    delete_questions_for_date,
    add_user,
    delete_user,
)

st.set_page_config(page_title="Admin — EPT Pro", page_icon="⚙️", layout="wide")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()

if not st.session_state.get("logged_in") or st.session_state.get("role") != "admin":
    st.error("Akses ditolak. Halaman ini khusus admin.")
    st.stop()

name = st.session_state.name

# ── Navbar ─────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1, 4, 1])
with c1:
    st.markdown('<span class="nav-logo">⚙️ Admin Panel</span>', unsafe_allow_html=True)
with c3:
    if st.button("Keluar", key="logout_btn"):
        logout()

st.markdown("---")
st.markdown(f"<h2>Selamat datang, <b>{name}</b> 🛡️</h2>", unsafe_allow_html=True)

# ── Tabs ────────────────────────────────────────────────────────────────────
tab_q, tab_scores, tab_users = st.tabs(["📝 Kelola Soal", "📊 Pantau Nilai", "👥 Kelola User"])


# ═══════════════════════════════════════════════════════════════════
#  TAB 1: KELOLA SOAL
# ═══════════════════════════════════════════════════════════════════
with tab_q:
    st.markdown("### 📅 Soal untuk Tanggal")
    
    col_date, col_info = st.columns([2, 3])
    with col_date:
        selected_date = st.date_input(
            "Pilih tanggal",
            value=date.today(),
            min_value=date.today() - timedelta(days=30),
            max_value=date.today() + timedelta(days=60),
        )
    
    selected_date_str = selected_date.isoformat()
    q_data = get_questions_for_date(selected_date_str)
    total_loaded = sum(len(v) for v in q_data.values())

    with col_info:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Listening", len(q_data["listening"]), f"/ 15")
        c2.metric("Structure", len(q_data["structure"]), f"/ 15")
        c3.metric("Reading", len(q_data["reading"]), f"/ 15")
        c4.metric("Total", total_loaded, f"/ 45")

    # ── Tampilkan soal aktif ────────────────────────────────────────
    if total_loaded > 0:
        st.markdown("#### Soal Aktif")
        for qtype, qlist in q_data.items():
            if qlist:
                with st.expander(f"📂 {qtype.capitalize()} ({len(qlist)} soal)", expanded=False):
                    for i, q in enumerate(qlist):
                        st.markdown(f"**{i+1}. {q['question']}**")
                        options_label = ["A", "B", "C", "D"]
                        for j, opt in enumerate(q["options"]):
                            icon = "✅" if j == q["correct"] else "○"
                            st.markdown(f"  {icon} **{options_label[j]}.** {opt}")
                        if q.get("script"):
                            st.caption(f"Script: _{q['script']}_")
                        if q.get("passage"):
                            st.caption(f"Passage: _{q['passage'][:100]}..._")
                        st.divider()

        if st.button(f"🗑️ Hapus SEMUA soal tanggal {selected_date_str}", type="secondary"):
            delete_questions_for_date(selected_date_str)
            st.success("Soal berhasil dihapus!")
            st.rerun()
    else:
        st.info(f"Belum ada soal untuk tanggal **{selected_date_str}**.")

    # ── Form Input Soal ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ➕ Tambah Soal Baru")

    with st.form("add_question_form", clear_on_submit=True):
        col_type, col_no = st.columns(2)
        with col_type:
            q_type = st.selectbox("Tipe Soal", ["listening", "structure", "reading"])
        with col_no:
            q_no = st.number_input("Nomor Soal", min_value=1, max_value=15, value=1)

        q_question = st.text_area("Pertanyaan *", placeholder="Tulis soal di sini...")

        if q_type == "listening":
            q_script = st.text_area("Script Audio (untuk TTS)", placeholder="Teks yang akan dibacakan...")
            q_passage = ""
        elif q_type == "reading":
            q_passage = st.text_area("Passage / Bacaan", placeholder="Teks bacaan untuk soal ini...")
            q_script = ""
        else:
            q_script = ""
            q_passage = ""

        col_a, col_b = st.columns(2)
        with col_a:
            opt_a = st.text_input("Opsi A *")
            opt_c = st.text_input("Opsi C *")
        with col_b:
            opt_b = st.text_input("Opsi B *")
            opt_d = st.text_input("Opsi D *")

        correct = st.radio("Kunci Jawaban *", ["A (0)", "B (1)", "C (2)", "D (3)"], horizontal=True)
        correct_idx = ["A (0)", "B (1)", "C (2)", "D (3)"].index(correct)

        submitted = st.form_submit_button("💾 Simpan Soal", use_container_width=True, type="primary")
        if submitted:
            if not q_question or not opt_a or not opt_b or not opt_c or not opt_d:
                st.error("Lengkapi semua field wajib (*)")
            else:
                add_question({
                    "date": selected_date_str,
                    "no": q_no,
                    "type": q_type,
                    "question": q_question,
                    "option_a": opt_a,
                    "option_b": opt_b,
                    "option_c": opt_c,
                    "option_d": opt_d,
                    "correct": correct_idx,
                    "script": q_script,
                    "passage": q_passage,
                })
                st.success(f"✅ Soal berhasil disimpan untuk {selected_date_str}!")
                st.rerun()

    # ── Bulk Upload via CSV ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📤 Upload Soal via CSV")
    st.markdown("""
    **Format kolom CSV yang dibutuhkan:**
    `date, no, type, question, option_a, option_b, option_c, option_d, correct, script, passage`
    
    - `date` → format YYYY-MM-DD (contoh: 2025-07-14)  
    - `type` → `listening` / `structure` / `reading`  
    - `correct` → 0=A, 1=B, 2=C, 3=D
    """)

    uploaded = st.file_uploader("Upload file CSV soal", type=["csv"])
    if uploaded:
        df_upload = pd.read_csv(uploaded)
        st.dataframe(df_upload.head(10))
        if st.button("⬆️ Import Semua Soal dari CSV", type="primary"):
            count = 0
            for _, row in df_upload.iterrows():
                add_question(row.to_dict())
                count += 1
            st.success(f"✅ {count} soal berhasil diimport!")
            st.rerun()

    # ── Download Template CSV ──────────────────────────────────────────
    template_df = pd.DataFrame([{
        "date": date.today().isoformat(),
        "no": 1,
        "type": "listening",
        "question": "What does the man want to do?",
        "option_a": "Go to the library",
        "option_b": "Take a bus",
        "option_c": "Study at home",
        "option_d": "Visit a friend",
        "correct": 0,
        "script": "Man: I think I'll go to the library today.",
        "passage": "",
    }])
    st.download_button(
        "📥 Download Template CSV",
        data=template_df.to_csv(index=False).encode("utf-8"),
        file_name="template_soal_ept.csv",
        mime="text/csv",
    )


# ═══════════════════════════════════════════════════════════════════
#  TAB 2: PANTAU NILAI
# ═══════════════════════════════════════════════════════════════════
with tab_scores:
    st.markdown("### 📊 Semua Nilai Siswa")

    df_all = get_all_scores()
    if df_all.empty:
        st.info("Belum ada nilai masuk.")
    else:
        # Filter by date
        min_d = df_all["date"].min().date()
        max_d = df_all["date"].max().date()
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_date = st.date_input("Filter tanggal", value=max_d, min_value=min_d, max_value=max_d)
        with col_f2:
            all_users = ["Semua"] + sorted(df_all["username"].unique().tolist())
            filter_user = st.selectbox("Filter user", all_users)

        filtered = df_all.copy()
        filtered = filtered[filtered["date"].dt.date == filter_date]
        if filter_user != "Semua":
            filtered = filtered[filtered["username"] == filter_user]

        st.markdown(f"**{len(filtered)} data** ditemukan")
        display_cols = ["name", "date", "listening", "structure", "reading", "total", "accuracy", "timestamp"]
        st.dataframe(
            filtered[display_cols].rename(columns={
                "name": "Nama", "date": "Tanggal",
                "listening": "LST", "structure": "STR",
                "reading": "RDG", "total": "Total",
                "accuracy": "Akurasi", "timestamp": "Waktu"
            }),
            use_container_width=True, hide_index=True
        )

        # Leaderboard hari ini
        st.markdown("### 🏆 Leaderboard Hari Ini")
        today_scores = df_all[df_all["date"].dt.date == date.today()].copy()
        if today_scores.empty:
            st.info("Belum ada yang mengerjakan tes hari ini.")
        else:
            today_scores = today_scores.sort_values("total", ascending=False).reset_index(drop=True)
            today_scores.index += 1
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            today_scores["Rank"] = [medals.get(i, str(i)) for i in today_scores.index]
            st.dataframe(
                today_scores[["Rank", "name", "total", "accuracy"]].rename(
                    columns={"name": "Nama", "total": "Skor", "accuracy": "Akurasi"}
                ),
                use_container_width=True, hide_index=True
            )

        # Download semua nilai
        csv_all = df_all.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Export Semua Nilai (.csv)",
            data=csv_all, file_name="semua_nilai_ept.csv", mime="text/csv",
        )


# ═══════════════════════════════════════════════════════════════════
#  TAB 3: KELOLA USER
# ═══════════════════════════════════════════════════════════════════
with tab_users:
    st.markdown("### 👥 Daftar User")
    users = get_user_registry()
    if users:
        user_df = pd.DataFrame([
            {"Username": u, "Nama": d["name"], "Role": d["role"]}
            for u, d in users.items()
        ])
        st.dataframe(user_df, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada user terdaftar.")

    st.markdown("---")
    st.markdown("### ➕ Tambah User Baru")
    with st.form("add_user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username *")
            new_name = st.text_input("Nama Lengkap *")
        with col2:
            new_password = st.text_input("Password *", type="password")
            new_role = st.selectbox("Role", ["user", "admin"])

        if st.form_submit_button("💾 Tambah User", type="primary", use_container_width=True):
            if not new_username or not new_password or not new_name:
                st.error("Semua field wajib diisi!")
            elif new_username in users:
                st.error("Username sudah ada!")
            else:
                add_user(new_username, new_password, new_name, new_role)
                st.success(f"✅ User '{new_username}' berhasil ditambahkan!")
                st.rerun()

    st.markdown("---")
    st.markdown("### 🗑️ Hapus User")
    if users:
        del_username = st.selectbox("Pilih user untuk dihapus", list(users.keys()))
        if st.button("🗑️ Hapus User", type="secondary"):
            delete_user(del_username)
            st.success(f"User '{del_username}' berhasil dihapus.")
            st.rerun()
