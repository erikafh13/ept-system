"""pages/4_Result.py — Hasil simulasi + notifikasi WA otomatis."""

import os
import streamlit as st
from utils.session import init_session
from utils.sheets import get_user_scores, get_user_registry
from utils.whatsapp import notify_user_result

st.set_page_config(page_title="Hasil Simulasi — EPT Pro", page_icon="🏆", layout="centered")

css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

score = st.session_state.get("last_score")
if not score:
    st.switch_page("pages/1_Dashboard.py")

username = st.session_state.username
name     = st.session_state.name
total    = score["listening"] + score["structure"] + score["reading"]
accuracy = round((total / 45) * 100, 1)

if   accuracy >= 85: grade, gc, gm = "A", "#10B981", "Luar biasa! Performa sangat baik 🎉"
elif accuracy >= 70: grade, gc, gm = "B", "#3B82F6", "Bagus! Terus tingkatkan 💪"
elif accuracy >= 55: grade, gc, gm = "C", "#F59E0B", "Cukup baik, masih bisa lebih! 📈"
elif accuracy >= 40: grade, gc, gm = "D", "#F97316", "Perlu lebih banyak latihan 📚"
else:                grade, gc, gm = "E", "#EF4444", "Jangan menyerah, terus berlatih! 🔥"

# Kirim WA hasil (sekali saja per sesi, pakai flag)
if not st.session_state.get("wa_result_sent"):
    try:
        users = get_user_registry()
        phone = users.get(username, {}).get("phone", "")
        if phone:
            notify_user_result(phone, name, score["listening"], score["structure"], score["reading"])
    except Exception:
        pass
    st.session_state.wa_result_sent = True

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="result-hero">
    <div class="result-grade" style="color:{gc};">{grade}</div>
    <h1 class="result-title">Simulasi Selesai!</h1>
    <p class="result-msg">{gm}</p>
</div>""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
for col, label, val, color in zip(
    [c1, c2, c3, c4],
    ["Listening", "Structure", "Reading", "Total"],
    [score["listening"], score["structure"], score["reading"], total],
    ["blue", "purple", "orange", "green"],
):
    col.markdown(f"""<div class="score-card {color}">
        <div class="score-num">{val}</div>
        <div class="score-lbl">{label}<br><small>/{"15" if label != "Total" else "45"}</small></div>
    </div>""", unsafe_allow_html=True)

st.markdown(f"""
<div class="accuracy-bar-wrap">
    <div class="accuracy-label">Akurasi: <b>{accuracy}%</b></div>
    <div class="accuracy-bar-bg">
        <div class="accuracy-bar-fill" style="width:{accuracy}%;background:{gc};"></div>
    </div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Perbandingan dengan skor sebelumnya
df = get_user_scores(username)
if len(df) >= 2:
    prev  = df.iloc[1]
    delta = total - int(prev["total"])
    st.markdown(f"""<div class="comparison-box">
        vs. Tes Sebelumnya: <b>{"+" if delta >= 0 else ""}{delta} poin</b>
        {"📈" if delta > 0 else ("➡️" if delta == 0 else "📉")}
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# Rekomendasi otomatis
st.markdown("### 💡 Rekomendasi Belajar")
recs = []
if score["listening"] < 10:
    recs.append("🎧 **Listening** — Dengarkan BBC Learning English atau VOA setiap hari.")
if score["structure"] < 10:
    recs.append("📐 **Structure** — Fokus grammar: tenses, passive voice, conditional sentences.")
if score["reading"] < 10:
    recs.append("📖 **Reading** — Latih skimming & scanning di artikel berbahasa Inggris.")
if not recs:
    recs.append("🌟 Performa sangat baik! Pertahankan dan terus latihan setiap hari.")
for r in recs:
    st.markdown(f"> {r}")

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Kembali ke Dashboard", use_container_width=True, type="primary"):
        st.session_state.last_score     = None
        st.session_state.wa_result_sent = False
        st.switch_page("pages/1_Dashboard.py")
with col2:
    if not df.empty:
        st.download_button(
            "⬇️ Unduh Riwayat CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"skor_ept_{username}.csv",
            mime="text/csv",
            use_container_width=True,
        )
