import streamlit as st
import pandas as pd
import json
import urllib.request
import urllib.error
import io

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="SPMB Jatim Scraper & Simulasi Peringkat",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan premium & modern (Dark Mode mewah)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Global Typography */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #0b0f19 !important;
        color: #f3f4f6 !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1f2937 !important;
    }
    
    /* Card design untuk Sekolah */
    .school-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .school-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 25px rgba(20, 184, 166, 0.15);
        border-color: #14b8a6;
    }
    
    .school-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .rank-display {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 12px 0;
        letter-spacing: -1px;
    }
    
    .rank-text-green { color: #10b981; }
    .rank-text-yellow { color: #f59e0b; }
    .rank-text-red { color: #ef4444; }
    
    .total-text {
        font-size: 0.9rem;
        color: #9ca3af;
        margin-bottom: 12px;
    }
    
    .stat-container {
        border-top: 1px solid #1e293b;
        padding-top: 10px;
        margin-top: 10px;
    }
    
    .stat-item {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        color: #9ca3af;
        margin-bottom: 4px;
    }
    
    .stat-value {
        font-weight: 600;
        color: #f3f4f6;
    }
    
    /* Judul Utama */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #14b8a6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        color: #9ca3af;
        margin-bottom: 30px;
    }

    /* Styler untuk Streamlit Element */
    div.stButton > button {
        background: linear-gradient(90deg, #0284c7 0%, #0d9488 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(20, 184, 166, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Definisikan 6 sekolah target berdasarkan permintaan user
TARGET_SCHOOLS = [
    {"id": "177", "name": "SMA Negeri 1"},
    {"id": "178", "name": "SMA Negeri 2"},
    {"id": "179", "name": "SMA Negeri 5"},
    {"id": "182", "name": "SMA Negeri 6"},
    {"id": "194", "name": "SMA Negeri 15"},
    {"id": "188", "name": "SMA Negeri 16"}
]

# Cache penarikan data agar tidak memberatkan server & cepat saat dijalankan ulang
@st.cache_data(ttl=900)  # cache 15 menit
def fetch_school_data(school_id, ranking_type):
    """Menarik data pemeringkatan akademik SMA Surabaya untuk kelulusan 2026"""
    if ranking_type == "Sementara":
        # API Pendaftaran Tahap 3 (Prestasi Akademik SMA) kelulusan tahun ini (2026)
        url = f"https://app.spmbjatim.net/api/acceptances/second-wave-registration/sma/grades?enable_pagination=0&filter[school_id]={school_id}&filter[graduation_year]=this_year"
    else:
        # Data final dari CDN statis SPMB Jatim (Kelulusan 2026 / tahun ini)
        url = f"https://static.spmbjatim.net/second-wave-acceptance/1/{school_id}.json"
        
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            if ranking_type == "Sementara":
                return res_json.get("data", [])
            else:
                # Format final dari static JSON adalah langsung berupa array pendaftar
                return res_json
    except urllib.error.HTTPError as e:
        # Jika final belum rilis, beri pesan informatif
        if ranking_type == "Final" and e.code == 404:
            return None
        st.error(f"HTTP Error {e.code} saat mengambil data SMA ID {school_id}")
        return []
    except Exception as e:
        st.error(f"Gagal menghubungi server untuk SMA ID {school_id}: {str(e)}")
        return []

# --- APP LAYOUT ---

# Judul Utama Aplikasi
st.markdown('<h1 class="main-title">📊 SPMB Jatim - Scraping & Simulasi Peringkat</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Analisis Real-time Hasil Pemeringkatan Akademik SMA Surabaya & Simulasi Kelulusan 2026</p>', unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.markdown("### 🎛️ Pengaturan & Filter")

# Pilihan Tipe Pemeringkatan
ranking_type = st.sidebar.selectbox(
    "Jenis Pemeringkatan",
    ["Sementara", "Final"],
    help="Pilih 'Sementara' untuk melihat data live PPDB yang diperbarui setiap 15 menit, atau 'Final' jika pengumuman kelulusan resmi telah dirilis."
)

# Input Nilai Akademik Pengguna
user_grade = st.sidebar.number_input(
    "Masukkan Nilai Akademik Anda",
    min_value=0.00,
    max_value=100.00,
    value=87.36,
    step=0.01,
    format="%.2f",
    help="Masukkan nilai rata-rata prestasi akademik Anda untuk mensimulasikan posisi peringkat."
)

# Tombol Refresh Cache Data
if st.sidebar.button("🔄 Refresh Data SPMB"):
    st.cache_data.clear()
    st.toast("Cache dibersihkan! Memuat ulang data dari SPMB Jatim...")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Catatan Aplikasi:**
- Data diperoleh langsung secara real-time dari API resmi `spmbjatim.net`.
- Simulasi dihitung dengan menyisipkan nilai Anda ke dalam database pendaftar aktif saat ini.
- Sekolah target disaring khusus Kota Surabaya (SMAN 1, 2, 5, 6, 15, 16).
""")

# --- LOAD DATA ---
with st.spinner("Mengambil data terbaru dari SPMB Jatim..."):
    raw_data = {}
    is_final_empty = False
    
    for sch in TARGET_SCHOOLS:
        data = fetch_school_data(sch["id"], ranking_type)
        if data is None and ranking_type == "Final":
            is_final_empty = True
            break
        raw_data[sch["id"]] = data

# Penanganan jika data final belum dirilis
if is_final_empty:
    st.warning("⚠️ Data Pemeringkatan Final untuk Kelulusan 2026 belum dirilis oleh SPMB Jatim. Silakan pilih 'Sementara' pada panel sebelah kiri.")
    st.stop()

# --- PROSES SIMULASI & PERINGKAT ---
processed_schools = []

for sch in TARGET_SCHOOLS:
    sch_id = sch["id"]
    students = raw_data.get(sch_id, [])
    
    # Normalisasi data pendaftar
    normalized_list = []
    for s in students:
        try:
            val_grade = float(s.get("grade_final", 0))
        except:
            val_grade = 0.0
            
        try:
            val_dist = int(s.get("distance", 0))
        except:
            val_dist = 0
            
        normalized_list.append({
            "Nama": s.get("name", "").upper(),
            "NISN": s.get("nisn", ""),
            "Nilai": val_grade,
            "Jarak (m)": val_dist,
            "Waktu Pendaftaran": s.get("registration_created_at", "-"),
            "is_sim": False
        })
        
    df_raw = pd.DataFrame(normalized_list)
    
    # Buat baris simulasi pengguna
    user_row = pd.DataFrame([{
        "Nama": "✨ SIMULASI ANDA (NILAI: " + str(user_grade) + ")",
        "NISN": "SIM-2026",
        "Nilai": float(user_grade),
        "Jarak (m)": 0,
        "Waktu Pendaftaran": "Sekarang",
        "is_sim": True
    }])
    
    # Gabungkan dan urutkan
    if df_raw.empty:
        df_combined = user_row
    else:
        df_combined = pd.concat([df_raw, user_row], ignore_index=True)
        
    # Urutkan berdasarkan Nilai descending (stable sort agar pendaftar lama tidak tergeser sembarangan)
    df_combined = df_combined.sort_values(by="Nilai", ascending=False, kind="stable").reset_index(drop=True)
    
    # Cari posisi index simulasi
    sim_idx = df_combined[df_combined["is_sim"] == True].index[0]
    rank = sim_idx + 1
    total_pendaftar = len(df_raw)
    
    # Statistik riil sekolah (tanpa nilai simulasi)
    if not df_raw.empty:
        max_val = df_raw["Nilai"].max()
        min_val = df_raw["Nilai"].min()
        avg_val = df_raw["Nilai"].mean()
    else:
        max_val = min_val = avg_val = 0.0
        
    processed_schools.append({
        "id": sch_id,
        "name": sch["name"],
        "rank": rank,
        "total": total_pendaftar,
        "max": max_val,
        "min": min_val,
        "avg": avg_val,
        "df": df_combined
    })

# --- RENDER DASHBOARD UTAMA ---
st.markdown("### 🏆 Dashboard Hasil Simulasi")
st.write("Di bawah ini adalah posisi peringkat simulasi Anda di masing-masing dari 6 sekolah target:")

# Baris pertama kartu simulasi (3 Kolom)
cols1 = st.columns(3)
for i in range(3):
    sch = processed_schools[i]
    # Tentukan persentase posisi untuk menentukan warna tingkat persaingan
    # Semakin kecil ranking/total, peluang semakin bagus
    ratio = sch["rank"] / max(sch["total"], 1)
    
    if ratio <= 0.4:
        rank_class = "rank-text-green"
        status_desc = "🟢 Peluang Sangat Aman (Top 40%)"
    elif ratio <= 0.8:
        rank_class = "rank-text-yellow"
        status_desc = "🟡 Bersaing Ketat (Top 40%-80%)"
    else:
        rank_class = "rank-text-red"
        status_desc = "🔴 Di Luar Zona Aman (>80%)"
        
    with cols1[i]:
        st.markdown(f"""
        <div class="school-card">
            <div class="school-title">{sch['name']}</div>
            <div style="font-size: 0.85rem; color: #9ca3af;">Simulasi Peringkat Anda:</div>
            <div class="rank-display {rank_class}">#{sch['rank']}</div>
            <div class="total-text">dari <b>{sch['total']}</b> pendaftar aktif</div>
            <div style="font-size: 0.85rem; font-weight: 600; margin-bottom: 12px;">{status_desc}</div>
            <div class="stat-container">
                <div class="stat-item"><span>Nilai Tertinggi:</span><span class="stat-value">{sch['max']:.2f}</span></div>
                <div class="stat-item"><span>Nilai Rata-rata:</span><span class="stat-value">{sch['avg']:.2f}</span></div>
                <div class="stat-item"><span>Nilai Terendah:</span><span class="stat-value">{sch['min']:.2f}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Baris kedua kartu simulasi (3 Kolom)
cols2 = st.columns(3)
for i in range(3, 6):
    sch = processed_schools[i]
    ratio = sch["rank"] / max(sch["total"], 1)
    
    if ratio <= 0.4:
        rank_class = "rank-text-green"
        status_desc = "🟢 Peluang Sangat Aman (Top 40%)"
    elif ratio <= 0.8:
        rank_class = "rank-text-yellow"
        status_desc = "🟡 Bersaing Ketat (Top 40%-80%)"
    else:
        rank_class = "rank-text-red"
        status_desc = "🔴 Di Luar Zona Aman (>80%)"
        
    with cols2[i-3]:
        st.markdown(f"""
        <div class="school-card">
            <div class="school-title">{sch['name']}</div>
            <div style="font-size: 0.85rem; color: #9ca3af;">Simulasi Peringkat Anda:</div>
            <div class="rank-display {rank_class}">#{sch['rank']}</div>
            <div class="total-text">dari <b>{sch['total']}</b> pendaftar aktif</div>
            <div style="font-size: 0.85rem; font-weight: 600; margin-bottom: 12px;">{status_desc}</div>
            <div class="stat-container">
                <div class="stat-item"><span>Nilai Tertinggi:</span><span class="stat-value">{sch['max']:.2f}</span></div>
                <div class="stat-item"><span>Nilai Rata-rata:</span><span class="stat-value">{sch['avg']:.2f}</span></div>
                <div class="stat-item"><span>Nilai Terendah:</span><span class="stat-value">{sch['min']:.2f}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- GRAFIK PERBANDINGAN NILAI ---
st.markdown("### 📊 Grafik Perbandingan Nilai")
# Siapkan data untuk grafik
chart_data = []
for sch in processed_schools:
    chart_data.append({
        "Sekolah": sch["name"],
        "Nilai Anda": user_grade,
        "Rata-rata Sekolah": sch["avg"],
        "Nilai Terendah": sch["min"],
        "Nilai Tertinggi": sch["max"]
    })
df_chart = pd.DataFrame(chart_data).set_index("Sekolah")
st.bar_chart(df_chart, height=350)

st.markdown("---")

# --- DETAIL TABEL PENDAFTAR ---
st.markdown("### 📋 Detail Tabel Pendaftar Per Sekolah")
st.write("Pilih salah satu sekolah di bawah ini untuk melihat daftar pendaftar lengkap dan posisi simulasi Anda dalam tabel:")

# Dropdown pilihan sekolah untuk melihat tabel detail
selected_sch_name = st.selectbox(
    "Pilih Sekolah Target",
    [sch["name"] for sch in processed_schools]
)

# Temukan sekolah yang dipilih
selected_sch = next(sch for sch in processed_schools if sch["name"] == selected_sch_name)
df_display = selected_sch["df"].copy()

# Buat kolom Peringkat
df_display.insert(0, "Peringkat", df_display.index + 1)

# Format nama kolom agar rapi di UI
df_display = df_display.rename(columns={
    "Waktu Pendaftaran": "Waktu Daftar"
})

# Drop kolom is_sim karena hanya untuk penandaan internal
is_sim_col = df_display["is_sim"]
df_display_clean = df_display.drop(columns=["is_sim"])

# Fungsi styling untuk menyorot baris simulasi user
def style_table(row):
    # Dapatkan status simulasi dari is_sim_col menggunakan indeks baris
    idx = row.name
    if is_sim_col.iloc[idx]:
        # Beri warna latar belakang teal transparan, border tebal, dan teks bold
        return ['background-color: rgba(20, 184, 166, 0.45); font-weight: bold; border: 2px solid #14b8a6; color: #ffffff;'] * len(row)
    return [''] * len(row)

# Render Dataframe dengan styling highlight
styled_df = df_display_clean.style.apply(style_table, axis=1)

# Tampilkan tabel detail
st.dataframe(
    styled_df,
    use_container_width=True,
    height=450
)

# --- EKSPOR DATA KE CSV ---
st.markdown("### 📥 Ekspor Data Hasil Scraping")
st.write("Unduh data pemeringkatan lengkap untuk sekolah yang sedang Anda lihat:")

# Siapkan data CSV untuk diunduh (hanya data asli tanpa baris simulasi)
df_export = selected_sch["df"][selected_sch["df"]["is_sim"] == False].copy()
df_export.insert(0, "Peringkat", range(1, len(df_export) + 1))
df_export = df_export.drop(columns=["is_sim"])

# Konversi ke CSV
csv_data = df_export.to_csv(index=False).encode('utf-8')

# Tombol download
st.download_button(
    label=f"💾 Unduh Data {selected_sch['name']} (CSV)",
    data=csv_data,
    file_name=f"ppdb_2026_{selected_sch['name'].replace(' ', '_').lower()}.csv",
    mime="text/csv",
    help=f"Mengunduh file CSV yang berisi data pendaftar asli di {selected_sch['name']}."
)
