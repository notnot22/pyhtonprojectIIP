import streamlit as st
import pandas as pd
import random
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib

# Set matplotlib to use a transparent background
matplotlib.rcParams['savefig.facecolor'] = 'none'

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

# Generate Fixed Expenses Data
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
    if "fixed_expenses" not in st.session_state:
        st.session_state.fixed_expenses = generate_fixed_expenses()
    if "variable_expenses" not in st.session_state:
        st.session_state.variable_expenses = []

    product_data = st.session_state.product_data
    sales_history = st.session_state.sales_history
    fixed_expenses = st.session_state.fixed_expenses
    variable_expenses = st.session_state.variable_expenses

    # Sidebar menu
    menu = ["Dashboard", "All Products", "Sales Transaction", "Sales Report", "Expenses"]
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

        st.subheader("Financial Overview")
        total_income = sales_df["TotalPrice"].sum()
        total_fixed_expenses = sum(fixed_expenses.values())
        total_variable_expenses = sum([expense["Amount"] for expense in variable_expenses])
        total_expenses = total_fixed_expenses + total_variable_expenses

        col1, col2 = st.columns(2)
        col1.metric("Total Income", f"Rp {total_income:,.0f}")
        col2.metric("Total Expenses", f"Rp {total_expenses:,.0f}")

        st.subheader("Income and Expenses Distribution")
        fig, ax = plt.subplots()
        labels = ["Income", "Fixed Expenses", "Variable Expenses"]
        sizes = [total_income, total_fixed_expenses, total_variable_expenses]
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

    elif choice == "All Products":
        st.subheader("All Products")
        st.dataframe(product_data)

        st.subheader("Add New Product")
        with st.form("add_product_form"):
            jenis_produk = st.selectbox("Jenis Produk", ["T-Shirts", "Jackets", "Flannel", "Sweater", "Jeans", "Shorts", "Chinos", "Sweat Pants"])
            nama_produk = st.text_input("Nama Produk")
            ukuran_produk = st.selectbox("Ukuran Produk", ["Small", "Medium", "Large"])
            warna_produk = st.selectbox("Warna Produk", ["Hijau", "Hitam", "Putih"])
            harga_produk = st.number_input("Harga Produk", min_value=100000, step=5000)
            stok_produk = st.number_input("Stok Produk", min_value=1, step=1)
            submit_new_product = st.form_submit_button("Add Product")

        if submit_new_product:
            new_id = product_data["IdProduk"].max() + 1
            new_product = {
                "IdProduk": new_id,
                "JenisProduk": jenis_produk,
                "NamaProduk": nama_produk,
                "UkuranProduk": ukuran_produk,
                "WarnaProduk": warna_produk,
                "HargaProduk": harga_produk,
                "StokProduk": stok_produk
            }
            st.session_state.product_data = pd.concat([product_data, pd.DataFrame([new_product])], ignore_index=True)
            st.success(f"Product {nama_produk} has been added successfully!")

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
            total_sales = total_sales.merge(product_data, on="IdProduk")[["IdProduk", "JenisProduk", "NamaProduk", "WarnaProduk", "TotalPrice"]]
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

    elif choice == "Expenses":
        st.subheader("Manage Expenses")

        st.subheader("Fixed Expenses")
        fixed_expenses_df = pd.DataFrame(list(fixed_expenses.items()), columns=["Expense Type", "Amount"])
        st.dataframe(fixed_expenses_df)

        st.subheader("Variable Expenses")
        with st.form("add_variable_expense_form"):
            expense_type = st.text_input("Expense Type")
            expense_amount = st.number_input("Amount", min_value=0, step=5000)
            add_expense = st.form_submit_button("Add Expense")

        if add_expense:
            variable_expenses.append({"Expense Type": expense_type, "Amount": expense_amount})
            st.success(f"Variable expense '{expense_type}' added successfully!")

        if variable_expenses:
            variable_expenses_df = pd.DataFrame(variable_expenses)
            st.dataframe(variable_expenses_df)
        else:
            st.info("No variable expenses recorded.")

if __name__ == "__main__":
    main()
