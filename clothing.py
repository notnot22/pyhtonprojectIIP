import streamlit as st
import pandas as pd
import random
from datetime import datetime
import matplotlib.pyplot as plt

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

# Main App
def main():
    st.title("Clothing Business Management")

    # Load product data
    if "product_data" not in st.session_state:
        st.session_state.product_data = generate_product_data()
    if "sales_history" not in st.session_state:
        st.session_state.sales_history = []

    product_data = st.session_state.product_data
    sales_history = st.session_state.sales_history

    # Sidebar menu
    menu = ["Dashboard", "All Products", "Sales Transaction", "Sales Report"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Dashboard":
        st.subheader("Top 10 Products by Sales")

        # Simulate random sales data for the top 10 products
        if not sales_history:
            for _ in range(50):
                random_product = random.choice(product_data["IdProduk"].values)
                random_quantity = random.randint(1, 5)
                product_index = product_data[product_data["IdProduk"] == random_product].index[0]
                sales_history.append({
                    "Date": datetime.now(),
                    "IdProduk": random_product,
                    "NamaProduk": product_data.loc[product_index, "NamaProduk"],
                    "Quantity": random_quantity,
                    "TotalPrice": random_quantity * product_data.loc[product_index, "HargaProduk"]
                })

        sales_df = pd.DataFrame(sales_history)
        top_products = sales_df.groupby("IdProduk")["Quantity"].sum().sort_values(ascending=False).head(10)
        top_products_df = product_data[product_data["IdProduk"].isin(top_products.index)]
        top_products_df = top_products_df.merge(top_products, on="IdProduk")
        top_products_df = top_products_df.rename(columns={"Quantity": "Total Quantity Sold"})
        st.dataframe(top_products_df)

    elif choice == "All Products":
        st.subheader("All Products")
        st.dataframe(product_data)

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
                    sales_history.append({
                        "Date": datetime.now(),
                        "IdProduk": product_id,
                        "NamaProduk": product_data.loc[product_index, "NamaProduk"].values[0],
                        "Quantity": quantity,
                        "TotalPrice": quantity * product_data.loc[product_index, "HargaProduk"].values[0]
                    })
                    st.success("Transaction Successful!")
                else:
                    st.error("Insufficient stock!")

        st.subheader("Sales History")
        sales_df = pd.DataFrame(sales_history)
        if not sales_df.empty:
            st.dataframe(sales_df)
        else:
            st.info("No sales history available.")

    elif choice == "Sales Report":
        st.subheader("Sales Report")
        sales_df = pd.DataFrame(sales_history)
        if not sales_df.empty:
            total_sales = sales_df.groupby("IdProduk")["TotalPrice"].sum().reset_index()
            total_sales = total_sales.merge(product_data, on="IdProduk")[["NamaProduk", "TotalPrice"]]
            total_sales = total_sales.rename(columns={"TotalPrice": "Total Earnings"})

            st.subheader("Total Earnings by Product")
            st.dataframe(total_sales)

            st.subheader("Sales Over Time")
            date_option = st.radio("Select Report Type", ["Daily", "Date Range"])

            if date_option == "Daily":
                selected_date = st.date_input("Select Date", value=datetime.now().date())
                filtered_sales = sales_df[sales_df["Date"].dt.date == selected_date]
            else:
                start_date = st.date_input("Start Date", value=datetime.now().date())
                end_date = st.date_input("End Date", value=datetime.now().date())
                filtered_sales = sales_df[(sales_df["Date"].dt.date >= start_date) & (sales_df["Date"].dt.date <= end_date)]

            if not filtered_sales.empty:
                st.bar_chart(filtered_sales.groupby(filtered_sales["Date"].dt.date)["TotalPrice"].sum())
            else:
                st.info("No sales data available for the selected period.")
        else:
            st.info("No sales data available.")

if __name__ == "__main__":
    main()
