import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# Impor Modul Subtes 1 - 8
from subtests.subtest_1_se import render_subtest_1_se
from subtests.subtest_2_wa import render_subtest_2_wa
from subtests.subtest_3_an import render_subtest_3_an
from subtests.subtest_4_ge import render_subtest_4_ge
from subtests.subtest_5_ra import render_subtest_5_ra
from subtests.subtest_6_zr import render_subtest_6_zr
from subtests.subtest_7_fa import render_subtest_7_fa
from subtests.subtest_8_wu import render_subtest_8_wu

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Portal Psikotes Potensi Karyawan",
    page_icon="🧠",
    layout="wide"
)

RESULTS_FILE = "rekap_psikotes_karyawan.csv"

# --- HELPER SESI & DISK PERSISTENCE ---
def get_temp_filename(email):
    safe_id = "".join(c for c in email if c.isalnum()) if email else "default"
    return f"temp_state_{safe_id}.json"

def save_app_state(email, user_info, answers, subtest, start_times):
    if not email:
        return
    filename = get_temp_filename(email)
    data = {
        "user_info": user_info,
        "answers": {str(k): v for k, v in answers.items() if v is not None},
        "current_subtest": subtest,
        "start_times": start_times
    }
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass

def load_app_state(email):
    if not email:
        return {}, {}, 1, {}
    filename = get_temp_filename(email)
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                answers = {int(k): v for k, v in data.get("answers", {}).items()}
                return (
                    data.get("user_info", {}),
                    answers,
                    data.get("current_subtest", 1),
                    data.get("start_times", {})
                )
        except Exception:
            pass
    return {}, {}, 1, {}

# --- KUNCI JAWABAN RESMI SUBTES 1 - 8 ---
ANSWER_KEYS_MC = {
    # Subtes 1
    1: "e) kewibawaan", 2: "c) boros", 3: "d) gempa bumi", 4: "d) khianat", 5: "d) kuku",
    6: "b) biasanya", 7: "c) lemak", 8: "a) lawan", 9: "e) hipotesis", 10: "b) sol",
    11: "c) kotak PPPK", 12: "d) 20", 13: "d) konservatif", 14: "e) selalu", 15: "c) 800",
    16: "a) kekuatan", 17: "b) biasanya", 18: "b) Bandung", 19: "c) kemungkinan menang", 20: "b) 130",

    # Subtes 2
    21: "b) panah", 22: "b) memaki", 23: "d) isi", 24: "c) melepaskan", 25: "c) perjalanan",
    26: "c) tugas", 27: "c) payung", 28: "d) kasar", 29: "d) sepeda", 30: "a) biola",
    31: "e) lurus", 32: "a) jam", 33: "a) kebijaksanaan", 34: "b) berjalan", 35: "c) potret",
    36: "a) panjang", 37: "d) gunting", 38: "e) masyarakat", 39: "b) menasehati", 40: "c) bulu",

    # Subtes 3
    41: "c) melupakan", 42: "e) sangkar", 43: "d) jalan raya", 44: "d) gelang", 45: "d) kubus",
    46: "a) menawarkan", 47: "d) tengik", 48: "b) sungai", 49: "e) pelindung", 50: "d) tukang emas",
    51: "c) nada", 52: "c) kelakar", 53: "c) suasana hati", 54: "c) sutra", 55: "d) panjang senar",
    56: "c) mutasi", 57: "c) es", 58: "d) dikikir", 59: "e) mikroskop", 60: "e) lautan api",

    # Subtes 5
    77: "35", 78: "280", 79: "205", 80: "26", 81: "30",
    82: "70", 83: "45", 84: "50", 85: "84", 86: "78",
    87: "19", 88: "6", 89: "75", 90: "90", 91: "120",
    92: "17", 93: "36", 94: "5", 95: "48", 96: "1",

    # Subtes 6
    97: "27", 98: "25", 99: "27", 100: "15", 101: "46",
    102: "10", 103: "42", 104: "7", 105: "5", 106: "14",
    107: "8", 108: "14", 109: "45", 110: "63", 111: "12",
    112: "80", 113: "14", 114: "12", 115: "63", 116: "10",

    # Subtes 7
    117: "a", 118: "c", 119: "d", 120: "b", 121: "d", 122: "e", 123: "c", 124: "e", 125: "e",
    126: "d", 127: "d", 128: "b", 129: "d", 130: "c", 131: "b", 132: "e", 133: "b", 134: "d", 135: "c", 136: "a",

    # Subtes 8
    137: "a", 138: "c", 139: "d", 140: "e", 141: "a", 142: "c", 143: "d", 144: "c", 145: "e",
    146: "a", 147: "b", 148: "d", 149: "e", 150: "b", 151: "d", 152: "b", 153: "a", 154: "e", 155: "b", 156: "c"
}

