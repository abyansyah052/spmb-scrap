import streamlit as st
import pandas as pd
import json
import urllib.request
import urllib.error
import io
import random

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

# Slider penyerapan tahap sebelumnya (Zonasi, Afirmasi, Mutasi, Lomba)
absorbed_rate = st.sidebar.slider(
    "Siswa Lolos Tahap I dan II (%)",
    min_value=10,
    max_value=90,
    value=65,
    step=5,
    help="Persentase estimasi siswa dengan nilai tinggi yang SUDAH diterima pada tahap sebelumnya (Zonasi dan Afirmasi) sehingga tidak ikut berkompetisi di Tahap III."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Simulasi Pilihan Sekolah Anda")
st.sidebar.write("Tentukan 3 sekolah pilihan Anda untuk disimulasikan dalam proses seleksi limpahan (cascade):")

school_options = {sch["name"]: sch["id"] for sch in TARGET_SCHOOLS}
school_names_list = list(school_options.keys())

pilihan_1 = st.sidebar.selectbox("Pilihan 1", school_names_list, index=2) # SMAN 5
pilihan_2 = st.sidebar.selectbox("Pilihan 2", school_names_list, index=1) # SMAN 2
pilihan_3 = st.sidebar.selectbox("Pilihan 3", school_names_list, index=4) # SMAN 15

user_choices_ids = [
    school_options[pilihan_1],
    school_options[pilihan_2],
    school_options[pilihan_3]
]

if st.sidebar.button("Refresh Data Live"):
    st.cache_data.clear()
    st.toast("Cache dibersihkan! Memuat ulang data dari SPMB Jatim...")
    st.rerun()

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

# --- SIMULASI LIMPAHAN KASKADE (CASCADE MATCHING SIMULATION) ---
# 1. Hitung total siswa di Surabaya dengan nilai > user_grade
students_above_user = calculate_students_above(user_grade)

# 2. Kurangi kompetitor kota yang sudah diterima di Tahap I & II
active_competitors_in_city = int(round(students_above_user * (1 - (absorbed_rate / 100.0))))

# 3. Jalankan simulasi kaskade di sisi server Python menggunakan data sebaran kota
def run_cascade_matching():
    # Set seed untuk konsistensi simulasi
    random.seed(42)
    
    # Bangun data nilai siswa Kota Surabaya secara lengkap berdasarkan sebaran resmi
    city_grades = []
    for _ in range(20): city_grades.append(random.uniform(95.001, 100.0))
    for _ in range(490): city_grades.append(random.uniform(90.001, 95.0))
    for _ in range(2350): city_grades.append(random.uniform(85.001, 90.0))
    for _ in range(6888): city_grades.append(random.uniform(80.001, 85.0))
    for _ in range(14409): city_grades.append(random.uniform(70.001, 80.0))
    for _ in range(2283): city_grades.append(random.uniform(50.0, 70.0))
    city_grades.sort(reverse=True)
    
    # Hilangkan siswa yang terserap Tahap I & II (Zonasi, Afirmasi, Mutasi)
    active_grades = [g for g in city_grades if random.random() > (absorbed_rate / 100.0)]
    
    # Susun pilihan sekolah untuk tiap siswa kota secara acak-proporsional sesuai bobot reputasi
    school_ids = ["179", "178", "194", "188", "182", "177"] # Urutan: SMAN 5, 2, 15, 16, 6, 1
    weights = [0.35, 0.25, 0.20, 0.10, 0.07, 0.03]
    
    sim_students = []
    for g in active_grades:
        c1 = random.choices(school_ids, weights=weights, k=1)[0]
        idx = school_ids.index(c1)
        c2 = school_ids[(idx + 1) % len(school_ids)]
        c3 = school_ids[(idx + 2) % len(school_ids)]
        sim_students.append({'grade': g, 'choices': [c1, c2, c3], 'accepted': None, 'is_user': False})
        
    # Masukkan user ke dalam data simulasi dengan pilihannya sendiri
    user_student = {
        'grade': float(user_grade),
        'choices': user_choices_ids,
        'accepted': None,
        'is_user': True
    }
    sim_students.append(user_student)
    
    # Urutkan seluruh siswa simulasi berdasarkan nilai akademik tertinggi
    sim_students.sort(key=lambda x: x['grade'], reverse=True)
    
    # Jalankan algoritma alokasi kaskade (Pendaftar lolos di pilihan 1, sisa limpahan turun ke pilihan 2 & 3)
    school_quotas = {sch["id"]: sch["quota"] for sch in processed_schools}
    accepted_lists = {sch["id"]: [] for sch in processed_schools}
    
    for s in sim_students:
        for choice in s['choices']:
            if len(accepted_lists[choice]) < school_quotas[choice]:
                accepted_lists[choice].append(s)
                s['accepted'] = choice
                break
                
    # Tarik data cutoff (nilai terendah yang diterima) dan peringkat simulasi user
    matching_summary = {}
    for sch in processed_schools:
        sch_id = sch["id"]
        accepted = accepted_lists[sch_id]
        cutoff_grade = accepted[-1]['grade'] if len(accepted) == school_quotas[sch_id] else 0.0
        
        # Cari rank simulasi user
        user_idx = [i for i, x in enumerate(accepted) if x['is_user']]
        if user_idx:
            rank_in_sim = user_idx[0] + 1
        else:
            # Jika user tidak masuk, estimasikan peringkatnya di antara peminat sekolah tersebut
            competitors_to_school = [x['grade'] for x in sim_students if x['choices'][0] == sch_id]
            competitors_to_school.append(float(user_grade))
            competitors_to_school.sort(reverse=True)
            rank_in_sim = competitors_to_school.index(float(user_grade)) + 1
            
        matching_summary[sch_id] = {
            "cutoff": cutoff_grade,
            "rank": rank_in_sim
        }
        
    return matching_summary, user_student['accepted']

# Eksekusi simulasi
sim_summary, user_accepted_school_id = run_cascade_matching()

# Hitung Peluang Diterima (%) berdasarkan hasil kaskade
forecasting_results = []
for sch in processed_schools:
    sch_id = sch["id"]
    cutoff = sim_summary[sch_id]["cutoff"]
    sim_rank = sim_summary[sch_id]["rank"]
    quota = sch["quota"]
    
    # Peluang dinamis berdasarkan kedekatan nilai dengan batas nilai cutoff simulasi
    if user_grade >= cutoff:
        chance = 99.0
    else:
        # Selisih nilai menentukan persentase peluang
        diff = cutoff - user_grade
        chance = (1.0 - (diff / 3.0)) * 100.0
        
    chance = max(5.0, min(95.0, chance))
    
    # Tentukan keterangan kelulusan simulasi
    if user_accepted_school_id == sch_id:
        status_label = "Diterima Simulasi (Prioritas)"
        chance = 99.0
    elif user_grade >= cutoff:
        status_label = "Lolos Batas Nilai"
    else:
        status_label = "Di Bawah Batas Nilai"
        
    forecasting_results.append({
        "id": sch_id,
        "name": sch["name"],
        "quota": quota,
        "current_rank": sch["rank"],
        "projected_rank": sim_rank,
        "cutoff": cutoff,
        "chance": chance,
        "status": status_label
    })

# Sinkronkan hasil forecasting ke object processed_schools
for sch in processed_schools:
    f_res = next(f for f in forecasting_results if f["id"] == sch["id"])
    sch["projected_rank"] = f_res["projected_rank"]
    sch["cutoff"] = f_res["cutoff"]
    sch["chance"] = f_res["chance"]
    sch["status"] = f_res["status"]

# --- RENDER DASHBOARD UTAMA ---
st.markdown("### Dashboard Hasil Simulasi dan Proyeksi Kelulusan")
st.write(f"Berikut adalah simulasi posisi saat ini serta hasil **Simulasi Limpahan Kaskade** peluang masuk Anda di 6 SMA target:")

# Highlight status penerimaan simulasi user
pilihan_names = {sch["id"]: sch["name"] for sch in TARGET_SCHOOLS}
if user_accepted_school_id:
    st.info(f"Hasil Alokasi Simulasi: Berdasarkan nilai {user_grade:.2f} dan urutan pilihan Anda, Anda diproyeksikan **Diterima di {pilihan_names[user_accepted_school_id]}**.")
else:
    st.warning(f"Hasil Alokasi Simulasi: Berdasarkan nilai {user_grade:.2f} dan urutan pilihan Anda, Anda diproyeksikan **Belum Lolos** di ketiga pilihan sekolah Anda karena nilai berada di bawah batas cutoff simulasi.")

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
            <div style="font-size: 0.85rem; color: #000000; margin-top: 10px; margin-bottom: 2px;">Prediksi Batas Nilai Cutoff:</div>
            <div class="rank-display">{sch['cutoff']:.2f}</div>
            <div style="font-size: 0.88rem; font-weight: 700; margin-bottom: 4px; color: #000000;">{status_desc}</div>
            <div style="font-size: 0.85rem; font-weight: 600; color: #7f1d1d;">Status: {sch['status']}</div>
            <div class="stat-container">
                <div class="stat-item"><span>Daya Tampung (Pagu):</span><span class="stat-value">{sch['capacity']}</span></div>
                <div class="stat-item"><span>Kuota Akademik (25%):</span><span class="stat-value">{sch['quota']}</span></div>
                <div class="stat-item"><span>Pendaftar Saat Ini:</span><span class="stat-value">{sch['total']}</span></div>
                <div class="stat-item"><span>Nilai Tertinggi:</span><span class="stat-value">{sch['max']:.2f}</span></div>
                <div class="stat-item"><span>Nilai Terendah:</span><span class="stat-value">{sch['min']:.2f}</span></div>
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
            <div style="font-size: 0.85rem; color: #000000; margin-top: 10px; margin-bottom: 2px;">Prediksi Batas Nilai Cutoff:</div>
            <div class="rank-display">{sch['cutoff']:.2f}</div>
            <div style="font-size: 0.88rem; font-weight: 700; margin-bottom: 4px; color: #000000;">{status_desc}</div>
            <div style="font-size: 0.85rem; font-weight: 600; color: #7f1d1d;">Status: {sch['status']}</div>
            <div class="stat-container">
                <div class="stat-item"><span>Daya Tampung (Pagu):</span><span class="stat-value">{sch['capacity']}</span></div>
                <div class="stat-item"><span>Kuota Akademik (25%):</span><span class="stat-value">{sch['quota']}</span></div>
                <div class="stat-item"><span>Pendaftar Saat Ini:</span><span class="stat-value">{sch['total']}</span></div>
                <div class="stat-item"><span>Nilai Tertinggi:</span><span class="stat-value">{sch['max']:.2f}</span></div>
                <div class="stat-item"><span>Nilai Terendah:</span><span class="stat-value">{sch['min']:.2f}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- DETAIL FIELD: FORECASTING & SEBARAN DATA KOTA ---
st.markdown("### Forecasting dan Analisis Sebaran Nilai Kota")
col_left, col_right = st.columns([2, 1])

with col_left:
    st.write("Analisis Proyeksi Akhir Keketatan Jalur Prestasi Akademik (Model Kaskade):")
    
    # Buat dataframe ringkasan forecasting untuk ditampilkan dalam bentuk tabel
    df_forecasting = pd.DataFrame([
        {
            "Sekolah": f["name"],
            "Kuota": f["quota"],
            "Peringkat Saat Ini": f["current_rank"],
            "Prediksi Peringkat Simulasi": f["projected_rank"],
            "Batas Nilai Lolos (Cutoff)": f"{f['cutoff']:.2f}",
            "Prediksi Peluang Lolos": f"{f['chance']:.1f}%",
            "Hasil Alokasi": f["status"]
        } for f in forecasting_results
    ])
    st.dataframe(df_forecasting, use_container_width=True, hide_index=True)

with col_right:
    st.write(f"Statistik Sebaran Nilai Kota Surabaya:")
    st.markdown(f"""
    - Jumlah siswa di Surabaya dengan nilai **> {user_grade:.2f}**: **{students_above_user} siswa**
    - Sisa kompetitor aktif setelah dikurangi penyerapan Tahap I & II (**{absorbed_rate}%**): **{active_competitors_in_city} siswa**
    - **Logika Kaskade (Limpahan)**: Sistem menyimulasikan 3 pilihan sekolah untuk masing-masing siswa kota. Siswa bernilai tinggi yang terdepak dari pilihan 1 (karena melebihi kuota) akan melimpah (*cascade*) ke pilihan 2 & 3, sehingga memperebutkan sisa kuota sekolah tingkat berikutnya secara dinamis.
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
