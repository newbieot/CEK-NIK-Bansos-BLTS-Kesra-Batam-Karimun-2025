import streamlit as st
import pandas as pd
import io
import qrcode
from PIL import Image

# --- LIBRARY PDF ---
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader, simpleSplit

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Cek Penerima BLTS KESRA - Pos Indonesia Batam",
    page_icon="📮",
    layout="centered"
)

# --- FUNGSI SENSOR (MASKING) ---
def sensor_teks(teks):
    teks = str(teks).strip().upper()
    if len(teks) <= 2: return teks
    kata_kata = teks.split()
    hasil = []
    for kata in kata_kata:
        if len(kata) > 2:
            hasil.append(kata[0] + '*' * (len(kata) - 1))
        else:
            hasil.append(kata)
    return " ".join(hasil)

# --- FUNGSI FORMAT RUPIAH ---
def format_rupiah(angka):
    try:
        val = float(angka)
        return f"Rp {val:,.0f}".replace(",", ".")
    except:
        return str(angka)

# --- FUNGSI GENERATE QR CODE ---
def get_qr_code_image(data_text):
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(str(data_text))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# --- FUNGSI PEMBUAT SURAT (LAYOUT 100% MIRIP) ---
def buat_surat_pdf(data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin_x = 2*cm
    
    # --- 1. HEADER & LOGO ---
    # Logo Pos Indonesia (Kiri Atas)
    try:
        c.drawImage("POSIND_Logo_1. Warna (2) (2)", margin_x, height - 3.5*cm, width=4*cm, preserveAspectRatio=True, mask='auto')
    except:
        pass # Lewati jika tidak ada logo

    # Judul Kanan Atas
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - margin_x, height - 2.5*cm, "PEMBERITAHUAN")
    
    c.setFont("Helvetica", 10)
    no_danom = str(data.get('No Danom', '')).strip()
    if not no_danom or no_danom == 'nan':
        no_danom = f"29400/{data['NIK']}/GEN"
    
    # Nomor Danom & Batch
    c.drawRightString(width - margin_x, height - 3.2*cm, f"Nomor Danom: {no_danom}")
    c.drawRightString(width - margin_x, height - 3.7*cm, f"BATCH ({str(data.get('Batch', 'MB-K01'))})")
    
    # --- 2. KEPADA (ALAMAT) ---
    y_pos = height - 5.5*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_x, y_pos, "KEPADA:")
    y_pos -= 0.5*cm
    c.drawString(margin_x, y_pos, "KEMENTERIAN SOSIAL") # Sesuai contoh
    y_pos -= 0.8*cm
    
    # Nama Penerima (Bold)
    nama = str(data['Nama']).upper()
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin_x, y_pos, nama)
    y_pos -= 0.5*cm
    
    # Alamat Lengkap (Regular)
    c.setFont("Helvetica", 10)
    alamat = str(data['Alamat']).upper()
    kel = str(data['Kelurahan']).upper()
    kec = str(data['Kecamatan']).upper()
    kab = str(data['Kabupaten']).upper()
    
    full_address = f"{alamat} KEL {kel} KEC {kec} {kab}"
    
    # Wrap text alamat (max lebar 10cm)
    lines = simpleSplit(full_address, "Helvetica", 10, 11*cm)
    for line in lines:
        c.drawString(margin_x, y_pos, line)
        y_pos -= 0.4*cm

    # --- 3. ISI SURAT ---
    y_body = height - 10*cm
    c.setFont("Helvetica", 10)
    c.drawString(margin_x, y_body, "Dengan Hormat,")
    y_body -= 0.6*cm
    
    intro = (
        "Berdasarkan Keputusan Pemerintah Republik Indonesia c.q. Kementerian Sosial Republik Indonesia, "
        "Bapak/Ibu/Sdr/i dinyatakan BERHAK memperoleh dana Bantuan Langsung Tunai Sementara "
        "Kesejahteraan Rakyat (BLTS Kesra) Tahun 2025 dari Kementerian Sosial RI dengan rincian dana "
        "bantuan sesuai tabel di bawah:"
    )
    
    body_width = width - (2 * margin_x)
    lines = simpleSplit(intro, "Helvetica", 10, body_width)
    for line in lines:
        c.drawString(margin_x, y_body, line)
        y_body -= 0.5*cm
        
    # --- 4. TABEL NOMINAL ---
    y_body -= 0.5*cm
    # Kotak Tabel
    c.rect(margin_x, y_body - 1.5*cm, body_width, 1.5*cm)
    # Garis Tengah Vertikal
    c.line(margin_x + body_width/2, y_body, margin_x + body_width/2, y_body - 1.5*cm)
    # Garis Header Horizontal
    c.line(margin_x, y_body - 0.7*cm, margin_x + body_width, y_body - 0.7*cm)
    
    # Teks Tabel
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(margin_x + body_width/4, y_body - 0.5*cm, "JENIS BANTUAN")
    c.drawCentredString(margin_x + 3*body_width/4, y_body - 0.5*cm, "JUMLAH DANA")
    
    c.setFont("Helvetica", 10)
    c.drawCentredString(margin_x + body_width/4, y_body - 1.2*cm, "BLTS KESRA 2025")
    c.setFont("Helvetica-Bold", 12)
    nominal = data.get('BSU', 900000)
    c.drawCentredString(margin_x + 3*body_width/4, y_body - 1.2*cm, format_rupiah(nominal))
    
    y_body -= 2.5*cm

    # --- 5. POIN PERHATIAN ---
    c.setFont("Helvetica", 10)
    c.drawString(margin_x, y_body, "Harap menjadi perhatian Bapak/Ibu penerima BLTS Kesra:")
    y_body -= 0.6*cm
    
    points = [
        "1. Persyaratan pengambilan/penerimaan BLTS Kesra Tahun 2025 dengan menunjukan KTP-el dan/atau Kartu Keluarga asli.",
        "2. Penggunaan dana BLTS Kesra Tahun 2025 tidak diperkenankan untuk membeli rokok, minuman keras, dan narkotika.",
        "3. Penyaluran dana BLTS Kesra Tahun 2025 diberikan tanpa ada potongan apapun dan oleh pihak manapun. Jika ada pemotongan silakan lapor ke WA 0812-2333-0332."
    ]
    
    for point in points:
        lines = simpleSplit(point, "Helvetica", 10, body_width)
        for i, line in enumerate(lines):
            offset = 0.4*cm if i > 0 else 0
            c.drawString(margin_x + offset, y_body, line)
            y_body -= 0.5*cm
        y_body -= 0.2*cm

    # --- 6. FOOTER & QR CODE CEKPOS ---
    y_footer = 4.5*cm
    
    # Kiri: Tanggal & Tanda Tangan Teks
    c.setFont("Helvetica", 10)
    c.drawString(width - 8*cm, y_footer, f"Batam, {pd.Timestamp.now().strftime('%d %B %Y')}")
    y_footer -= 0.5*cm
    c.drawString(width - 8*cm, y_footer, "PT POS INDONESIA (PERSERO)")
    y_footer -= 0.5*cm
    c.drawString(width - 8*cm, y_footer, "KCU BATAM 29400")
    
    # QR Code (Berisi Nomor Cekpos)
    # Letak: Di sebelah kanan bawah (area TTD)
    cekpos_val = str(data.get('Cekpos', data['NIK'])) # Pakai Cekpos, fallback ke NIK
    qr_img = get_qr_code_image(cekpos_val)
    
    # Simpan QR ke PDF
    c.drawInlineImage(qr_img, width - 6*cm, y_footer - 3*cm, width=2.5*cm, height=2.5*cm)
    
    # Teks di bawah QR
    c.setFont("Helvetica-Oblique", 7)
    c.drawCentredString(width - 4.75*cm, y_footer - 3.2*cm, f"Cekpos: {cekpos_val}")

    # Disclaimer Bawah
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, 1.5*cm, "Surat ini adalah dokumen sah yang diterbitkan secara elektronik dan tidak memerlukan tanda tangan basah.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# UI WEBSITE
# ==========================================

