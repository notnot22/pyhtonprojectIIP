import streamlit as st
import pandas as pd
import random
from datetime import datetime
import matplotlib.pyplot as plt
import sqlite3

# Database setup
conn = sqlite3.connect("business_management.db")
cursor = conn.cursor()

# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    product_id INTEGER,
    product_name TEXT,
    quantity INTEGER,
    total_price INTEGER
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    amount INTEGER,
    date TEXT
)''')

conn.commit()

# Generate Product Data
def generate_product_data():
    product_data = []
    jenis_produk = [
        "T-Shirts", "Jackets", "Flannel", "Sweater", "Jeans", "Shorts", "Chinos", "Sweat Pants"
    ]
    nama_produk = {
        "T-Shirts": ["Short Sleeve", "Long Sleeve", "AIRism Cotton", "Cotton"],
        "Jackets": ["Reversible Parka", "Pocketable UV Protection Parka", "BLOCKTECH Parka 3D Cut", "Zip Ip Blouson"],
        "Flannel": ["Flannel Shirt Long Sleeve", "Flannel Long Sleeve Checked", "Flannel Long Sleeve"],
        "Sweater": ["Crew Neck Long Sleeve Sweater", "Polo Sweater Short Sleeve", "3D Knit Crew Neck Sweater", "Waffle V Neck Sweater"],
        "Jeans": ["Wide Tapered Jeans", "Straight Jeans", "Slim Fit Jeans", "Ultra Stretch Skinny Fit Jeans"],
        "Shorts": ["Stretch Slim Fit Shorts", "Geared Shorts", "Ultra Stretch Shorts", "Cargo Shorts"],
        "Chinos": ["Slim Fit Chino Pants", "Pleated Wide Chino Pants", "Wide Fit Chino Pants", "Chino Shorts"],
        "Sweat Pants": ["Sweat Pants", "Sweat Wide Pants", "Ultra Stretch Sweat Shorts"]
    }
    ukuran_produk = ["Small", "Medium", "Large"]
    warna_produk = ["Hijau", "Hitam", "Putih"]

    id_counter = 1
    for jenis in jenis_produk:
        for nama in nama_produk[jenis]:
            for ukuran in ukuran_produk:
                for warna in warna_produk:
                    product_data.append({
                        "IdProduk": id_counter,
                        "JenisProduk": jenis,
                        "NamaProduk": nama,
                        "UkuranProduk": ukuran,
                        "WarnaProduk": warna,
                        "HargaProduk": random.randint(100000, 300000),
                        "StokProduk": 100
                    })
                    id_counter += 1
    return pd.DataFrame(product_data)

# Generate Fixed Expenses
def generate_fixed_expenses():
    return {
        "Gaji Karyawan": 5000000,
        "Bahan Baku": 7000000,
        "Utilitas": 2000000,
        "Advertising": 3000000,
        "Asuransi": 1500000
    }

# Main App
def main():
    st.title("Clothing Business Management")

    # Load product data
    if "product_data" not in st.session_state:
        st.session_state.product_data = generate_product_data()
    if "fixed_expenses" not in st.session_state:
        st.session_state.fixed_expenses = generate_fixed_expenses()

    product_data = st.session_state.product_data
    fixed_expenses = st.session_state.fixed_expenses

    # Sidebar menu
    menu = ["Dashboard", "All Products", "Sales Transaction", "Sales Report", "Expenses"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Dashboard":
        st.subheader("Dashboard")
        
        # Total Earnings
        sales_df = pd.read_sql_query("SELECT * FROM sales", conn)
        total_earnings = sales_df["total_price"].sum() if not sales_df.empty else 0

        # Total Expenses
        expenses_df = pd.read_sql_query("SELECT * FROM expenses", conn)
        total_expenses = expenses_df["amount"].sum() if not expenses_df.empty else 0

        # Financial Summary
        st.subheader("Financial Summary")
        col1, col2 = st.columns(2)
        col1.metric("Total Earnings", f"Rp {total_earnings:,}")
        col2.metric("Total Expenses", f"Rp {total_expenses:,}")

    elif choice == "All Products":
        st.subheader("All Products")
        st.dataframe(product_data)

        st.subheader("Update Stock")
        with st.form("update_stock_form"):
            product_id = st.number_input("Enter Product ID", min_value=1, step=1)
            additional_stock = st.number_input("Enter Additional Stock", min_value=1, step=1)
            update_stock = st.form_submit_button("Update Stock")

        if update_stock:
            product_index = product_data[product_data["IdProduk"] == product_id].index
            if product_index.empty:
                st.error("Product ID not found!")
            else:
                product_data.loc[product_index, "StokProduk"] += additional_stock
                st.success(f"Stock updated successfully for Product ID {product_id}!")

    elif choice == "Sales Transaction":
        st.subheader("Add Sales Transaction")

        with st.form("sales_form"):
            product_id = st.number_input("Enter Product ID", min_value=1, max_value=len(product_data), step=1)
            quantity = st.number_input("Enter Quantity Sold", min_value=1, step=1)
            submit = st.form_submit_button("Submit")

        if submit:
            product_index = product_data[product_data["IdProduk"] == product_id].index
            if product_index.empty:
                st.error("Product ID not found!")
            else:
                if product_data.loc[product_index, "StokProduk"].values[0] >= quantity:
                    product_data.loc[product_index, "StokProduk"] -= quantity
                    total_price = quantity * product_data.loc[product_index, "HargaProduk"].values[0]
                    cursor.execute("INSERT INTO sales (date, product_id, product_name, quantity, total_price) VALUES (?, ?, ?, ?, ?)",
                                   (datetime.now(), product_id, product_data.loc[product_index, "NamaProduk"].values[0], quantity, total_price))
                    conn.commit()
                    st.success("Transaction Successful!")
                else:
                    st.error("Insufficient stock!")

        st.subheader("Sales History")
        sales_df = pd.read_sql_query("SELECT * FROM sales", conn)
        st.dataframe(sales_df)

    elif choice == "Expenses":
        st.subheader("Expenses")

        st.subheader("Add Variable Expense")
        with st.form("add_variable_expense_form"):
            expense_type = st.selectbox("Expense Type", ["Peralatan", "Bangunan", "Cetakan"])
            expense_amount = st.number_input("Expense Amount", min_value=0, step=1000)
            add_expense = st.form_submit_button("Add Expense")

        if add_expense:
            cursor.execute("INSERT INTO expenses (type, amount, date) VALUES (?, ?, ?)",
                           (expense_type, expense_amount, datetime.now()))
            conn.commit()
            st.success(f"Expense {expense_type} of Rp {expense_amount:,} added successfully!")

        st.subheader("Expense History")
        expenses_df = pd.read_sql_query("SELECT * FROM expenses", conn)
        st.dataframe(expenses_df)

if __name__ == "__main__":
    main()
