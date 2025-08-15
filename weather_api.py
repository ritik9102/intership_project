import requests
import os
import streamlit as st
from datetime import datetime
import json

class WeatherAPI:
    """Handle OpenWeatherMap API interactions"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_current_weather(self, city):
        """Fetch current weather data for a city"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                st.error("Invalid API key. Please check your OpenWeatherMap API key.")
                return None
            elif response.status_code == 404:
                st.error(f"City '{city}' not found. Please check the city name.")
                return None
            else:
                st.error(f"API request failed with status code: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
            return None
        except requests.exceptions.ConnectionError:
            st.error("Connection error. Please check your internet connection.")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return None
    
    def get_forecast(self, city, days=5):
        """Fetch 5-day weather forecast for a city"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (every 3 hours)
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                st.error("Invalid API key. Please check your OpenWeatherMap API key.")
                return None
            elif response.status_code == 404:
                st.error(f"City '{city}' not found. Please check the city name.")
                return None
            else:
                st.error(f"API request failed with status code: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
            return None
        except requests.exceptions.ConnectionError:
            st.error("Connection error. Please check your internet connection.")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return None
    
    def get_historical_weather(self, city, start_date, end_date):
        """Fetch historical weather data (requires different API endpoint)"""
        # Note: Historical data requires a different API plan
        # This is a placeholder for future implementation
        st.warning("Historical weather data requires a premium API plan.")
        return None
    
    def validate_api_key(self):
        """Validate the API key by making a test request"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': 'London',
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            return response.status_code == 200
            
        except:
            return False
    
    @staticmethod
    def format_timestamp(timestamp):
        """Format Unix timestamp to readable datetime"""
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def kelvin_to_celsius(kelvin):
        """Convert Kelvin to Celsius"""
        return kelvin - 273.15
    
    @staticmethod
    def kelvin_to_fahrenheit(kelvin):
        """Convert Kelvin to Fahrenheit"""
        return (kelvin - 273.15) * 9/5 + 32
