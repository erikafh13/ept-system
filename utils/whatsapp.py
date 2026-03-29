"""
utils/whatsapp.py — Kirim notifikasi WhatsApp via Fonnte API.

Fonnte adalah layanan WhatsApp gateway gratis untuk Indonesia.
Daftar di https://fonnte.com → hubungkan HP → salin token.

Tambahkan ke .streamlit/secrets.toml:
  [whatsapp]
  token        = "TOKEN_FONNTE_KAMU"
  admin_number = "628123456789"
"""

import streamlit as st
import requests
from datetime import date


def _get_wa_config() -> dict:
    """
    Ambil konfigurasi WA dari secrets dengan aman.
    FIX: st.secrets tidak punya method .get() seperti dict biasa,
    harus pakai try/except atau akses langsung dengan key check.
    """
    try:
        return {
            "token":        st.secrets["whatsapp"]["token"],
            "admin_number": st.secrets["whatsapp"]["admin_number"],
        }
    except (KeyError, Exception):
        return {"token": "", "admin_number": ""}


def _send_wa(target: str, message: str) -> bool:
    """
    Kirim pesan WhatsApp ke nomor target via Fonnte API.
    target : format internasional tanpa '+', contoh '628123456789'
    Return : True jika berhasil, False jika gagal.
    """
    if not target:
        return False

    cfg   = _get_wa_config()
    token = cfg.get("token", "")
    if not token:
        return False

    try:
        resp = requests.post(
            "https://api.fonnte.com/send",
            headers={"Authorization": token},
            data={"target": target, "message": message},
            timeout=10,
        )
        result = resp.json()
        # Fonnte mengembalikan {"status": true/false, ...}
        return bool(result.get("status", False))
    except Exception as e:
        print(f"[WA Error] {e}")
        return False


# ── Fungsi notifikasi ─────────────────────────────────────────────────────────

def notify_admin_soal_belum_ada(admin_number: str = None) -> bool:
    """Kirim WA ke admin jika soal hari ini belum diisi."""
    if not admin_number:
        admin_number = _get_wa_config().get("admin_number", "")
    if not admin_number:
        return False

    today = date.today().strftime("%d %B %Y")
    msg = (
        f"⚠️ *EPT Pro System — Pengingat Soal*\n\n"
        f"Halo Admin! 👋\n\n"
        f"Soal untuk hari ini (*{today}*) belum tersedia di sistem EPT.\n\n"
        f"Silakan login ke panel admin dan lakukan *Draw Soal Harian* "
        f"atau tambahkan 45 soal manual (15 Listening + 15 Structure + 15 Reading).\n\n"
        f"_Pesan otomatis dari EPT Pro System_ 🎓"
    )
    return _send_wa(admin_number, msg)


def notify_user_reminder(user_number: str, user_name: str) -> bool:
    """Kirim WA pengingat latihan harian ke user."""
    today = date.today().strftime("%d %B %Y")
    msg = (
        f"🎓 *EPT Pro — Pengingat Latihan Harian*\n\n"
        f"Halo *{user_name}*! 👋\n\n"
        f"Jangan lupa latihan EPT hari ini (*{today}*)!\n"
        f"Soal baru sudah tersedia di sistem.\n\n"
        f"Konsistensi adalah kunci sukses. Yuk latihan sekarang! 💪\n\n"
        f"_Pesan otomatis dari EPT Pro System_ 🎓"
    )
    return _send_wa(user_number, msg)


def notify_user_result(user_number: str, user_name: str,
                       listening: int, structure: int, reading: int) -> bool:
    """Kirim WA hasil tes ke user setelah selesai simulasi."""
    total    = listening + structure + reading
    accuracy = round((total / 45) * 100, 1)

    if   accuracy >= 85: grade, emoji = "A", "🏆"
    elif accuracy >= 70: grade, emoji = "B", "🎯"
    elif accuracy >= 55: grade, emoji = "C", "📈"
    else:                grade, emoji = "D", "💪"

    today = date.today().strftime("%d %B %Y")
    msg = (
        f"{emoji} *Hasil Simulasi EPT — {today}*\n\n"
        f"Halo *{user_name}*! Berikut hasil latihanmu:\n\n"
        f"🎧 Listening : *{listening}/15*\n"
        f"📐 Structure : *{structure}/15*\n"
        f"📖 Reading   : *{reading}/15*\n"
        f"─────────────────\n"
        f"📊 Total     : *{total}/45*\n"
        f"✅ Akurasi   : *{accuracy}%*\n"
        f"🎓 Grade     : *{grade}*\n\n"
        f"Terus semangat berlatih! Sampai besok 🌟\n\n"
        f"_EPT Pro System_ 🎓"
    )
    return _send_wa(user_number, msg)


def notify_admin_daily_summary(participants: int, avg_score: float,
                                top_name: str, top_score: int,
                                admin_number: str = None) -> bool:
    """
    Kirim ringkasan harian ke admin.
    FIX: admin_number sekarang opsional, diambil dari secrets jika tidak diisi.
    """
    if not admin_number:
        admin_number = _get_wa_config().get("admin_number", "")
    if not admin_number:
        return False

    today = date.today().strftime("%d %B %Y")
    msg = (
        f"📋 *Ringkasan Harian EPT — {today}*\n\n"
        f"👥 Peserta hari ini : *{participants} orang*\n"
        f"📊 Rata-rata skor   : *{avg_score:.1f}/45*\n"
        f"🏆 Skor tertinggi   : *{top_name}* ({top_score}/45)\n\n"
        f"_Laporan otomatis EPT Pro System_ 🎓"
    )
    return _send_wa(admin_number, msg)
