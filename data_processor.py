import pandas as pd
import numpy as np
from datetime import datetime
import json
import io

class DataProcessor:
    """Process and transform weather data for analysis and visualization"""
    
    def __init__(self):
        pass
    
    def process_current_weather(self, weather_data):
        """Process current weather data into a structured format"""
        if not weather_data:
            return None
            
        try:
            processed_data = {
                'city': weather_data['name'],
                'country': weather_data['sys']['country'],
                'datetime': datetime.fromtimestamp(weather_data['dt']),
                'temperature': weather_data['main']['temp'],
                'feels_like': weather_data['main']['feels_like'],
                'humidity': weather_data['main']['humidity'],
                'pressure': weather_data['main']['pressure'],
                'wind_speed': weather_data.get('wind', {}).get('speed', 0),
                'wind_direction': weather_data.get('wind', {}).get('deg', 0),
                'cloudiness': weather_data.get('clouds', {}).get('all', 0),
                'weather_main': weather_data['weather'][0]['main'],
                'weather_description': weather_data['weather'][0]['description'],
                'visibility': weather_data.get('visibility', 0) / 1000,  # Convert to km
                'sunrise': datetime.fromtimestamp(weather_data['sys']['sunrise']),
                'sunset': datetime.fromtimestamp(weather_data['sys']['sunset'])
            }
            
            return processed_data
            
        except KeyError as e:
            print(f"Missing key in weather data: {e}")
            return None
        except Exception as e:
            print(f"Error processing current weather data: {e}")
            return None
    
    def process_forecast_data(self, forecast_data):
        """Process forecast data into a pandas DataFrame"""
        if not forecast_data or 'list' not in forecast_data:
            return pd.DataFrame()
            
        try:
            forecast_list = []
            
            for item in forecast_data['list']:
                forecast_point = {
                    'datetime': datetime.fromtimestamp(item['dt']),
                    'temperature': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'temp_min': item['main']['temp_min'],
                    'temp_max': item['main']['temp_max'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'wind_speed': item.get('wind', {}).get('speed', 0),
                    'wind_direction': item.get('wind', {}).get('deg', 0),
                    'cloudiness': item.get('clouds', {}).get('all', 0),
                    'weather_main': item['weather'][0]['main'],
                    'weather_description': item['weather'][0]['description'],
                    'precipitation_3h': item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0)
                }
                forecast_list.append(forecast_point)
            
            df = pd.DataFrame(forecast_list)
            
            # Add derived columns
            df['date'] = df['datetime'].dt.date
            df['hour'] = df['datetime'].dt.hour
            df['day_of_week'] = df['datetime'].dt.day_name()
            df['is_daytime'] = ((df['hour'] >= 6) & (df['hour'] <= 18))
            
            return df
            
        except Exception as e:
            print(f"Error processing forecast data: {e}")
            return pd.DataFrame()
    
    def calculate_daily_aggregates(self, df):
        """Calculate daily aggregates from hourly forecast data"""
        if df.empty:
            return pd.DataFrame()
            
        try:
            daily_agg = df.groupby('date').agg({
                'temperature': ['min', 'max', 'mean'],
                'humidity': 'mean',
                'pressure': 'mean',
                'wind_speed': 'mean',
                'precipitation_3h': 'sum',
                'cloudiness': 'mean'
            }).round(2)
            
            # Flatten column names
            daily_agg.columns = ['_'.join(col).strip() for col in daily_agg.columns.values]
            daily_agg = daily_agg.reset_index()
            
            return daily_agg
            
        except Exception as e:
            print(f"Error calculating daily aggregates: {e}")
            return pd.DataFrame()
    
    def detect_weather_patterns(self, df):
        """Detect weather patterns and anomalies"""
        if df.empty:
            return {}
            
        try:
            patterns = {}
            
            # Temperature patterns
            patterns['avg_temperature'] = df['temperature'].mean()
            patterns['temp_range'] = df['temperature'].max() - df['temperature'].min()
            patterns['temp_trend'] = self._calculate_trend(df['temperature'])
            
            # Humidity patterns
            patterns['avg_humidity'] = df['humidity'].mean()
            patterns['humidity_trend'] = self._calculate_trend(df['humidity'])
            
            # Pressure patterns
            patterns['avg_pressure'] = df['pressure'].mean()
            patterns['pressure_trend'] = self._calculate_trend(df['pressure'])
            
            # Wind patterns
            patterns['avg_wind_speed'] = df['wind_speed'].mean()
            patterns['max_wind_speed'] = df['wind_speed'].max()
            
            # Weather conditions frequency
            weather_counts = df['weather_main'].value_counts()
            patterns['dominant_weather'] = weather_counts.index[0] if not weather_counts.empty else 'Unknown'
            
            return patterns
            
        except Exception as e:
            print(f"Error detecting weather patterns: {e}")
            return {}
    
    def _calculate_trend(self, series):
        """Calculate trend direction for a time series"""
        if len(series) < 2:
            return 'stable'
            
        try:
            # Simple linear regression slope
            x = np.arange(len(series))
            slope = np.polyfit(x, series, 1)[0]
            
            if slope > 0.1:
                return 'increasing'
            elif slope < -0.1:
                return 'decreasing'
            else:
                return 'stable'
                
        except:
            return 'stable'
    
    def export_to_csv(self, df):
        """Export DataFrame to CSV format"""
        if df.empty:
            return ""
            
        try:
            output = io.StringIO()
            df.to_csv(output, index=False)
            return output.getvalue()
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return ""
    
    def export_to_json(self, df):
        """Export DataFrame to JSON format"""
        if df.empty:
            return ""
            
        try:
            # Convert datetime objects to strings for JSON serialization
            df_copy = df.copy()
            if 'datetime' in df_copy.columns:
                df_copy['datetime'] = df_copy['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            return df_copy.to_json(orient='records', indent=2)
            
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return ""
    
    def filter_data_by_time_range(self, df, start_time=None, end_time=None):
        """Filter DataFrame by time range"""
        if df.empty:
            return df
            
        try:
            filtered_df = df.copy()
            
            if start_time:
                filtered_df = filtered_df[filtered_df['datetime'] >= start_time]
            
            if end_time:
                filtered_df = filtered_df[filtered_df['datetime'] <= end_time]
            
            return filtered_df
            
        except Exception as e:
            print(f"Error filtering data by time range: {e}")
            return df
    
    def calculate_comfort_index(self, df):
        """Calculate a weather comfort index based on temperature, humidity, and wind"""
        if df.empty:
            return df
            
        try:
            df_copy = df.copy()
            
            # Normalize values (0-1 scale)
            temp_score = np.clip((df_copy['temperature'] - 10) / 25, 0, 1)  # Optimal around 20-25°C
            humidity_score = 1 - np.abs(df_copy['humidity'] - 50) / 50  # Optimal around 50%
            wind_score = np.clip(1 - df_copy['wind_speed'] / 20, 0, 1)  # Lower wind is better
            
            # Weighted comfort index
            df_copy['comfort_index'] = (
                temp_score * 0.5 + 
                humidity_score * 0.3 + 
                wind_score * 0.2
            ) * 100
            
            return df_copy
            
        except Exception as e:
            print(f"Error calculating comfort index: {e}")
            return df
    
    def get_data_summary(self, df):
        """Get a statistical summary of the weather data"""
        if df.empty:
            return {}
            
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            summary = df[numeric_columns].describe().round(2)
            
            return summary.to_dict()
            
        except Exception as e:
            print(f"Error generating data summary: {e}")
            return {}
