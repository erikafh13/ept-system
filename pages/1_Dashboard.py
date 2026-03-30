"""pages/1_Dashboard.py — Dashboard utama untuk user."""

import os
import streamlit as st
import altair as alt
from datetime import date, timedelta
from utils.session import init_session
from utils.auth import logout
from utils.sheets import get_questions_for_date, get_user_scores, has_done_test_today
from utils.question_pool import get_or_create_todays_questions, get_pool_stats
from utils.whatsapp import notify_admin_soal_belum_ada

st.set_page_config(page_title="Dashboard — EPT Pro", page_icon="📊", layout="wide")

css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
if st.session_state.get("role") == "admin":
    st.switch_page("pages/2_Admin.py")

username = st.session_state.username
name     = st.session_state.name

# ── Navbar ────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1, 4, 1])
with c1:
    st.markdown('<span class="nav-logo">🎓 EPT Pro</span>', unsafe_allow_html=True)
with c3:
    if st.button("Keluar", key="nav_logout"):
        logout()
st.markdown("---")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <div class="greeting">Halo, <span class="name-highlight">{name}</span> 👋</div>
    <div class="date-badge">📅 {date.today().strftime('%A, %d %B %Y')}</div>
</div>""", unsafe_allow_html=True)

# ── Ambil soal hari ini (hanya sekali per sesi) ───────────────────────────────
if "questions_today" not in st.session_state or not st.session_state.questions_today:
    pool_stats = get_pool_stats()
    if pool_stats.get("total", 0) >= 45:
        questions = get_or_create_todays_questions(per_section=15)
        st.session_state.soal_mode = "pool"
    else:
        questions = get_questions_for_date()
        st.session_state.soal_mode = "manual"
    st.session_state.questions_today = questions

questions = st.session_state.questions_today
# FIX: pakai .get() dengan default agar tidak KeyError saat session direset
soal_mode = st.session_state.get("soal_mode", "manual")

total_q    = sum(len(v) for v in questions.values())
done_today = has_done_test_today(username)
df_scores  = get_user_scores(username)

# ── Hitung streak ─────────────────────────────────────────────────────────────
streak = 0
if not df_scores.empty:
    sorted_dates = df_scores["date"].dt.date.sort_values(ascending=False).tolist()
    for i, d in enumerate(sorted_dates):
        if d == date.today() - timedelta(days=i):
            streak += 1
        else:
            break

best_score = int(df_scores["total"].max()) if not df_scores.empty else 0

# ── Stat cards ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
for col, num, label, color in zip(
    [c1, c2, c3, c4],
    [total_q, "✅" if done_today else "❌", f"{best_score}/45", f"{streak}🔥"],
    ["Soal Tersedia", "Status Hari Ini", "Skor Terbaik", "Hari Berturut"],
    ["blue", "green" if done_today else "red", "purple", "orange"],
):
    col.markdown(f"""<div class="stat-card {color}">
        <div class="stat-num">{num}</div>
        <div class="stat-label">{label}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Action cards ──────────────────────────────────────────────────────────────
col_start, col_hist = st.columns(2)

with col_start:
    st.markdown('<div class="action-card primary">', unsafe_allow_html=True)
    st.markdown("### 🚀 Simulasi EPT Hari Ini")
    if done_today:
        st.success("✅ Kamu sudah mengerjakan tes hari ini!")
        st.markdown("Soal baru tersedia besok.")
    elif total_q < 45:
        st.error(f"⚠️ Soal belum lengkap ({total_q}/45). Hubungi admin.")
        if st.button("📲 Ingatkan Admin via WhatsApp", key="wa_admin"):
            ok = notify_admin_soal_belum_ada()
            if ok:
                st.success("Notifikasi terkirim ke admin!")
            else:
                st.warning("Fitur WA belum dikonfigurasi. Isi token di secrets.toml.")
    else:
        mode_label = "🎲 Soal Acak (Pool)" if soal_mode == "pool" else "📋 Soal Manual"
        st.markdown(f"""
        {mode_label} — Siap: **{len(questions['listening'])} Listening** ·
        **{len(questions['structure'])} Structure** ·
        **{len(questions['reading'])} Reading**
        """)
        if st.button("▶️ Mulai Simulasi Sekarang", use_container_width=True, key="start_test"):
            st.session_state.update({
                "test_active":     True,
                "test_section":    "listening",
                "test_idx":        0,
                "answers":         {},
                "questions_today": questions,
            })
            st.switch_page("pages/3_Test.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col_hist:
    st.markdown('<div class="action-card secondary">', unsafe_allow_html=True)
    st.markdown("### 📋 Riwayat & Ekspor")
    if df_scores.empty:
        st.info("Belum ada riwayat. Selesaikan simulasi pertamamu!")
    else:
        recent = df_scores.head(5)[["date", "total", "accuracy"]].copy()
        recent["date"] = recent["date"].dt.strftime("%d %b")
        recent.columns = ["Tanggal", "Skor", "Akurasi"]
        st.dataframe(recent, use_container_width=True, hide_index=True)
        csv = df_scores.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Unduh CSV",
            data=csv,
            file_name=f"skor_{username}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Grafik progress ───────────────────────────────────────────────────────────
if not df_scores.empty and len(df_scores) > 1:
    st.markdown("### 📈 Grafik Progress 30 Hari Terakhir")
    chart_df             = df_scores.head(30).sort_values("date").copy()
    chart_df["date_str"] = chart_df["date"].dt.strftime("%d %b")
    melted = chart_df[["date_str", "listening", "structure", "reading", "total"]].melt(
        id_vars="date_str", var_name="Bagian", value_name="Skor"
    )
    chart = (
        alt.Chart(melted)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("date_str:N", title="Tanggal", sort=None),
            y=alt.Y("Skor:Q"),
            color=alt.Color(
                "Bagian:N",
                scale=alt.Scale(
                    domain=["listening", "structure", "reading", "total"],
                    range=["#3B82F6", "#8B5CF6", "#F97316", "#10B981"],
                ),
            ),
            tooltip=["date_str", "Bagian", "Skor"],
        )
        .properties(height=280)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

# ── Navigasi cepat ────────────────────────────────────────────────────────────
st.markdown("### ⚡ Akses Cepat")
nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button("📊 Analitik Saya", use_container_width=True):
        st.switch_page("pages/5_Analitik.py")
with nav2:
    if st.button("🏆 Leaderboard", use_container_width=True):
        st.switch_page("pages/6_Leaderboard.py")
with nav3:
    if st.button("📚 Materi Belajar", use_container_width=True):
        st.switch_page("pages/7_Materi.py")
