import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Bike Sharing Analysis",
    page_icon="🚲",
    layout="wide"
)

# Function to load data
@st.cache_data
def load_data():
    # Mendapatkan direktori file ini (script yang sedang dijalankan)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Bangun path absolut untuk setiap file data
    day_path = os.path.join(current_dir, 'day.csv')
    hour_path = os.path.join(current_dir, 'hour.csv')
    hour_clean_path = os.path.join(current_dir, 'bike_sharing_hourly_cleaned.csv')

    # Membaca file CSV
    df_day = pd.read_csv(day_path)
    df_hour = pd.read_csv(hour_path)
    df_hour_clean = pd.read_csv(hour_clean_path)

    return df_day, df_hour, df_hour_clean

# Load data
df_day, df_hour, df_hour_clean = load_data()

# Mapping dictionaries
season_map = {
    1: 'Musim Semi',
    2: 'Musim Panas',
    3: 'Musim Gugur',
    4: 'Musim Dingin'
}

weather_map = {
    1: 'Cerah',
    2: 'Berkabut',
    3: 'Hujan/Salju Ringan',
    4: 'Hujan/Salju Lebat'
}

weather_mapfactor = {
    1: 'Cerah',
    2: 'Berkabut',
    3: 'Hujan/Salju Ringan',
    4: 'Hujan/Salju Lebat'
}

# Main title
st.title("🚲 Bike Sharing Analysis Dashboard")
st.markdown("---")

# Sidebar for navigation
st.sidebar.title("Menu")
analysis = st.sidebar.radio(
    "Select Analysis:",
    ["Overview",
     "Seasonal & Weather Patterns",
     "Working Day Analysis",
     "Weather Impact"]
)

if analysis == "Overview":
    st.header("📊 Overview of Bike Sharing Data")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rentals", f"{df_day['cnt'].sum():,}")
    with col2:
        st.metric("Avg Daily Rentals", f"{df_day['cnt'].mean():.0f}")
    with col3:
        st.metric("Max Daily Rentals", f"{df_day['cnt'].max():,}")
    with col4:
        st.metric("Total Days", f"{len(df_day):,}")

elif analysis == "Seasonal & Weather Patterns":
    st.header("🌤️ Seasonal and Weather Patterns Analysis")
    
    # Tab untuk memisahkan visualisasi
    tab1, tab2 = st.tabs(["Seasonal Analysis", "Weather Analysis"])
    
    with tab1:
        # Analisis Musim
        seasonal_data = df_day.groupby('season')[['casual', 'registered']].mean()
        seasonal_data.index = seasonal_data.index.map(season_map)
        
        fig_seasonal = px.bar(
            seasonal_data,
            barmode='group',
            title='Average Rentals by Season: Casual vs Registered Users',
            labels={'value': 'Average Rentals', 'variable': 'User Type', 'season': 'Season'},
            height=500
        )
        st.plotly_chart(fig_seasonal, use_container_width=True)
        
        # Tambahan insight musiman
        st.info('💡 **Insight:**\n\n'
                '- Musim gugur memiliki tingkat penyewaan tertinggi untuk pengguna terdaftar\n'
                '- Musim semi menunjukkan penggunaan terendah untuk kedua kategori\n'
                '- Perbedaan musiman lebih signifikan pada pengguna casual')
        
    with tab2:
        # Analisis Cuaca
        weather_data = df_day.groupby('weathersit')[['casual', 'registered']].mean()
        weather_data.index = weather_data.index.map(weather_map)
         
        fig_weather = px.bar(
            weather_data,
            barmode='group',
            title='Average Rentals by Weather Condition',
            labels={'value': 'Average Rentals', 'variable': 'User Type', 'weathersit': 'Weather Condition'},
            height=500
        )
        st.plotly_chart(fig_weather, use_container_width=True)
        
        # Tambahan insight cuaca
        st.info('💡 **Insight:**\n\n'
                '- Cuaca cerah menghasilkan penggunaan tertinggi\n'
                '- Hujan/salju ringan berdampak sangat signifikan, menurunkan penggunaan untuk pengguna casual\n'
                '- Pengguna registered menunjukkan ketahanan lebih baik terhadap kondisi cuaca buruk')

