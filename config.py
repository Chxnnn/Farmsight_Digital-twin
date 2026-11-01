import json
import os

CROP_NAME = "Wheat"
INITIAL_STAGE = "Seedling"
INITIAL_HEIGHT = 5      # cm
INITIAL_HEALTH = 100    # percent

WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY") # Set your own key

# Location configuration file
_LOCATION_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'location_config.json')

# Default location (Uttar Pradesh, India)
_DEFAULT_LOCATION = {
    "coords": {"lat": 26.974583, "lon": 83.529583},
    "coords_display": {"lat": "26°58′28.5″N", "lon": "83°31′46.5″E"},
    "name": "East, Uttar Pradesh, India"
}

def _load_location():
    """Load location from JSON file or return default"""
    if os.path.exists(_LOCATION_CONFIG_FILE):
        try:
            with open(_LOCATION_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load location config: {e}")
    return _DEFAULT_LOCATION.copy()

def _save_location(location_data):
    """Save location to JSON file"""
    try:
        with open(_LOCATION_CONFIG_FILE, 'w') as f:
            json.dump(location_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving location config: {e}")
        return False

def update_location(lat, lon, location_name, dms_lat, dms_lon):
    """Update location configuration dynamically"""
    location_data = {
        "coords": {"lat": lat, "lon": lon},
        "coords_display": {"lat": dms_lat, "lon": dms_lon},
        "name": location_name
    }
    
    if _save_location(location_data):
        # Update module-level variables
        global LOCATION_COORDS, LOCATION_COORDS_DISPLAY, LOCATION_NAME
        LOCATION_COORDS = location_data["coords"]
        LOCATION_COORDS_DISPLAY = location_data["coords_display"]
        LOCATION_NAME = location_data["name"]
        return True
    return False

# Load location on module import
_current_location = _load_location()
LOCATION_COORDS = _current_location["coords"]
LOCATION_COORDS_DISPLAY = _current_location["coords_display"]
LOCATION_NAME = _current_location["name"]
