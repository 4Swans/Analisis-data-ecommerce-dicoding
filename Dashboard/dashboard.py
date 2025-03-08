import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
def load_data():
    order_items_df = pd.read_csv("./Dashboard/order_items.csv")
    products_df = pd.read_csv("./Dashboard/products.csv")
    category_translation_df = pd.read_csv("./Dashboard/category.csv")
    order_payments_df = pd.read_csv("./Dashboard/payments.csv")
    orders_df = pd.read_csv("./Dashboard/orders.csv")
    
    # Convert order_purchase_timestamp to datetime
    orders_df["order_purchase_timestamp"] = pd.to_datetime(orders_df["order_purchase_timestamp"])
    return order_items_df, products_df, category_translation_df, order_payments_df, orders_df

# Load Data
order_items_df, products_df, category_translation_df, order_payments_df, orders_df = load_data()

# Get available years
available_years = sorted(orders_df["order_purchase_timestamp"].dt.year.unique(), reverse=True)
available_years.insert(0, "Semua Tahun")  # Tambahkan opsi untuk semua tahun
selected_year = st.sidebar.selectbox("Pilih Tahun Transaksi", available_years)


# Filter data berdasarkan tahun yang dipilih
if selected_year != "Semua Tahun":
    filtered_orders = orders_df[orders_df["order_purchase_timestamp"].dt.year == selected_year]
else:
    filtered_orders = orders_df

#total pesanan dalam dataset
total_orders = order_items_df["order_id"].nunique()

#total pesanan yang memiliki pembayaran (terkonfirmasi)
confirm_buy = order_items_df.merge(order_payments_df, on="order_id", how="inner")
confirm_buy_orders = confirm_buy["order_id"].nunique()



# Title
st.title("Dashboard Analisis Data E-Commerce")

# Section Ringkasan Transaksi
st.subheader(f"Ringkasan Transaksi")

col1, col2 = st.columns(2)
col1.metric("Total Pesanan dalam Dataset", f"{total_orders:,}")
col2.metric("Total Pesanan Terkonfirmasi", f"{confirm_buy_orders:,}")

# Sidebar Menu
menu = st.sidebar.selectbox("Pilih Analisis", ["Kategori Produk Terlaris", "Distribusi Metode Pembayaran", "RFM Analysis"])

st.sidebar.markdown("""       
# Creator\n                   
### Name  : Dimas Bagus Setya Putra
Dicoding  : dimasbagus-sp
### Email : dimasbagus1263@gmail.com 
""")


if menu == "Kategori Produk Terlaris":
    st.subheader(f"10 Kategori Produk dengan Penjualan Terbanyak ({selected_year})")
    filtered_order_items = order_items_df[order_items_df["order_id"].isin(filtered_orders["order_id"])]
    merged_df = filtered_order_items.merge(products_df, on="product_id", how="left")
    merged_df = merged_df.merge(category_translation_df, on="product_category_name", how="left")
    category_sales = merged_df.groupby("product_category_name_english").size().reset_index(name="sales_count")
    
    plt.figure(figsize=(12, 6), facecolor='#f9f9f9')
    ax = sns.barplot(
        data=category_sales.sort_values("sales_count", ascending=False).head(10),
        x="sales_count",
        y="product_category_name_english",
        palette="rocket",   
        edgecolor='.2',    
        linewidth=0.5,      
        alpha=0.9          
    )
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(0.5)
    ax.spines['left'].set_linewidth(0.5)
    
    for i in ax.containers:
        ax.bar_label(i, fmt='%d', padding=5, fontsize=9)
    
    plt.grid(axis="x", linestyle="--", alpha=0.3, color='gray')
    plt.xlabel("Jumlah Penjualan", fontsize=11, fontweight='bold')
    plt.ylabel("Kategori Produk", fontsize=11, fontweight='bold')
    plt.title(f"10 Kategori Produk dengan Penjualan Terbanyak ({selected_year})", fontsize=15, fontweight='bold', pad=15)
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    st.pyplot(plt)
    with st.expander("ℹ️ Penjelasan Grafik"):
        st.markdown("""
        Grafik ini menunjukkan **10 kategori produk dengan penjualan terbanyak** dalam tahun yang dipilih.  
        Kategori diurutkan berdasarkan jumlah penjualan tertinggi.
        """, unsafe_allow_html=True)


