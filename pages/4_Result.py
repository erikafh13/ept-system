"""pages/4_Result.py — Halaman hasil simulasi EPT."""

import streamlit as st
from utils.session import init_session
from utils.sheets import get_user_scores

st.set_page_config(page_title="Hasil Simulasi — EPT Pro", page_icon="🏆", layout="centered")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

score = st.session_state.get("last_score")
if not score:
    st.switch_page("pages/1_Dashboard.py")

username = st.session_state.username

total = score["listening"] + score["structure"] + score["reading"]
accuracy = round((total / 45) * 100, 1)

# ── Tentukan grade ──────────────────────────────────────────────────────────
if accuracy >= 85:
    grade, grade_color, grade_msg = "A", "#10B981", "Luar biasa! Performa sangat baik 🎉"
elif accuracy >= 70:
    grade, grade_color, grade_msg = "B", "#3B82F6", "Bagus! Terus tingkatkan 💪"
elif accuracy >= 55:
    grade, grade_color, grade_msg = "C", "#F59E0B", "Cukup baik, masih bisa lebih! 📈"
elif accuracy >= 40:
    grade, grade_color, grade_msg = "D", "#F97316", "Perlu lebih banyak latihan 📚"
else:
    grade, grade_color, grade_msg = "E", "#EF4444", "Jangan menyerah, terus berlatih! 🔥"

# ── Render ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="result-hero">
    <div class="result-grade" style="color:{grade_color};">{grade}</div>
    <h1 class="result-title">Simulasi Selesai!</h1>
    <p class="result-msg">{grade_msg}</p>
</div>
""", unsafe_allow_html=True)

# Skor cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="score-card blue">
        <div class="score-num">{score['listening']}</div>
        <div class="score-lbl">Listening<br><small>/ 15</small></div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="score-card purple">
        <div class="score-num">{score['structure']}</div>
        <div class="score-lbl">Structure<br><small>/ 15</small></div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="score-card orange">
        <div class="score-num">{score['reading']}</div>
        <div class="score-lbl">Reading<br><small>/ 15</small></div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="score-card green">
        <div class="score-num">{total}</div>
        <div class="score-lbl">Total<br><small>/ 45</small></div>
    </div>""", unsafe_allow_html=True)

st.markdown(f"""
<div class="accuracy-bar-wrap">
    <div class="accuracy-label">Akurasi: <b>{accuracy}%</b></div>
    <div class="accuracy-bar-bg">
        <div class="accuracy-bar-fill" style="width:{accuracy}%; background:{grade_color};"></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Comparison dengan skor sebelumnya ──────────────────────────────────────
df = get_user_scores(username)
if len(df) >= 2:
    prev = df.iloc[1]
    delta = total - int(prev["total"])
    delta_str = f"+{delta}" if delta >= 0 else str(delta)
    st.markdown(f"""
    <div class="comparison-box">
        <b>vs. Tes Sebelumnya:</b> {delta_str} poin 
        {'📈' if delta > 0 else ('➡️' if delta == 0 else '📉')}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tombol aksi ────────────────────────────────────────────────────────────
col_dash, col_dl = st.columns(2)
with col_dash:
    if st.button("🏠 Kembali ke Dashboard", use_container_width=True, type="primary"):
        st.session_state.last_score = None
        st.switch_page("pages/1_Dashboard.py")

with col_dl:
    if not df.empty:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Unduh Riwayat CSV",
            data=csv,
            file_name=f"skor_ept_{username}.csv",
            mime="text/csv",
            use_container_width=True,
        )
