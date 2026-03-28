"""pages/3_Test.py — Halaman simulasi EPT."""

import streamlit as st
from utils.session import init_session
from utils.sheets import save_score

st.set_page_config(page_title="Simulasi EPT", page_icon="📝", layout="centered")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

if not st.session_state.get("test_active"):
    st.switch_page("pages/1_Dashboard.py")

SECTIONS = ["listening", "structure", "reading"]
SECTION_ICONS = {"listening": "🎧", "structure": "📐", "reading": "📖"}
SECTION_LABELS = {"listening": "Listening", "structure": "Structure", "reading": "Reading"}

username = st.session_state.username
name = st.session_state.name
section = st.session_state.test_section
idx = st.session_state.test_idx
questions_today = st.session_state.questions_today
answers = st.session_state.answers


# ── Selesai semua bagian ────────────────────────────────────────────────────
def finish_test():
    qs = st.session_state.questions_today
    score_l = score_s = score_r = 0

    for i, q in enumerate(qs.get("listening", [])):
        if answers.get(f"listening_{i}") == q["correct"]:
            score_l += 1
    for i, q in enumerate(qs.get("structure", [])):
        if answers.get(f"structure_{i}") == q["correct"]:
            score_s += 1
    for i, q in enumerate(qs.get("reading", [])):
        if answers.get(f"reading_{i}") == q["correct"]:
            score_r += 1

    save_score(username, name, score_l, score_s, score_r)
    st.session_state.last_score = {"listening": score_l, "structure": score_s, "reading": score_r}
    st.session_state.test_active = False
    st.switch_page("pages/4_Result.py")


# ── Ambil list soal sesi ini ────────────────────────────────────────────────
current_list = questions_today.get(section, [])
if not current_list:
    st.error(f"Tidak ada soal untuk bagian {section}.")
    st.stop()

total_in_section = len(current_list)
q_data = current_list[idx]
answer_key = f"{section}_{idx}"

# ── Progress bar ────────────────────────────────────────────────────────────
section_num = SECTIONS.index(section)
total_done = sum(len(questions_today.get(s, [])) for s in SECTIONS[:section_num]) + idx
total_all = sum(len(questions_today.get(s, [])) for s in SECTIONS)
progress = total_done / total_all if total_all > 0 else 0

st.markdown(f"""
<div class="test-header">
    <div class="test-section-badge">{SECTION_ICONS[section]} {SECTION_LABELS[section]}</div>
    <div class="test-progress-label">Soal {idx+1} / {total_in_section} &nbsp;·&nbsp; Total {total_done+1}/{total_all}</div>
</div>
""", unsafe_allow_html=True)

st.progress(progress)
st.markdown("<br>", unsafe_allow_html=True)

# ── Konten spesifik bagian ──────────────────────────────────────────────────
if section == "listening":
    with st.expander("🎧 Putar Audio (TTS via Browser)", expanded=True):
        script_text = q_data.get("script", "")
        if script_text:
            # TTS via HTML5 + Web Speech API (browser native, tidak perlu API key)
            safe_text = script_text.replace("'", "\\'").replace('"', '\\"')
            st.markdown(f"""
            <div class="tts-container">
                <p class="tts-script"><em>"{script_text}"</em></p>
                <button class="tts-btn" onclick="speakText('{safe_text}')">▶ Putar Audio</button>
                <button class="tts-btn secondary" onclick="window.speechSynthesis.cancel()">■ Stop</button>
            </div>
            <script>
            function speakText(text) {{
                window.speechSynthesis.cancel();
                const utter = new SpeechSynthesisUtterance(text);
                utter.lang = 'en-US';
                utter.rate = 0.85;
                utter.pitch = 1.0;
                window.speechSynthesis.speak(utter);
            }}
            </script>
            """, unsafe_allow_html=True)
        else:
            st.warning("Tidak ada script audio untuk soal ini.")

elif section == "reading":
    if q_data.get("passage"):
        with st.expander("📖 Baca Passage", expanded=True):
            st.markdown(f"""
            <div class="passage-box">
                <p>{q_data['passage']}</p>
            </div>
            """, unsafe_allow_html=True)

# ── Pertanyaan & Pilihan ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="question-box">
    <div class="question-text">{idx+1}. {q_data['question']}</div>
</div>
""", unsafe_allow_html=True)

options = q_data.get("options", ["", "", "", ""])
current_answer = answers.get(answer_key)

opt_labels = ["A", "B", "C", "D"]
for i, opt in enumerate(options):
    selected = current_answer == i
    btn_class = "option-btn selected" if selected else "option-btn"
    if st.button(
        f"**{opt_labels[i]}.** {opt}",
        key=f"opt_{answer_key}_{i}",
        use_container_width=True,
        type="primary" if selected else "secondary",
    ):
        st.session_state.answers[answer_key] = i
        st.rerun()

# ── Navigasi ─────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_back, col_spacer, col_next = st.columns([1, 2, 1])

with col_back:
    if idx > 0:
        if st.button("◀ Kembali", use_container_width=True):
            st.session_state.test_idx -= 1
            st.rerun()
    elif section != "listening":
        prev_section = SECTIONS[SECTIONS.index(section) - 1]
        prev_count = len(questions_today.get(prev_section, []))
        if st.button(f"◀ Kembali ke {SECTION_LABELS[prev_section]}", use_container_width=True):
            st.session_state.test_section = prev_section
            st.session_state.test_idx = prev_count - 1
            st.rerun()

with col_next:
    answered = answer_key in st.session_state.answers
    is_last_in_section = idx == total_in_section - 1
    is_last_section = section == "reading"

    if is_last_in_section and is_last_section:
        label = "✅ Selesai & Lihat Nilai"
    elif is_last_in_section:
        next_sec = SECTIONS[SECTIONS.index(section) + 1]
        label = f"Lanjut ke {SECTION_LABELS[next_sec]} ▶"
    else:
        label = "Lanjut ▶"

    if st.button(label, use_container_width=True, type="primary", disabled=not answered):
        if is_last_in_section and is_last_section:
            finish_test()
        elif is_last_in_section:
            st.session_state.test_section = SECTIONS[SECTIONS.index(section) + 1]
            st.session_state.test_idx = 0
            st.rerun()
        else:
            st.session_state.test_idx += 1
            st.rerun()

# ── Sidebar: Peta soal ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗺️ Peta Soal")
    for sec in SECTIONS:
        sec_list = questions_today.get(sec, [])
        st.markdown(f"**{SECTION_ICONS[sec]} {SECTION_LABELS[sec]}**")
        cols = st.columns(5)
        for i in range(len(sec_list)):
            k = f"{sec}_{i}"
            done = k in answers
            active = sec == section and i == idx
            label = f"**{i+1}**" if active else (f"~~{i+1}~~" if done else str(i+1))
            cols[i % 5].markdown(label)
        st.markdown("")