GE_KEYS = {
    61: {2: ["bunga", "kembang", "perdu"], 1: ["tumbuhan", "tumbuh-tumbuhan", "tangkai", "harum"]},
    62: {2: ["alat indera", "indera", "panca indera"], 1: ["organ", "alat tubuh"]},
    63: {2: ["hablur", "kristal", "zat arang"], 1: ["berkilauan", "mengkilat", "bening"]},
    64: {2: ["musim"], 1: ["cuaca"]},
    65: {2: ["pembawa berita", "alat perhubungan"], 1: ["telekomunikasi", "perhubungan", "komunikasi"]},
    66: {2: ["alat optik", "optik"], 1: ["lensa"]},
    67: {2: ["alat pencernaan", "perut", "isi perut", "pencernaan makanan"], 1: ["jalan makanan"]},
    68: {2: ["jumlah", "kuantitas", "penyebut jumlah", "penyertaan jumlah"], 1: ["mengukur", "ukuran"]},
    69: {2: ["bibit", "bakal", "embrio", "alat pembiak", "permulaan penghidupan"], 1: ["sel", "pembiakan"]},
    70: {2: ["simbol", "lambang", "tanda"], 1: ["nama", "tanda pengenal"]},
    71: {2: ["makhluk", "organism", "makhluk hidup"], 1: ["tumbuh", "ilmu hayat", "biologi"]},
    72: {2: ["wadah", "tempat pengisi", "tempat penyimpan", "tempat"], 1: ["alat", "tempat sesuatu", "benda"]},
    73: {2: ["pengertian waktu", "batas"], 1: ["waktu", "lamanya", "masa", "saat"]},
    74: {2: ["kata sifat", "watak", "sifat karakter"], 1: ["sifat"]},
    75: {2: ["regulator harga", "pengertian ekonomi"], 1: ["dagang", "pembelian", "penjualan", "niaga", "jual beli"]},
    76: {2: ["pengertian ruang", "penyebut ruang"], 1: ["arah", "tempat", "ruang", "letak", "penunjuk tempat", "penentuan daerah"]}
}

def calculate_ge_score(q_id, user_ans):
    if not user_ans:
        return 0
    ans_clean = str(user_ans).strip().lower()
    for kw in GE_KEYS.get(q_id, {}).get(2, []):
        if kw in ans_clean:
            return 2
    for kw in GE_KEYS.get(q_id, {}).get(1, []):
        if kw in ans_clean:
            return 1
    return 0

def calculate_scores():
    user_answers = st.session_state.get("answers", {})
    score_sub1 = sum(1 for q_id in range(1, 21) if user_answers.get(q_id) == ANSWER_KEYS_MC.get(q_id))
    score_sub2 = sum(1 for q_id in range(21, 41) if user_answers.get(q_id) == ANSWER_KEYS_MC.get(q_id))
    score_sub3 = sum(1 for q_id in range(41, 61) if user_answers.get(q_id) == ANSWER_KEYS_MC.get(q_id))
    score_sub4 = sum(calculate_ge_score(q_id, user_answers.get(q_id)) for q_id in range(61, 77))
    score_sub5 = sum(1 for q_id in range(77, 97) if str(user_answers.get(q_id, '')).strip() == ANSWER_KEYS_MC.get(q_id))
    score_sub6 = sum(1 for q_id in range(97, 117) if str(user_answers.get(q_id, '')).strip() == ANSWER_KEYS_MC.get(q_id))
    score_sub7 = sum(1 for q_id in range(117, 137) if str(user_answers.get(q_id, '')).strip().lower() == ANSWER_KEYS_MC.get(q_id))
    score_sub8 = sum(1 for q_id in range(137, 157) if str(user_answers.get(q_id, '')).strip().lower() == ANSWER_KEYS_MC.get(q_id))
    
    total_raw = score_sub1 + score_sub2 + score_sub3 + score_sub4 + score_sub5 + score_sub6 + score_sub7 + score_sub8
    return {
        "Subtes_1": score_sub1,
        "Subtes_2": score_sub2,
        "Subtes_3": score_sub3,
        "Subtes_4": score_sub4,
        "Subtes_5": score_sub5,
        "Subtes_6": score_sub6,
        "Subtes_7": score_sub7,
        "Subtes_8": score_sub8,
        "Total_Skor_Mentah": total_raw
    }

