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
        "Gaji Karyawan": 15000000,
        "Bahan Baku": 10000000,
        "Utilitas": 5000000,
        "Advertising": 5000000,
        "Asuransi": 2000000
    }

# Main App
def main():
    st.title("Clothing Business Management")

    # Initialize session state
    if "product_data" not in st.session_state:
        st.session_state.product_data = generate_product_data()
    if "sales_history" not in st.session_state:
        st.session_state.sales_history = []
    if "fixed_expenses" not in st.session_state:
        st.session_state.fixed_expenses = generate_fixed_expenses()
    if "variable_expenses" not in st.session_state:
        st.session_state.variable_expenses = []
    if "customers" not in st.session_state:
        # Predefined customers
        st.session_state.customers = {
            "ctm1": "John Doe",
            "ctm2": "Jane Smith",
            "ctm3": "Alice Brown",
            "ctm4": "Bob White"
        }
    product_data = st.session_state.product_data
    sales_history = st.session_state.sales_history
    fixed_expenses = st.session_state.fixed_expenses
    variable_expenses = st.session_state.variable_expenses
    customers = st.session_state.customers

    # Sidebar menu
    menu = ["Dashboard", "All Products", "Sales Transaction", "Sales Report", "Expenses", "All Customer"]
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

        # Financial Summary
        st.subheader("Financial Summary")
        total_earnings = sales_df["TotalPrice"].sum() if not sales_df.empty else 0
        total_fixed_expenses = sum(fixed_expenses.values())
        total_variable_expenses = sum(item["Amount"] for item in variable_expenses)
        total_expenses = total_fixed_expenses + total_variable_expenses

        st.metric("Total Earnings", f"Rp {total_earnings:,}")
        st.metric("Total Expenses", f"Rp {total_expenses:,}")

        # Pie Chart
        st.subheader("Earnings vs Expenses")
        labels = ["Earnings", "Fixed Expenses", "Variable Expenses"]
        values = [total_earnings, total_fixed_expenses, total_variable_expenses]
        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90, textprops={"color": "white"})
        ax.axis("equal")  # Equal aspect ratio ensures the pie is drawn as a circle.
        fig.patch.set_alpha(0)  # Transparent background
        st.pyplot(fig)

    elif choice == "All Products":
        st.subheader("All Products")
        st.dataframe(product_data)

        st.subheader("Low Stock Alerts")
        low_stock_threshold = 20
        low_stock_products = product_data[product_data["StokProduk"] < low_stock_threshold]
        if not low_stock_products.empty:
            st.warning("Some products have low stock!")
            st.dataframe(low_stock_products)
        else:
            st.success("All products have sufficient stock.")

        st.subheader("Update Product Stock")
        with st.form("update_stock_form"):
            product_id = st.number_input("Enter Product ID", min_value=1, max_value=len(product_data), step=1)
            additional_stock = st.number_input("Additional Stock", min_value=1, step=1)
            submit_update_stock = st.form_submit_button("Update Stock")

        if submit_update_stock:
            product_index = product_data[product_data["IdProduk"] == product_id].index
            if not product_index.empty:
                product_data.loc[product_index, "StokProduk"] += additional_stock
                st.success(f"Stock for Product ID {product_id} updated successfully!")
            else:
                st.error("Product ID not found!")

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

        # Radio button to select new or existing customer
        customer_type = st.radio("Select Customer Type", ["New Customer", "Existing Customer"])

        with st.form("sales_form"):
            if customer_type == "New Customer":
                customer_name = st.text_input("Enter Customer Name")
                if st.form_submit_button("Add New Customer"):
                    new_customer_id = f"ctm{len(customers) + 1}"
                    customers[new_customer_id] = customer_name
                    st.session_state.customers = customers
                    customer_id = new_customer_id
                    st.success(f"New customer {customer_name} added with ID {new_customer_id}")
            elif customer_type == "Existing Customer":
                customer_id = st.selectbox("Select Existing Customer ID", list(customers.keys()))

            # Input transaction details
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
                    product_data.loc[product_index, "StokProduk"] -= quantity
                    sales_history.append({
                        "Date": pd.Timestamp(transaction_date),
                        "IdProduk": product_id,
                        "NamaProduk": product_data.loc[product_index, "NamaProduk"].values[0],
                        "Quantity": quantity,
                        "TotalPrice": quantity * product_data.loc[product_index, "HargaProduk"].values[0],
                        "CustomerId": customer_id
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
        st.subheader("Expenses")

        # Fixed Expenses
        st.subheader("Fixed Expenses")
        fixed_expenses_df = pd.DataFrame(list(fixed_expenses.items()), columns=["Expense Type", "Amount"])
        st.dataframe(fixed_expenses_df)

        # Variable Expenses
        st.subheader("Variable Expenses")
        variable_expenses_df = pd.DataFrame(variable_expenses)
        if not variable_expenses_df.empty:
            st.dataframe(variable_expenses_df)
        else:
            st.info("No variable expenses added.")

        st.subheader("Add Variable Expense")
        with st.form("add_variable_expense_form"):
            expense_type = st.selectbox("Expense Type", ["Peralatan", "Bangunan", "Cetakan"])
            expense_amount = st.number_input("Expense Amount", min_value=0, step=1000)
            add_expense = st.form_submit_button("Add Expense")

        if add_expense:
            variable_expenses.append({"Expense Type": expense_type, "Amount": expense_amount})
            st.success(f"Expense {expense_type} of Rp {expense_amount:,} added successfully!")

        # Expense Breakdown Chart
        st.subheader("Expense Breakdown")
        expense_labels = ["Fixed Expenses", "Variable Expenses"]
        expense_values = [sum(fixed_expenses.values()), sum(item["Amount"] for item in variable_expenses)]
        fig, ax = plt.subplots()
        ax.pie(expense_values, labels=expense_labels, autopct="%1.1f%%", startangle=90, textprops={"color": "white"})
        ax.axis("equal")  # Equal aspect ratio ensures the pie is drawn as a circle.
        fig.patch.set_alpha(0)  # Transparent background
        st.pyplot(fig)

    elif choice == "All Customer":
        st.subheader("All Customers")
        customers_df = pd.DataFrame(list(customers.items()), columns=["Customer ID", "Customer Name"])
        st.dataframe(customers_df)

        st.subheader("Customer Purchase History")
        customer_id_input = st.text_input("Enter Customer ID to view purchase history")

        if customer_id_input in customers:
            customer_sales = [sale for sale in sales_history if sale.get("CustomerId") == customer_id_input]
            customer_sales_df = pd.DataFrame(customer_sales)
            if not customer_sales_df.empty:
                st.dataframe(customer_sales_df)
            else:
                st.info(f"No transactions found for Customer ID {customer_id_input}.")
        else:
            st.info("Customer ID not found.")

if __name__ == "__main__":
    main()
