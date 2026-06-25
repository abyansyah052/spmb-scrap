import streamlit as st
import pandas as pd
import json
import urllib.request
import urllib.error
import io

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="SPMB Jatim Scraper dan Simulasi Peringkat",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan Kontras Tinggi (Background Putih, Teks Hitam, Tanpa Emoticon)
st.markdown("""
<style>
    /* Global Typography dan Warna */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: Arial, sans-serif !important;
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #000000 !important;
    }
    
    /* Paksa semua teks di sidebar berwarna hitam */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #000000 !important;
    }
    
    /* Card design untuk Sekolah */
    .school-card {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 8px !important;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: none !important;
    }
    
    .school-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #000000 !important;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .rank-display {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 12px 0;
        letter-spacing: -1px;
        color: #000000 !important;
    }
    
    .total-text {
        font-size: 0.9rem;
        color: #000000 !important;
        margin-bottom: 12px;
    }
    
    .stat-container {
        border-top: 1px solid #000000 !important;
        padding-top: 10px;
        margin-top: 10px;
    }
    
    .stat-item {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        color: #000000 !important;
        margin-bottom: 4px;
    }
    
    .stat-value {
        font-weight: 600;
        color: #000000 !important;
    }
    
    /* Judul Utama */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #000000 !important;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        color: #000000 !important;
        margin-bottom: 30px;
    }

    /* Tombol Streamlit Kontras Tinggi */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: none !important;
        box-shadow: none !important;
    }
    div.stButton > button:hover {
        background-color: #e5e7eb !important;
    }

    /* Mengubah semua teks standar menjadi hitam */
    p, span, label, li, h1, h2, h3, h4, h5, h6, select, input {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# Definisikan 6 sekolah target beserta data kapasitas (pagu) resmi
TARGET_SCHOOLS = [
    {"id": "177", "name": "SMA Negeri 1", "capacity": 281},
    {"id": "178", "name": "SMA Negeri 2", "capacity": 351},
    {"id": "179", "name": "SMA Negeri 5", "capacity": 353},
    {"id": "182", "name": "SMA Negeri 6", "capacity": 316},
    {"id": "194", "name": "SMA Negeri 15", "capacity": 424},
    {"id": "188", "name": "SMA Negeri 16", "capacity": 387}
]

# Data Persebaran Nilai Hasil TKA Kota Surabaya berdasarkan screenshot pengguna
SURABAYA_GRADE_DISTRIBUTION = [
    {"low": 95.001, "high": 100.0, "count": 20},
    {"low": 90.001, "high": 95.0, "count": 490},
    {"low": 85.001, "high": 90.0, "count": 2350},
    {"low": 80.001, "high": 85.0, "count": 6888},
    {"low": 70.001, "high": 80.0, "count": 14409},
    {"low": 0.0, "high": 70.0, "count": 2283}
]

def calculate_students_above(grade):
    """Menghitung estimasi jumlah siswa di Kota Surabaya dengan nilai > grade menggunakan interpolasi linier"""
    total_above = 0
    for bracket in SURABAYA_GRADE_DISTRIBUTION:
        low = bracket["low"]
        high = bracket["high"]
        count = bracket["count"]
        
        if grade >= high:
            # Nilai input lebih besar dari batas atas braket, tidak ada siswa di atasnya di braket ini
            continue
        elif grade <= low:
            # Nilai input lebih kecil dari batas bawah braket, semua siswa di braket ini memiliki nilai > grade
            total_above += count
        else:
            # Nilai input berada di dalam braket ini, lakukan interpolasi linier
            ratio = (high - grade) / (high - low)
            total_above += count * ratio
            
    return int(round(total_above))

@st.cache_data(ttl=900)
def fetch_school_data(school_id):
    """Menarik data live pemeringkatan sementara akademik SMA Surabaya untuk kelulusan 2026"""
    url = f"https://app.spmbjatim.net/api/acceptances/second-wave-registration/sma/grades?enable_pagination=0&filter[school_id]={school_id}&filter[graduation_year]=this_year"
    
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
            return res_json.get("data", [])
    except urllib.error.HTTPError as e:
        st.error(f"HTTP Error {e.code} saat mengambil data SMA ID {school_id}")
        return []
    except Exception as e:
        st.error(f"Gagal menghubungi server untuk SMA ID {school_id}: {str(e)}")
        return []

# --- APP LAYOUT ---

st.markdown('<h1 class="main-title">SPMB Jatim Scraper dan Simulasi Peringkat</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Analisis Real-time Hasil Pemeringkatan Akademik SMA Surabaya dan Simulasi Kelulusan 2026</p>', unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.markdown("### Pengaturan dan Filter")

user_grade = st.sidebar.number_input(
    "Masukkan Nilai Akademik Anda",
    min_value=0.00,
    max_value=100.00,
    value=87.36,
    step=0.01,
    format="%.2f",
    help="Masukkan nilai rata-rata prestasi akademik Anda untuk mensimulasikan posisi peringkat."
)

if st.sidebar.button("Refresh Data Live"):
    st.cache_data.clear()
    st.toast("Cache dibersihkan! Memuat ulang data dari SPMB Jatim...")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Catatan Aplikasi:**
- Data diperoleh langsung secara real-time dari API resmi spmbjatim.net.
- Simulasi dihitung dengan menyisipkan nilai Anda ke dalam database pendaftar aktif saat ini.
- Sekolah target disaring khusus Kota Surabaya (SMAN 1, 2, 5, 6, 15, 16).
""")

