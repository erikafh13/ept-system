"""pages/3_Test.py — Simulasi EPT dengan timer countdown & log jawaban."""

import os
import time
import streamlit as st
from datetime import date
from utils.session import init_session
from utils.sheets import save_score
from utils.analytics import save_answer_log
from gtts import gTTS
import tempfile

st.set_page_config(page_title="Simulasi EPT", page_icon="📝", layout="centered")

css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()

# Proteksi login TANPA redirect
if not st.session_state.get("logged_in"):
    st.warning("Silakan login terlebih dahulu.")
    st.stop()

# Proteksi test aktif TANPA redirect
if not st.session_state.get("test_active"):
    st.warning("Silakan mulai test dari dashboard.")
    st.stop()
    
SECTIONS       = ["listening", "structure", "reading"]
SECTION_ICONS  = {"listening": "🎧", "structure": "📐", "reading": "📖"}
SECTION_LABELS = {"listening": "Listening", "structure": "Structure", "reading": "Reading"}
TEST_SECONDS   = 90 * 60   # 90 menit

username  = st.session_state.username
name      = st.session_state.name
section   = st.session_state.test_section
idx       = st.session_state.test_idx
questions = st.session_state.questions_today
answers   = st.session_state.answers

# ── Timer ─────────────────────────────────────────────────────────────────────
# FIX: simpan start time sekali, hitung elapsed setiap render
if "test_start_time" not in st.session_state:
    st.session_state.test_start_time = time.time()

elapsed   = time.time() - st.session_state.test_start_time
remaining = max(0, TEST_SECONDS - elapsed)
mins, secs = divmod(int(remaining), 60)
timer_color = (
    "#EF4444" if remaining < 300 else
    ("#F59E0B" if remaining < 900 else "#10B981")
)


# ── Fungsi submit ─────────────────────────────────────────────────────────────
def finish_test() -> None:
    qs  = st.session_state.questions_today
    ans = st.session_state.answers
    s_l = s_s = s_r = 0

    for i, q in enumerate(qs.get("listening", [])):
        if ans.get(f"listening_{i}") == q["correct"]:  s_l += 1
    for i, q in enumerate(qs.get("structure", [])):
        if ans.get(f"structure_{i}") == q["correct"]:  s_s += 1
    for i, q in enumerate(qs.get("reading", [])):
        if ans.get(f"reading_{i}") == q["correct"]:    s_r += 1

    save_score(username, name, s_l, s_s, s_r)
    save_answer_log(username, date.today().isoformat(), ans, qs)

    st.session_state.last_score    = {"listening": s_l, "structure": s_s, "reading": s_r}
    st.session_state.test_active   = False
    st.session_state.wa_result_sent = False
    if "test_start_time" in st.session_state:
        del st.session_state["test_start_time"]
    st.switch_page("pages/4_Result.py")


# Auto-submit jika waktu habis
if remaining <= 0:
    st.warning("⏰ Waktu habis! Jawaban dikumpulkan otomatis.")
    time.sleep(1)
    finish_test()

# ── Header & progress ──────────────────────────────────────────────────────────
current_list     = questions.get(section, [])
total_in_section = len(current_list)
if not current_list:
    st.error(f"Tidak ada soal untuk bagian {section}.")
    st.stop()

q_data     = current_list[idx]
answer_key = f"{section}_{idx}"
sec_num    = SECTIONS.index(section)
total_done = sum(len(questions.get(s, [])) for s in SECTIONS[:sec_num]) + idx
total_all  = sum(len(questions.get(s, [])) for s in SECTIONS)

col_badge, col_timer = st.columns([3, 1])
with col_badge:
    st.markdown(f"""<div class="test-section-badge">
        {SECTION_ICONS[section]} {SECTION_LABELS[section]}
        &nbsp;·&nbsp; Soal {idx+1}/{total_in_section}
    </div>""", unsafe_allow_html=True)
with col_timer:
    st.markdown(f"""<div class="timer-box" style="border-color:{timer_color};color:{timer_color};">
        ⏱ {mins:02d}:{secs:02d}
    </div>""", unsafe_allow_html=True)

if "last_tick" not in st.session_state:
    st.session_state.last_tick = time.time()

