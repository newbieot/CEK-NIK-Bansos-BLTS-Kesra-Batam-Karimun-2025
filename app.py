import streamlit as st
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Cek Penerima BLTS KESRA - Pos Indonesia Batam",
    page_icon="📮",
    layout="centered"
)

# --- FUNGSI SENSOR (MASKING) ---
def sensor_teks(teks):
    """Menyensor sebagian huruf (BUDI -> B***)"""
    teks = str(teks).strip().upper()
    if len(teks) <= 2:
        return teks
    
    kata_kata = teks.split()
    hasil = []
    
    for kata in kata_kata:
        if len(kata) > 2:
            kata_baru = kata[0] + '*' * (len(kata) - 1)
            hasil.append(kata_baru)
        else:
            hasil.append(kata)
    return " ".join(hasil)

# ==========================================
# BAGIAN HEADER (LOGO KIRI & JUDUL KANAN)
# ==========================================

# Bagi layar atas: Logo (Kecil) dan Teks (Besar)
col_logo, col_judul = st.columns([1, 4])

with col_logo:
    # --- LOGO POS ---
    try:
        # Pastikan file logo.png ada di folder yang sama
        st.image("POSIND_Logo_1. Warna (2) (2).png", width=130) 
    except:
        # Cadangan jika file tidak ada
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Logo_Pos_Indonesia_%282023%29.png/640px-Logo_Pos_Indonesia_%282023%29.png", width=130)

with col_judul:
    # --- JUDUL & KETERANGAN WILAYAH ---
    st.markdown("""
    <div style="margin-top: 5px;">
        <h3 style="margin-bottom: 5px; line-height: 1.2;">
            Cek Penerima Bantuan Langsung Tunai Sementara Kesejahteraan Rakyat (BLTS KESRA)
        </h3>
        
        <p style="font-size: 13px; margin-top: 8px; margin-bottom: 8px; color: #444;">
            Website ini disediakan khusus untuk cek NIK Penerima Bantuan di wilayah 
            <b>Kota Batam, Kabupaten Karimun, dan Kabupaten Pelalawan (Kecamatan Kuala Kampar)</b>
        </p>
        
        <p style="font-size: 14px; color: #FF6F00; font-weight: bold; margin-top: 5px;">
            Disediakan oleh PT Pos Indonesia (Persero)<br>
            Kantor Cabang Utama Batam 29400
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# LOGIKA PROGRAM (SMART DETECTOR)
# ==========================================

# --- LOAD DATA ---
@st.cache_data
def load_data():
    file_path = "Belum Terbayar 07 Desember 2025 pukul 06.00.xlsx"
    try:
        xls = pd.ExcelFile(file_path)
        target_sheet = None
        header_row = 0
        
        # --- LOOPING CARI SHEET YANG BENAR ---
        # Script akan membuka setiap sheet dan mencari kolom 'NIK' & 'NAMA'
        for sheet in xls.sheet_names:
            # Baca 10 baris pertama tiap sheet
            df_tmp = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=10)
            
            for i, row in df_tmp.iterrows():
                row_str = row.astype(str).str.lower().tolist()
                # Kunci: Harus ada kata 'nik' dan 'nama' di baris tersebut
                if any('nik' in s for s in row_str) and any('nama' in s for s in row_str):
                    target_sheet = sheet
                    header_row = i
                    break
            if target_sheet: break
        
        # Jika sheet ketemu, baru load datanya
        if target_sheet:
            df = pd.read_excel(xls, sheet_name=target_sheet, header=header_row)
            df.columns = df.columns.str.strip() # Hapus spasi di nama kolom
            
            if 'NIK' in df.columns:
                # Bersihkan NIK dari karakter aneh dan '.0'
                df['NIK'] = df['NIK'].astype(str).str.replace("'", "").str.replace("nan", "").str.strip()
                df['NIK'] = df['NIK'].apply(lambda x: x.split('.')[0])
            return df
        else:
            return None
    except Exception as e:
        return None

df = load_data()

# Jika data gagal dimuat
if df is None:
    st.error("⚠️ Sistem sedang sibuk atau File Database belum terdeteksi.")
    st.info("Pastikan file Excel sudah diupload dengan nama: Belum Terbayar 07 Desember 2025 pukul 06.00.xlsx")
    st.stop()

# --- FORM PENCARIAN ---
st.info("Silakan masukkan Nomor Induk Kependudukan (NIK) Anda.")
nik_input = st.text_input("NIK (Sesuai KTP):", max_chars=16)

if st.button("🔍 CEK STATUS SAYA", type="primary", use_container_width=True):
    if not nik_input:
        st.warning("Mohon isi NIK terlebih dahulu.")
    else:
        # Cari Data
        hasil = df[df['NIK'] == nik_input]
        
        if not hasil.empty:
            # --- JIKA DATA DITEMUKAN (BERHAK) ---
            data = hasil.iloc[0]
            
            # Lakukan Sensor (Masking)
            nama_sensor = sensor_teks(data['Nama'])
            alamat_sensor = sensor_teks(data['Alamat'])
            kecamatan = data['Kecamatan']
            kelurahan = data['Kelurahan']
            
            st.success("✅ SELAMAT! ANDA TERDAFTAR SEBAGAI PENERIMA.")
            
            # Tampilkan Data Tersensor
            with st.container(border=True):
                st.markdown(f"**NAMA PENERIMA:** \n### {nama_sensor}")
                st.markdown(f"**ALAMAT:** \n{alamat_sensor}")
                st.markdown(f"**WILAYAH:** \n{kelurahan}, {kecamatan}")
            
            # Instruksi
            st.warning("""
            **📢 INSTRUKSI PENGAMBILAN DI KANTOR POS:**
            
            Silakan datang ke **Kantor Pos Terdekat** (Sesuai Domisili/Jadwal) dengan membawa:
            1. **KTP Asli** (Elektronik)
            2. **Kartu Keluarga (KK) Asli**
            """)
            
        else:
            # --- JIKA TIDAK DITEMUKAN ---
            st.error("❌ Mohon Maaf, NIK Tidak Ditemukan.")
            st.write("NIK Anda belum terdaftar sebagai penerima bantuan pada tahap ini.")
            st.caption("Pastikan NIK yang dimasukkan sudah benar.")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2025 PT Pos Indonesia (Persero) KCU Batam 29400")
