# 🎓 EPT Pro System — Fixed & Complete

Sistem latihan EPT berbasis Streamlit + Google Sheets.

---

## 📋 FORMAT GOOGLE SPREADSHEET

Buat **1 Google Spreadsheet** dengan **6 sheet** berikut (nama harus PERSIS):

### Sheet 1: `Users`
| username | password | name | role | phone |
|----------|----------|------|------|-------|
| budi | budi123 | Budi Santoso | user | 628123456789 |
| admin | admin123 | Administrator | admin | 628987654321 |

> `role` hanya boleh: `user` atau `admin`
> `phone` format internasional tanpa +, contoh: `628123456789`

---

### Sheet 2: `Questions`
*(Untuk soal manual per tanggal — opsional jika pakai Pool)*

| date | no | type | question | option_a | option_b | option_c | option_d | correct | script | passage |
|------|----|------|----------|----------|----------|----------|----------|---------|--------|---------|
| 2025-07-14 | 1 | listening | What does the man want? | Go home | Buy food | Study | Sleep | 0 | Man: I want to go home. | |
| 2025-07-14 | 1 | structure | She ___ every day. | go | goes | going | gone | 1 | | |
| 2025-07-14 | 1 | reading | What is the main idea? | Topic A | Topic B | Topic C | Topic D | 2 | | The article says... |

> `type`: `listening` / `structure` / `reading`
> `correct`: 0=A, 1=B, 2=C, 3=D
> `script`: isi untuk listening (teks yang dibacakan TTS)
> `passage`: isi untuk reading (teks bacaan)

---

### Sheet 3: `Scores`
*(Diisi OTOMATIS oleh sistem — buat sheet kosong dengan header ini)*

| username | name | date | listening | structure | reading | total | accuracy | timestamp |
|----------|------|------|-----------|-----------|---------|-------|----------|-----------|

---

### Sheet 4: `AnswerLog`
*(Diisi OTOMATIS oleh sistem — buat sheet kosong dengan header ini)*

| username | date | question_date | section | q_no | is_correct | user_answer | correct_answer | timestamp |
|----------|------|---------------|---------|------|------------|-------------|----------------|-----------|

---

### Sheet 5: `QuestionPool`
*(Diisi via upload CSV di halaman Bank Soal — buat sheet kosong dengan header ini)*

| pool_id | type | question | option_a | option_b | option_c | option_d | correct | script | passage | difficulty |
|---------|------|----------|----------|----------|----------|----------|---------|--------|---------|------------|
| L001 | listening | What does she say? | She is tired | She is hungry | She is happy | She is busy | 0 | Woman: I'm so tired. | | easy |

> `pool_id`: ID unik, contoh L001 (Listening), S001 (Structure), R001 (Reading)
> `difficulty`: `easy` / `medium` / `hard`

---

### Sheet 6: `DailyDraw`
*(Diisi OTOMATIS oleh sistem — buat sheet kosong dengan header ini)*

| date | pool_id | no | type |
|------|---------|----|------|

---

## ⚙️ SETUP LANGKAH PER LANGKAH

### 1. Clone / Download
```bash
git clone https://github.com/username/ept-system.git
cd ept-system
pip install -r requirements.txt
```

### 2. Buat Google Spreadsheet
- Buat spreadsheet baru di Google Drive
- Buat 6 sheet dengan nama PERSIS seperti di atas
- Isi header masing-masing sheet (copy dari tabel di atas)
- Salin **ID spreadsheet** dari URL

### 3. Google Cloud Service Account
1. Buka https://console.cloud.google.com
2. Buat/pilih project → aktifkan **Google Sheets API** dan **Google Drive API**
3. IAM & Admin → Service Accounts → Create → buat key (JSON)
4. Download file JSON → isinya nanti disalin ke secrets.toml
5. **Share** spreadsheet ke email service account (beri akses **Editor**)

### 4. Isi secrets.toml
Edit file `.streamlit/secrets.toml`:
```toml
[spreadsheet]
id = "ID_SPREADSHEET_KAMU"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = """-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----"""
client_email = "...@....iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."

[whatsapp]
token = "TOKEN_DARI_FONNTE.COM"
admin_number = "628123456789"
```

### 5. Setup WhatsApp (Fonnte)
1. Daftar di https://fonnte.com (gratis)
2. Add Device → scan QR dengan HP yang akan jadi pengirim WA
3. Salin token → isi di secrets.toml bagian `[whatsapp]`

### 6. Tambah User Pertama (Admin)
Isi sheet `Users` secara manual untuk akun pertama:
```
username: admin
password: admin123
name: Administrator
role: admin
phone: 628xxx (opsional)
```

### 7. Import Bank Soal
1. Jalankan aplikasi: `streamlit run app.py`
2. Login sebagai admin
3. Buka halaman **🎲 Bank Soal**
4. Tab "Import Soal" → upload `BANK_SOAL_EPT_LENGKAP.csv`
5. Tab "Konfigurasi Draw" → klik **"Buat Draw Baru untuk Hari Ini"**

### 8. Jalankan
```bash
streamlit run app.py
```

---

## 🚀 Deploy ke Streamlit Cloud (Gratis)
1. Push kode ke GitHub (**TANPA** file secrets.toml)
2. Buka https://share.streamlit.io
3. Connect repo → Main file: `app.py`
4. Advanced settings → Secrets → paste isi secrets.toml
5. Deploy!

---

## 📊 Alur Penggunaan Harian

**Admin (setiap pagi):**
1. Login → halaman 🎲 Bank Soal
2. Klik "Buat Draw Baru" → sistem pilih 45 soal acak
3. Kirim notifikasi WA ke semua user via halaman ⚙️ Admin

**User:**
1. Terima notifikasi WA
2. Login → klik "Mulai Simulasi"
3. Kerjakan 45 soal (90 menit)
4. Lihat hasil + terima WA hasil otomatis

