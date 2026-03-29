"""pages/2_Admin.py — Panel kontrol admin."""

import os
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from utils.session import init_session
from utils.auth import logout
from utils.sheets import (
    get_questions_for_date, get_all_scores, get_user_registry,
    add_question, delete_questions_for_date,
    add_user, delete_user, get_all_user_phones,
)
from utils.whatsapp import (
    notify_admin_soal_belum_ada,
    notify_user_reminder,
    notify_admin_daily_summary,
)

st.set_page_config(page_title="Admin — EPT Pro", page_icon="⚙️", layout="wide")

css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()
if not st.session_state.get("logged_in") or st.session_state.get("role") != "admin":
    st.error("⛔ Akses ditolak. Halaman ini khusus admin.")
    st.stop()

name = st.session_state.name

# ── Navbar ────────────────────────────────────────────────────────────────────
c1, _, c3 = st.columns([1, 4, 1])
with c1:
    st.markdown('<span class="nav-logo">⚙️ Admin</span>', unsafe_allow_html=True)
with c3:
    if st.button("Keluar", key="nav_logout"):
        logout()
st.markdown("---")
st.markdown(f"<h2>Selamat datang, <b>{name}</b> 🛡️</h2>", unsafe_allow_html=True)

# Status soal hari ini
q_today     = get_questions_for_date()
total_today = sum(len(v) for v in q_today.values())
if total_today < 45:
    st.warning(f"⚠️ Soal manual hari ini baru {total_today}/45. Gunakan Pool System atau tambah manual.")
else:
    st.success(f"✅ Soal manual hari ini sudah lengkap ({total_today}/45)")

st.markdown("<br>", unsafe_allow_html=True)

tab_q, tab_wa, tab_scores, tab_users = st.tabs(
    ["📝 Kelola Soal Manual", "📲 Notifikasi WhatsApp", "📊 Pantau Nilai", "👥 Kelola User"]
)


# ═══════════════════════════════════════════════════════════════════
#  TAB 1: KELOLA SOAL MANUAL
# ═══════════════════════════════════════════════════════════════════
with tab_q:
    st.info("💡 Gunakan **halaman 🎲 Bank Soal** untuk sistem soal acak (direkomendasikan). Tab ini untuk input soal manual per tanggal.")

    col_d, _ = st.columns([2, 3])
    with col_d:
        sel_date = st.date_input(
            "Pilih tanggal",
            value=date.today(),
            min_value=date.today() - timedelta(days=30),
            max_value=date.today() + timedelta(days=60),
        )
    sel_str = sel_date.isoformat()
    qd      = get_questions_for_date(sel_str)
    total_loaded = sum(len(v) for v in qd.values())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Listening", f"{len(qd['listening'])}/15")
    c2.metric("Structure",  f"{len(qd['structure'])}/15")
    c3.metric("Reading",    f"{len(qd['reading'])}/15")
    c4.metric("Total",      f"{total_loaded}/45")

    if total_loaded > 0:
        for qtype, qlist in qd.items():
            if not qlist:
                continue
            with st.expander(f"📂 {qtype.capitalize()} ({len(qlist)} soal)"):
                for i, q in enumerate(qlist):
                    st.markdown(f"**{i+1}. {q['question']}**")
                    for j, opt in enumerate(q["options"]):
                        st.markdown(f"  {'✅' if j == q['correct'] else '○'} **{'ABCD'[j]}.** {opt}")
                    if q.get("script"):
                        st.caption(f"Script: _{q['script']}_")
                    if q.get("passage"):
                        st.caption(f"Passage: _{q['passage'][:80]}..._")
                    st.divider()

        if st.button(f"🗑️ Hapus SEMUA soal tanggal {sel_str}", type="secondary"):
            delete_questions_for_date(sel_str)
            st.success("Dihapus!")
            st.rerun()
    else:
        st.info(f"Belum ada soal untuk {sel_str}.")

    st.markdown("---")
    st.markdown("### ➕ Tambah Soal Baru")
    with st.form("add_q_form", clear_on_submit=True):
        col_t, col_n = st.columns(2)
        with col_t:
            q_type = st.selectbox("Tipe", ["listening", "structure", "reading"])
        with col_n:
            q_no = st.number_input("Nomor", min_value=1, max_value=15, value=1)

        q_question = st.text_area("Pertanyaan *")
        q_script   = st.text_area("Script Audio (khusus listening)") if q_type == "listening" else ""
        q_passage  = st.text_area("Passage (khusus reading)")        if q_type == "reading"   else ""

        ca, cb = st.columns(2)
        with ca:
            oa = st.text_input("Opsi A *")
            oc = st.text_input("Opsi C *")
        with cb:
            ob = st.text_input("Opsi B *")
            od = st.text_input("Opsi D *")

        correct_map = {"A (0)": 0, "B (1)": 1, "C (2)": 2, "D (3)": 3}
        correct_raw = st.radio("Kunci Jawaban *", list(correct_map.keys()), horizontal=True)

        if st.form_submit_button("💾 Simpan Soal", use_container_width=True, type="primary"):
            if not all([q_question, oa, ob, oc, od]):
                st.error("Lengkapi semua field yang wajib (*)")
            else:
                add_question({
                    "date": sel_str, "no": q_no, "type": q_type,
                    "question": q_question,
                    "option_a": oa, "option_b": ob, "option_c": oc, "option_d": od,
                    "correct":  correct_map[correct_raw],
                    "script":   q_script, "passage": q_passage,
                })
                st.success("✅ Soal disimpan!")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📤 Upload Soal via CSV")
    st.markdown("""
    **Format kolom:** `date, no, type, question, option_a, option_b, option_c, option_d, correct, script, passage`
    - `correct`: 0=A, 1=B, 2=C, 3=D
    """)
    uploaded = st.file_uploader("Upload CSV Soal Manual", type=["csv"])
    if uploaded:
        df_up = pd.read_csv(uploaded)
        st.dataframe(df_up.head(), use_container_width=True)
        if st.button("⬆️ Import dari CSV", type="primary"):
            for _, row in df_up.iterrows():
                add_question(row.to_dict())
            st.success(f"✅ {len(df_up)} soal diimport!")
            st.rerun()

    tmpl = pd.DataFrame([{
        "date": date.today().isoformat(), "no": 1, "type": "listening",
        "question": "What does the man want?",
        "option_a": "Go home", "option_b": "Buy food",
        "option_c": "Study",   "option_d": "Sleep",
        "correct": 0, "script": "Man: I want to go home.", "passage": "",
    }])
    st.download_button(
        "📥 Download Template CSV",
        data=tmpl.to_csv(index=False).encode("utf-8"),
        file_name="template_soal_manual.csv",
        mime="text/csv",
    )


