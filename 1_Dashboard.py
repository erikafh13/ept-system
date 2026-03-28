"""pages/1_Dashboard.py — Dashboard utama untuk user."""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
from utils.session import init_session
from utils.auth import logout
from utils.sheets import (
    get_questions_for_date,
    get_user_scores,
    has_done_test_today,
)

st.set_page_config(page_title="Dashboard — EPT Pro", page_icon="📊", layout="wide")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()

# Guard: harus login dan bukan admin
if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
if st.session_state.get("role") == "admin":
    st.switch_page("pages/2_Admin.py")

username = st.session_state.username
name = st.session_state.name

# ── Navbar ─────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1, 4, 1])
with c1:
    st.markdown('<span class="nav-logo">🎓 EPT Pro</span>', unsafe_allow_html=True)
with c3:
    if st.button("Keluar", key="logout_btn"):
        logout()

st.markdown("---")

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <div class="greeting">Halo, <span class="name-highlight">{name}</span> 👋</div>
    <div class="date-badge">📅 {date.today().strftime('%A, %d %B %Y')}</div>
</div>
""", unsafe_allow_html=True)

# ── Cek soal tersedia ───────────────────────────────────────────────────────
questions = get_questions_for_date()
total_q = sum(len(v) for v in questions.values())
done_today = has_done_test_today(username)

# ── Quick Stats ─────────────────────────────────────────────────────────────
df_scores = get_user_scores(username)

total_sessions = len(df_scores)
best_score = int(df_scores["total"].max()) if not df_scores.empty else 0
streak = 0
if not df_scores.empty:
    sorted_dates = df_scores["date"].dt.date.sort_values(ascending=False).tolist()
    today_dt = date.today()
    for i, d in enumerate(sorted_dates):
        from datetime import timedelta
        if d == today_dt - timedelta(days=i):
            streak += 1
        else:
            break

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class="stat-card blue">
        <div class="stat-num">{total_q}</div>
        <div class="stat-label">Soal Tersedia Hari Ini</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="stat-card {'green' if done_today else 'red'}">
        <div class="stat-num">{'✅' if done_today else '❌'}</div>
        <div class="stat-label">Status Tes Hari Ini</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="stat-card purple">
        <div class="stat-num">{best_score}<span style="font-size:1rem">/45</span></div>
        <div class="stat-label">Skor Terbaik</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="stat-card orange">
        <div class="stat-num">{streak}🔥</div>
        <div class="stat-label">Hari Berturut-turut</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Action Cards ────────────────────────────────────────────────────────────
col_start, col_history = st.columns(2)

with col_start:
    st.markdown('<div class="action-card primary">', unsafe_allow_html=True)
    st.markdown("### 🚀 Mulai Simulasi EPT")
    if done_today:
        st.warning("Kamu sudah mengerjakan tes hari ini! Coba lagi besok.")
        st.markdown("""
        > Jadwal tes berikutnya otomatis tersedia besok pagi ketika admin memperbarui soal.
        """)
    elif total_q < 45:
        st.error(f"Soal hari ini belum lengkap ({total_q}/45). Hubungi admin.")
    else:
        st.markdown(f"""
        Soal hari ini siap! **{questions['listening'].__len__()} Listening**, 
        **{questions['structure'].__len__()} Structure**, **{questions['reading'].__len__()} Reading**.
        """)
        if st.button("▶️  Mulai Simulasi Sekarang", key="start_test", use_container_width=True):
            st.session_state.test_active = True
            st.session_state.test_section = "listening"
            st.session_state.test_idx = 0
            st.session_state.answers = {}
            st.session_state.questions_today = questions
            st.switch_page("pages/3_Test.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col_history:
    st.markdown('<div class="action-card secondary">', unsafe_allow_html=True)
    st.markdown("### 📊 Riwayat Skor")
    if df_scores.empty:
        st.info("Belum ada riwayat. Selesaikan simulasi pertamamu!")
    else:
        # Tampilkan 5 terbaru
        recent = df_scores.head(5)[["date", "total", "accuracy"]].copy()
        recent["date"] = recent["date"].dt.strftime("%d %b")
        recent.columns = ["Tanggal", "Skor", "Akurasi"]
        st.dataframe(recent, use_container_width=True, hide_index=True)

        # Download CSV
        csv = df_scores.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️  Unduh CSV Lengkap",
            data=csv,
            file_name=f"skor_ept_{username}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Progress Chart ──────────────────────────────────────────────────────────
if not df_scores.empty and len(df_scores) > 1:
    st.markdown("### 📈 Grafik Progress 30 Hari Terakhir")

    chart_df = df_scores.head(30).copy()
    chart_df["date_str"] = chart_df["date"].dt.strftime("%d %b")
    chart_df = chart_df.sort_values("date")

    # Melt untuk multi-line chart
    melted = chart_df[["date_str", "listening", "structure", "reading", "total"]].melt(
        id_vars="date_str", var_name="Bagian", value_name="Skor"
    )

    chart = (
        alt.Chart(melted)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("date_str:N", title="Tanggal", sort=None),
            y=alt.Y("Skor:Q", title="Skor"),
            color=alt.Color(
                "Bagian:N",
                scale=alt.Scale(
                    domain=["listening", "structure", "reading", "total"],
                    range=["#3B82F6", "#8B5CF6", "#F97316", "#10B981"],
                ),
            ),
            tooltip=["date_str", "Bagian", "Skor"],
        )
        .properties(height=300)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

    # Per-section breakdown (latest test)
    st.markdown("### 🎯 Rincian Skor Terakhir")
    latest = df_scores.iloc[0]
    b1, b2, b3 = st.columns(3)
    with b1:
        st.metric("Listening", f"{int(latest['listening'])}", help="Maks 15 soal")
    with b2:
        st.metric("Structure", f"{int(latest['structure'])}", help="Maks 15 soal")
    with b3:
        st.metric("Reading", f"{int(latest['reading'])}", help="Maks 15 soal")