elif menu == "Distribusi Metode Pembayaran":
    st.subheader(f"Distribusi Metode Pembayaran ({selected_year})")
    filtered_payments = order_payments_df[order_payments_df["order_id"].isin(filtered_orders["order_id"])]
    payment_distribution = filtered_payments.groupby("payment_type").size().reset_index(name="transaction_count")
    
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='#f9f9f9')
    wedges, texts, autotexts = ax.pie(
        payment_distribution["transaction_count"],
        autopct=lambda p: '{:.1f}%'.format(p) if p > 5 else '',
        startangle=140,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
    )
    ax.legend(wedges, payment_distribution["payment_type"], title="Metode Pembayaran", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    st.pyplot(fig)
    with st.expander("ℹ️ Penjelasan Grafik"):
        st.markdown("""
        Pie chart ini menampilkan **persentase penggunaan metode pembayaran** dalam transaksi e-commerce.  
        Metode dengan persentase kecil (< 5%) tidak ditampilkan untuk menjaga keterbacaan.
        """, unsafe_allow_html=True)


elif menu == "RFM Analysis":
    st.subheader(f"Ringkasan RFM Analysis ({selected_year})")
    rfm_df = filtered_orders[["order_id", "customer_id", "order_purchase_timestamp"]].merge(
        order_items_df, on="order_id", how="left"
    ).merge(
        order_payments_df, on="order_id", how="left"
    )
    max_date = filtered_orders["order_purchase_timestamp"].max()
    
    rfm_df = rfm_df.groupby("customer_id").agg({
        "order_purchase_timestamp": lambda x: (max_date - x.max()).days,
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()
    
    rfm_df.columns = ["customer_id", "Recency", "Frequency", "Monetary"]
    st.dataframe(rfm_df.describe())

    fig, axes = plt.subplots(1, 3, figsize=(18, 5), facecolor='#f9f9f9')

# Visualisasi
# Recency
    sns.histplot(rfm_df["Recency"], bins=20, kde=True, ax=axes[0], color="royalblue")
    axes[0].set_title("Distribusi Recency", fontsize=12, fontweight='bold')
    axes[0].set_xlabel("Hari sejak transaksi terakhir", fontsize=10)
    axes[0].set_ylabel("Jumlah Pelanggan", fontsize=10)
    axes[0].grid(axis='y', linestyle='--', alpha=0.5)

    # Frequency
    sns.histplot(rfm_df["Frequency"], bins=20, kde=True, ax=axes[1], color="seagreen")
    axes[1].set_title("Distribusi Frequency", fontsize=12, fontweight='bold')
    axes[1].set_xlabel("Jumlah Transaksi", fontsize=10)
    axes[1].set_ylabel("Jumlah Pelanggan", fontsize=10)
    axes[1].grid(axis='y', linestyle='--', alpha=0.5)

    # Monetary
    sns.histplot(rfm_df["Monetary"], bins=20, kde=True, ax=axes[2], color="crimson")
    axes[2].set_title("Distribusi Monetary", fontsize=12, fontweight='bold')
    axes[2].set_xlabel("Total Pembelian (Rupiah)", fontsize=10)
    axes[2].set_ylabel("Jumlah Pelanggan", fontsize=10)
    axes[2].grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    st.pyplot(fig)
    with st.expander("ℹ️ Penjelasan Analisis"):
        st.markdown("""
        **RFM Analysis** mengelompokkan pelanggan berdasarkan:
        - **Recency**: Berapa hari sejak terakhir bertransaksi.
        - **Frequency**: Seberapa sering pelanggan melakukan transaksi.
        - **Monetary**: Total nilai transaksi yang dilakukan oleh pelanggan.
        """, unsafe_allow_html=True)