# update tiap 3 detik (lebih aman)
if remaining > 0 and (time.time() - st.session_state.last_tick >= 3):
    st.session_state.last_tick = time.time()
    st.rerun()

st.progress(total_done / total_all if total_all > 0 else 0)
st.markdown("<br>", unsafe_allow_html=True)

if section == "listening":
    with st.expander("🎧 Audio Listening", expanded=True):

        script_text = q_data.get("script", "")

        if script_text:

            # Generate audio hanya jika soal berubah
            if (
                "tts_audio" not in st.session_state
                or st.session_state.get("last_text") != script_text
            ):
                tts = gTTS(script_text, lang="en")

                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tts.save(tmp_file.name)

                st.session_state.tts_audio = tmp_file.name
                st.session_state.last_text = script_text

            st.audio(st.session_state.tts_audio)

        else:
            st.warning("Tidak ada teks untuk audio.")
            
elif section == "reading" and q_data.get("passage"):
    with st.expander("📖 Baca Passage", expanded=True):
        st.markdown(
            f'<div class="passage-box">{q_data["passage"]}</div>',
            unsafe_allow_html=True,
        )

# ── Pertanyaan & pilihan jawaban ──────────────────────────────────────────────
st.markdown(f"""
<div class="question-box">
    <div class="question-num">Soal {idx + 1}</div>
    <div class="question-text">{q_data['question']}</div>
</div>""", unsafe_allow_html=True)

current_ans = answers.get(answer_key)
for i, opt in enumerate(q_data.get("options", [])):
    selected = current_ans == i
    if st.button(
        f"**{'ABCD'[i]}.** {opt}",
        key=f"opt_{answer_key}_{i}",
        use_container_width=True,
        type="primary" if selected else "secondary",
    ):
        st.session_state.answers[answer_key] = i
        st.rerun()

# ── Navigasi ──────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_back, _, col_next = st.columns([1, 2, 1])
answered = answer_key in st.session_state.answers

with col_back:
    if idx > 0:
        if st.button("◀ Kembali", use_container_width=True, key="nav_back"):
            st.session_state.test_idx -= 1
            st.rerun()
    elif section != "listening":
        prev_sec   = SECTIONS[sec_num - 1]
        prev_count = len(questions.get(prev_sec, []))
        if st.button(f"◀ {SECTION_LABELS[prev_sec]}", use_container_width=True, key="nav_prev_sec"):
            st.session_state.test_section = prev_sec
            st.session_state.test_idx     = prev_count - 1
            st.rerun()

with col_next:
    last_in_sec = idx == total_in_section - 1
    last_sec    = section == "reading"

    if last_in_sec and last_sec:
        label = "✅ Kumpulkan Jawaban"
    elif last_in_sec:
        label = f"Ke {SECTION_LABELS[SECTIONS[sec_num + 1]]} ▶"
    else:
        label = "Lanjut ▶"

    if st.button(label, use_container_width=True, type="primary",
                 disabled=not answered, key="nav_next"):
        if last_in_sec and last_sec:
            finish_test()
        elif last_in_sec:
            st.session_state.test_section = SECTIONS[sec_num + 1]
            st.session_state.test_idx     = 0
            st.rerun()
        else:
            st.session_state.test_idx += 1
            st.rerun()

# ── Sidebar: peta soal ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗺️ Peta Soal")
    for sec in SECTIONS:
        sec_list = questions.get(sec, [])
        if not sec_list:
            continue
        st.markdown(f"**{SECTION_ICONS[sec]} {SECTION_LABELS[sec]}**")
        answered_n = sum(1 for i in range(len(sec_list)) if f"{sec}_{i}" in answers)
        st.caption(f"{answered_n}/{len(sec_list)} dijawab")
        cols = st.columns(5)
        for i in range(len(sec_list)):
            k    = f"{sec}_{i}"
            icon = "🟦" if (sec == section and i == idx) else ("🟩" if k in answers else "⬜")
            cols[i % 5].markdown(icon)
        st.markdown("")
    st.markdown("---")
    total_ans = len(answers)
    st.metric("Total Dijawab", f"{total_ans}/{total_all}")
    st.progress(total_ans / total_all if total_all > 0 else 0)

    # Tombol darurat submit
    st.markdown("---")
    if st.button("⚠️ Submit Sekarang", type="secondary", use_container_width=True):
        finish_test()
