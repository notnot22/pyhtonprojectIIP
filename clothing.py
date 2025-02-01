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
    if "sales_history" not in st.session_state:
        st.session_state.sales_history = []
    if "customer_data" not in st.session_state:
        st.session_state.customer_data = {}
    if "fixed_expenses" not in st.session_state:
        st.session_state.fixed_expenses = generate_fixed_expenses()
    if "variable_expenses" not in st.session_state:
        st.session_state.variable_expenses = []

    product_data = st.session_state.product_data
    sales_history = st.session_state.sales_history
    customer_data = st.session_state.customer_data
    fixed_expenses = st.session_state.fixed_expenses
    variable_expenses = st.session_state.variable_expenses

    # Sidebar menu
    menu = ["Dashboard", "All Products", "Sales Transaction", "Sales Report", "Expenses", "All Customers"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Sales Transaction":
        st.subheader("Add Sales Transaction")

        with st.form("sales_form"):
            customer_option = st.radio("Customer Type", ["New Customer", "Existing Customer"])
            if customer_option == "New Customer":
                customer_name = st.text_input("Customer Name")
                customer_id = f"ctm{len(customer_data) + 1}"
            else:
                customer_id = st.text_input("Enter Customer ID")
                customer_name = customer_data.get(customer_id, "Unknown")

            product_id = st.number_input("Enter Product ID", min_value=1, max_value=len(product_data), step=1)
            quantity = st.number_input("Enter Quantity Sold", min_value=1, step=1)
            transaction_date = st.date_input("Select Transaction Date", value=datetime.now().date())
            submit = st.form_submit_button("Submit")

        if submit:
            product_index = product_data[product_data["IdProduk"] == product_id].index
            if product_index.empty:
                st.error("Product ID not found!")
            else:
                if product_data.loc[product_index, "StokProduk"].values[0] >= quantity:
                    total_price = quantity * product_data.loc[product_index, "HargaProduk"].values[0]
                    product_data.loc[product_index, "StokProduk"] -= quantity
                    sales_history.append({
                        "Date": pd.Timestamp(transaction_date),
                        "CustomerID": customer_id,
                        "Customer": customer_name,
                        "IdProduk": product_id,
                        "NamaProduk": product_data.loc[product_index, "NamaProduk"].values[0],
                        "Quantity": quantity,
                        "TotalPrice": total_price
                    })
                    if customer_option == "New Customer":
                        customer_data[customer_id] = customer_name
                    st.success("Transaction Successful!")
                else:
                    st.error("Insufficient stock!")

    elif choice == "All Customers":
        st.subheader("All Customers")
        customer_df = pd.DataFrame(customer_data.items(), columns=["Customer ID", "Customer Name"])
        st.dataframe(customer_df)

        st.subheader("Customer Purchase History")
        selected_customer_id = st.text_input("Enter Customer ID to View Purchase History")
        if selected_customer_id:
            customer_sales = [sale for sale in sales_history if sale["CustomerID"] == selected_customer_id]
            if customer_sales:
                st.dataframe(pd.DataFrame(customer_sales))
            else:
                st.info("No purchase history for this customer.")

if __name__ == "__main__":
    main()