# --- LOAD DATA ---
with st.spinner("Mengambil data terbaru dari SPMB Jatim..."):
    raw_data = {}
    for sch in TARGET_SCHOOLS:
        raw_data[sch["id"]] = fetch_school_data(sch["id"])

# --- PROSES SIMULASI & PERINGKAT ---
processed_schools = []

for sch in TARGET_SCHOOLS:
    sch_id = sch["id"]
    students = raw_data.get(sch_id, [])
    
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
    
    user_row = pd.DataFrame([{
        "Nama": "SIMULASI ANDA (NILAI: " + str(user_grade) + ")",
        "NISN": "SIM-2026",
        "Nilai": float(user_grade),
        "Jarak (m)": 0,
        "Waktu Pendaftaran": "Sekarang",
        "is_sim": True
    }])
    
    if df_raw.empty:
        df_combined = user_row
    else:
        df_combined = pd.concat([df_raw, user_row], ignore_index=True)
        
    df_combined = df_combined.sort_values(by="Nilai", ascending=False, kind="stable").reset_index(drop=True)
    
    sim_idx = df_combined[df_combined["is_sim"] == True].index[0]
    rank = sim_idx + 1
    total_pendaftar = len(df_raw)
    
    if not df_raw.empty:
        max_val = df_raw["Nilai"].max()
        min_val = df_raw["Nilai"].min()
        avg_val = df_raw["Nilai"].mean()
    else:
        max_val = min_val = avg_val = 0.0
        
    processed_schools.append({
        "id": sch_id,
        "name": sch["name"],
        "capacity": sch["capacity"],
        "quota": int(round(sch["capacity"] * 0.25)), # Jalur Nilai Akademik kuotanya 25%
        "rank": rank,
        "total": total_pendaftar,
        "max": max_val,
        "min": min_val,
        "avg": avg_val,
        "df": df_combined
    })

# --- HITUNG BOBOT PREFERENSI & FORECASTING ---
# Hitung total siswa di Surabaya dengan nilai > user_grade
students_above_user = calculate_students_above(user_grade)

# Hitung jumlah siswa pendaftar nyata di 6 sekolah target yang saat ini nilainya di atas user_grade
current_competitors_per_school = {}
total_current_competitors = 0
for sch in processed_schools:
    sch_id = sch["id"]
    df_real = sch["df"][sch["df"]["is_sim"] == False]
    above_count = len(df_real[df_real["Nilai"] > user_grade])
    current_competitors_per_school[sch_id] = above_count
    total_current_competitors += above_count

# Bobot popularitas default sekolah berdasarkan top 3 (SMAN 5 > SMAN 2 > SMAN 15 > SMAN 16 > SMAN 6 > SMAN 1)
default_popularity_weights = {
    "179": 0.28,  # SMAN 5
    "178": 0.22,  # SMAN 2
    "194": 0.18,  # SMAN 15
    "188": 0.14,  # SMAN 16
    "182": 0.11,  # SMAN 6
    "177": 0.07   # SMAN 1
}

# Gabungkan data sebaran nyata di lapangan saat ini (70%) dengan bobot reputasi bawaan (30%)
school_weights = {}
for sch in processed_schools:
    sch_id = sch["id"]
    if total_current_competitors > 0:
        real_share = current_competitors_per_school[sch_id] / total_current_competitors
        school_weights[sch_id] = 0.7 * real_share + 0.3 * default_popularity_weights.get(sch_id, 0.1)
    else:
        school_weights[sch_id] = default_popularity_weights.get(sch_id, 0.1)

# Normalisasi bobot agar jumlahnya pas 1.0 di antara 6 sekolah kita
sum_weights = sum(school_weights.values())
if sum_weights > 0:
    for sch_id in school_weights:
        school_weights[sch_id] /= sum_weights

