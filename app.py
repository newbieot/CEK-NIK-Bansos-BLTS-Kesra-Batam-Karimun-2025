import streamlit as st
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Cek Bansos Batam & Karimun", page_icon="📮")

# --- FUNGSI SENSOR (MASKING) ---
def sensor_teks(teks):
    """Mengubah sebagian huruf menjadi bintang (*) agar privasi terjaga"""
    teks = str(teks).strip()
    if len(teks) <= 2:
        return teks # Kalau terlalu pendek, jangan disensor
    
    kata_kata = teks.split()
    hasil_sensor = []
    
    for kata in kata_kata:
        if len(kata) > 2:
            # Ambil huruf pertama, sisanya bintang
            kata_baru = kata[0] + '*' * (len(kata) - 1)
            hasil_sensor.append(kata_baru)
        else:
            hasil_sensor.append(kata)
            
    return " ".join(hasil_sensor)

# --- JUDUL & LOGO ---
st.title("📮 Cek Status Penerima Bansos")
st.subheader("Kota Batam & Kabupaten Karimun T.A 2025")
st.markdown("---")

# --- INPUT PENCARIAN ---
nik_input = st.text_input("Masukkan Nomor Induk Kependudukan (NIK) Anda:", max_chars=16)

# --- TOMBOL CEK ---
if st.button("🔍 Cek Data Saya"):
    if not nik_input:
        st.warning("Mohon isi NIK terlebih dahulu.")
    else:
        # --- BACA DATA (Ganti nama file ini dengan file asli Anda nanti) ---
        # File excel harus satu folder dengan script ini
        try:
            # Menggunakan caching agar website tidak lambat
            @st.cache_data
            def load_data():
                # Ganti nama file di bawah ini sesuai file Excel Anda yang sudah bersih
                df = pd.read_excel("Belum Terbayar 07 Desember 2025 pukul 06.00.xlsx")
                # Pastikan NIK jadi string
                df['NIK'] = df['NIK'].astype(str).str.replace("'", "").str.replace("nan", "").str.strip()
                return df

            df = load_data()
            
            # --- LOGIKA PENCARIAN ---
            # Cari NIK yang persis sama
            hasil = df[df['NIK'] == nik_input]
            
            if not hasil.empty:
                # --- JIKA DATA DITEMUKAN (BERHAK) ---
                data_penerima = hasil.iloc[0]
                
                st.success("✅ SELAMAT! ANDA TERDAFTAR SEBAGAI PENERIMA.")
                
                # Tampilkan Info Tersensor
                st.markdown("### Data Penerima:")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info("**Nama:**")
                    st.write(f"### {sensor_teks(data_penerima['Nama'])}") # Nama disensor
                with col2:
                    st.info("**Alamat:**")
                    st.write(f"### {sensor_teks(data_penerima['Alamat'])}") # Alamat disensor
                
                st.write(f"**Wilayah:** {data_penerima['Kelurahan']}, {data_penerima['Kecamatan']}")
                
                # --- INSTRUKSI PENTING ---
                st.warning("""
                **INSTRUKSI PENGAMBILAN:**
                Silakan datang ke **KANTOR POS TERDEKAT** sesuai domisili.
                
                Wajib Membawa:
                1. **KTP Asli** (Elektronik)
                2. **Kartu Keluarga (KK) Asli**
                3. Screenshot/Fungsi Layar bukti ini (Opsional)
                """)
                
            else:
                # --- JIKA DATA TIDAK DITEMUKAN ---
                st.error("❌ Data NIK tidak ditemukan dalam daftar penerima tahap ini.")
                st.write("Mohon periksa kembali NIK yang Anda masukkan atau hubungi perangkat kelurahan setempat.")
                
        except Exception as e:
            st.error(f"Terjadi kesalahan sistem: {e}")
            st.info("Pastikan file Excel sudah diupload ke sistem.")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2025 Pemerintah Kota Batam & Kabupaten Karimun - Bansos Kesejahteraan Rakyat")