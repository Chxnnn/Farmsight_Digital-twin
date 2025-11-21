"""
Google Earth Engine NDVI Integration
Fetches real NDVI data from Sentinel-2 satellites
"""
import ee
import numpy as np
from datetime import datetime, timedelta
import json
import os
import random

# Global flag for Earth Engine initialization
_EE_INITIALIZED = False
MIN_NDVI_VARIATION = 0.05
CELL_SAMPLE_BUFFER_METERS = 50


def _has_enough_variation(ndvi_grid, min_range=MIN_NDVI_VARIATION):
    """Check NDVI grid variation to avoid flat heatmaps"""
    if not ndvi_grid:
        return False
    flat = [
        val for row in ndvi_grid for val in row
        if val is not None
    ]
    if not flat:
        return False
    variation = max(flat) - min(flat)
    return variation >= min_range

def initialize_earth_engine():
    """Initialize Google Earth Engine"""
    global _EE_INITIALIZED
    
    if _EE_INITIALIZED:
        return True
    
    try:
        print("🔗 Connecting to Earth Engine...")
        ee.Initialize()
        _EE_INITIALIZED = True
        print("✅ Earth Engine initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Earth Engine initialization failed: {e}")
        print("💡 Run: earthengine authenticate --project YOUR_PROJECT_ID")
        return False


