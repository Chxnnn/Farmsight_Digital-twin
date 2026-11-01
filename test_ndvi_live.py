#!/usr/bin/env python3
"""
Quick test to check if Earth Engine NDVI is being fetched
"""
import sys
sys.path.insert(0, '/Users/chethanam/Downloads/digitaltwin')

from data_ingest import get_weather
import config
import json

print("=" * 70)
print("🧪 TESTING NDVI DATA SOURCE")
print("=" * 70)

lat = config.LOCATION_COORDS.get('lat', 31.3260)
lon = config.LOCATION_COORDS.get('lon', 75.5762)
print(f"\n📍 Location: {lat}, {lon}")

print("\n🌦️ Calling get_weather()...")
print("-" * 70)

weather = get_weather(crop_health=0.7)

print("-" * 70)

ndvi_grid = weather.get('ndvi_grid', [])
if ndvi_grid:
    flat = [v for row in ndvi_grid for v in row]
    print(f"\n✅ NDVI Grid Retrieved:")
    print(f"   Size: {len(ndvi_grid)}x{len(ndvi_grid[0])}")
    print(f"   Min: {min(flat):.3f}")
    print(f"   Max: {max(flat):.3f}")
    print(f"   Mean: {sum(flat)/len(flat):.3f}")
    
    # Check if it's likely simulated or real
    unique = len(set(flat))
    variation = max(flat) - min(flat)
    
    print(f"\n📊 Analysis:")
    print(f"   Unique values: {unique}/{len(flat)}")
    print(f"   Variation: {variation:.3f}")
    
    if max(flat) > 0.7:
        print(f"\n🟡 HIGH VALUES DETECTED (max={max(flat):.3f})")
        print(f"   This maps to YELLOW in the heatmap colorscale")
        print(f"   Likely using SIMULATED data (tends to be 0.5-0.8)")
    elif max(flat) < 0.4:
        print(f"\n🔵 LOW VALUES DETECTED (max={max(flat):.3f})")
        print(f"   This maps to BLUE/TEAL in the heatmap colorscale")
        print(f"   Likely using REAL satellite data (winter/fallow)")
    
    # Show sample
    print(f"\n   First 3x3 sample:")
    for i in range(min(3, len(ndvi_grid))):
        print(f"   {[f'{v:.2f}' for v in ndvi_grid[i][:3]]}")
else:
    print(f"\n❌ No NDVI grid in weather data!")

print("\n" + "=" * 70)

