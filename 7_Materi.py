"""pages/7_Materi.py — Bank materi & tips belajar EPT."""

import streamlit as st
from utils.session import init_session
from utils.auth import logout

st.set_page_config(page_title="Materi Belajar — EPT Pro", page_icon="📚", layout="wide")

with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session()
if not st.session_state.get("logged_in"):
    st.switch_page("app.py")

c1, _, c3 = st.columns([1, 4, 1])
with c1: st.markdown('<span class="nav-logo">📚 Materi</span>', unsafe_allow_html=True)
with c3:
    if st.button("Keluar"): logout()
st.markdown("---")

st.markdown("## 📚 Bank Materi & Tips Belajar EPT")

tab_l, tab_s, tab_r, tab_tips = st.tabs(["🎧 Listening", "📐 Structure", "📖 Reading", "💡 Tips & Strategi"])

# ── LISTENING ───────────────────────────────────────────────────────────────
with tab_l:
    st.markdown("""
    ### 🎧 Strategi Listening EPT

    Bagian Listening menguji kemampuanmu memahami percakapan dan monolog dalam bahasa Inggris.

    #### Tipe Soal Umum:
    - **Short Conversation** — dialog pendek antara 2 orang
    - **Long Conversation** — percakapan lebih panjang (3-5 pertukaran)
    - **Short Talk / Monologue** — pengumuman, ceramah singkat

    #### Tips Menjawab:
    1. **Baca soal sebelum audio diputar** — ketahui apa yang harus diperhatikan
    2. **Fokus pada kata kunci** — siapa, apa, di mana, kapan, mengapa
    3. **Perhatikan intonasi** — nada bicara menunjukkan emosi dan maksud
    4. **Jangan terjebak distractor** — jawaban salah sering memakai kata dari audio
    5. **Pilih jawaban, lanjutkan** — jangan terlalu lama di satu soal

    #### Ekspresi Penting:
    """)

    expressions = {
        "Setuju": ["That's right.", "Exactly!", "I couldn't agree more.", "You're absolutely right."],
        "Tidak Setuju": ["I don't think so.", "Actually...", "On the contrary...", "I beg to differ."],
        "Saran": ["Why don't you...?", "You should...", "How about...?", "I suggest..."],
        "Permintaan": ["Could you...?", "Would you mind...?", "Can I...?", "I was wondering if..."],
    }
    for cat, exps in expressions.items():
        with st.expander(f"💬 {cat}"):
            for e in exps:
                st.markdown(f"- *{e}*")

    st.markdown("""
    #### Sumber Latihan Mandiri:
    - 🎙️ [BBC Learning English](https://www.bbc.co.uk/learningenglish)
    - 🎙️ [VOA Learning English](https://learningenglish.voanews.com)
    - 🎵 Tonton film/series berbahasa Inggris dengan subtitle Inggris
    - 🎧 Podcast: *English Pod*, *6 Minute English*, *Stuff You Should Know*
    """)

# ── STRUCTURE ────────────────────────────────────────────────────────────────
with tab_s:
    st.markdown("### 📐 Materi Grammar — Structure EPT")

    tenses = {
        "Simple Present": ("I work every day.", "S + V1/V1s"),
        "Present Continuous": ("She is working now.", "S + is/am/are + V-ing"),
        "Simple Past": ("He worked yesterday.", "S + V2"),
        "Past Continuous": ("They were working when I called.", "S + was/were + V-ing"),
        "Present Perfect": ("I have finished my homework.", "S + has/have + V3"),
        "Past Perfect": ("She had left before he arrived.", "S + had + V3"),
        "Simple Future": ("We will go tomorrow.", "S + will + V1"),
        "Future Continuous": ("I will be studying at 8 PM.", "S + will be + V-ing"),
    }

    st.markdown("#### ⏰ 16 Tenses — Yang Paling Sering Keluar")
    for tense, (ex, pattern) in tenses.items():
        with st.expander(f"**{tense}**"):
            st.markdown(f"**Pattern:** `{pattern}`")
            st.markdown(f"**Contoh:** *{ex}*")

    st.markdown("---")
    st.markdown("#### 📌 Topik Grammar Penting Lainnya")

    grammar_topics = {
        "Subject-Verb Agreement": """
- Singular subject → singular verb: *The boy **runs** fast.*
- Plural subject → plural verb: *The boys **run** fast.*
- **Everyone, someone, nobody** → singular verb
- **Either/Neither + nor/or** → verb mengikuti subject terdekat
        """,
        "Conditional Sentences": """
| Tipe | Rumus | Contoh |
|------|-------|--------|
| 0 (Fakta) | If + S1, S + V1 | If water boils, it evaporates. |
| 1 (Possible) | If + S1, S + will + V1 | If it rains, I will stay home. |
| 2 (Unreal present) | If + S2, S + would + V1 | If I were rich, I would travel. |
| 3 (Unreal past) | If + S3 (had+V3), S + would have + V3 | If I had studied, I would have passed. |
        """,
        "Passive Voice": """
- Active: *The teacher **explains** the lesson.*
- Passive: *The lesson **is explained** by the teacher.*
- Rumus: S + to be + V3 (+ by + agent)
        """,
        "Relative Clauses": """
- **who/that** → untuk orang: *The man **who** called me is my uncle.*
- **which/that** → untuk benda: *The book **which** I read was interesting.*
- **whose** → kepunyaan: *The girl **whose** bag I found is Maria.*
- **where** → tempat: *The city **where** I was born is Surabaya.*
        """,
    }
    for topic, content in grammar_topics.items():
        with st.expander(f"📖 {topic}"):
            st.markdown(content)

