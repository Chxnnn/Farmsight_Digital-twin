"""
Test script to check NDVI integration
"""
import json
from data_ingest import get_weather
import config

print("=" * 60)
print("🧪 NDVI INTEGRATION TEST")
print("=" * 60)

# Get coordinates from config
lat = config.LOCATION_COORDS.get('lat', 31.3260)
lon = config.LOCATION_COORDS.get('lon', 75.5762)
print(f"\n📍 Location: {lat}, {lon}")

# Test weather data retrieval (which includes NDVI)
print("\n🌦️ Fetching weather data (includes NDVI)...")
weather_data = get_weather(crop_health=0.7)

print(f"\n📊 Weather Data Keys: {list(weather_data.keys())}")

# Check NDVI grid
if 'ndvi_grid' in weather_data:
    ndvi_grid = weather_data['ndvi_grid']
    print(f"\n✅ NDVI grid found!")
    print(f"   Grid size: {len(ndvi_grid)}x{len(ndvi_grid[0]) if ndvi_grid else 0}")
    
    # Flatten and analyze
    flat_values = [val for row in ndvi_grid for val in row]
    if flat_values:
        import numpy as np
        print(f"   Min NDVI: {min(flat_values):.3f}")
        print(f"   Max NDVI: {max(flat_values):.3f}")
        print(f"   Mean NDVI: {np.mean(flat_values):.3f}")
        print(f"   Std Dev: {np.std(flat_values):.3f}")
        print(f"   Range: {max(flat_values) - min(flat_values):.3f}")
        
        # Show first 3x3 sample
        print(f"\n   Sample (first 3x3):")
        for i in range(min(3, len(ndvi_grid))):
            row = ndvi_grid[i][:3]
            print(f"   Row {i}: {[f'{v:.3f}' for v in row]}")
        
        # Check if all values are the same (yellow heatmap issue)
        unique_values = len(set(flat_values))
        print(f"\n   Unique values: {unique_values}/{len(flat_values)}")
        if unique_values < 5:
            print("   ⚠️ WARNING: Very low variation - this will cause flat color heatmap!")
        
        # Check color distribution
        very_low = sum(1 for v in flat_values if v < 0.3)
        low = sum(1 for v in flat_values if 0.3 <= v < 0.5)
        medium = sum(1 for v in flat_values if 0.5 <= v < 0.7)
        high = sum(1 for v in flat_values if 0.7 <= v < 0.9)
        very_high = sum(1 for v in flat_values if v >= 0.9)
        
        print(f"\n   Color distribution:")
        print(f"   Very Low  (<0.3): {very_low} cells - Dark Blue")
        print(f"   Low    (0.3-0.5): {low} cells - Teal")
        print(f"   Medium (0.5-0.7): {medium} cells - Green")
        print(f"   High   (0.7-0.9): {high} cells - Yellow-Green")
        print(f"   Very High (≥0.9): {very_high} cells - Bright Yellow")
        
        if high + very_high > 80:
            print("\n   🟡 Most values are in YELLOW range - this explains the yellow heatmap!")
else:
    print(f"\n❌ No NDVI grid in weather data!")

print("\n" + "=" * 60)