# ═══════════════════════════════════════════════════════════════════
#  TAB 2: NOTIFIKASI WHATSAPP
# ═══════════════════════════════════════════════════════════════════
with tab_wa:
    st.markdown("### 📲 Pusat Notifikasi WhatsApp")
    st.info("""
    Notifikasi WA menggunakan **Fonnte API** (gratis untuk Indonesia).
    Pastikan sudah mengisi `token` dan `admin_number` di `.streamlit/secrets.toml`.
    """)

    # Ingatkan admin soal belum ada
    st.markdown("#### 🔔 Kirim Pengingat ke Admin")
    col_cek, col_notif = st.columns(2)
    with col_cek:
        st.metric(
            "Soal Hari Ini",
            f"{total_today}/45",
            delta="Lengkap ✅" if total_today >= 45 else f"Kurang {45 - total_today} soal ⚠️",
        )
    with col_notif:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📨 Kirim Pengingat ke Admin", use_container_width=True):
            ok = notify_admin_soal_belum_ada()
            st.success("Terkirim! 🎉") if ok else st.error("Gagal. Cek token di secrets.toml.")

    st.markdown("---")
    st.markdown("#### 📣 Blast Pengingat ke Semua User")
    user_phones = get_all_user_phones()
    if not user_phones:
        st.warning("Belum ada user dengan nomor WA. Tambahkan di tab Kelola User.")
    else:
        st.markdown(f"**{len(user_phones)} user** siap menerima notifikasi:")
        st.dataframe(
            pd.DataFrame(user_phones)[["name", "phone"]].rename(
                columns={"name": "Nama", "phone": "Nomor WA"}
            ),
            hide_index=True,
        )
        if st.button(f"📲 Kirim ke {len(user_phones)} User", type="primary"):
            success = fail = 0
            prog = st.progress(0)
            for i, u in enumerate(user_phones):
                ok = notify_user_reminder(u["phone"], u["name"])
                if ok: success += 1
                else:  fail    += 1
                prog.progress((i + 1) / len(user_phones))
            st.success(f"✅ Berhasil: {success} | ❌ Gagal: {fail}")

    st.markdown("---")
    st.markdown("#### 📋 Kirim Ringkasan Harian ke Admin")
    df_all       = get_all_scores()
    today_scores = (
        df_all[df_all["date"].dt.date == date.today()]
        if not df_all.empty else pd.DataFrame()
    )
    if today_scores.empty:
        st.info("Belum ada peserta yang mengerjakan tes hari ini.")
    else:
        participants = len(today_scores)
        avg_score    = float(today_scores["total"].mean())
        top_row      = today_scores.sort_values("total", ascending=False).iloc[0]
        top_name     = str(top_row["name"])
        top_score    = int(top_row["total"])

        st.markdown(f"""
        **Preview ringkasan:**
        - 👥 Peserta: **{participants}**
        - 📊 Rata-rata: **{avg_score:.1f}/45**
        - 🏆 Tertinggi: **{top_name}** ({top_score}/45)
        """)
        if st.button("📨 Kirim Ringkasan ke Admin via WA", type="primary"):
            # FIX: gunakan signature baru — admin_number diambil dari secrets otomatis
            ok = notify_admin_daily_summary(participants, avg_score, top_name, top_score)
            st.success("Terkirim!") if ok else st.error("Gagal. Cek konfigurasi WA di secrets.toml.")

    st.markdown("---")
    st.markdown("#### ⚙️ Cara Konfigurasi WhatsApp")
    st.code("""
# .streamlit/secrets.toml

[whatsapp]
token        = "TOKEN_DARI_FONNTE.COM"
admin_number = "628123456789"   # nomor WA admin (tanpa +)
    """, language="toml")
    st.markdown("[📖 Cara mendapatkan token Fonnte →](https://fonnte.com)")


