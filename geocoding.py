"""
Geocoding utilities for converting coordinates to location names
"""
import requests
import time

def reverse_geocode(lat, lon):
    """
    Convert latitude/longitude to a human-readable location name
    Uses OpenStreetMap Nominatim API (free, no API key required)
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        
    Returns:
        dict with location information:
        {
            'city': 'City name',
            'state': 'State name',
            'country': 'Country name',
            'full_address': 'Complete address',
            'display_name': 'Short display name'
        }
    """
    try:
        # Nominatim API endpoint
        url = "https://nominatim.openstreetmap.org/reverse"
        
        # Parameters
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'addressdetails': 1,
            'zoom': 10  # City level
        }
        
        # Headers (Nominatim requires a User-Agent)
        headers = {
            'User-Agent': 'DigitalTwinDashboard/1.0 (Farm Management System)'
        }
        
        print(f"🌍 Looking up location for: {lat}, {lon}")
        
        # Make request
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            
            # Extract location components
            city = (address.get('city') or 
                   address.get('town') or 
                   address.get('village') or 
                   address.get('municipality') or
                   address.get('county') or
                   'Unknown City')
            
            state = (address.get('state') or 
                    address.get('state_district') or
                    address.get('region') or
                    'Unknown State')
            
            country = address.get('country', 'Unknown Country')
            
            # Create display name
            display_name = f"{city}, {state}, {country}"
            
            result = {
                'city': city,
                'state': state,
                'country': country,
                'full_address': data.get('display_name', ''),
                'display_name': display_name,
                'raw_data': data
            }
            
            print(f"✅ Found location: {display_name}")
            return result
            
        else:
            print(f"❌ Geocoding API error: {response.status_code}")
            return None
            
    except requests.Timeout:
        print("⏱️ Geocoding API timeout")
        return None
    except Exception as e:
        print(f"❌ Geocoding error: {e}")
        return None


def get_location_name(lat, lon, fallback="Unknown Location"):
    """
    Get a simple location name string from coordinates
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        fallback: Default name if lookup fails
        
    Returns:
        str: Location name like "City, State, Country"
    """
    location = reverse_geocode(lat, lon)
    if location:
        return location['display_name']
    return fallback


def decimal_to_dms(decimal, is_latitude=True):
    """
    Convert decimal degrees to DMS (Degrees Minutes Seconds) format
    
    Args:
        decimal: Decimal degrees (e.g., 26.974583)
        is_latitude: True for lat (N/S), False for lon (E/W)
        
    Returns:
        str: DMS format like "26°58′28.5″N"
    """
    # Determine direction
    if is_latitude:
        direction = 'N' if decimal >= 0 else 'S'
    else:
        direction = 'E' if decimal >= 0 else 'W'
    
    # Work with absolute value
    decimal = abs(decimal)
    
    # Extract degrees
    degrees = int(decimal)
    
    # Extract minutes
    minutes_decimal = (decimal - degrees) * 60
    minutes = int(minutes_decimal)
    
    # Extract seconds
    seconds = (minutes_decimal - minutes) * 60
    
    # Format as DMS
    return f"{degrees}°{minutes}′{seconds:.1f}″{direction}"


def dms_to_decimal(degrees, minutes, seconds, direction):
    """
    Convert DMS to decimal degrees
    
    Args:
        degrees: Degrees (int)
        minutes: Minutes (int)
        seconds: Seconds (float)
        direction: 'N', 'S', 'E', or 'W'
        
    Returns:
        float: Decimal degrees
    """
    decimal = degrees + (minutes / 60) + (seconds / 3600)
    
    if direction in ['S', 'W']:
        decimal *= -1
        
    return decimal


# Example usage and testing
if __name__ == "__main__":
    # Test with the coordinates from config
    test_lat = 26.974583
    test_lon = 83.529583
    
    print("=" * 60)
    print("🌍 REVERSE GEOCODING TEST")
    print("=" * 60)
    
    # Get full location info
    location = reverse_geocode(test_lat, test_lon)
    
    if location:
        print(f"\n📍 Coordinates: {test_lat}, {test_lon}")
        print(f"🏙️  City: {location['city']}")
        print(f"🗺️  State: {location['state']}")
        print(f"🌏 Country: {location['country']}")
        print(f"📝 Display: {location['display_name']}")
        print(f"\n📬 Full Address:")
        print(f"   {location['full_address']}")
    else:
        print("❌ Could not determine location")
    
    print("\n" + "=" * 60)
    print("🔢 COORDINATE CONVERSION TEST")
    print("=" * 60)
    
    # Test DMS conversion
    dms_lat = decimal_to_dms(test_lat, is_latitude=True)
    dms_lon = decimal_to_dms(test_lon, is_latitude=False)
    
    print(f"\n📊 Decimal to DMS:")
    print(f"   Lat: {test_lat} → {dms_lat}")
    print(f"   Lon: {test_lon} → {dms_lon}")
    
    # Test reverse conversion
    back_lat = dms_to_decimal(26, 58, 28.5, 'N')
    back_lon = dms_to_decimal(83, 31, 46.5, 'E')
    
    print(f"\n📊 DMS to Decimal:")
    print(f"   {dms_lat} → {back_lat}")
    print(f"   {dms_lon} → {back_lon}")
    
    print("\n" + "=" * 60)

