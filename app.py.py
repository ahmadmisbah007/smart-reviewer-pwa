import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. KONFIGURASI HALAMAN & UTILS
# ==========================================
st.set_page_config(
    page_title="Evaluator Judul Skripsi/Tesis - MP, MPI, PAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
    <style>
    .main { padding: 1.5rem; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
    .metric-box { padding: 1rem; border-radius: 10px; background-color: #f0f2f6; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Inisialisasi Session State untuk Menyimpan Riwayat Review (Database Sementara)
if "history_reviews" not in st.session_state:
    st.session_state["history_reviews"] = []

st.title("🎓 Sistem Evaluasi & Review Judul Skripsi/Tesis")
st.caption("Asisten Kaprodi untuk Penilaian Kelayakan Judul Multiprodi (MP, MPI, PAI)")

# ==========================================
# 2. FORMULIR INPUT MAHASISWA
# ==========================================
st.subheader("📋 Form Pengajuan Judul Mahasiswa")

col1, col2 = st.columns([1, 1])

with col1:
    nama = st.text_input("Nama Lengkap Mahasiswa", placeholder="Contoh: Ahmad Syarifuddin")
    nim = st.text_input("NIM / ID Mahasiswa", placeholder="Contoh: 202100123")
    jenjang = st.radio("Jenjang Program", ["S1 Skripsi", "S2 Tesis"], horizontal=True)
    
    prodi = st.selectbox("Program Studi", [
        "MPI (Manajemen Pendidikan Islam)", 
        "MP (Manajemen Pendidikan)", 
        "PAI (Pendidikan Agama Islam)"
    ])

with col2:
    # Logic Rumpun Kajian Dinamis Sesuai Prodi
    if "MPI" in prodi:
        options_rumpun = [
            "Manajemen Lembaga Pendidikan Islam (Pesantren/Madrasah/SIT)",
            "Kepemimpinan & Manajemen Strategis Pendidikan Islam",
            "Manajemen SDM & Supervisi Pendidikan Islam",
            "Manajemen Kurikulum & Pembelajaran Keislaman",
            "Manajemen Keuangan, Wakaf & Sarpras Lembaga Islam",
            "Manajemen Humas, Pemasaran & Digital Branding",
            "Manajemen Kesiswaan & Kesantrian (Boarding System)",
            "Manajemen Sistem Informasi & Digitalisasi Pendidikan Islam"
        ]
    elif "MP" in prodi:
        options_rumpun = [
            "Manajemen Satuan & Organisasi Pendidikan (Sekolah/PT)",
            "Kepemimpinan & Manajemen Strategis Pendidikan",
            "Manajemen Penjaminan Mutu & Akreditasi Sekolah",
            "Manajemen SDM & Supervisi Pendidikan",
            "Manajemen Kurikulum & Pembelajaran",
            "Manajemen Pembiayaan, Sarana & Prasarana",
            "Manajemen Humas, Pemasaran & Kemitraan Sekolah/DUDI",
            "Manajemen Sistem Informasi & Digitalisasi Pendidikan"
        ]
    else:  # PAI
        options_rumpun = [
            "Metodologi & Inovasi Pembelajaran PAI",
            "Pengembangan Kurikulum & Bahan Ajar PAI",
            "Evaluasi & Asesmen Pembelajaran PAI",
            "Pendidikan Karakter & Moderasi Beragama",
            "Psikologi & Bimbingan Konseling Islam dalam Pembelajaran",
            "Pendidikan Agama Islam Berbasis Digital / EdTech",
            "Pendidikan Agama Islam dalam Keluarga & Masyarakat",
            "Studi Teks & Pemikiran Pendidikan Islam"
        ]

    rumpun = st.selectbox("Rumpun / Scope Kajian", options_rumpun)
    
    metode = st.selectbox("Metode Penelitian", [
        "Kualitatif (Studi Lapangan / Field Research)",
        "Kualitatif (Penelitian Pustaka / Library Research)",
        "Kuantitatif",
        "Mixed Methods",
        "R&D (Research & Development)"
    ])
    
    lokus = st.text_input(
        "Lokus / Objek Penelitian Utama", 
        placeholder="Nama Sekolah/Pesantren (Lapangan) atau Nama Tokoh/Buku/Regulasi (Pustaka)"
    )

st.markdown("---")
st.subheader("📖 Substansi Akademik & Integrasi")

judul = st.text_area("Usulan Judul Skripsi / Tesis", placeholder="Masukkan judul lengkap yang diajukan...")
rumusan_masalah = st.text_area("Rumusan Masalah Utama", placeholder="1. Bagaimana...\n2. Bagaimana...", height=100)

# Form Khusus Integrasi Keislaman untuk MPI & PAI
integrasi_keislaman = ""
if "MPI" in prodi or "PAI" in prodi:
    integrasi_keislaman = st.text_input(
        "Integrasi Nilai Keislaman (Wajib untuk MPI & PAI)", 
        placeholder="Rujukan Ayat Al-Qur'an, Hadis, atau Kaidah Fiqhiyah/Pedagogis"
    )

# ==========================================
# 3. ENGINE EVALUASI AI (AUTO-REVIEWER)
# ==========================================
if st.button("🚀 Process & Review Judul"):
    if not nama or not judul or not rumusan_masalah or not lokus:
        st.error("⚠️ Silakan lengkapi Nama, Judul, Lokus/Objek Penelitian, dan Rumusan Masalah terlebih dahulu.")
    else:
        score = 0
        feedback = []
        is_pustaka = "Pustaka" in metode

        # A. Evaluasi Lokus & Objek Penelitian (30 Poin)
        if is_pustaka:
            keywords_pustaka = ["perspektif", "pemikiran", "konsep", "analisis", "kebijakan", "uu", "permendikbud", "kitab", "buku", "tokoh", "tafsir"]
            has_pustaka_kw = any(kw in judul.lower() or kw in lokus.lower() for kw in keywords_pustaka)
            if has_pustaka_kw:
                score += 30
                feedback.append("✅ **Objek Pustaka Teridentifikasi**: Judul dan objek kajian memuat spesifikasi tokoh, karya, atau regulasi yang jelas.")
            else:
                score += 15
                feedback.append("⚠️ **Objek Pustaka Kurang Spesifik**: Disarankan mempertegas nama tokoh, buku, atau kebijakan yang menjadi fokus kaji.")
        else:
            if len(lokus) > 3:
                score += 30
                feedback.append("✅ **Lokus Penelitian Lapangan Clear**: Objek/lokasi penelitian terdefinisi secara spesifik.")
            else:
                score += 10
                feedback.append("⚠️ **Lokus Belum Jelas**: Sebutkan lokasi spesifik (misal: nama madrasah/sekolah/pesantren).")

        # B. Evaluasi Kata Kunci Sesuai Prodi & Rumpun (35 Poin)
        text_full = (judul + " " + rumusan_masalah).lower()
        
        if "MPI" in prodi:
            kw_prodi = ["manajemen", "kelola", "strategi", "kepemimpinan", "mutu", "sdm", "keuangan", "pesantren", "madrasah", "pengelolaan"]
        elif "MP" in prodi:
            kw_prodi = ["manajemen", "kelola", "strategi", "kepemimpinan", "mutu", "sdm", "keuangan", "sekolah", "supervisi", "pengelolaan"]
        else: # PAI
            kw_prodi = ["pembelajaran", "kurikulum", "metode", "media", "hasil belajar", "akhlak", "karakter", "pai", "pendidikan agama islam", "didaktik"]

        matched_kw = [kw for kw in kw_prodi if kw in text_full]
        if len(matched_kw) >= 2:
            score += 35
            feedback.append(f"✅ **Kesesuaian Prodi ({prodi})**: Terdeteksi kata kunci akademis yang kuat ({', '.join(matched_kw[:3])}).")
        else:
            score += 15
            feedback.append(f"⚠️ **Kesesuaian Prodi**: Kata kunci khas rumpun {prodi} masih minim dalam judul/rumusan masalah.")

        # C. Evaluasi Integrasi Keislaman (15 Poin)
        if "MPI" in prodi or "PAI" in prodi:
            if len(integrasi_keislaman) > 5:
                score += 15
                feedback.append("✅ **Integrasi Keislaman**: Terisi rujukan dalil/nilai keislaman pendukung.")
            else:
                feedback.append("⚠️ **Integrasi Keislaman**: Dihimbau mengisi landasan dalil Al-Qur'an/Hadis/Kaidah.")
        else:
            score += 15  # Default full point untuk MP Umum

        # D. Evaluasi Kebaruan & Relevansi / Novelty (20 Poin)
        kw_novelty = ["digital", "era 5.0", "inovasi", "modern", "relevansi", "kontemporer", "kurikulum merdeka", "spmi", "dudi"]
        if any(kw in text_full for kw in kw_novelty):
            score += 20
            feedback.append("✅ **Kebaruan Isu (Novelty)**: Judul diangkat dari isu kontemporer/modern.")
        else:
            score += 10
            feedback.append("ℹ️ **Saran Kebaruan**: Pertimbangkan menambahkan variabel kontekstual (misal: era digital, kurikulum merdeka, dll).")

        # Tentukan Status Final ACC
        if score >= 80:
            status_acc = "LAYAK ACC"
        elif score >= 60:
            status_acc = "REVISI RINGAN"
        else:
            status_acc = "PERLU DITINJAU / TOLAK"

        # Simpan ke Data Riwayat (Session State)
        data_row = {
            "Tanggal": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "NIM": nim,
            "Nama": nama,
            "Prodi": prodi,
            "Jenjang": jenjang,
            "Judul": judul,
            "Lokus/Objek": lokus,
            "Rumpun": rumpun,
            "Metode": metode,
            "Skor AI": score,
            "Status ACC": status_acc,
            "Integrasi Keislaman": integrasi_keislaman if integrasi_keislaman else "-"
        }
        st.session_state["history_reviews"].append(data_row)

        # ==========================================
        # 4. TAMPILAN HASIL EVALUASI (DASHBOARD)
        # ==========================================
        st.markdown("---")
        st.header("📊 Hasil Evaluasi Auto-Reviewer AI")

        col_res1, col_res2 = st.columns([1, 2])

        with col_res1:
            st.metric(label="Skor Kelayakan", value=f"{score} / 100")
            if status_acc == "LAYAK ACC":
                st.success(f"STATUS: {status_acc}")
            elif status_acc == "REVISI RINGAN":
                st.warning(f"STATUS: {status_acc}")
            else:
                st.error(f"STATUS: {status_acc}")

        with col_res2:
            st.subheader("Catatan & Feedback Evaluator:")
            for item in feedback:
                st.write(item)

        # ==========================================
        # 5. REKOMENDASI DUAL-MODEL RUMUSAN MASALAH
        # ==========================================
        st.markdown("---")
        st.subheader("💡 Rekomendasi Refinansi Rumusan Masalah")
        st.write("Kaprodi dapat menyarankan salah satu dari 2 opsi template rumusan masalah baku berikut kepada mahasiswa:")

        tab1, tab2 = st.tabs(["Opsi A: Model Alur Manajerial / POAC", "Opsi B: Model Sub-Strategi & Relevansi"])

        with tab1:
            st.info("**Opsi A (Cocok untuk Penelitian Lapangan & Manajemen Operasional)**")
            st.markdown(f"""
            1. Bagaimana **perencanaan** {judul} di {lokus}?
            2. Bagaimana **pelaksanaan / pengorganisasian** {judul} di {lokus}?
            3. Bagaimana **evaluasi dan pengawasan** {judul} di {lokus}?
            """)

        with tab2:
            st.info("**Opsi B (Cocok untuk Penelitian Pustaka, Strategis, & PAI)**")
            st.markdown(f"""
            1. Bagaimana **konsep dasar dan formulasi** {judul}?
            2. Bagaimana **analisis kritis/implementasi** {judul} pada {lokus}?
            3. Bagaimana **relevansi dan implikasi** {judul} terhadap tantangan pendidikan saat ini?
            """)

# ==========================================
# 6. PANEL KAPRODI: REKAP DATA & EKSPOR EXCEL
# ==========================================
st.markdown("---")
st.header("📂 Panel Rekapitulasi Kaprodi & Ekspor Data")

if len(st.session_state["history_reviews"]) > 0:
    df_history = pd.DataFrame(st.session_state["history_reviews"])
    st.dataframe(df_history, use_container_width=True)

    col_dl1, col_dl2 = st.columns(2)

    with col_dl1:
        # Ekspor ke CSV
        csv_data = df_history.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Rekap Data (CSV)",
            data=csv_data,
            file_name=f"rekap_review_judul_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    with col_dl2:
        # Ekspor ke Excel (.xlsx)
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_history.to_excel(writer, index=False, sheet_name='Rekap Review')
        
        st.download_button(
            label="📊 Download Rekap Data (Excel .xlsx)",
            data=buffer.getvalue(),
            file_name=f"rekap_review_judul_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Belum ada data judul yang diproses pada sesi ini. Silakan isi form di atas dan klik 'Process & Review Judul'.")