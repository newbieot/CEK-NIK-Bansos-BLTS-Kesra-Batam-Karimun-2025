import streamlit as st
import pandas as pd
import io
import qrcode
import os
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

# --- FUNGSI SENSOR ---
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

# --- FUNGSI QR CODE ---
def get_qr_code_image(data_text):
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(str(data_text))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

# --- FUNGSI BANTUAN GAMBAR ---
def gambar_safe(c, path, x, y, width, height):
    """Menggambar logo jika file ada, jika tidak ada dilewati agar tidak error"""
    if os.path.exists(path):
        try:
            c.drawImage(path, x, y, width=width, height=height, preserveAspectRatio=True, mask='auto')
        except:
            pass # Skip jika file rusak

# --- FUNGSI PEMBUAT SURAT (REVISI FINAL) ---
def buat_surat_pdf(data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin_x = 2*cm
    
    # ==============================
    # 1. KOP SURAT (3 LOGO)
    # ==============================
    y_logo = height - 2.5*cm # Posisi Y Logo
    
    # A. Logo PosIND (Kiri)
    gambar_safe(c, "Logo PosIND.png", margin_x, y_logo - 0.5*cm, 3.5*cm, 1.8*cm)

    # B. Logo Garuda (Tengah)
    # Hitung tengah halaman
    garuda_w = 2.0*cm
    x_garuda = (width / 2) - (garuda_w / 2)
    gambar_safe(c, "garuda.png", x_garuda, y_logo - 0.5*cm, garuda_w, 2.0*cm)

    # C. Logo Kemensos (Kanan)
    kemensos_w = 3.5*cm
    x_kemensos = width - margin_x - kemensos_w
    gambar_safe(c, "kemensos.png", x_kemensos, y_logo - 0.5*cm, kemensos_w, 1.8*cm)

    # ==============================
    # 2. HEADER JUDUL
    # ==============================
    # Turun di bawah logo
    y_header = y_logo - 1.5*cm
    
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - margin_x, y_header, "PEMBERITAHUAN")
    
    c.setFont("Helvetica", 10)
    no_danom = str(data.get('No Danom', '')).strip()
    if not no_danom or no_danom == 'nan':
        no_danom = f"29400/{data['NIK']}/GEN"
    
    batch_txt = f"BATCH ({str(data.get('Batch', 'MB-K01'))})"
    
    c.drawRightString(width - margin_x, y_header - 0.5*cm, f"Nomor Danom: {no_danom}")
    c.drawRightString(width - margin_x, y_header - 1.0*cm, batch_txt)
    
    # ==============================
    # 3. KEPADA (REVISI: HAPUS KATA KEMENSOS)
    # ==============================
    y_pos = y_header - 2.5*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin_x, y_pos, "KEPADA:")
    y_pos -= 0.5*cm
    c.drawString(margin_x, y_pos, "YTH. PENERIMA BANTUAN SOSIAL")
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
    
    # Wrap text alamat
    lines = simpleSplit(full_address, "Helvetica", 10, 11*cm)
    for line in lines:
        c.drawString(margin_x, y_pos, line)
        y_pos -= 0.4*cm

    # ==============================
    # 4. ISI SURAT
    # ==============================
    y_body = height - 11*cm 
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
        
    # TABEL
    y_body -= 0.5*cm
    c.rect(margin_x, y_body - 1.5*cm, body_width, 1.5*cm)
    c.line(margin_x + body_width/2, y_body, margin_x + body_width/2, y_body - 1.5*cm)
    c.line(margin_x, y_body - 0.7*cm, margin_x + body_width, y_body - 0.7*cm)
    
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(margin_x + body_width/4, y_body - 0.5*cm, "JENIS BANTUAN")
    c.drawCentredString(margin_x + 3*body_width/4, y_body - 0.5*cm, "JUMLAH DANA")
    
    c.setFont("Helvetica", 10)
    c.drawCentredString(margin_x + body_width/4, y_body - 1.2*cm, "BLTS KESRA 2025")
    c.setFont("Helvetica-Bold", 12)
    nominal = data.get('BSU', 900000)
    c.drawCentredString(margin_x + 3*body_width/4, y_body - 1.2*cm, format_rupiah(nominal))
    
    y_body -= 2.5*cm

    # POIN PERHATIAN
    c.setFont("Helvetica", 10)
    c.drawString(margin_x, y_body, "Harap menjadi perhatian Bapak/Ibu penerima BLTS Kesra:")
    y_body -= 0.6*cm
    
    points = [
        "1. Persyaratan pengambilan/penerimaan BLTS Kesra Tahun 2025 dengan menunjukan KTP-el dan/atau Kartu Keluarga asli.",
        "2. Penggunaan dana BLTS Kesra Tahun 2025 tidak diperkenankan untuk membeli rokok, minuman keras, dan narkotika.",
        "3. Penyaluran dana BLTS Kesra Tahun 2025 diberikan tanpa ada potongan apapun. Jika ada pemotongan, lapor ke WA 0812-2333-0332."
    ]
    
    for point in points:
        lines = simpleSplit(point, "Helvetica", 10, body_width)
        for i, line in enumerate(lines):
            offset = 0.4*cm if i > 0 else 0
            c.drawString(margin_x + offset, y_body, line)
            y_body -= 0.5*cm
        y_body -= 0.2*cm

    # ==============================
    # 5. FOOTER (TTD & QR)
    # ==============================
    y_ttd_start = 5.5 * cm  
    right_align_x = width - margin_x 
    
    c.setFont("Helvetica", 10)
    c.drawRightString(right_align_x, y_ttd_start, f"Batam, {pd.Timestamp.now().strftime('%d %B %Y')}")
    c.drawRightString(right_align_x, y_ttd_start - 0.5*cm, "PT POS INDONESIA (PERSERO)")
    c.drawRightString(right_align_x, y_ttd_start - 1.0*cm, "KCU BATAM 29400")
    
    # QR CODE
    qr_size = 2.5 * cm
    qr_y_pos = 2.2 * cm 
    qr_x_pos = right_align_x - qr_size 
    
    cekpos_val = str(data.get('Cekpos', data['NIK']))
    qr_img = get_qr_code_image(cekpos_val)
    
    c.drawInlineImage(qr_img, qr_x_pos, qr_y_pos, width=qr_size, height=qr_size)
    c.setFont("Helvetica-Oblique", 7)
    c.drawCentredString(qr_x_pos + (qr_size/2), qr_y_pos - 0.3*cm, f"Cekpos: {cekpos_val}")

    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, 1.0*cm, "Surat ini adalah dokumen sah yang diterbitkan secara elektronik dan tidak memerlukan tanda tangan basah.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ==========================================
# UI WEBSITE
# ==========================================

col_logo, col_judul = st.columns([1, 4])
with col_logo:
    # Menggunakan Logo PosIND.png untuk tampilan website juga
    if os.path.exists("Logo PosIND.png"):
        st.image("Logo PosIND.png", width=130)
    else:
        # Cadangan jika belum upload
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
    st.error("⚠️ Database belum siap.")
    st.stop()

st.info("Silakan masukkan Nomor Induk Kependudukan (NIK) Anda.")
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
            
            st.markdown("---")
            st.write("### 📄 Unduh Surat Pemberitahuan")
            st.info("Unduh surat ini sebagai bukti valid.")
            
            pdf_bytes = buat_surat_pdf(data)
            st.download_button(
                label="⬇️ UNDUH SURAT PDF",
                data=pdf_bytes,
                file_name=f"Surat_{data['NIK']}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
            st.warning("**Wajib membawa KTP & KK Asli saat pencairan.**")
        else:
            st.error("❌ NIK Tidak Ditemukan.")

st.markdown("---")
st.caption("© 2025 PT Pos Indonesia (Persero) KCU Batam 29400")
