import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

class WeatherVisualizations:
    """Create various weather data visualizations"""
    
    def __init__(self):
        # Set style for better-looking plots
        plt.style.use('default')
        sns.set_palette("husl")
        
    def create_temperature_line_chart(self, df):
        """Create a line chart showing temperature trends over time"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot temperature lines
        ax.plot(df['datetime'], df['temperature'], 
                label='Temperature', linewidth=2, marker='o', markersize=3)
        ax.plot(df['datetime'], df['feels_like'], 
                label='Feels Like', linewidth=2, linestyle='--', alpha=0.7)
        
        # Formatting
        ax.set_xlabel('Date & Time')
        ax.set_ylabel('Temperature (°C)')
        ax.set_title('Temperature Trend Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        return fig
    
    def create_temperature_bar_chart(self, df):
        """Create a bar chart showing daily temperature ranges"""
        # Group by date to get daily min/max temperatures
        daily_temps = df.groupby(df['datetime'].dt.date).agg({
            'temperature': ['min', 'max', 'mean'],
            'humidity': 'mean'
        }).round(1)
        
        daily_temps.columns = ['min_temp', 'max_temp', 'avg_temp', 'avg_humidity']
        daily_temps = daily_temps.reset_index()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = range(len(daily_temps))
        width = 0.35
        
        # Create bars
        bars1 = ax.bar([i - width/2 for i in x], daily_temps['min_temp'], 
                      width, label='Min Temperature', alpha=0.8)
        bars2 = ax.bar([i + width/2 for i in x], daily_temps['max_temp'], 
                      width, label='Max Temperature', alpha=0.8)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}°C', ha='center', va='bottom', fontsize=8)
        
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}°C', ha='center', va='bottom', fontsize=8)
        
        # Formatting
        ax.set_xlabel('Date')
        ax.set_ylabel('Temperature (°C)')
        ax.set_title('Daily Temperature Range')
        ax.set_xticks(x)
        ax.set_xticklabels([date.strftime('%m/%d') for date in daily_temps['datetime']])
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig
    
    def create_temp_humidity_scatter(self, df):
        """Create a scatter plot of temperature vs humidity"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create scatter plot with color based on pressure
        scatter = ax.scatter(df['temperature'], df['humidity'], 
                           c=df['pressure'], cmap='viridis', 
                           alpha=0.7, s=50, edgecolors='black', linewidth=0.5)
        
        # Add colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Pressure (hPa)')
        
        # Add trend line
        z = np.polyfit(df['temperature'], df['humidity'], 1)
        p = np.poly1d(z)
        ax.plot(df['temperature'], p(df['temperature']), 
                "r--", alpha=0.8, linewidth=2, label='Trend Line')
        
        # Formatting
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Humidity (%)')
        ax.set_title('Temperature vs Humidity Relationship')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_correlation_heatmap(self, df):
        """Create a heatmap showing correlation between weather metrics"""
        # Select numeric columns for correlation
        numeric_cols = ['temperature', 'feels_like', 'humidity', 'pressure', 'wind_speed']
        correlation_data = df[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Create heatmap
        sns.heatmap(correlation_data, annot=True, cmap='coolwarm', center=0,
                   square=True, ax=ax, cbar_kws={'shrink': 0.8})
        
        # Formatting
        ax.set_title('Weather Metrics Correlation Matrix')
        plt.tight_layout()
        return fig
    
    def create_wind_direction_plot(self, df):
        """Create a polar plot showing wind direction distribution"""
        if 'wind_direction' not in df.columns:
            return None
            
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        # Convert wind direction to radians
        theta = np.radians(df['wind_direction'])
        
        # Create polar scatter plot
        ax.scatter(theta, df['wind_speed'], c=df['temperature'], 
                  cmap='coolwarm', alpha=0.7, s=50)
        
        # Formatting
        ax.set_title('Wind Direction and Speed Distribution')
        try:
            ax.set_theta_zero_location('N')
            ax.set_theta_direction(-1)
        except AttributeError:
            # Fallback for older matplotlib versions
            pass
        
        plt.tight_layout()
        return fig
    
    def create_hourly_temperature_heatmap(self, df):
        """Create a heatmap showing temperature by hour and day"""
        # Create pivot table with hour vs day
        df['hour'] = df['datetime'].dt.hour
        df['day'] = df['datetime'].dt.strftime('%m/%d')
        
        pivot_data = df.pivot_table(values='temperature', 
                                   index='hour', columns='day', 
                                   aggfunc='mean')
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create heatmap
        sns.heatmap(pivot_data, cmap='RdYlBu_r', annot=True, fmt='.1f',
                   ax=ax, cbar_kws={'label': 'Temperature (°C)'})
        
        # Formatting
        ax.set_title('Hourly Temperature Patterns')
        ax.set_xlabel('Date')
        ax.set_ylabel('Hour of Day')
        
        plt.tight_layout()
        return fig
    
    def create_weather_summary_plot(self, df):
        """Create a comprehensive weather summary plot"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Temperature trend
        ax1.plot(df['datetime'], df['temperature'], 'b-', linewidth=2)
        ax1.set_title('Temperature Trend')
        ax1.set_ylabel('Temperature (°C)')
        ax1.grid(True, alpha=0.3)
        
        # Humidity trend
        ax2.plot(df['datetime'], df['humidity'], 'g-', linewidth=2)
        ax2.set_title('Humidity Trend')
        ax2.set_ylabel('Humidity (%)')
        ax2.grid(True, alpha=0.3)
        
        # Pressure trend
        ax3.plot(df['datetime'], df['pressure'], 'r-', linewidth=2)
        ax3.set_title('Pressure Trend')
        ax3.set_ylabel('Pressure (hPa)')
        ax3.grid(True, alpha=0.3)
        
        # Wind speed trend
        ax4.plot(df['datetime'], df['wind_speed'], 'm-', linewidth=2)
        ax4.set_title('Wind Speed Trend')
        ax4.set_ylabel('Wind Speed (m/s)')
        ax4.grid(True, alpha=0.3)
        
        # Format x-axes
        for ax in [ax1, ax2, ax3, ax4]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        return fig
