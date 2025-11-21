"""
Preprocessing and data cleaning module
"""

def clean_and_extract(weather_data):
    """
    Clean and extract weather data
    Takes raw weather dictionary and returns cleaned version
    """
    if not weather_data:
        # Return default values if no data
        return {
            'temperature': 20.0,
            'humidity': 50,
            'rainfall': 0.0,
            'soil_moisture': 40.0,
            'ndvi_grid': [[0.5] * 10 for _ in range(10)],
            'conditions': 'Unknown',
            'wind_speed': 10.0,
            'pressure': 1013
        }
    
    # Ensure all required fields exist with defaults
    cleaned = {
        'temperature': weather_data.get('temperature', 20.0),
        'humidity': weather_data.get('humidity', 50),
        'rainfall': weather_data.get('rainfall', 0.0),
        'soil_moisture': weather_data.get('soil_moisture', 40.0),
        'ndvi_grid': weather_data.get('ndvi_grid', [[0.5] * 10 for _ in range(10)]),
        'conditions': weather_data.get('conditions', 'Clear'),
        'wind_speed': weather_data.get('wind_speed', 10.0),
        'pressure': weather_data.get('pressure', 1013)
    }
    
    return cleaned