# Lakukan proyeksi akhir dan peluang masuk
forecasting_results = []
for sch in processed_schools:
    sch_id = sch["id"]
    quota = sch["quota"]
    
    # Estimasi kompetitor proyeksi = total siswa di surabaya > user_grade * bobot sekolah tersebut
    projected_competitors = students_above_user * school_weights[sch_id]
    
    # Proyeksi peringkat akhir = kompetitor + 1
    projected_rank = int(round(projected_competitors)) + 1
    
    # Hitung peluang kelulusan: rasio antara kuota dibanding proyeksi peringkat
    if projected_rank <= quota:
        acceptance_chance = 99.0
    else:
        acceptance_chance = (quota / projected_rank) * 100.0
        
    # Batasi minimal peluang di angka 5%
    acceptance_chance = max(5.0, min(99.0, acceptance_chance))
    
    forecasting_results.append({
        "id": sch_id,
        "name": sch["name"],
        "quota": quota,
        "current_rank": sch["rank"],
        "projected_rank": projected_rank,
        "chance": acceptance_chance
    })

# Tambahkan hasil forecasting ke object processed_schools
for sch in processed_schools:
    f_res = next(f for f in forecasting_results if f["id"] == sch["id"])
    sch["projected_rank"] = f_res["projected_rank"]
    sch["chance"] = f_res["chance"]

# --- RENDER DASHBOARD UTAMA ---
st.markdown("### Dashboard Hasil Simulasi dan Proyeksi Kelulusan")
st.write(f"Berikut adalah simulasi posisi saat ini serta proyeksi akhir (Forecasting) peluang masuk Anda di 6 SMA target:")

