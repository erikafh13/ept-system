# 🎓 EPT Pro System

Sistem latihan **English Proficiency Test (EPT)** berbasis **Streamlit** dengan **Google Sheets** sebagai database soal dan nilai. Dirancang untuk pengelolaan soal harian, mode admin & user, serta tracker progress otomatis.

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 🔐 Login Multi-Role | Sistem login dengan peran **Admin** dan **User** |
| 📅 Soal Harian | Admin mengganti 45 soal setiap hari via Google Sheets |
| 🎧 Audio Listening | TTS otomatis via Web Speech API browser (tanpa API key berbayar) |
| 📊 Progress Tracker | Grafik perkembangan skor harian per user |
| 🏆 Leaderboard | Peringkat nilai harian untuk semua user |
| ⬇️ Export CSV | User & admin dapat mengunduh riwayat nilai |
| 📤 Bulk Upload | Admin bisa upload banyak soal sekaligus via CSV |

---

## 🗂️ Struktur Proyek

```
ept-system/
│
├── app.py                    # Entry point & routing login
├── requirements.txt          # Dependensi Python
├── .gitignore
│
├── pages/
│   ├── 1_Dashboard.py        # Dashboard user (statistik, mulai tes)
│   ├── 2_Admin.py            # Panel admin (kelola soal, nilai, user)
│   ├── 3_Test.py             # Halaman simulasi soal
│   └── 4_Result.py           # Halaman hasil & skor
│
├── utils/
│   ├── __init__.py
│   ├── session.py            # Manajemen session state
│   ├── auth.py               # Login & logout logic
│   └── sheets.py             # Semua interaksi Google Sheets
│
├── assets/
│   └── style.css             # CSS global (font, warna, komponen)
│
└── .streamlit/
    ├── config.toml           # Konfigurasi tema Streamlit
    └── secrets.toml          # ⚠️ RAHASIA — tidak di-commit ke Git
```

---

## 🗃️ Struktur Google Spreadsheet

Buat **1 Google Spreadsheet** dengan **3 sheet** berikut:

### Sheet 1: `Users`
| username | password | name | role |
|----------|----------|------|------|
| budi123 | pass123 | Budi Santoso | user |
| admin | adminpass | Administrator | admin |

### Sheet 2: `Questions`
| date | no | type | question | option_a | option_b | option_c | option_d | correct | script | passage |
|------|----|------|----------|----------|----------|----------|----------|---------|--------|---------|
| 2025-07-14 | 1 | listening | What does the man want? | Go home | Buy food | Study | Sleep | 0 | Man: I want to go home. | |
| 2025-07-14 | 1 | structure | She ___ to school every day. | go | goes | going | gone | 1 | | |
| 2025-07-14 | 1 | reading | What is the main idea? | Topic A | Topic B | Topic C | Topic D | 2 | | The article discusses... |

> **Keterangan kolom `correct`:** `0` = A, `1` = B, `2` = C, `3` = D  
> **Kolom `script`:** Diisi untuk soal listening (teks yang dibacakan TTS)  
> **Kolom `passage`:** Diisi untuk soal reading (teks bacaan)

### Sheet 3: `Scores`
*(Diisi otomatis oleh sistem, tidak perlu diisi manual)*
| username | name | date | listening | structure | reading | total | accuracy | timestamp |
|----------|------|------|-----------|-----------|---------|-------|----------|-----------|

---

## ⚙️ Setup & Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/username/ept-system.git
cd ept-system
```

### 2. Install Dependensi
```bash
pip install -r requirements.txt
```

### 3. Buat Google Cloud Service Account

1. Buka [Google Cloud Console](https://console.cloud.google.com)
2. Buat project baru (atau gunakan yang sudah ada)
3. Aktifkan **Google Sheets API** dan **Google Drive API**
4. Buat **Service Account** → buat key → download file `.json`
5. Salin isi file `.json` ke `.streamlit/secrets.toml` (lihat contoh di bawah)

### 4. Share Google Spreadsheet ke Service Account

- Buka Google Spreadsheet kamu
- Klik **Share** → tambahkan email service account (format: `nama@project.iam.gserviceaccount.com`)
- Beri akses **Editor**

### 5. Isi File Secrets

Buat file `.streamlit/secrets.toml` (jangan di-commit ke Git!):

```toml
[spreadsheet]
id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"  # ID dari URL spreadsheet

[gcp_service_account]
type = "service_account"
project_id = "nama-project-kamu"
private_key_id = "abc123..."
private_key = """-----BEGIN RSA PRIVATE KEY-----
... isi private key ...
-----END RSA PRIVATE KEY-----"""
client_email = "service-account@project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```

> 💡 **ID Spreadsheet** bisa ditemukan di URL:  
> `https://docs.google.com/spreadsheets/d/`**`INI_ADALAH_ID`**`/edit`

### 6. Jalankan Aplikasi
```bash
streamlit run app.py
```

---

## 👤 Cara Login Pertama Kali

Setelah setup, tambahkan user pertama (admin) langsung ke sheet `Users`:

| username | password | name | role |
|----------|----------|------|------|
| admin | admin123 | Administrator | admin |

Lalu login dengan username `admin` dan password `admin123`.

---

## 📋 Alur Penggunaan Harian (Admin)

1. **Setiap pagi**, admin masuk ke panel Admin → tab **Kelola Soal**
2. Pilih tanggal hari ini
3. Input 45 soal (15 Listening + 15 Structure + 15 Reading), atau
4. Upload sekaligus via **CSV** menggunakan template yang tersedia
5. User bisa mulai tes hari itu

---

## 📦 Upload Soal via CSV (Cara Cepat)

1. Download template CSV dari halaman Admin
2. Isi soal di Excel/Google Sheets
3. Export sebagai `.csv`
4. Upload di panel Admin → tab Kelola Soal

**Format wajib:**
```
date,no,type,question,option_a,option_b,option_c,option_d,correct,script,passage
2025-07-14,1,listening,What does the man say?,He is tired,He is hungry,He is happy,He is busy,0,Man: I'm really tired today.,
```

---

## 🚀 Deploy ke Streamlit Cloud (Gratis)

1. Push kode ke GitHub (pastikan **tidak** ada `secrets.toml`)
2. Buka [share.streamlit.io](https://share.streamlit.io)
3. Connect repository GitHub kamu
4. Set **Main file path**: `app.py`
5. Di **Advanced settings → Secrets**, paste isi `secrets.toml` kamu
6. Deploy!

---

## 🛡️ Keamanan

- ✅ File `secrets.toml` sudah masuk `.gitignore` — tidak akan terupload ke GitHub
- ✅ Password user disimpan di Google Sheets (untuk produksi, disarankan pakai hashing)
- ✅ Akses admin divalidasi di setiap halaman admin
- ⚠️ Untuk keamanan lebih, gunakan password hashing (bcrypt) di `utils/auth.py`

---

## 🤝 Kontribusi

Pull request dan issue sangat disambut! Untuk perubahan besar, buka issue terlebih dahulu.

---

## 📄 Lisensi

MIT License — bebas digunakan dan dimodifikasi.
