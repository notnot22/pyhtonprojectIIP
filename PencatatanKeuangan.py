import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Fungsi untuk menginisialisasi data
@st.cache_data
def initialize_data():
    return pd.DataFrame(columns=["Tanggal", "Kategori", "Tipe", "Jumlah", "Keterangan"])

# Inisialisasi data
if "data_keuangan" not in st.session_state:
    st.session_state["data_keuangan"] = initialize_data()

# Fungsi untuk menambah data
def tambah_transaksi(tanggal, kategori, tipe, jumlah, keterangan):
    data_baru = {
        "Tanggal": tanggal,
        "Kategori": kategori,
        "Tipe": tipe,
        "Jumlah": jumlah,
        "Keterangan": keterangan,
    }
    st.session_state["data_keuangan"] = pd.concat(
        [st.session_state["data_keuangan"], pd.DataFrame([data_baru])],
        ignore_index=True,
    )

# Fungsi untuk menghitung ringkasan
def hitung_ringkasan(data):
    pemasukan = data[data["Tipe"] == "Pemasukan"]["Jumlah"].sum()
    pengeluaran = data[data["Tipe"] == "Pengeluaran"]["Jumlah"].sum()
    saldo = pemasukan - pengeluaran
    return pemasukan, pengeluaran, saldo

# Fungsi untuk membuat laporan berdasarkan rentang waktu
def buat_laporan(data, periode):
    if data.empty:
        return pd.DataFrame()

    data["Tanggal"] = pd.to_datetime(data["Tanggal"])
    if periode == "Harian":
        return data[data["Tanggal"] == datetime.now().date()]
    elif periode == "Mingguan":
        start_date = datetime.now().date() - timedelta(days=7)
        return data[data["Tanggal"] >= start_date]
    elif periode == "Bulanan":
        start_date = datetime.now().date().replace(day=1)
        return data[data["Tanggal"] >= start_date]
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
kategori = st.selectbox("Kategori", ["Makanan", "Transportasi", "Hiburan", "Gaji", "Lainnya"])
tipe = st.radio("Tipe Transaksi", ["Pemasukan", "Pengeluaran"])
jumlah = st.number_input("Jumlah", min_value=0.0, step=0.01)
keterangan = st.text_area("Keterangan", placeholder="Tuliskan detail transaksi")

if st.button("Tambah Transaksi"):
    if jumlah > 0:
        tambah_transaksi(tanggal, kategori, tipe, jumlah, keterangan)
        st.success("Transaksi berhasil ditambahkan!")
    else:
        st.error("Jumlah harus lebih dari 0.")

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
periode = st.selectbox("Pilih Periode", ["Harian", "Mingguan", "Bulanan"])
laporan = buat_laporan(st.session_state["data_keuangan"], periode)
if laporan.empty:
    st.warning("Tidak ada data untuk periode ini.")
else:
    st.dataframe(laporan)

# Menampilkan grafik
st.header("Grafik Keuangan")
buat_grafik(st.session_state["data_keuangan"])
