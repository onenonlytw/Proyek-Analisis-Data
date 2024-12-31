import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

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
    
    # Convert dteday to datetime
    df_day['dteday'] = pd.to_datetime(df_day['dteday'])
    df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])
    
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

# Date range filter in sidebar
st.sidebar.title("Rentang Waktu")
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df_day['dteday'].min(), df_day['dteday'].max()],
    min_value=df_day['dteday'].min(),
    max_value=df_day['dteday'].max()
)

# Apply date filter to dataframes
mask_day = (
    (df_day['dteday'].dt.date >= date_range[0]) &
    (df_day['dteday'].dt.date <= date_range[1])
)

mask_hour = (
    (df_hour['dteday'].dt.date >= date_range[0]) &
    (df_hour['dteday'].dt.date <= date_range[1])
)

df_day_filtered = df_day[mask_day]
df_hour_filtered = df_hour[mask_hour]

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
        st.metric("Total Rentals", f"{df_day_filtered['cnt'].sum():,}")
    with col2:
        st.metric("Avg Daily Rentals", f"{df_day_filtered['cnt'].mean():.0f}")
    with col3:
        st.metric("Max Daily Rentals", f"{df_day_filtered['cnt'].max():,}")
    with col4:
        st.metric("Total Days", f"{len(df_day_filtered):,}")
        

elif analysis == "Seasonal & Weather Patterns":
    st.header("🌤️ Seasonal and Weather Patterns Analysis")
    
    tab1, tab2 = st.tabs(["Seasonal Analysis", "Weather Analysis"])
    
    with tab1:
        # Add season selector for this specific view
        selected_year = st.selectbox(
            "Select Year",
            options=[2011, 2012],
            key="season_year"
        )
        
        # Filter data by year
        year_filter = 1 if selected_year == 2012 else 0
        seasonal_data = df_day_filtered[df_day_filtered['yr'] == year_filter].groupby('season')[['casual', 'registered']].mean()
        seasonal_data.index = seasonal_data.index.map(season_map)
        
        fig_seasonal = px.bar(
            seasonal_data,
            barmode='group',
            title=f'Average Rentals by Season: Casual vs Registered Users ({selected_year})',
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
        # Add hour range selector for weather analysis
        hour_range = st.slider(
            "Select Hour Range",
            0, 23,
            (0, 23),
            key="weather_hours"
        )
        
        # Filter hour data
        weather_hour_data = df_hour_filtered[
            (df_hour_filtered['hr'] >= hour_range[0]) &
            (df_hour_filtered['hr'] <= hour_range[1])
        ]
        
        weather_data = weather_hour_data.groupby('weathersit')[['casual', 'registered']].mean()
        weather_data.index = weather_data.index.map(weather_map)
        
        fig_weather = px.bar(
            weather_data,
            barmode='group',
            title=f'Average Rentals by Weather Condition (Hours: {hour_range[0]}:00 - {hour_range[1]}:00)',
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
    
    # Add user type selector
    user_type = st.radio(
        "Select User Type",
        ["All Users", "Casual", "Registered"],
        key="working_day_user_type"
    )
    
    # Prepare data based on user selection
    if user_type == "All Users":
        metric = 'cnt'
    elif user_type == "Casual":
        metric = 'casual'
    else:
        metric = 'registered'
    
    # Mapping untuk workingday
    workingday_map = {0: 'Holiday', 1: 'Working Day'}
    
    hourly_patterns = df_hour_filtered.groupby(['hr', 'workingday'])[metric].mean().unstack()
    hourly_patterns.columns = [workingday_map[col] for col in hourly_patterns.columns]
    
    fig_hourly = px.line(
        hourly_patterns,
        title=f'Average Hourly Rentals: Working Days vs Holidays ({user_type})',
        labels={'value': 'Average Rentals', 'hr': 'Hour of Day'},
        height=500
    )
    st.plotly_chart(fig_hourly, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Working Day Statistics")
        st.dataframe(df_hour_filtered[df_hour_filtered['workingday']==1][metric].describe())
    with col2:
        st.subheader("Holiday Statistics")
        st.dataframe(df_hour_filtered[df_hour_filtered['workingday']==0][metric].describe())
    
    # Tambahan insight tren
    st.info('💡 **Insight:**\n\n'
            '- Terdapat perbedaan pola yang jelas antara penggunaan di hari kerja dan hari libur\n'
            '- Hari kerja menunjukkan dua puncak penggunaan yang distinct, yaitu pada pagi hari dan sore hari\n'
            '- Rata-rata penggunaan di hari kerja sedikit lebih tinggi dibanding hari libur\n'
            '- Hari libur memperlihatkan pola yang lebih merata sepanjang hari dengan puncak di tengah hari\n'
            '- Variabilitas penggunaan di hari kerja (std: 185.1) juga lebih tinggi dibandingkan hari libur (std: 172.8), menunjukkan konsentrasi penggunaan yang lebih tinggi pada jam-jam tertentu')

else:  # Weather Impact
    st.header("🌡️ Weather Impact Analysis")
    
    # Add temperature range filter
    temp_range = st.slider(
        "Select Temperature Range (Normalized)",
        float(df_hour_filtered['temp'].min()),
        float(df_hour_filtered['temp'].max()),
        (float(df_hour_filtered['temp'].min()), float(df_hour_filtered['temp'].max())),
        key="weather_temp"
    )
    
    # Filter data by temperature
    weather_temp_data = df_hour_filtered[
        (df_hour_filtered['temp'] >= temp_range[0]) &
        (df_hour_filtered['temp'] <= temp_range[1])
    ]
    
    fig_box = px.box(
        weather_temp_data,
        x='weathersit',
        y='cnt',
        title=f'Rental Distribution by Weather Situation (Temp Range: {temp_range[0]:.2f} - {temp_range[1]:.2f})',
        labels={'weathersit': 'Weather Condition', 'cnt': 'Number of Rentals'},
        height=500
    )
    fig_box.update_xaxes(ticktext=list(weather_mapfactor.values()),
                     tickvals=list(weather_mapfactor.keys()))

    st.plotly_chart(fig_box, use_container_width=True)
    
    st.subheader("Weather Statistics")
    cols = st.columns(len(weather_temp_data['weathersit'].unique()))
    
    for idx, weather in enumerate(sorted(weather_temp_data['weathersit'].unique())):
        with cols[idx]:
            st.write(f"{weather_map[weather]}")
            stats = weather_temp_data[weather_temp_data['weathersit'] == weather]['cnt'].describe()
            st.dataframe(stats)
    
    # Tambahan insight faktor cuaca
    st.info('💡 **Insight:**\n\n'
                '- Cuaca cerah menghasilkan rata-rata penggunaan tertinggi 204.9 sepeda/jam, sementara kondisi berkabut menurunkan penggunaan menjadi rata-rata 175.2 sepeda/jam\n'
                '- Dampak paling signifikan terlihat pada kondisi hujan/salju ringan yang menurunkan penggunaan hingga 111.6 sepeda/jam, dan kondisi hujan/salju lebat yang menurunkan penggunaan secara drastis menjadi hanya 74.3 sepeda/jam\n'
                '- Kondisi cuaca menjadi salah satu faktor penentu utama dalam keputusan pengguna untuk menyewa sepeda, dengan pengaruh yang lebih kuat pada pengguna casual dibandingkan pengguna registered')

# Footer
st.markdown("---")
st.markdown("Created with ❤️")