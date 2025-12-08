import streamlit as st
import pandas as pd
import io
from PIL import Image

# --- LIBRARY UNTUK PDF ---
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Cek Penerima BLTS KESRA - Pos Indonesia Batam",
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

# --- FUNGSI FORMAT RUPIAH ---
def format_rupiah(angka):
    try:
        return f"Rp {int(angka):,}".replace(",", ".")
    except:
        return str(angka)

# --- FUNGSI PEMBUAT SURAT PDF (MIRIP CONTOH) ---
def buat_surat_pdf(data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # --- 1. LOGO & KOP SURAT ---
    try:
        # Gunakan logo lokal jika ada, atau link jika tidak ada
        logo_path = "POSIND_Logo_1. Warna (2) (2).png" 
        c.drawImage(logo_path, 2*cm, height - 3.5*cm, width=3*cm, preserveAspectRatio=True, mask='auto')
    except:
        pass # Jika logo gagal load, lewati saja

    # Judul Besar Kanan
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 2*cm, height - 2.5*cm, "PEMBERITAHUAN")
    
    c.setFont("Helvetica", 10)
    # Nomor Danom & Batch (Ambil dari data, kalau tidak ada pakai default)
    no_danom = str(data.get('No Danom', f"29400/{data['NIK']}/GEN"))
    batch = str(data.get('Batch', 'MB-K01'))
    
    c.drawRightString(width - 2*cm, height - 3*cm, f"Nomor Danom: {no_danom}")
    c.drawRightString(width - 2*cm, height - 3.5*cm, f"BATCH ({batch})")

    # Garis Pembatas
    c.setLineWidth(1)
    c.line(2*cm, height - 4*cm, width - 2*cm, height - 4*cm)

    # --- 2. KOTAK KEPADA (ALAMAT) ---
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, height - 5*cm, "KEPADA:")
    c.drawString(2*cm, height - 5.5*cm, "YTH. PENERIMA BANTUAN SOSIAL")
    
    # Kotak Nama & Alamat (Tanpa Sensor)
    c.rect(2*cm, height - 9*cm, 10*cm, 3*cm)
    
    text_object = c.beginText(2.5*cm, height - 6.5*cm)
    text_object.setFont("Helvetica-Bold", 11)
    text_object.textLine(str(data['Nama']).upper()) # NAMA ASLI
    
    text_object.setFont("Helvetica", 10)
    text_object.textLine(str(data['Alamat']).upper()) # ALAMAT ASLI
    text_object.textLine(f"KEL. {str(data['Kelurahan']).upper()}")
    text_object.textLine(f"KEC. {str(data['Kecamatan']).upper()}")
    text_object.textLine(f"KOTA/KAB {str(data['Kabupaten']).upper()}")
    c.drawText(text_object)

    # --- 3. ISI SURAT ---
    start_y = height - 10*cm
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, start_y, "Dengan Hormat,")
    
    paragraf1 = [
        "Berdasarkan Keputusan Pemerintah Republik Indonesia c.q. Kementerian Sosial Republik",
        "Indonesia, Bapak/Ibu/Sdr/i dinyatakan BERHAK memperoleh dana Bantuan Langsung Tunai",
        "Sementara Kesejahteraan Rakyat (BLTS Kesra) Tahun 2025 dengan rincian sebagai berikut:"
    ]
    
    text_y = start_y - 0.7*cm
    for line in paragraf1:
        c.drawString(2*cm, text_y, line)
        text_y -= 0.5*cm
        
    # --- 4. TABEL RINCIAN BANTUAN ---
    text_y -= 0.5*cm
    c.setFont("Helvetica-Bold", 12)
    nilai_bantuan = data.get('BSU', 900000) # Default 900rb jika kolom BSU tidak ada
    c.drawString(3*cm, text_y, f"Total Bantuan: {format_rupiah(nilai_bantuan)}")
    
    # --- 5. SYARAT & KETENTUAN ---
    text_y -= 1.5*cm
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, text_y, "Harap menjadi perhatian Bapak/Ibu penerima BLTS Kesra:")
    text_y -= 0.7*cm
    
    poin_poin = [
        "1. Persyaratan pengambilan dengan menunjukan KTP-el Asli dan/atau Kartu Keluarga Asli.",
        "2. Penggunaan dana BLTS Kesra tidak diperkenankan untuk membeli rokok, minuman keras,",
        "   dan narkotika.",
        "3. Penyaluran dana ini diberikan TANPA ADA POTONGAN APAPUN oleh pihak manapun.",
        "   Jika ada pemotongan oleh Petugas Kantorpos, laporkan ke WA 0812-2333-0332."
    ]
    
    for line in poin_poin:
        c.drawString(2*cm, text_y, line)
        text_y -= 0.5*cm

    # --- 6. FOOTER / TTD ---
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width/2, 2*cm, "Surat ini diterbitkan secara elektronik oleh PT Pos Indonesia (Persero) dan sah tanpa tanda tangan basah.")
    c.drawCentredString(width/2, 1.5*cm, f"Dicetak pada tanggal: {pd.Timestamp.now().strftime('%d-%m-%Y')}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# UI / TAMPILAN WEBSITE
# ==========================================

col_logo, col_judul = st.columns([1, 4])
with col_logo:
    try:
        st.image("logo.png", width=130) 
    except:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Logo_Pos_Indonesia_%282023%29.png/640px-Logo_Pos_Indonesia_%282023%29.png", width=130)

with col_judul:
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
    st.error("⚠️ Sistem sedang sibuk atau File Database belum terdeteksi.")
    st.stop()

# --- FORM INPUT ---
st.info("Silakan masukkan Nomor Induk Kependudukan (NIK) Anda.")
nik_input = st.text_input("NIK (Sesuai KTP):", max_chars=16)

if st.button("🔍 CEK STATUS SAYA", type="primary", use_container_width=True):
    if not nik_input:
        st.warning("Mohon isi NIK terlebih dahulu.")
    else:
        hasil = df[df['NIK'] == nik_input]
        
        if not hasil.empty:
            # --- JIKA DATA DITEMUKAN ---
            data = hasil.iloc[0]
            
            # Data Sensor untuk Tampilan Layar
            nama_sensor = sensor_teks(data['Nama'])
            alamat_sensor = sensor_teks(data['Alamat'])
            kecamatan = data['Kecamatan']
            kelurahan = data['Kelurahan']
            
            st.success("✅ SELAMAT! ANDA TERDAFTAR SEBAGAI PENERIMA.")
            
            with st.container(border=True):
                st.markdown(f"**NAMA PENERIMA:** \n### {nama_sensor}")
                st.markdown(f"**ALAMAT:** \n{alamat_sensor}")
                st.markdown(f"**WILAYAH:** \n{kelurahan}, {kecamatan}")
            
            st.markdown("---")
            st.write("### 📄 Unduh Surat Pemberitahuan")
            st.info("Silakan unduh surat di bawah ini. Data di dalam surat **TIDAK DISENSOR** untuk keperluan verifikasi di Kantor Pos.")
            
            # --- GENERATE PDF ---
            pdf_bytes = buat_surat_pdf(data)
            
            # --- TOMBOL DOWNLOAD ---
            st.download_button(
                label="⬇️ UNDUH SURAT PEMBERITAHUAN (PDF)",
                data=pdf_bytes,
                file_name=f"Surat_Pemberitahuan_{data['NIK']}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
            
            st.warning("""
            **📢 INSTRUKSI PENGAMBILAN:**
            Bawa Surat Pemberitahuan ini (boleh digital/di-print) beserta **KTP & KK Asli** ke Kantor Pos.
            """)
            
        else:
            st.error("❌ Mohon Maaf, NIK Tidak Ditemukan.")
            st.write("NIK Anda belum terdaftar sebagai penerima bantuan pada tahap ini.")
            st.caption("Pastikan NIK yang dimasukkan sudah benar.")

st.markdown("---")
st.caption("© 2025 PT Pos Indonesia (Persero) KCU Batam 29400")

