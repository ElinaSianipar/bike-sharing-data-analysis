import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard Bike Sharing", layout="wide")

# Judul
st.title("Dashboard Analisis Bike Sharing")
st.write("Analisis dataset penyewaan sepeda berdasarkan kategori hari, angin, dan cuaca.")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("day.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])
    
    # Tambahan: Membuat kategori penyewaan untuk visualisasi cuaca
    # Rendah < 2000, Sedang 2000-5000, Tinggi > 5000 (Asumsi berdasarkan grafik kamu)
    bins = [0, 2000, 5000, df['cnt'].max()]
    labels = ['Rendah', 'Sedang', 'Tinggi']
    df['kategori_penyewaan'] = pd.cut(df['cnt'], bins=bins, labels=labels)
    
    return df

df = load_data()

# ======================
# SIDEBAR (FILTER)
# ======================
st.sidebar.header("Filter Data")
start_date = st.sidebar.date_input("Start Date", df['dteday'].min())
end_date = st.sidebar.date_input("End Date", df['dteday'].max())

filtered_df = df[
    (df['dteday'] >= pd.to_datetime(start_date)) &
    (df['dteday'] <= pd.to_datetime(end_date))
]

# ======================
# 1. PERBANDINGAN HARI BIASA VS LIBUR
# ======================
st.subheader("Perbandingan Rata-rata Penyewaan: Hari Biasa vs Hari Libur")

# Mapping data (0: Hari Biasa, 1: Hari Libur)
workingday_map = {0: 'Hari Libur', 1: 'Hari Biasa'}
temp_df = filtered_df.copy()
temp_df['workingday'] = temp_df['workingday'].map(workingday_map)

avg_rental = temp_df.groupby('workingday')['cnt'].mean().reset_index()

fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.barplot(data=avg_rental, x='workingday', y='cnt', palette=['#76b5a3', '#f29e7c'], ax=ax1)

# Tambah label nilai di atas bar
for p in ax1.patches:
    ax1.annotate(f'{p.get_height():.1f}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', xytext=(0, 5), textcoords='offset points')

ax1.set_title("Perbandingan Rata-rata Penyewaan Sepeda Hari Biasa vs Hari Libur (2011-2012)")
ax1.set_xlabel("Kategori Hari")
ax1.set_ylabel("Rata-rata Jumlah Penyewaan")
st.pyplot(fig1)

# ======================
# 2. HUBUNGAN KECEPATAN ANGIN (SCATTER + REGRESI)
# ======================
st.subheader("Hubungan Kecepatan Angin dengan Penyewaan")

fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.regplot(data=filtered_df, x='windspeed', y='cnt', 
            scatter_kws={'alpha':0.5, 'color':'#4e92c2'}, 
            line_kws={'color':'red'}, ax=ax2)

ax2.set_title("Hubungan Kecepatan Angin dengan Penyewaan Sepeda (2011-2012)")
ax2.set_xlabel("Windspeed")
ax2.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig2)

# ======================
# 3. DISTRIBUSI KATEGORI BERDASARKAN CUACA
# ======================
st.subheader("Distribusi Kategori Penyewaan Berdasarkan Cuaca")

# Menghitung jumlah hari untuk setiap kombinasi cuaca dan kategori
weather_dist = filtered_df.groupby(['weathersit', 'kategori_penyewaan'], observed=True).size().reset_index(name='jumlah_hari')

fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.barplot(data=weather_dist, x='weathersit', y='jumlah_hari', hue='kategori_penyewaan', ax=ax3)

ax3.set_title("Distribusi Kategori Penyewaan Berdasarkan Cuaca")
ax3.set_xlabel("Kondisi Cuaca")
ax3.set_ylabel("Jumlah Hari")
ax3.legend(title='kategori_penyewaan')
st.pyplot(fig3)

# ======================
# INSIGHT
# ======================
st.subheader("Insight")
st.write(f"""
- **Kategori Hari:** Rata-rata penyewaan pada **Hari Biasa ({avg_rental.loc[avg_rental['workingday']=='Hari Biasa', 'cnt'].values[0]:.1f})** lebih tinggi dibandingkan Hari Libur.
- **Kecepatan Angin:** Garis regresi merah menunjukkan tren **negatif**, artinya semakin tinggi kecepatan angin, jumlah penyewaan cenderung menurun.
- **Cuaca:** Kondisi cuaca 1 (Cerah) mendominasi jumlah hari dengan kategori penyewaan 'Sedang' dan 'Tinggi'.
""")