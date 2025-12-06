import streamlit as st
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Cek Bansos Batam & Karimun",
    page_icon="📮",
    layout="centered"
)

# --- FUNGSI SENSOR (MASKING) ---
def sensor_teks(teks):
    """Mengubah teks menjadi tersensor (Budi -> B***)"""
    teks = str(teks).strip().upper()
    if len(teks) <= 2:
        return teks
    
    kata_kata = teks.split()
    hasil = []
    
    for kata in kata_kata:
        if len(kata) > 2:
            # Ambil huruf pertama, sisanya bintang
            # Contoh: BATAM -> B****
            kata_baru = kata[0] + '*' * (len(kata) - 1)
            hasil.append(kata_baru)
        else:
            hasil.append(kata)
    return " ".join(hasil)

# --- JUDUL & HEADER ---
st.title("📮 Cek Bansos Kesejahteraan Rakyat")
st.write("Pemerintah Kota Batam & Kabupaten Karimun T.A 2025")
st.markdown("---")

# --- LOAD DATA (CACHE AGAR CEPAT) ---
@st.cache_data
def load_data():
    # Ganti nama file ini sesuai file Excel Anda
    file_path = "Belum Terbayar 07 Desember 2025 pukul 06.00.xlsx"
    
    # Baca Excel, cari sheet yang ada datanya (seperti script kita sebelumnya)
    xls = pd.ExcelFile(file_path)
    target_sheet = None
    header_row = 0
    
    for sheet in xls.sheet_names:
        df_tmp = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=10)
        # Cari sheet yang ada kolom NIK
        for i, row in df_tmp.iterrows():
            row_str = row.astype(str).str.lower().tolist()
            if any('nik' in s for s in row_str) and any('nama' in s for s in row_str):
                target_sheet = sheet
                header_row = i
                break
        if target_sheet: break
    
    if target_sheet:
        df = pd.read_excel(xls, sheet_name=target_sheet, header=header_row)
        # Bersihkan NIK
        df.columns = df.columns.str.strip()
        if 'NIK' in df.columns:
            df['NIK'] = df['NIK'].astype(str).str.replace("'", "").str.replace("nan", "").str.strip()
            # Pastikan NIK yang ada .0 di belakang (format excel) hilang
            df['NIK'] = df['NIK'].apply(lambda x: x.split('.')[0])
        return df
    else:
        return None

try:
    df = load_data()
    if df is None:
        st.error("Gagal memuat database. Hubungi Admin.")
        st.stop()
except Exception as e:
    st.error(f"Error Database: {e}")
    st.stop()

# --- FORM PENCARIAN ---
st.info("Silakan masukkan NIK (Nomor Induk Kependudukan) sesuai KTP untuk mengecek status.")
nik_input = st.text_input("Masukkan NIK Anda:", max_chars=16, placeholder="Contoh: 2171xxxxxxxxx")

if st.button("🔍 CEK STATUS SAYA", type="primary"):
    if not nik_input:
        st.warning("Mohon isi NIK terlebih dahulu.")
    else:
        # Cari NIK
        hasil = df[df['NIK'] == nik_input]
        
        if not hasil.empty:
            # --- JIKA DITEMUKAN (BERHAK) ---
            data = hasil.iloc[0]
            nama_sensor = sensor_teks(data['Nama'])
            alamat_sensor = sensor_teks(data['Alamat'])
            kecamatan = data['Kecamatan']
            kelurahan = data['Kelurahan']
            
            st.success("✅ SELAMAT! ANDA TERDAFTAR SEBAGAI PENERIMA.")
            
            # Tampilkan Kartu Data
            with st.container(border=True):
                st.markdown(f"**NAMA:** \n### {nama_sensor}")
                st.markdown(f"**ALAMAT:** \n{alamat_sensor}")
                st.markdown(f"**WILAYAH:** \n{kelurahan}, {kecamatan}")
            
            # Instruksi Pengambilan
            st.warning("""
            **📢 INSTRUKSI PENGAMBILAN:**
            
            Silakan datang ke **KANTOR POS TERDEKAT** sesuai domisili Anda.
            
            **WAJIB MEMBAWA DOKUMEN ASLI:**
            1. **KTP Asli** (Elektronik)
            2. **Kartu Keluarga (KK) Asli**
            
            *Mohon tunjukkan bukti tampilan ini kepada petugas jika diperlukan.*
            """)
            
        else:
            # --- JIKA TIDAK DITEMUKAN ---
            st.error("❌ Mohon Maaf, NIK tidak ditemukan.")
            st.write("NIK Anda belum terdaftar sebagai penerima bantuan pada tahap ini.")
            st.caption("Pastikan NIK yang Anda masukkan sudah benar sesuai KTP.")

# --- FOOTER ---
st.markdown("---")
st.caption("Sistem Pengecekan Mandiri - Data per Desember 2025")
