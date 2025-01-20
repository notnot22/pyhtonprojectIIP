import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# File untuk menyimpan data
DATA_FILE = "data_keuangan.csv"

# Fungsi untuk memuat data dari file
@st.cache_data
def load_data():
    try:
        return pd.read_csv(DATA_FILE, parse_dates=["Tanggal"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Tanggal", "Kategori", "Tipe", "Jumlah", "Keterangan"])

# Fungsi untuk menyimpan data ke file
def save_data(data):
    data.to_csv(DATA_FILE, index=False)

# Inisialisasi data
if "data_keuangan" not in st.session_state:
    st.session_state["data_keuangan"] = load_data()

# Harga produk
HARGA_PRODUK = {
    "Produk A": 50000,
    "Produk B": 35000,
    "Produk C": 32000,
    "Produk D": 27000,
    "Produk E": 40000
}

# Fungsi untuk menambah data
def tambah_transaksi(tanggal, kategori, tipe, jumlah, keterangan):
    data_baru = pd.DataFrame([{
        "Tanggal": pd.to_datetime(tanggal),
        "Kategori": kategori,
        "Tipe": tipe,
        "Jumlah": jumlah,
        "Keterangan": keterangan,
    }])

    # Tambahkan data baru ke session_state dan simpan ke file
    st.session_state["data_keuangan"] = pd.concat(
        [st.session_state["data_keuangan"], data_baru],
        ignore_index=True
    )
    save_data(st.session_state["data_keuangan"])

# Fungsi untuk menghitung ringkasan
def hitung_ringkasan(data):
    pemasukan = data[data["Tipe"] == "Pemasukan"]["Jumlah"].sum()
    pengeluaran = data[data["Tipe"] == "Pengeluaran"]["Jumlah"].sum()
    saldo = pemasukan - pengeluaran
    return pemasukan, pengeluaran, saldo

# Fungsi untuk membuat laporan berdasarkan rentang waktu
def buat_laporan(data, periode, tanggal_awal=None, tanggal_akhir=None):
    if data.empty:
        return pd.DataFrame()

    data["Tanggal"] = pd.to_datetime(data["Tanggal"])
    if periode == "Harian":
        return data[data["Tanggal"] == pd.Timestamp(datetime.now().date())]
    elif periode == "Rentang Tanggal" and tanggal_awal and tanggal_akhir:
        return data[(data["Tanggal"] >= pd.to_datetime(tanggal_awal)) & (data["Tanggal"] <= pd.to_datetime(tanggal_akhir))]
    return data

# Fungsi untuk membuat grafik
def buat_grafik(data):
    if data.empty:
        st.warning("Tidak ada data untuk ditampilkan dalam grafik.")
        return

    data["Tanggal"] = pd.to_datetime(data["Tanggal"])
    data.sort_values("Tanggal", inplace=True)

    pemasukan = data[data["Tipe"] == "Pemasukan"].groupby("Tanggal")["Jumlah"].sum()
    pengeluaran = data[data["Tipe"] == "Pengeluaran"].groupby("Tanggal")["Jumlah"].sum()

    plt.figure(figsize=(10, 6))
    plt.plot(pemasukan.index, pemasukan.values, label="Pemasukan", marker="o")
    plt.plot(pengeluaran.index, pengeluaran.values, label="Pengeluaran", marker="o")
    plt.title("Grafik Pemasukan dan Pengeluaran")
    plt.xlabel("Tanggal")
    plt.ylabel("Jumlah")
    plt.legend()
    plt.grid()
    st.pyplot(plt)

# Halaman utama
st.title("Aplikasi Pencatatan Keuangan")
st.markdown("Kelola keuangan Anda dengan mudah dan terorganisir.")

# Form untuk menambah transaksi
st.header("Tambah Transaksi")
tanggal = st.date_input("Tanggal", value=datetime.now().date())
tipe = st.radio("Tipe Transaksi", ["Pemasukan", "Pengeluaran"])

if tipe == "Pemasukan":
    st.subheader("Masukkan Jumlah untuk Masing-Masing Produk")
    jumlah_produk = {}
    total_pemasukan = 0
    for produk, harga in HARGA_PRODUK.items():
        jumlah_unit = st.number_input(f"{produk} - Harga per Produk (Rp {harga:,})", min_value=0, step=1, value=0)
        total_harga = jumlah_unit * harga
        jumlah_produk[produk] = total_harga
        total_pemasukan += total_harga

    st.write(f"Total Pemasukan: Rp {total_pemasukan:,.2f}")
    jumlah = total_pemasukan
    kategori = "Penjualan Produk"
else:
    kategori = st.selectbox("Kategori", ["Gaji", "Utilitas", "Perlengkapan", "Sewa"])
    jumlah = st.number_input("Jumlah Pengeluaran (Rp)", min_value=0.0, step=0.01)

keterangan = st.text_area("Keterangan", placeholder="Tuliskan detail transaksi")

if st.button("Tambah Transaksi"):
    try:
        if jumlah > 0:
            if tipe == "Pemasukan":
                for produk, total_harga in jumlah_produk.items():
                    if total_harga > 0:
                        tambah_transaksi(tanggal, produk, tipe, total_harga, keterangan)
            else:
                tambah_transaksi(tanggal, kategori, tipe, jumlah, keterangan)
            st.success("Transaksi berhasil ditambahkan!")
        else:
            st.error("Jumlah harus lebih dari 0.")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

# Menampilkan data keuangan
st.header("Riwayat Transaksi")
if st.session_state["data_keuangan"].empty:
    st.info("Belum ada transaksi yang tercatat.")
else:
    st.dataframe(st.session_state["data_keuangan"])

# Menampilkan ringkasan
st.header("Ringkasan Keuangan")
pemasukan, pengeluaran, saldo = hitung_ringkasan(st.session_state["data_keuangan"])
st.metric("Total Pemasukan", f"Rp {pemasukan:,.2f}")
st.metric("Total Pengeluaran", f"Rp {pengeluaran:,.2f}")
st.metric("Saldo", f"Rp {saldo:,.2f}")

# Menampilkan laporan
st.header("Laporan Keuangan")
periode = st.selectbox("Pilih Periode", ["Harian", "Rentang Tanggal"])
if periode == "Rentang Tanggal":
    tanggal_awal = st.date_input("Tanggal Awal", value=datetime.now().date() - timedelta(days=7))
    tanggal_akhir = st.date_input("Tanggal Akhir", value=datetime.now().date())
    laporan = buat_laporan(st.session_state["data_keuangan"], periode, tanggal_awal, tanggal_akhir)
else:
    laporan = buat_laporan(st.session_state["data_keuangan"], periode)

if laporan.empty:
    st.warning("Tidak ada data untuk periode ini.")
else:
    st.dataframe(laporan)

# Menampilkan grafik
st.header("Grafik Keuangan")
buat_grafik(st.session_state["data_keuangan"])
