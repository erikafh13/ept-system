"""pages/5_Analitik.py — Analisis mendalam soal & performa."""

import streamlit as st
import altair as alt
import pandas as pd
from utils.session import init_session
from utils.auth import logout
from utils.analytics import get_answer_log, get_hardest_questions, get_user_weak_sections, get_section_difficulty, get_user_trend
from utils.sheets import get_all_scores, get_user_scores

st.set_page_config(page_title="Analitik — EPT Pro", page_icon="📊", layout="wide")

import os
css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()
if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

username = st.session_state.username
role     = st.session_state.get("role", "user")

# Navbar
c1, _, c3 = st.columns([1, 4, 1])
with c1: st.markdown('<span class="nav-logo">📊 Analitik</span>', unsafe_allow_html=True)
with c3:
    if st.button("Keluar"): logout()
st.markdown("---")

df_log = get_answer_log()

# ═══════════════════════════════════════════════════════════════════
#  VIEW ADMIN: semua user
# ═══════════════════════════════════════════════════════════════════
if role == "admin":
    st.markdown("## 📊 Analitik Admin — Semua User")

    tab_soal, tab_user, tab_compare = st.tabs(["🔍 Analisis Soal", "👤 Per User", "📈 Perbandingan"])

    # ── Tab 1: Soal Tersulit ────────────────────────────────────────
    with tab_soal:
        st.markdown("### 🔴 Soal dengan Tingkat Kesalahan Tertinggi")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            sec_filter = st.selectbox("Filter Section", ["Semua", "listening", "structure", "reading"])
        with col_f2:
            top_n = st.slider("Tampilkan top N soal", 5, 20, 10)

        sec_arg = None if sec_filter == "Semua" else sec_filter
        hard_df = get_hardest_questions(df_log, section=sec_arg, top_n=top_n)

        if hard_df.empty:
            st.info("Belum ada data jawaban. Data akan muncul setelah peserta mengerjakan tes.")
        else:
            # Bar chart
            chart = alt.Chart(hard_df).mark_bar(color="#EF4444").encode(
                x=alt.X("error_rate:Q", title="Tingkat Kesalahan (%)", scale=alt.Scale(domain=[0,100])),
                y=alt.Y("q_no:O", title="No. Soal", sort="-x"),
                color=alt.Color("section:N", scale=alt.Scale(
                    domain=["listening","structure","reading"],
                    range=["#3B82F6","#8B5CF6","#F97316"])),
                tooltip=["question_date","section","q_no","total","wrong","error_rate"],
            ).properties(height=350)
            st.altair_chart(chart, use_container_width=True)

            st.dataframe(hard_df.rename(columns={
                "question_date":"Tanggal","section":"Section","q_no":"No Soal",
                "total":"Total Jawab","wrong":"Salah","error_rate":"Error Rate %"
            }), use_container_width=True, hide_index=True)

        # ── Kesulitan per section ─────────────────────────────────
        st.markdown("### 🎯 Rata-rata Akurasi per Section")
        sec_diff = get_section_difficulty(df_log)
        if not sec_diff.empty:
            bar = alt.Chart(sec_diff).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
                x=alt.X("section:N", title="Section"),
                y=alt.Y("accuracy:Q", title="Akurasi (%)", scale=alt.Scale(domain=[0,100])),
                color=alt.Color("section:N", scale=alt.Scale(
                    domain=["listening","structure","reading"],
                    range=["#3B82F6","#8B5CF6","#F97316"])),
                tooltip=["section","accuracy","total","correct"],
            ).properties(height=250)
            st.altair_chart(bar, use_container_width=True)

    # ── Tab 2: Per User ─────────────────────────────────────────────
    with tab_user:
        st.markdown("### 👤 Analisis Per User")
        df_scores = get_all_scores()

        if df_scores.empty:
            st.info("Belum ada data skor.")
        else:
            all_usernames = sorted(df_scores["username"].unique().tolist())
            selected_user = st.selectbox("Pilih User", all_usernames)

            weak = get_user_weak_sections(selected_user, df_log)
            if weak:
                st.markdown("#### 💡 Profil Kekuatan/Kelemahan")
                cw1, cw2, cw3 = st.columns(3)
                for col, sec, icon in zip([cw1, cw2, cw3], ["listening","structure","reading"], ["🎧","📐","📖"]):
                    acc = weak.get(sec, 0)
                    color = "green" if acc >= 70 else ("orange" if acc >= 50 else "red")
                    col.markdown(f"""<div class="stat-card {color}">
                        <div class="stat-num">{acc}%</div>
                        <div class="stat-label">{icon} {sec.capitalize()}</div>
                    </div>""", unsafe_allow_html=True)

            # Tren akurasi
            trend = get_user_trend(selected_user, df_log)
            if not trend.empty:
                st.markdown("#### 📈 Tren Akurasi Harian")
                trend_chart = alt.Chart(trend).mark_line(point=True, strokeWidth=2).encode(
                    x=alt.X("date:T", title="Tanggal"),
                    y=alt.Y("accuracy:Q", title="Akurasi (%)", scale=alt.Scale(domain=[0,100])),
                    color=alt.Color("section:N"),
                    tooltip=["date","section","accuracy","total","correct"],
                ).properties(height=280).interactive()
                st.altair_chart(trend_chart, use_container_width=True)

            # Riwayat skor
            user_df = df_scores[df_scores["username"] == selected_user].copy()
            user_df["date"] = user_df["date"].dt.strftime("%d %b %Y")
            st.markdown("#### 📋 Riwayat Skor")
            st.dataframe(user_df[["date","listening","structure","reading","total","accuracy"]].rename(
                columns={"date":"Tanggal","listening":"LST","structure":"STR",
                         "reading":"RDG","total":"Total","accuracy":"Akurasi"}
            ), use_container_width=True, hide_index=True)

    # ── Tab 3: Perbandingan ─────────────────────────────────────────
    with tab_compare:
        st.markdown("### 📊 Perbandingan Antar User")
        df_scores = get_all_scores()
        if df_scores.empty:
            st.info("Belum ada data.")
        else:
            # Rata-rata skor per user
            avg_df = df_scores.groupby(["username","name"])["total"].agg(
                ["mean","max","count"]).reset_index()
            avg_df.columns = ["username","name","rata_rata","tertinggi","jumlah_tes"]
            avg_df["rata_rata"] = avg_df["rata_rata"].round(1)
            avg_df = avg_df.sort_values("rata_rata", ascending=False)

            bars = alt.Chart(avg_df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
                x=alt.X("name:N", sort="-y", title="Nama"),
                y=alt.Y("rata_rata:Q", title="Rata-rata Skor", scale=alt.Scale(domain=[0,45])),
                color=alt.Color("rata_rata:Q", scale=alt.Scale(scheme="blues")),
                tooltip=["name","rata_rata","tertinggi","jumlah_tes"],
            ).properties(height=300)
            st.altair_chart(bars, use_container_width=True)

            st.dataframe(avg_df.rename(columns={
                "name":"Nama","rata_rata":"Rata-rata","tertinggi":"Tertinggi","jumlah_tes":"Jumlah Tes"
            })[["Nama","Rata-rata","Tertinggi","Jumlah Tes"]], use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════
#  VIEW USER: hanya data diri sendiri
# ═══════════════════════════════════════════════════════════════════
else:
    st.markdown(f"## 📊 Analitik Pribadi — {st.session_state.name}")

    df_scores = get_user_scores(username)
    weak      = get_user_weak_sections(username, df_log)
    trend     = get_user_trend(username, df_log)

    if df_scores.empty:
        st.info("Belum ada data. Selesaikan simulasi pertamamu dulu!")
        st.stop()

    # Profil kekuatan/kelemahan
    st.markdown("### 💡 Profil Kekuatanmu")
    cw1, cw2, cw3 = st.columns(3)
    for col, sec, icon in zip([cw1, cw2, cw3], ["listening","structure","reading"], ["🎧","📐","📖"]):
        acc   = weak.get(sec, 0)
        color = "green" if acc >= 70 else ("orange" if acc >= 50 else "red")
        label = "Kuat 💪" if acc >= 70 else ("Cukup 📈" if acc >= 50 else "Perlu Latihan 🔥")
        col.markdown(f"""<div class="stat-card {color}">
            <div class="stat-num">{acc}%</div>
            <div class="stat-label">{icon} {sec.capitalize()}<br><small>{label}</small></div>
        </div>""", unsafe_allow_html=True)

    # Rekomendasi
    st.markdown("### 🎯 Fokus Latihan")
    for sec, icon in zip(["listening","structure","reading"], ["🎧","📐","📖"]):
        acc = weak.get(sec, 100)
        if acc < 60:
            tips = {
                "listening": "Dengarkan podcast BBC Learning English atau VOA Learning English setiap hari.",
                "structure": "Pelajari 12 tenses, passive voice, dan conditional sentences.",
                "reading": "Baca artikel berita bahasa Inggris dan latih skimming & scanning."
            }
            st.warning(f"{icon} **{sec.capitalize()} ({acc}%)** — {tips[sec]}")

    # Tren skor total
    if not df_scores.empty and len(df_scores) > 1:
        st.markdown("### 📈 Tren Skor Total")
        chart_df = df_scores.sort_values("date").copy()
        chart_df["date_str"] = chart_df["date"].dt.strftime("%d %b")
        line = alt.Chart(chart_df).mark_line(point=True, color="#2563EB", strokeWidth=2.5).encode(
            x=alt.X("date_str:N", title="Tanggal", sort=None),
            y=alt.Y("total:Q", title="Skor Total", scale=alt.Scale(domain=[0,45])),
            tooltip=["date_str","total","listening","structure","reading"],
        ).properties(height=280).interactive()
        st.altair_chart(line, use_container_width=True)

    # Tren per section
    if not trend.empty:
        st.markdown("### 📊 Akurasi per Section")
        tc = alt.Chart(trend).mark_line(point=True, strokeWidth=2).encode(
            x=alt.X("date:T", title="Tanggal"),
            y=alt.Y("accuracy:Q", title="Akurasi (%)", scale=alt.Scale(domain=[0,100])),
            color=alt.Color("section:N", scale=alt.Scale(
                domain=["listening","structure","reading"],
                range=["#3B82F6","#8B5CF6","#F97316"])),
            tooltip=["date","section","accuracy"],
        ).properties(height=250).interactive()
        st.altair_chart(tc, use_container_width=True)

    # Tabel riwayat
    st.markdown("### 📋 Riwayat Lengkap")
    show_df = df_scores.copy()
    show_df["date"] = show_df["date"].dt.strftime("%d %b %Y")
    st.dataframe(show_df[["date","listening","structure","reading","total","accuracy"]].rename(
        columns={"date":"Tanggal","listening":"LST","structure":"STR",
                 "reading":"RDG","total":"Total","accuracy":"Akurasi"}
    ), use_container_width=True, hide_index=True)
