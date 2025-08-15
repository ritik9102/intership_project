import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from weather_api import WeatherAPI
from visualizations import WeatherVisualizations
from data_processor import DataProcessor

# Page configuration
st.set_page_config(
    page_title="Weather Data Visualization Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def get_weather_api():
    api_key = os.getenv("OPENWEATHERMAP_API_KEY", "your_api_key_here")
    return WeatherAPI(api_key)

@st.cache_resource
def get_visualizations():
    return WeatherVisualizations()

@st.cache_resource
def get_data_processor():
    return DataProcessor()

def main():
    st.title("🌤️ Weather Data Visualization Dashboard")
    st.markdown("Interactive weather data analysis with real-time API integration")
    
    # Initialize components
    weather_api = get_weather_api()
    visualizations = get_visualizations()
    data_processor = get_data_processor()
    
    # Sidebar configuration
    st.sidebar.header("Dashboard Configuration")
    
    # City selection
    city = st.sidebar.text_input("Enter City Name", value="London", help="Enter a valid city name")
    
    # Data options
    st.sidebar.subheader("Data Options")
    show_current = st.sidebar.checkbox("Show Current Weather", value=True)
    show_forecast = st.sidebar.checkbox("Show 5-Day Forecast", value=True)
    show_historical = st.sidebar.checkbox("Show Historical Trends", value=False)
    
    # Visualization options
    st.sidebar.subheader("Visualization Options")
    chart_types = st.sidebar.multiselect(
        "Select Chart Types",
        ["Line Chart", "Bar Chart", "Scatter Plot", "Heatmap"],
        default=["Line Chart", "Bar Chart"]
    )
    
    # Main content area
    if st.sidebar.button("Fetch Weather Data", type="primary"):
        if not city.strip():
            st.error("Please enter a valid city name")
            return
            
        with st.spinner(f"Fetching weather data for {city}..."):
            try:
                # Current weather
                current_data = None
                if show_current:
                    current_data = weather_api.get_current_weather(city)
                    if current_data:
                        st.success(f"Successfully fetched current weather data for {city}")
                    else:
                        st.error("Failed to fetch current weather data")
                        return
                
                # Forecast data
                forecast_data = None
                if show_forecast:
                    forecast_data = weather_api.get_forecast(city)
                    if forecast_data:
                        st.success(f"Successfully fetched forecast data for {city}")
                    else:
                        st.warning("Failed to fetch forecast data")
                
                # Process and display data
                if current_data or forecast_data:
                    display_weather_dashboard(
                        current_data, forecast_data, city, chart_types, 
                        visualizations, data_processor
                    )
                
            except Exception as e:
                st.error(f"Error fetching weather data: {str(e)}")
                st.info("Please check your internet connection and API key configuration")
    
    # Display sample dashboard on first load
    if "data_fetched" not in st.session_state:
        st.info("👆 Configure your settings in the sidebar and click 'Fetch Weather Data' to get started")
        display_sample_dashboard()

def display_weather_dashboard(current_data, forecast_data, city, chart_types, visualizations, data_processor):
    """Display the main weather dashboard with data and visualizations"""
    
    # Current weather section
    if current_data:
        st.header(f"Current Weather in {city}")
        
        # Current weather metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Temperature",
                value=f"{current_data['main']['temp']:.1f}°C",
                delta=f"Feels like {current_data['main']['feels_like']:.1f}°C"
            )
        
        with col2:
            st.metric(
                label="Humidity",
                value=f"{current_data['main']['humidity']}%"
            )
        
        with col3:
            st.metric(
                label="Pressure",
                value=f"{current_data['main']['pressure']} hPa"
            )
        
        with col4:
            st.metric(
                label="Wind Speed",
                value=f"{current_data['wind']['speed']} m/s"
            )
        
        # Weather description
        st.info(f"**Conditions:** {current_data['weather'][0]['description'].title()}")
    
    # Forecast section
    if forecast_data:
        st.header("5-Day Weather Forecast")
        
        # Process forecast data
        df_forecast = data_processor.process_forecast_data(forecast_data)
        
        if not df_forecast.empty:
            # Display visualizations based on selected chart types
            if "Line Chart" in chart_types:
                st.subheader("Temperature Trend (Line Chart)")
                fig_line = visualizations.create_temperature_line_chart(df_forecast)
                st.pyplot(fig_line)
            
            if "Bar Chart" in chart_types:
                st.subheader("Daily Temperature Range (Bar Chart)")
                fig_bar = visualizations.create_temperature_bar_chart(df_forecast)
                st.pyplot(fig_bar)
            
            if "Scatter Plot" in chart_types:
                st.subheader("Temperature vs Humidity (Scatter Plot)")
                fig_scatter = visualizations.create_temp_humidity_scatter(df_forecast)
                st.pyplot(fig_scatter)
            
            if "Heatmap" in chart_types:
                st.subheader("Weather Metrics Correlation (Heatmap)")
                fig_heatmap = visualizations.create_correlation_heatmap(df_forecast)
                st.pyplot(fig_heatmap)
            
            # Data export section
            st.header("Data Export")
            col1, col2 = st.columns(2)
            
            with col1:
                csv_data = data_processor.export_to_csv(df_forecast)
                st.download_button(
                    label="Download Forecast Data (CSV)",
                    data=csv_data,
                    file_name=f"weather_forecast_{city}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                json_data = data_processor.export_to_json(df_forecast)
                st.download_button(
                    label="Download Forecast Data (JSON)",
                    data=json_data,
                    file_name=f"weather_forecast_{city}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
            # Raw data table
            with st.expander("View Raw Forecast Data"):
                st.dataframe(df_forecast, use_container_width=True)

def display_sample_dashboard():
    """Display a sample dashboard layout without real data"""
    st.header("Weather Dashboard Preview")
    st.info("This is a preview of the dashboard layout. Configure settings in the sidebar to fetch real weather data.")
    
    # Sample metrics layout
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Temperature", "-- °C", "-- °C")
    with col2:
        st.metric("Humidity", "-- %")
    with col3:
        st.metric("Pressure", "-- hPa")
    with col4:
        st.metric("Wind Speed", "-- m/s")
    
    st.info("**Conditions:** No data available")
    
    # Sample chart placeholders
    st.subheader("Weather Visualizations")
    st.info("Charts will appear here after fetching data")

if __name__ == "__main__":
    main()
