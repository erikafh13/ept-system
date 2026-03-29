"""pages/3_Test.py — Simulasi EPT dengan timer countdown & log jawaban."""

import streamlit as st
import time
from datetime import date
from utils.session import init_session
from utils.sheets import save_score
from utils.analytics import save_answer_log

st.set_page_config(page_title="Simulasi EPT", page_icon="📝", layout="centered")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
if not st.session_state.get("test_active"):
    st.switch_page("pages/1_Dashboard.py")

SECTIONS      = ["listening", "structure", "reading"]
SECTION_ICONS = {"listening": "🎧", "structure": "📐", "reading": "📖"}
SECTION_LABELS= {"listening": "Listening", "structure": "Structure", "reading": "Reading"}
TEST_SECONDS  = 90 * 60   # 90 menit

username  = st.session_state.username
name      = st.session_state.name
section   = st.session_state.test_section
idx       = st.session_state.test_idx
questions = st.session_state.questions_today
answers   = st.session_state.answers

# Timer init
if "test_start_time" not in st.session_state:
    st.session_state.test_start_time = time.time()
elapsed   = time.time() - st.session_state.test_start_time
remaining = max(0, TEST_SECONDS - elapsed)
mins, secs = divmod(int(remaining), 60)
timer_color = "#EF4444" if remaining < 300 else ("#F59E0B" if remaining < 900 else "#10B981")


def finish_test():
    qs = st.session_state.questions_today
    s_l = s_s = s_r = 0
    for i, q in enumerate(qs.get("listening", [])):
        if answers.get(f"listening_{i}") == q["correct"]: s_l += 1
    for i, q in enumerate(qs.get("structure", [])):
        if answers.get(f"structure_{i}") == q["correct"]: s_s += 1
    for i, q in enumerate(qs.get("reading", [])):
        if answers.get(f"reading_{i}") == q["correct"]: s_r += 1

    save_score(username, name, s_l, s_s, s_r)
    save_answer_log(username, date.today().isoformat(), answers, qs)
    st.session_state.last_score = {"listening": s_l, "structure": s_s, "reading": s_r}
    st.session_state.test_active = False
    if "test_start_time" in st.session_state:
        del st.session_state["test_start_time"]
    st.switch_page("pages/4_Result.py")


if remaining == 0:
    st.warning("⏰ Waktu habis! Jawaban dikumpulkan otomatis.")
    time.sleep(1)
    finish_test()

# ── Progress & header ───────────────────────────────────────────────────────
current_list     = questions.get(section, [])
total_in_section = len(current_list)
if not current_list:
    st.error("Tidak ada soal."); st.stop()
q_data     = current_list[idx]
answer_key = f"{section}_{idx}"

sec_num    = SECTIONS.index(section)
total_done = sum(len(questions.get(s, [])) for s in SECTIONS[:sec_num]) + idx
total_all  = sum(len(questions.get(s, [])) for s in SECTIONS)

col_badge, col_timer = st.columns([3, 1])
with col_badge:
    st.markdown(f"""<div class="test-section-badge">
        {SECTION_ICONS[section]} {SECTION_LABELS[section]} &nbsp;·&nbsp; Soal {idx+1}/{total_in_section}
    </div>""", unsafe_allow_html=True)
with col_timer:
    st.markdown(f"""<div class="timer-box" style="border-color:{timer_color};color:{timer_color};">
        ⏱ {mins:02d}:{secs:02d}
    </div>""", unsafe_allow_html=True)

st.progress(total_done / total_all if total_all > 0 else 0)
st.markdown("<br>", unsafe_allow_html=True)

# ── Konten spesifik ─────────────────────────────────────────────────────────
if section == "listening":
    with st.expander("🎧 Audio Listening", expanded=True):
        script_text = q_data.get("script", "")
        if script_text:
            safe = script_text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
            st.markdown(f"""
            <div class="tts-container">
                <p class="tts-script"><em>"{script_text}"</em></p>
                <button class="tts-btn" onclick="speakText('{safe}')">▶ Putar Audio</button>
                <button class="tts-btn secondary" onclick="window.speechSynthesis.cancel()">■ Stop</button>
            </div>
            <script>
            function speakText(text) {{
                window.speechSynthesis.cancel();
                const u = new SpeechSynthesisUtterance(text);
                u.lang='en-US'; u.rate=0.85; u.pitch=1.0;
                window.speechSynthesis.speak(u);
            }}
            </script>""", unsafe_allow_html=True)
        else:
            st.info("Tidak ada script audio.")

elif section == "reading" and q_data.get("passage"):
    with st.expander("📖 Baca Passage", expanded=True):
        st.markdown(f'<div class="passage-box">{q_data["passage"]}</div>', unsafe_allow_html=True)

# ── Soal ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="question-box">
    <div class="question-num">Soal {idx+1}</div>
    <div class="question-text">{q_data['question']}</div>
</div>""", unsafe_allow_html=True)

current_ans = answers.get(answer_key)
for i, opt in enumerate(q_data.get("options", [])):
    if st.button(f"**{'ABCD'[i]}.** {opt}", key=f"opt_{answer_key}_{i}",
                 use_container_width=True, type="primary" if current_ans == i else "secondary"):
        st.session_state.answers[answer_key] = i
        st.rerun()

# ── Navigasi ─────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_back, _, col_next = st.columns([1, 2, 1])
answered = answer_key in st.session_state.answers

with col_back:
    if idx > 0:
        if st.button("◀ Kembali", use_container_width=True):
            st.session_state.test_idx -= 1; st.rerun()
    elif section != "listening":
        prev = SECTIONS[sec_num - 1]
        if st.button(f"◀ {SECTION_LABELS[prev]}", use_container_width=True):
            st.session_state.test_section = prev
            st.session_state.test_idx = len(questions.get(prev, [])) - 1
            st.rerun()

with col_next:
    last_in_sec = idx == total_in_section - 1
    last_sec    = section == "reading"
    label = "✅ Kumpulkan" if (last_in_sec and last_sec) else (
        f"Ke {SECTION_LABELS[SECTIONS[sec_num+1]]} ▶" if last_in_sec else "Lanjut ▶")
    if st.button(label, use_container_width=True, type="primary", disabled=not answered):
        if last_in_sec and last_sec: finish_test()
        elif last_in_sec:
            st.session_state.test_section = SECTIONS[sec_num + 1]
            st.session_state.test_idx = 0; st.rerun()
        else:
            st.session_state.test_idx += 1; st.rerun()

# Auto-refresh timer tiap 30 detik
st.markdown('<script>setTimeout(()=>window.location.reload(),30000)</script>', unsafe_allow_html=True)

# ── Sidebar peta soal ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗺️ Peta Soal")
    for sec in SECTIONS:
        sec_list = questions.get(sec, [])
        if not sec_list: continue
        st.markdown(f"**{SECTION_ICONS[sec]} {SECTION_LABELS[sec]}**")
        answered_n = sum(1 for i in range(len(sec_list)) if f"{sec}_{i}" in answers)
        st.caption(f"{answered_n}/{len(sec_list)} dijawab")
        cols = st.columns(5)
        for i in range(len(sec_list)):
            k = f"{sec}_{i}"
            icon = "🟦" if (sec == section and i == idx) else ("🟩" if k in answers else "⬜")
            cols[i % 5].markdown(icon)
        st.markdown("")
    st.markdown("---")
    total_ans = len(answers)
    st.metric("Total Dijawab", f"{total_ans}/{total_all}")
    st.progress(total_ans / total_all if total_all > 0 else 0)