def get_sentinel2_ndvi(lat, lon, days_back=30, grid_size=10):
    """Fetch NDVI data from Sentinel-2"""
    
    if not initialize_earth_engine():
        return None
    
    try:
        # Define area
        buffer_meters = 500
        point = ee.Geometry.Point([lon, lat])
        aoi = point.buffer(buffer_meters).bounds()
        
        # Date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Get Sentinel-2 imagery
        sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
            .filterBounds(aoi) \
            .filterDate(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        
        count = sentinel2.size().getInfo()
        if count == 0:
            print(f"⚠️ No cloud-free images found for {lat}, {lon}")
            return None
        
        image = sentinel2.sort('system:time_start', False).first()
        image_date = datetime.fromtimestamp(image.get('system:time_start').getInfo() / 1000)
        cloud_cover = image.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()
        
        print(f"📅 Found image from {image_date.strftime('%Y-%m-%d')}, cloud cover: {cloud_cover:.1f}%")
        
        # Calculate NDVI
        nir = image.select('B8')
        red = image.select('B4')
        ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI').clip(aoi)
        
        # Get mean
        stats = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi,
            scale=10,
            maxPixels=1e9
        )
        ndvi_mean = stats.get('NDVI').getInfo()
        
        # Sample grid
        lon_min, lon_max = lon - 0.005, lon + 0.005
        lat_min, lat_max = lat - 0.005, lat + 0.005
        lon_step = (lon_max - lon_min) / grid_size
        lat_step = (lat_max - lat_min) / grid_size
        
        ndvi_grid = []
        for i in range(grid_size):
            row = []
            for j in range(grid_size):
                sample_lon = lon_min + (j + 0.5) * lon_step
                sample_lat = lat_max - (i + 0.5) * lat_step
                sample_point = ee.Geometry.Point([sample_lon, sample_lat])
                sample_region = sample_point.buffer(CELL_SAMPLE_BUFFER_METERS).bounds()
                
                try:
                    stats = ndvi.reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=sample_region,
                        scale=10,
                        bestEffort=True,
                        maxPixels=1e9
                    )
                    val_obj = stats.get('NDVI')
                    val = val_obj.getInfo() if val_obj is not None else None
                except Exception as sample_error:
                    print(f"⚠️ NDVI sample error at cell ({i},{j}): {sample_error}")
                    val = None
                
                if val is not None:
                    val = round(max(-1.0, min(1.0, float(val))), 3)
                else:
                    fallback_val = ndvi_mean if ndvi_mean else 0.5
                    val = round(float(fallback_val), 3)
                
                row.append(val)
            ndvi_grid.append(row)
        
        # Stats and validation
        flat_values = [val for r in ndvi_grid for val in r if val is not None]
        if not flat_values:
            print("⚠️ Earth Engine returned empty NDVI grid")
            return None
        
        ndvi_min = float(min(flat_values))
        ndvi_max = float(max(flat_values))
        ndvi_mean_value = float(np.mean(flat_values)) if flat_values else (ndvi_mean if ndvi_mean else 0.5)
        ndvi_std = float(np.std(flat_values)) if flat_values else 0.0
        variation = ndvi_max - ndvi_min
        
        print(f"✅ Retrieved {grid_size}x{grid_size} NDVI grid | mean: {ndvi_mean_value:.3f} | min/max: {ndvi_min:.3f}/{ndvi_max:.3f} | std: {ndvi_std:.3f}")
        
        if variation < MIN_NDVI_VARIATION:
            print(f"⚠️ NDVI variation only {variation:.3f} (< {MIN_NDVI_VARIATION}); falling back to simulated data")
            return None
        
        return {
            'ndvi_grid': ndvi_grid,
            'ndvi_mean': round(ndvi_mean_value, 3),
            'ndvi_min': round(ndvi_min, 3),
            'ndvi_max': round(ndvi_max, 3),
            'ndvi_std': round(ndvi_std, 3),
            'date': image_date.strftime('%Y-%m-%d'),
            'cloud_cover': round(cloud_cover, 1),
            'satellite': 'Sentinel-2',
            'source': 'sentinel2',
            'success': True
        }
    except Exception as e:
        print(f"❌ Error fetching NDVI: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_cached_ndvi(lat, lon, cache_file='ndvi_cache.json', max_age_days=7):
    """Get cached NDVI data"""
    if not os.path.exists(cache_file):
        return None
    
    try:
        with open(cache_file, 'r') as f:
            cache = json.load(f)
        
        cache_key = f"{lat:.4f},{lon:.4f}"
        if cache_key in cache:
            cached = cache[cache_key]
            cached_date = datetime.strptime(cached['date'], '%Y-%m-%d')
            age = (datetime.now() - cached_date).days
            
            if age <= max_age_days:
                if _has_enough_variation(cached.get('ndvi_grid')):
                    print(f"📦 Using cached NDVI from {cached['date']} ({age} days old)")
                    cached['source'] = 'cache'
                    return cached
                print("⚠️ Cached NDVI grid is flat, discarding cache entry")
            else:
                print(f"⏰ Cache too old ({age} days)")
        return None
    except Exception as e:
        print(f"⚠️ Cache error: {e}")
        return None


def save_ndvi_cache(lat, lon, data, cache_file='ndvi_cache.json'):
    """Save NDVI to cache"""
    try:
        cache = {}
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache = json.load(f)
        
        cache_key = f"{lat:.4f},{lon:.4f}"
        cache[cache_key] = data
        
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
        print("💾 NDVI cached")
    except Exception as e:
        print(f"⚠️ Cache save error: {e}")


def generate_simulated_ndvi(lat, lon, grid_size=10):
    """Generate simulated NDVI as fallback"""
    base = 0.5 + (90 - abs(lat)) / 180 * 0.3
    ndvi_grid = []
    
    for i in range(grid_size):
        row = []
        for j in range(grid_size):
            dist = np.sqrt((i - 4.5)**2 + (j - 4.5)**2) / 6.0
            val = base * (1 - dist * 0.3)
            val += np.sin(i * 0.8) * np.cos(j * 0.8) * 0.12
            val += random.uniform(-0.08, 0.08)
            
            if i < 2 or j < 2:
                val -= 0.15
            elif i > 7 and j > 7:
                val -= 0.10
            elif 3 <= i <= 6 and 3 <= j <= 6:
                val += 0.15
            
            row.append(round(max(0.15, min(0.95, val)), 3))
        ndvi_grid.append(row)
    
    flat = [val for row in ndvi_grid for val in row]
    return {
        'ndvi_grid': ndvi_grid,
        'ndvi_mean': round(float(np.mean(flat)), 3),
        'ndvi_min': round(float(np.min(flat)), 3),
        'ndvi_max': round(float(np.max(flat)), 3),
        'ndvi_std': round(float(np.std(flat)), 3),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'cloud_cover': 0.0,
        'satellite': 'Simulated',
        'source': 'simulated',
        'success': False
    }


def get_ndvi_with_fallback(lat, lon, use_cache=True):
    """Get NDVI with automatic fallback"""
    
    # Try cache
    if use_cache:
        cached = get_cached_ndvi(lat, lon)
        if cached:
            return cached
    
    # Try Earth Engine
    print(f"🛰️ Fetching REAL NDVI for {lat}, {lon}...")
    ee_data = get_sentinel2_ndvi(lat, lon)
    
    if ee_data:
        if _has_enough_variation(ee_data.get('ndvi_grid')):
            save_ndvi_cache(lat, lon, ee_data)
            return ee_data
        print("⚠️ Earth Engine grid lacked variation, switching to simulated data")
    
    # Fallback
    print("⚠️ Using simulated NDVI")
    return generate_simulated_ndvi(lat, lon)


# Test
if __name__ == "__main__":
    print("=" * 60)
    print("🛰️ EARTH ENGINE NDVI TEST")
    print("=" * 60)
    
    lat, lon = 31.3260, 75.5762
    print(f"\n📍 Testing: {lat}, {lon}")
    
    if initialize_earth_engine():
        print("\n✅ Earth Engine ready!")
        result = get_ndvi_with_fallback(lat, lon, use_cache=False)
        print(f"\n📊 Result:")
        print(f"   Source: {result['source']}")
        print(f"   Satellite: {result['satellite']}")
        print(f"   Date: {result['date']}")
        print(f"   Mean NDVI: {result['ndvi_mean']}")
    else:
        print("\n❌ Not authenticated")
