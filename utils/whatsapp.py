"""
utils/whatsapp.py — Kirim notifikasi WhatsApp via Fonnte API.

Fonnte adalah layanan WhatsApp gateway gratis untuk Indonesia.
Daftar di https://fonnte.com dan dapatkan token device kamu.

Tambahkan ke .streamlit/secrets.toml:
  [whatsapp]
  token = "TOKEN_FONNTE_KAMU"
  admin_number = "6283164090690"    # nomor WA admin (format internasional)
"""

import streamlit as st
import requests
from datetime import date


def _send_wa(target: str, message: str) -> bool:
    """
    Kirim pesan WhatsApp ke nomor target.
    target: format internasional tanpa '+', contoh '628123456789'
    Kembalikan True jika berhasil.
    """
    try:
        token = st.secrets.get("whatsapp", {}).get("token", "")
        if not token:
            # Jika token belum diisi, skip silently (tidak error)
            return False

        resp = requests.post(
            "https://api.fonnte.com/send",
            headers={"Authorization": token},
            data={"target": target, "message": message},
            timeout=10,
        )
        result = resp.json()
        return result.get("status", False)
    except Exception as e:
        print(f"[WA Error] {e}")
        return False


# ── Pesan-pesan notifikasi ──────────────────────────────────────────────────

def notify_admin_soal_belum_ada(admin_number: str = None):
    """Kirim WA ke admin jika soal hari ini belum diisi."""
    if admin_number is None:
        admin_number = st.secrets.get("whatsapp", {}).get("admin_number", "")
    if not admin_number:
        return False

    today = date.today().strftime("%d %B %Y")
    msg = (
        f"⚠️ *EPT Pro System — Pengingat Soal*\n\n"
        f"Halo Admin! 👋\n\n"
        f"Soal untuk hari ini (*{today}*) belum diisi di sistem EPT.\n\n"
        f"Silakan login ke panel admin dan tambahkan 45 soal "
        f"(15 Listening + 15 Structure + 15 Reading) sebelum peserta mulai berlatih.\n\n"
        f"🔗 Akses sistem: _[link aplikasi kamu]_\n\n"
        f"_Pesan otomatis dari EPT Pro System_ 🎓"
    )
    return _send_wa(admin_number, msg)


def notify_user_reminder(user_number: str, user_name: str):
    """Kirim WA pengingat harian ke user."""
    today = date.today().strftime("%d %B %Y")
    msg = (
        f"🎓 *EPT Pro — Pengingat Latihan Harian*\n\n"
        f"Halo *{user_name}*! 👋\n\n"
        f"Jangan lupa latihan EPT hari ini (*{today}*)! "
        f"Soal baru sudah tersedia di sistem.\n\n"
        f"Konsistensi adalah kunci sukses. Yuk latihan sekarang! 💪\n\n"
        f"_Pesan otomatis dari EPT Pro System_ 🎓"
    )
    return _send_wa(user_number, msg)


def notify_user_result(user_number: str, user_name: str, listening: int, structure: int, reading: int):
    """Kirim WA ke user berisi hasil tes setelah selesai."""
    total = listening + structure + reading
    accuracy = round((total / 45) * 100, 1)

    if accuracy >= 85:
        grade, emoji = "A", "🏆"
    elif accuracy >= 70:
        grade, emoji = "B", "🎯"
    elif accuracy >= 55:
        grade, emoji = "C", "📈"
    else:
        grade, emoji = "D", "💪"

    today = date.today().strftime("%d %B %Y")
    msg = (
        f"{emoji} *Hasil Simulasi EPT — {today}*\n\n"
        f"Halo *{user_name}*! Berikut hasil latihanmu:\n\n"
        f"🎧 Listening  : *{listening}/15*\n"
        f"📐 Structure  : *{structure}/15*\n"
        f"📖 Reading    : *{reading}/15*\n"
        f"──────────────────\n"
        f"📊 Total      : *{total}/45*\n"
        f"✅ Akurasi    : *{accuracy}%*\n"
        f"🎓 Grade      : *{grade}*\n\n"
        f"Terus semangat berlatih! Sampai besok 🌟\n\n"
        f"_EPT Pro System_ 🎓"
    )
    return _send_wa(user_number, msg)


def notify_admin_daily_summary(admin_number: str, participants: int, avg_score: float, top_name: str, top_score: int):
    """Kirim ringkasan harian ke admin (dipanggil manual dari admin panel)."""
    if not admin_number:
        admin_number = st.secrets.get("whatsapp", {}).get("admin_number", "")
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