# --- INITIALIZATION & ROUTING ---
params = st.query_params
param_email = params.get("email", "")

if "page" not in st.session_state:
    st.session_state.page = params.get("page", "register")
if "current_subtest" not in st.session_state:
    st.session_state.current_subtest = int(params.get("subtest", "1"))
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "start_times" not in st.session_state:
    st.session_state.start_times = {}

if param_email:
    u_info, u_ans, u_sub, u_times = load_app_state(param_email)
    if u_info:
        st.session_state.user_info.update(u_info)
    if u_ans:
        st.session_state.answers.update(u_ans)
    if u_times:
        st.session_state.start_times.update(u_times)
    if "page" in params:
        st.session_state.page = params["page"]
    if "subtest" in params:
        st.session_state.current_subtest = int(params["subtest"])

email = st.session_state.user_info.get("email", "") or param_email

# --- 1. HALAMAN REGISTRASI ---
if st.session_state.page == "register":
    st.title("🏛️ Portal Psikotes Potensi Karyawan")
    st.subheader("Registrasi Peserta Ujian Online")
    st.info("Mohon isi data diri Anda dengan lengkap sebelum memulai psikotes.")

    with st.form("form_registrasi"):
        nama = st.text_input("Nama Lengkap:")
        email_in = st.text_input("Alamat Email:")
        posisi = st.text_input("Posisi yang Dilamar:", placeholder="Contoh: Staff Operasional / Admin")

        btn_start = st.form_submit_button("Mulai Psikotes 🚀", type="primary")

        if btn_start:
            if not nama or not email_in or not posisi:
                st.error("⚠️ Mohon lengkapi seluruh kolom formulir!")
            else:
                st.session_state.user_info = {
                    "nama": nama,
                    "email": email_in,
                    "posisi": posisi,
                    "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.page = "test"
                st.session_state.current_subtest = 1
                st.query_params["page"] = "test"
                st.query_params["subtest"] = "1"
                st.query_params["email"] = email_in
                
                save_app_state(email_in, st.session_state.user_info, st.session_state.answers, 1, st.session_state.start_times)
                st.rerun()

# --- 2. HALAMAN TEST (ROUTING KE MODUL SUBTES) ---
elif st.session_state.page == "test":
    st.caption(
        f"👤 Peserta: **{st.session_state.user_info.get('nama', '')}** | "
        f"💼 Posisi: **{st.session_state.user_info.get('posisi', '')}**"
    )
    st.markdown("---")

    curr_sub = st.session_state.current_subtest
    if curr_sub == 1:
        render_subtest_1_se()
    elif curr_sub == 2:
        render_subtest_2_wa()
    elif curr_sub == 3:
        render_subtest_3_an()
    elif curr_sub == 4:
        render_subtest_4_ge()
    elif curr_sub == 5:
        render_subtest_5_ra()
    elif curr_sub == 6:
        render_subtest_6_zr()
    elif curr_sub == 7:
        render_subtest_7_fa()
    elif curr_sub == 8:
        render_subtest_8_wu()
    elif curr_sub >= 9:
        st.session_state.page = "result"
        st.query_params["page"] = "result"
        st.rerun()

# --- 3. HALAMAN RESULT ---
elif st.session_state.page == "result":
    st.title("✅ Psikotes Selesai")
    st.success(f"Terima kasih **{st.session_state.user_info.get('nama', '')}**, seluruh jawaban Anda telah berhasil disimpan.")

    scores = calculate_scores()
    record = {**st.session_state.user_info, **scores}

    df_new = pd.DataFrame([record])
    if os.path.exists(RESULTS_FILE):
        df_old = pd.read_csv(RESULTS_FILE, sep=';')
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new

    df_final.to_csv(RESULTS_FILE, index=False, sep=';', encoding='utf-8-sig')

    st.info("Data hasil ujian Anda telah tersimpan secara otomatis di dalam sistem.")
    st.markdown("---")
    if st.button("🔄 Selesai & Kembali ke Halaman Utama", type="primary"):
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()