# ── READING ─────────────────────────────────────────────────────────────────
with tab_r:
    st.markdown("""
    ### 📖 Strategi Reading EPT

    #### Tipe Pertanyaan:
    - **Main Idea** — Apa ide pokok passage?
    - **Detail** — Fakta spesifik dalam teks
    - **Inference** — Kesimpulan yang tersirat
    - **Vocabulary in Context** — Makna kata dalam konteks
    - **Author's Purpose** — Mengapa teks ini ditulis?

    #### Teknik Membaca:
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **🔍 Skimming** (Membaca Cepat)
        Baca hanya kalimat pertama & terakhir tiap paragraf untuk menangkap ide utama.
        Gunakan untuk: soal main idea, topic.
        """)
    with col2:
        st.markdown("""
        **🎯 Scanning** (Mencari Detail)
        Cari kata kunci spesifik tanpa membaca seluruh teks.
        Gunakan untuk: soal detail, angka, nama, tanggal.
        """)

    st.markdown("""
    #### Strategi Menjawab:
    1. Baca pertanyaan **sebelum** membaca passage
    2. Tandai kata kunci di soal
    3. Temukan bagian relevan di teks (scanning)
    4. Eliminasi jawaban yang jelas salah
    5. Pilih jawaban yang **paling sesuai teks**, bukan opinimu

    #### Kosakata Akademik yang Sering Keluar:
    """)
    vocab = {
        "analyze": "menganalisis", "significant": "signifikan/penting",
        "imply": "menyiratkan", "contrast": "bertentangan",
        "emphasize": "menekankan", "consequently": "akibatnya",
        "whereas": "sementara/padahal", "nevertheless": "namun demikian",
        "furthermore": "lebih jauh lagi", "hypothesis": "hipotesis",
    }
    cols = st.columns(2)
    for i, (word, meaning) in enumerate(vocab.items()):
        cols[i%2].markdown(f"- **{word}** = *{meaning}*")

# ── TIPS UMUM ────────────────────────────────────────────────────────────────
with tab_tips:
    st.markdown("### 💡 Tips & Strategi Umum EPT")

    st.markdown("""
    #### 📅 Jadwal Belajar Ideal (30 menit/hari)
    | Hari | Fokus |
    |------|-------|
    | Senin | Listening — short conversation |
    | Selasa | Grammar — tenses & agreement |
    | Rabu | Reading — main idea & inference |
    | Kamis | Vocabulary building |
    | Jumat | Simulasi penuh (45 soal) |
    | Sabtu | Review jawaban salah |
    | Minggu | Istirahat / review ringan |
    """)

    st.markdown("---")
    st.markdown("""
    #### ⏱️ Manajemen Waktu saat Tes
    - Total: **90 menit** untuk 45 soal = **2 menit/soal**
    - Listening: ~20 menit (15 soal)
    - Structure: ~25 menit (15 soal)
    - Reading: ~45 menit (15 soal)

    #### 🎯 Strategi Eliminasi
    1. Coret jawaban yang jelas salah (biasanya ada 1-2)
    2. Dari sisa 2-3 pilihan, cari yang paling spesifik sesuai konteks
    3. **Jangan biarkan kosong** — tidak ada pengurangan nilai

    #### 🧠 Mindset Mengerjakan Soal
    - Jika ragu, **tandai dan lanjut** — jangan terjebak satu soal
    - Percayai insting pertamamu untuk multiple choice
    - Tenang dan bernapas — panik menurunkan performa

    #### 📱 Aplikasi Pendukung
    - **Duolingo** — vocab harian & gamified learning
    - **Grammarly** — cek grammar tulisanmu
    - **Quizlet** — flashcard kosakata
    - **BBC Learning English App** — listening practice
    """)

    st.success("""
    💪 **Ingat:** Konsistensi lebih penting dari intensitas.
    Latihan 30 menit setiap hari lebih efektif dari belajar 5 jam sekali seminggu!
    """)