elif analysis == "Working Day Analysis":
    st.header("📅 Working Day vs Holiday Analysis")
    
    # Hourly patterns
    hourly_patterns = df_hour.groupby(['hr', 'workingday'])['cnt'].mean().unstack()
    fig_hourly = px.line(
        hourly_patterns,
        title='Average Hourly Rentals: Working Days vs Holidays',
        labels={'value': 'Average Rentals', 'hr': 'Hour of Day'},
        height=500
    )
    st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Tambahan statistik
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Working Day Statistics")
        st.dataframe(df_hour[df_hour['workingday']==1]['cnt'].describe())
    with col2:
        st.subheader("Holiday Statistics")
        st.dataframe(df_hour[df_hour['workingday']==0]['cnt'].describe())
        
    # Tambahan insight tren
    st.info('💡 **Insight:**\n\n'
            '- Terdapat perbedaan pola yang jelas antara penggunaan di hari kerja dan hari libur\n'
            '- Hari kerja menunjukkan dua puncak penggunaan yang distinct, yaitu pada pagi hari dan sore hari\n'
            '- Rata-rata penggunaan di hari kerja sedikit lebih tinggi dibanding hari libur\n'
            '- Hari libur memperlihatkan pola yang lebih merata sepanjang hari dengan puncak di tengah har\n'
            '- Variabilitas penggunaan di hari kerja (std: 185.1) juga lebih tinggi dibandingkan hari libur (std: 172.8), menunjukkan konsentrasi penggunaan yang lebih tinggi pada jam-jam tertentu')

else:  # Weather Impact
    st.header("🌡️ Weather Impact Analysis")
    
    # Weather situation box plot
    fig_box = px.box(
        df_hour,
        x='weathersit',
        y='cnt',
        title='Rental Distribution by Weather Situation',
        labels={'weathersit': 'Weather Condition', 'cnt': 'Number of Rentals'},
        height=500
    )
    fig_box.update_xaxes(ticktext=list(weather_mapfactor.values()),
                     tickvals=list(weather_mapfactor.keys()))

    st.plotly_chart(fig_box, use_container_width=True)
    
    # st.write("Unique weather situations:", df_hour_clean['weathersit'].unique())
    
     # Tampilkan statistik dalam kolom
    st.subheader("Weather Statistics")
    
    # Buat kolom berdasarkan jumlah kondisi cuaca unik
    weather_conditions = sorted(df_hour_clean['weathersit'].unique())
    cols = st.columns(len(weather_conditions))
    
    # Tampilkan statistik untuk setiap kondisi cuaca dalam kolom
    for idx, weather in enumerate(weather_conditions):
        with cols[idx]:
            st.write(f"{weather}")
            stats = df_hour_clean[df_hour_clean['weathersit'] == weather]['cnt'].describe()
            st.dataframe(stats)
    
    # Tambahan insight faktor cuaca
    st.info('💡 **Insight:**\n\n'
                '- Cuaca cerah menghasilkan rata-rata penggunaan tertinggi 204.9 sepeda/jam, sementara kondisi berkabut menurunkan penggunaan menjadi rata-rata 175.2 sepeda/jam\n'
                '- Dampak paling signifikan terlihat pada kondisi hujan/salju ringan yang menurunkan penggunaan hingga 111.6 sepeda/jam, dan kondisi hujan/salju lebat yang menurunkan penggunaan secara drastis menjadi hanya 74.3 sepeda/jam\n'
                '- Kondisi cuaca menjadi salah satu faktor penentu utama dalam keputusan pengguna untuk menyewa sepeda, dengan pengaruh yang lebih kuat pada pengguna casual dibandingkan pengguna registered')   

# Footer
st.markdown("---")
st.markdown("Created with ❤️")