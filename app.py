import streamlit as st
import pandas as pd
from PIL import Image

# --- KONFIGURASI HALAMAN (WAJIB PALING ATAS) ---
st.set_page_config(
    page_title="Cek Bansos - Pos Indonesia KCU Batam",
    page_icon="📮",
    layout="centered"
)

# --- FUNGSI SENSOR (MASKING) ---
def sensor_teks(teks):
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

# Kita bagi layar atas menjadi 2 kolom dengan perbandingan 1 : 4
# Kolom 1 (Kecil) untuk Logo, Kolom 2 (Besar) untuk Teks
col_logo, col_judul = st.columns([1, 4])

with col_logo:
    # --- LOGO DI KIRI ATAS ---
    # width=130 mengatur agar logo kecil & proporsional (tidak raksasa)
    try:
        st.image("POSIND_Logo_1. Warna (2) (2).png", width=130) 
    except:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Logo_Pos_Indonesia_%282023%29.png/640px-Logo_Pos_Indonesia_%282023%29.png", width=130)

with col_judul:
    # --- JUDUL DI SEBELAH KANAN LOGO ---
    # Menggunakan HTML agar jarak antar baris lebih rapi
    st.markdown("""
    <div style="margin-top: 10px;">
        <h3 style="margin-bottom: 0px;">Cek Bansos Kesejahteraan Rakyat</h3>
        <p style="font-size: 14px; color: #FF6F00; font-weight: bold; margin-top: 5px;">
            Disediakan oleh PT Pos Indonesia (Persero)<br>
            Kantor Cabang Utama Batam 29400
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# LOGIKA PROGRAM (SAMA SEPERTI SEBELUMNYA)
# ==========================================

# --- LOAD DATA ---
@st.cache_data
def load_data():
    file_path = "Belum Terbayar 07 Desember 2025 pukul 06.00.xlsx"
    try:
        xls = pd.ExcelFile(file_path)
        target_sheet = None
        header_row = 0
        
        for sheet in xls.sheet_names:
            df_tmp = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=10)
            for i, row in df_tmp.iterrows():
                row_str = row.astype(str).str.lower().tolist()
                if any('nik' in s for s in row_str) and any('nama' in s for s in row_str):
                    target_sheet = sheet
                    header_row = i
                    break
            if target_sheet: break
        
        if target_sheet:
            df = pd.read_excel(xls, sheet_name=target_sheet, header=header_row)
            df.columns = df.columns.str.strip()
            if 'NIK' in df.columns:
                df['NIK'] = df['NIK'].astype(str).str.replace("'", "").str.replace("nan", "").str.strip()
                df['NIK'] = df['NIK'].apply(lambda x: x.split('.')[0])
            return df
        else:
            return None
    except Exception as e:
        return None

df = load_data()

if df is None:
    st.error("⚠️ Database belum siap. Mohon hubungi admin Pos Indonesia Batam.")
    st.stop()

# --- FORM PENCARIAN ---
st.info("Masukkan Nomor Induk Kependudukan (NIK) Anda untuk pengecekan.")
nik_input = st.text_input("NIK (Sesuai KTP):", max_chars=16)

if st.button("🔍 CEK STATUS SAYA", type="primary", use_container_width=True):
    if not nik_input:
        st.warning("Mohon isi NIK terlebih dahulu.")
    else:
        hasil = df[df['NIK'] == nik_input]
        
        if not hasil.empty:
            data = hasil.iloc[0]
            nama_sensor = sensor_teks(data['Nama'])
            alamat_sensor = sensor_teks(data['Alamat'])
            kecamatan = data['Kecamatan']
            kelurahan = data['Kelurahan']
            
            st.success("✅ SELAMAT! ANDA TERDAFTAR SEBAGAI PENERIMA.")
            
            with st.container(border=True):
                st.markdown(f"**NAMA:** \n### {nama_sensor}")
                st.markdown(f"**ALAMAT:** \n{alamat_sensor}")
                st.markdown(f"**WILAYAH:** \n{kelurahan}, {kecamatan}")
            
            st.warning("""
            **📢 INSTRUKSI PENGAMBILAN DI KANTOR POS:**
            
            Silakan datang ke **Kantor Pos Terdekat** dengan membawa:
            1. **KTP Asli** (Elektronik)
            2. **Kartu Keluarga (KK) Asli**
            """)
            
        else:
            st.error("❌ Mohon Maaf, NIK Tidak Ditemukan.")
            st.write("NIK Anda belum terdaftar sebagai penerima bantuan pada tahap ini.")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2025 PT Pos Indonesia (Persero) KCU Batam 29400")