# ═══════════════════════════════════════════════════════════════════
#  TAB 3: PANTAU NILAI
# ═══════════════════════════════════════════════════════════════════
with tab_scores:
    st.markdown("### 📊 Semua Nilai Siswa")
    df_all = get_all_scores()
    if df_all.empty:
        st.info("Belum ada nilai.")
    else:
        min_d = df_all["date"].min().date()
        max_d = df_all["date"].max().date()
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_date = st.date_input("Filter tanggal", max_d, min_d, max_d)
        with col_f2:
            all_u    = ["Semua"] + sorted(df_all["username"].unique().tolist())
            filter_u = st.selectbox("Filter user", all_u)

        filtered = df_all[df_all["date"].dt.date == filter_date]
        if filter_u != "Semua":
            filtered = filtered[filtered["username"] == filter_u]

        st.dataframe(
            filtered[["name", "date", "listening", "structure", "reading", "total", "accuracy", "timestamp"]].rename(
                columns={
                    "name": "Nama", "date": "Tanggal",
                    "listening": "LST", "structure": "STR",
                    "reading": "RDG", "total": "Total",
                    "accuracy": "Akurasi", "timestamp": "Waktu",
                }
            ),
            use_container_width=True, hide_index=True,
        )

        # Leaderboard hari ini
        st.markdown("### 🏆 Leaderboard Hari Ini")
        today_s = (
            df_all[df_all["date"].dt.date == date.today()]
            .sort_values("total", ascending=False)
            .reset_index(drop=True)
        )
        if today_s.empty:
            st.info("Belum ada yang mengerjakan tes hari ini.")
        else:
            today_s.index += 1
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            today_s["Rank"] = [medals.get(i, str(i)) for i in today_s.index]
            st.dataframe(
                today_s[["Rank", "name", "total", "accuracy"]].rename(
                    columns={"name": "Nama", "total": "Skor", "accuracy": "Akurasi"}
                ),
                use_container_width=True, hide_index=True,
            )

        st.download_button(
            "⬇️ Export Semua Nilai (.csv)",
            data=df_all.to_csv(index=False).encode("utf-8"),
            file_name="semua_nilai_ept.csv",
            mime="text/csv",
        )


# ═══════════════════════════════════════════════════════════════════
#  TAB 4: KELOLA USER
# ═══════════════════════════════════════════════════════════════════
with tab_users:
    st.markdown("### 👥 Daftar User")
    users = get_user_registry()
    if users:
        udf = pd.DataFrame([
            {"Username": u, "Nama": d["name"], "Role": d["role"], "No WA": d.get("phone", "")}
            for u, d in users.items()
        ])
        st.dataframe(udf, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada user.")

    st.markdown("---")
    st.markdown("### ➕ Tambah User Baru")
    with st.form("add_user_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nu = st.text_input("Username *")
            nn = st.text_input("Nama Lengkap *")
        with c2:
            np_ = st.text_input("Password *", type="password")
            nr  = st.selectbox("Role", ["user", "admin"])
        nph = st.text_input("Nomor WA (opsional)", placeholder="628123456789")

        if st.form_submit_button("💾 Tambah User", type="primary", use_container_width=True):
            if not all([nu, np_, nn]):
                st.error("Semua field yang bertanda * wajib diisi!")
            elif nu in users:
                st.error("Username sudah ada!")
            else:
                add_user(nu, np_, nn, nr, nph)
                st.success(f"✅ User '{nu}' berhasil ditambahkan!")
                st.rerun()

    st.markdown("---")
    st.markdown("### 🗑️ Hapus User")
    if users:
        du = st.selectbox("Pilih user yang akan dihapus", list(users.keys()))
        if st.button("🗑️ Hapus User Ini", type="secondary"):
            delete_user(du)
            st.success(f"User '{du}' berhasil dihapus.")
            st.rerun()