col_logo, col_judul = st.columns([1, 4])
with col_logo:
    try: st.image("POSIND_Logo_1. Warna (2) (2)", width=130) 
    except: st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Logo_Pos_Indonesia_%282023%29.png/640px-Logo_Pos_Indonesia_%282023%29.png", width=130)

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
    st.error("⚠️ Database belum siap.")
    st.stop()

# --- FORM ---
st.info("Silakan masukkan Nomor Induk Kependudukan (NIK) Anda.")
nik_input = st.text_input("NIK (Sesuai KTP):", max_chars=16)

if st.button("🔍 CEK STATUS SAYA", type="primary", use_container_width=True):
    if not nik_input:
        st.warning("Mohon isi NIK terlebih dahulu.")
    else:
        hasil = df[df['NIK'] == nik_input]
        
        if not hasil.empty:
            data = hasil.iloc[0]
            
            # Tampilan Web (Disensor)
            st.success("✅ SELAMAT! ANDA TERDAFTAR SEBAGAI PENERIMA.")
            with st.container(border=True):
                st.markdown(f"**NAMA:** \n### {sensor_teks(data['Nama'])}")
                st.markdown(f"**ALAMAT:** \n{sensor_teks(data['Alamat'])}")
                st.markdown(f"**WILAYAH:** \n{data['Kelurahan']}, {data['Kecamatan']}")
            
            st.markdown("---")
            st.write("### 📄 Unduh Surat Pemberitahuan")
            st.info("Surat ini wajib dibawa ke Kantor Pos. Data di dalam surat **LENGKAP (TIDAK DISENSOR)**.")
            
            # Download Button
            pdf_bytes = buat_surat_pdf(data)
            st.download_button(
                label="⬇️ UNDUH SURAT PDF",
                data=pdf_bytes,
                file_name=f"Surat_Pemberitahuan_{data['NIK']}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
            
            st.warning("**Jangan lupa bawa KTP & KK Asli saat pencairan.**")
        else:
            st.error("❌ NIK Tidak Ditemukan.")
            st.write("Belum terdaftar sebagai penerima bantuan tahap ini.")

st.markdown("---")
st.caption("© 2025 PT Pos Indonesia (Persero) KCU Batam 29400")
