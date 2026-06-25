# SPMB Jatim Scraper dan Simulasi Peringkat PPDB 2026

Aplikasi berbasis web menggunakan Streamlit (Python) untuk melakukan penarikan data (scraping) hasil pemeringkatan akademik SMA Negeri di Surabaya (Jalur Prestasi Akademik Lulusan 2026) secara real-time dan mensimulasikan posisi peringkat berdasarkan nilai yang diinput.

## Fitur Utama
1. **Scraping Real-time**: Menarik data langsung dari API resmi spmbjatim.net secara langsung (terhindar dari masalah CORS di browser).
2. **Simulasi Peringkat Mandiri**: Masukkan nilai akademik Anda (default: 87.36) dan sistem akan menghitung posisi peringkat Anda secara otomatis di 6 sekolah target secara berdampingan.
3. **Kartu Peluang Kelulusan**: Menampilkan indikator persaingan:
   - Peluang Sangat Aman (Top 40%)
   - Bersaing Ketat (Top 40% - 80%)
   - Di Luar Zona Aman (>80%)
4. **Grafik Metrik Sekolah**: Perbandingan visual antara Nilai Anda, Rata-rata Sekolah, Nilai Terendah, dan Nilai Tertinggi di masing-masing sekolah.
5. **Tabel Detail dan Highlight**: Menampilkan data seluruh siswa pendaftar asli dan menyisipkan baris "SIMULASI ANDA" dengan highlight warna kuning stabilo berdaya kontras tinggi.
6. **Ekspor CSV**: Unduh data pendaftar asli per sekolah dalam format CSV untuk kebutuhan analisis lebih lanjut.

## Sekolah Target (Surabaya)
1. SMAN 1 Surabaya (ID: 177)
2. SMAN 2 Surabaya (ID: 178)
3. SMAN 5 Surabaya (ID: 179)
4. SMAN 6 Surabaya (ID: 182)
5. SMAN 15 Surabaya (ID: 194)
6. SMAN 16 Surabaya (ID: 188)

---

## Cara Menjalankan di Lokal

### 1. Persyaratan Sistem
Pastikan Anda sudah menginstal Python (versi 3.8 ke atas) di komputer Anda.

### 2. Instalasi Dependensi
Jalankan perintah berikut di terminal Anda:
```bash
# Buat virtual environment (opsional tapi disarankan)
python -m venv venv

# Aktifkan virtual environment
# Untuk Mac/Linux:
source venv/bin/activate
# Untuk Windows (CMD):
venv\Scripts\activate.bat
# Untuk Windows (PowerShell):
venv\Scripts\Activate.ps1

# Instal dependensi
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi
Setelah dependensi terinstal, jalankan perintah berikut:
```bash
streamlit run app.py
```
Aplikasi secara otomatis akan terbuka di browser Anda pada alamat http://localhost:8501.

---

## Cara Hosting Gratis di Streamlit Cloud
1. Pastikan kode Anda sudah di-push ke repositori GitHub Anda (misalnya https://github.com/abyansyah052/spmb-scrap.git).
2. Kunjungi Streamlit Community Cloud (https://streamlit.io/cloud) dan login menggunakan akun GitHub Anda.
3. Klik tombol New App.
4. Pilih repositori, branch (misalnya main atau master), dan tentukan file utama yaitu app.py.
5. Klik Deploy! Aplikasi Anda akan aktif dan online secara gratis dalam beberapa menit.
