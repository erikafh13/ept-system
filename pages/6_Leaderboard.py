"""pages/6_Leaderboard.py — Papan peringkat publik."""

import streamlit as st
import altair as alt
import pandas as pd
from datetime import date, timedelta
from utils.session import init_session
from utils.auth import logout
from utils.sheets import get_all_scores

st.set_page_config(page_title="Leaderboard — EPT Pro", page_icon="🏆", layout="wide")

import os
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()
if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

c1, _, c3 = st.columns([1, 4, 1])
with c1: st.markdown('<span class="nav-logo">🏆 Leaderboard</span>', unsafe_allow_html=True)
with c3:
    if st.button("Keluar"): logout()
st.markdown("---")

df = get_all_scores()

period = st.radio("Periode", ["Hari Ini", "7 Hari Terakhir", "30 Hari Terakhir", "Semua Waktu"],
                  horizontal=True)

today = date.today()
if period == "Hari Ini":
    filtered = df[df["date"].dt.date == today]
elif period == "7 Hari Terakhir":
    filtered = df[df["date"].dt.date >= today - timedelta(days=7)]
elif period == "30 Hari Terakhir":
    filtered = df[df["date"].dt.date >= today - timedelta(days=30)]
else:
    filtered = df.copy()

if filtered.empty:
    st.info("Belum ada data untuk periode ini.")
    st.stop()

# Agregasi
agg = filtered.groupby(["username","name"]).agg(
    skor_terbaik=("total","max"),
    rata_rata=("total","mean"),
    jumlah_tes=("total","count"),
).reset_index().sort_values("skor_terbaik", ascending=False).reset_index(drop=True)
agg.index += 1
agg["rata_rata"] = agg["rata_rata"].round(1)

medals = {1:"🥇",2:"🥈",3:"🥉"}
agg["#"] = [medals.get(i, str(i)) for i in agg.index]

# Top 3 highlight
st.markdown("### 🥇 Top 3")
top3 = agg.head(3)
cols = st.columns(3)
podium = [(0,"🥇","#F59E0B"),(1,"🥈","#94A3B8"),(2,"🥉","#B45309")]
for col, (i, medal, color) in zip(cols, podium):
    if i < len(top3):
        row = top3.iloc[i]
        col.markdown(f"""
        <div style="text-align:center; padding:1.5rem; background:white;
             border-radius:20px; border:2px solid {color}; margin:0.5rem 0;">
            <div style="font-size:3rem;">{medal}</div>
            <div style="font-size:1.1rem; font-weight:800; color:#0F172A;">{row['name']}</div>
            <div style="font-size:2rem; font-weight:800; color:{color};">{int(row['skor_terbaik'])}<span style="font-size:1rem;">/45</span></div>
            <div style="font-size:0.75rem; color:#94A3B8;">Rata-rata: {row['rata_rata']} · {int(row['jumlah_tes'])}x tes</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Bar chart
st.markdown("### 📊 Skor Terbaik Semua Peserta")
chart = alt.Chart(agg.head(20)).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
    x=alt.X("name:N", sort="-y", title="Nama"),
    y=alt.Y("skor_terbaik:Q", title="Skor Terbaik", scale=alt.Scale(domain=[0,45])),
    color=alt.Color("skor_terbaik:Q", scale=alt.Scale(scheme="blues", domain=[0,45])),
    tooltip=["name","skor_terbaik","rata_rata","jumlah_tes"],
).properties(height=300)
st.altair_chart(chart, use_container_width=True)

# Tabel lengkap
st.markdown("### 📋 Peringkat Lengkap")
highlight_user = st.session_state.username
display = agg[["#","name","skor_terbaik","rata_rata","jumlah_tes"]].rename(
    columns={"name":"Nama","skor_terbaik":"Terbaik","rata_rata":"Rata-rata","jumlah_tes":"Tes"})
st.dataframe(display, use_container_width=True, hide_index=True)

# Posisi user sendiri
user_row = agg[agg["username"] == highlight_user]
if not user_row.empty:
    pos = user_row.index[0]
    st.info(f"📍 Posisimu saat ini: **#{pos} dari {len(agg)} peserta**")