cols1 = st.columns(3)
for i in range(3):
    sch = processed_schools[i]
    chance_val = sch["chance"]
    
    if chance_val >= 75.0:
        status_desc = f"Peluang Sangat Tinggi: {chance_val:.1f}%"
    elif chance_val >= 40.0:
        status_desc = f"Peluang Cukup Bersaing: {chance_val:.1f}%"
    else:
        status_desc = f"Peluang Ketat: {chance_val:.1f}%"
        
    with cols1[i]:
        st.markdown(f"""
        <div class="school-card">
            <div class="school-title">{sch['name']}</div>
            <div style="font-size: 0.85rem; color: #000000; margin-bottom: 2px;">Peringkat Saat Ini / Kuota:</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #000000;">#{sch['rank']} / {sch['quota']}</div>
            <div style="font-size: 0.85rem; color: #000000; margin-top: 10px; margin-bottom: 2px;">Proyeksi Peringkat Akhir:</div>
            <div class="rank-display">#{sch['projected_rank']}</div>
            <div style="font-size: 0.88rem; font-weight: 700; margin-bottom: 12px; color: #000000;">{status_desc}</div>
            <div class="stat-container">
                <div class="stat-item"><span>Daya Tampung (Pagu):</span><span class="stat-value">{sch['capacity']}</span></div>
                <div class="stat-item"><span>Kuota Akademik (25%):</span><span class="stat-value">{sch['quota']}</span></div>
                <div class="stat-item"><span>Pendaftar Saat Ini:</span><span class="stat-value">{sch['total']}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

cols2 = st.columns(3)
for i in range(3, 6):
    sch = processed_schools[i]
    chance_val = sch["chance"]
    
    if chance_val >= 75.0:
        status_desc = f"Peluang Sangat Tinggi: {chance_val:.1f}%"
    elif chance_val >= 40.0:
        status_desc = f"Peluang Cukup Bersaing: {chance_val:.1f}%"
    else:
        status_desc = f"Peluang Ketat: {chance_val:.1f}%"
        
    with cols2[i-3]:
        st.markdown(f"""
        <div class="school-card">
            <div class="school-title">{sch['name']}</div>
            <div style="font-size: 0.85rem; color: #000000; margin-bottom: 2px;">Peringkat Saat Ini / Kuota:</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #000000;">#{sch['rank']} / {sch['quota']}</div>
            <div style="font-size: 0.85rem; color: #000000; margin-top: 10px; margin-bottom: 2px;">Proyeksi Peringkat Akhir:</div>
            <div class="rank-display">#{sch['projected_rank']}</div>
            <div style="font-size: 0.88rem; font-weight: 700; margin-bottom: 12px; color: #000000;">{status_desc}</div>
            <div class="stat-container">
                <div class="stat-item"><span>Daya Tampung (Pagu):</span><span class="stat-value">{sch['capacity']}</span></div>
                <div class="stat-item"><span>Kuota Akademik (25%):</span><span class="stat-value">{sch['quota']}</span></div>
                <div class="stat-item"><span>Pendaftar Saat Ini:</span><span class="stat-value">{sch['total']}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- DETAIL FIELD: FORECASTING & SEBARAN DATA KOTA ---
st.markdown("### Forecasting dan Analisis Sebaran Nilai Kota")
col_left, col_right = st.columns([2, 1])

with col_left:
    st.write("Analisis Proyeksi Akhir Keketatan Jalur Prestasi Akademik:")
    
    # Buat dataframe ringkasan forecasting untuk ditampilkan dalam bentuk tabel
    df_forecasting = pd.DataFrame([
        {
            "Sekolah": f["name"],
            "Kuota": f["quota"],
            "Peringkat Saat Ini": f["current_rank"],
            "Proyeksi Peringkat Akhir": f["projected_rank"],
            "Prediksi Peluang Diterima": f"{f['chance']:.1f}%",
            "Keterangan": "Sangat Tinggi" if f["chance"] >= 75.0 else ("Cukup Bersaing" if f["chance"] >= 40.0 else "Persaingan Ketat")
        } for f in forecasting_results
    ])
    st.dataframe(df_forecasting, use_container_width=True, hide_index=True)

with col_right:
    st.write(f"Statistik Sebaran Nilai Kota Surabaya:")
    st.markdown(f"""
    - Jumlah siswa di Surabaya dengan nilai **> {user_grade:.2f}**: **{students_above_user} siswa**
    - Potensi akumulasi persaingan: Dengan total **{students_above_user}** siswa bernilai di atas Anda di Surabaya, keketatan sekolah unggulan (Top 3: SMAN 5, 2, 15) akan meningkat signifikan di akhir masa pendaftaran seiring masuknya pendaftaran baru.
    """)
    
    # Tampilkan tabel sebaran data asli sebagai referensi pengguna
    df_dist_ref = pd.DataFrame(SURABAYA_GRADE_DISTRIBUTION)
    df_dist_ref = df_dist_ref.rename(columns={
        "low": "Batas Bawah",
        "high": "Batas Atas",
        "count": "Jumlah Siswa"
    })
    st.dataframe(df_dist_ref, use_container_width=True, hide_index=True)

st.markdown("---")

# --- GRAFIK PERBANDINGAN NILAI ---
st.markdown("### Grafik Perbandingan Nilai")
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
st.markdown("### Detail Tabel Pendaftar Per Sekolah")
st.write("Pilih salah satu sekolah di bawah ini untuk melihat daftar pendaftar lengkap dan posisi simulasi Anda dalam tabel:")

selected_sch_name = st.selectbox(
    "Pilih Sekolah Target",
    [sch["name"] for sch in processed_schools]
)

selected_sch = next(sch for sch in processed_schools if sch["name"] == selected_sch_name)
df_display = selected_sch["df"].copy()
df_display.insert(0, "Peringkat", df_display.index + 1)
df_display = df_display.rename(columns={
    "Waktu Pendaftaran": "Waktu Daftar"
})

is_sim_col = df_display["is_sim"]
df_display_clean = df_display.drop(columns=["is_sim"])

# Styling fungsi untuk menyorot baris simulasi dengan kontras tinggi (kuning stabilo)
def style_table(row):
    idx = row.name
    if is_sim_col.iloc[idx]:
        return ['background-color: #ffff00; font-weight: bold; border: 2px solid #000000; color: #000000;'] * len(row)
    return [''] * len(row)

styled_df = df_display_clean.style.apply(style_table, axis=1)

st.dataframe(
    styled_df,
    use_container_width=True,
    height=450
)

# --- EKSPOR DATA KE CSV ---
st.markdown("### Ekspor Data Hasil Scraping")
st.write("Unduh data pemeringkatan lengkap untuk sekolah yang sedang Anda lihat:")

df_export = selected_sch["df"][selected_sch["df"]["is_sim"] == False].copy()
df_export.insert(0, "Peringkat", range(1, len(df_export) + 1))
df_export = df_export.drop(columns=["is_sim"])

csv_data = df_export.to_csv(index=False).encode('utf-8')

st.download_button(
    label=f"Unduh Data {selected_sch['name']} (CSV)",
    data=csv_data,
    file_name=f"ppdb_2026_{selected_sch['name'].replace(' ', '_').lower()}.csv",
    mime="text/csv",
    help=f"Mengunduh file CSV yang berisi data pendaftar asli di {selected_sch['name']}."
)
