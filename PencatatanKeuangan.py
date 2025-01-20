import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# File untuk menyimpan data
DATA_FILE = "data_keuangan.csv"
STOCK_FILE = "stok_produk.csv"

# Fungsi untuk memuat data dari file
@st.cache_data
def load_data():
    try:
        return pd.read_csv(DATA_FILE, parse_dates=["Tanggal"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Tanggal", "Kategori", "Tipe", "Jumlah", "Keterangan"])

@st.cache_data
def load_stock():
    try:
        return pd.read_csv(STOCK_FILE)
    except FileNotFoundError:
        stok_awal = pd.DataFrame({
            "Kode Produk": [f"P{i+1:03d}" for i in range(32)],
            "Produk": [
                "T-Shirts", "T-Shirts", "T-Shirts", "T-Shirts",
                "Jackets", "Jackets", "Jackets", "Jackets",
                "Flannel", "Flannel", "Flannel",
                "Sweater", "Sweater", "Sweater", "Sweater",
                "Jeans", "Jeans", "Jeans", "Jeans",
                "Shorts", "Shorts", "Shorts", "Shorts",
                "Chinos", "Chinos", "Chinos", "Chinos",
                "Sweat Pants", "Sweat Pants", "Sweat Pants"
            ],
            "Merek": [
                "Short Sleeve", "Long Sleeve", "AIRism Cotton", "Cotton",
                "Reversible Parka", "Pocketable UV Protection Parka", "BLOCKTECH Parka 3D Cut", "Zip Ip Blouson",
                "Flannel Shirt Long Sleeve", "Flannel Long Sleeve Checked", "Flannel Long Sleeve",
                "Crew Neck Long Sleeve Sweater", "Polo Sweater Short Sleeve", "3D Knit Crew Neck Sweater", "Waffle V Neck Sweater",
                "Wide Tapered Jeans", "Straight Jeans", "Slim Fit Jeans", "Ultra Strech Skinny Fit Jeans",
                "Stretch Slim Fit Shorts", "Geared Shorts", "Ultra Stretch Shorts", "Cargo Shorts",
                "Slim Fit Chino Pants", "Pleated Wide Chino Pants", "Wide Fit Chino Pants", "Chino Shorts",
                "Sweat Pants", "Sweat Wide Pants", "Ultra Stretch Sweat Shorts"
            ],
            "UkuranProduk": ["Small", "Medium", "Large"] * 11,
            "WarnaProduk": ["Hijau", "Hitam", "Putih"] * 11,
            "HargaProduk": [
                120000, 125000, 130000, 110000,
                250000, 275000, 300000, 220000,
                150000, 160000, 155000,
                180000, 190000, 185000, 175000,
                210000, 220000, 200000, 195000,
                100000, 105000, 110000, 115000,
                140000, 145000, 150000, 135000,
                90000, 95000, 100000
            ],
            "Stok": [100] * 32
        })
        stok_awal.to_csv(STOCK_FILE, index=False)
        return stok_awal

# Fungsi untuk menyimpan data ke file
def save_data(data):
    data.to_csv(DATA_FILE, index=False)

def save_stock(stock):
    stock.to_csv(STOCK_FILE, index=False)

# Inisialisasi data
if "data_keuangan" not in st.session_state:
    st.session_state["data_keuangan"] = load_data()

if "stok_produk" not in st.session_state:
    st.session_state["stok_produk"] = load_stock()

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

# Fungsi untuk mengurangi stok produk
def kurangi_stok(produk, jumlah):
    stok_produk = st.session_state["stok_produk"]
    if produk in stok_produk["Produk"].values:
        indeks = stok_produk[stok_produk["Produk"] == produk].index[0]
        stok_produk.at[indeks, "Stok"] -= jumlah
        save_stock(stok_produk)

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

# Tambahkan menu navigasi di Streamlit
menu = st.sidebar.radio("Menu", ["Pencatatan Keuangan", "Manajemen Stok Produk"])

if menu == "Pencatatan Keuangan":
    # Form untuk mencatat transaksi
    st.header("Pencatatan Keuangan")
    tanggal = st.date_input("Tanggal", value=datetime.now().date())
    tipe = st.radio("Tipe Transaksi", ["Pemasukan", "Pengeluaran"])

    if tipe == "Pemasukan":
        st.subheader("Masukkan Jumlah untuk Masing-Masing Produk")
        col1, col2 = st.columns(2)
        jumlah_produk = {}
        total_pemasukan = 0

        stok_produk = st.session_state["stok_produk"]
        for idx, produk in enumerate(stok_produk.itertuples()):
            kolom = col1 if idx % 2 == 0 else col2
            with kolom:
                jumlah_unit = st.number_input(f"{produk.Produk} - Rp {produk.Harga:,}", min_value=0, step=1, key=f"jumlah_{produk.Produk}")
                total_harga = jumlah_unit * produk.Harga
                jumlah_produk[produk.Produk] = jumlah_unit
                total_pemasukan += total_harga

        st.write(f"*Total Pemasukan:* Rp {total_pemasukan:,.2f}")
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
                    for produk, jumlah_unit in jumlah_produk.items():
                        if jumlah_unit > 0:
                            total_harga = jumlah_unit * stok_produk[stok_produk["Produk"] == produk]["Harga"].values[0]
                            tambah_transaksi(tanggal, produk, tipe, total_harga, keterangan)
                            kurangi_stok(produk, jumlah_unit)
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

    # Ringkasan keuangan
    st.header("Ringkasan Keuangan")
    pemasukan, pengeluaran, saldo = hitung_ringkasan(st.session_state["data_keuangan"])
    st.metric("Total Pemasukan", f"Rp {pemasukan:,.2f}")
    st.metric("Total Pengeluaran", f"Rp {pengeluaran:,.2f}")
    st.metric("Saldo", f"Rp {saldo:,.2f}")

    # Grafik keuangan
    st.header("Grafik Keuangan")
    buat_grafik(st.session_state["data_keuangan"])

elif menu == "Manajemen Stok Produk":
    st.header("Manajemen Stok Produk")
    stok_produk = st.session_state["stok_produk"]

    # Menampilkan stok saat ini
    st.subheader("Stok Produk Saat Ini")
    st.dataframe(stok_produk)

    # Form untuk menambahkan stok
    st.subheader("Tambah Stok Produk")
    produk_tambah = st.selectbox("Pilih Produk", stok_produk["Produk"])
    jumlah_tambah = st.number_input("Jumlah Stok yang Akan Ditambahkan", min_value=0, step=1)
    if st.button("Tambah Stok"):
        if jumlah_tambah > 0:
            indeks = stok_produk[stok_produk["Produk"] == produk_tambah].index[0]
            stok_produk.at[indeks, "Stok"] += jumlah_tambah
            save_stock(stok_produk)
            st.success(f"Stok untuk {produk_tambah} berhasil ditambahkan.")
        else:
            st.error("Jumlah harus lebih dari 0.")

    # Form untuk mengurangi stok
    st.subheader("Kurangi Stok Produk")
    produk_kurang = st.selectbox("Pilih Produk untuk Dikurangi", stok_produk["Produk"])
    jumlah_kurang = st.number_input("Jumlah Stok yang Akan Dikurangi", min_value=0, step=1)
    if st.button("Kurangi Stok"):
        indeks = stok_produk[stok_produk["Produk"] == produk_kurang].index[0]
        if jumlah_kurang > 0 and stok_produk.at[indeks, "Stok"] >= jumlah_kurang:
            stok_produk.at[indeks, "Stok"] -= jumlah_kurang
            save_stock(stok_produk)
            st.success(f"Stok untuk {produk_kurang} berhasil dikurangi.")
        else:
            st.error("Jumlah harus lebih dari 0 dan tidak boleh melebihi stok saat ini.")
