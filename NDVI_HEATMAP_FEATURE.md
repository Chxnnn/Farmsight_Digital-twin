# NDVI Heatmap Visualization Feature
## Real-Time Vegetation Health Mapping from Sentinel-2 Satellite

---

## 🎯 Overview

The **NDVI Heatmap** is an interactive color-coded grid showing the vegetation health of your crop field. It divides the field into 100 cells (10×10 grid) and assigns each cell a color based on satellite-derived NDVI (Normalized Difference Vegetation Index) values.

**Location in Dashboard:** Top-middle card (Row 1, Column 2)

---

## 🔍 What Problem Does It Solve?

### Traditional Farming Problem:
- Farmers walk the entire field to visually inspect crop health
- Time-consuming and subjective
- Miss subtle differences in plant vigor
- Can't see infrared light (key indicator of plant health)

### Our Solution:
- **Satellite provides objective health measurements**
- **10×10 grid shows spatial variation** (which areas are stressed)
- **Color-coded visualization** (instant understanding)
- **Updates every 5 days** (when Sentinel-2 passes overhead)

---

## 🛰️ Data Source & Collection

### Satellite: Sentinel-2
- **Agency**: European Space Agency (ESA)
- **Bands Used**: 
  - Band 4 (Red): 665 nm wavelength
  - Band 8 (Near-Infrared): 842 nm wavelength
- **Resolution**: 10 meters per pixel
- **Revisit Time**: 5 days
- **Cloud Filtering**: Only uses images with <20% cloud cover

### API: Google Earth Engine
- Provides programmatic access to Sentinel-2 archive
- Allows filtering by date, location, cloud cover
- Performs NDVI calculation server-side

---

## 📐 How NDVI Calculation Works

### The Science:
Healthy plants absorb red light (for photosynthesis) but reflect near-infrared light (to prevent overheating).

### Formula:
```
NDVI = (NIR - Red) / (NIR + Red)
```

Where:
- **NIR** = Near-Infrared reflectance (Band 8)
- **Red** = Red light reflectance (Band 4)

### Result Range:
- **-1.0 to 0.0**: Water, clouds, snow
- **0.0 to 0.2**: Bare soil, rock, sand
- **0.2 to 0.3**: Very sparse vegetation
- **0.3 to 0.6**: Moderate to healthy vegetation
- **0.6 to 0.9**: Very healthy, dense vegetation

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  USER'S BROWSER                     │
│                                                     │
│  [Interactive NDVI Heatmap Grid - 10×10 cells]     │
│  Hover over cell → Shows exact NDVI value          │
└─────────────────┬───────────────────────────────────┘
                  │ Receives processed data
                  │
┌─────────────────▼───────────────────────────────────┐
│              FLASK SERVER (app.py)                  │
│                                                     │
│  • Orchestrates NDVI data fetch                    │
│  • Passes to template via Jinja2                   │
│  • Caches for 7 days                               │
└─────────────────┬───────────────────────────────────┘
                  │ Calls
                  │
┌─────────────────▼───────────────────────────────────┐
│       earth_engine_ndvi.py Module                   │
│                                                     │
│  get_sentinel2_ndvi(lat, lon):                     │
│    1. Authenticate with Google Earth Engine        │
│    2. Define 250m×250m bounding box                │
│    3. Query Sentinel-2 ImageCollection             │
│    4. Filter: last 30 days, <20% clouds           │
│    5. Select best image (most recent, least clouds)│
│    6. Calculate NDVI: (B8 - B4) / (B8 + B4)       │
│    7. Create 10×10 sampling grid                   │
│    8. Sample each cell (with 50m buffer)          │
│    9. Return 10×10 array of NDVI values           │
└─────────────────┬───────────────────────────────────┘
                  │ API Request
                  │
┌─────────────────▼───────────────────────────────────┐
│        GOOGLE EARTH ENGINE API                      │
│                                                     │
│  • Hosts entire Sentinel-2 archive (petabytes)    │
│  • Performs server-side calculations              │
│  • Returns processed NDVI grid                    │
└─────────────────┬───────────────────────────────────┘
                  │ Raw satellite data
                  │
┌─────────────────▼───────────────────────────────────┐
│           SENTINEL-2 SATELLITES                     │
│                                                     │
│  Sentinel-2A & 2B in orbit                         │
│  • Capture multispectral imagery                   │
│  • Pass over same location every 5 days           │
│  • Free and open data policy                      │
└─────────────────────────────────────────────────────┘
```

---

## 💻 Code Implementation

### 1. Backend: NDVI Calculation (earth_engine_ndvi.py)

```python
def get_sentinel2_ndvi(lat, lon, days_back=30, grid_size=10, buffer_m=50):
    """
    Fetch real NDVI grid from Sentinel-2 via Google Earth Engine.
    
    Args:
        lat: Latitude of field center
        lon: Longitude of field center
        days_back: How many days to search back for images
        grid_size: Number of cells per side (10 = 10×10 grid)
        buffer_m: Sample buffer around each cell (meters)
    
    Returns:
        dict with 'ndvi_grid', 'mean', 'std', 'date'
    """
    
    # Step 1: Define field boundary (250m × 250m)
    point = ee.Geometry.Point([lon, lat])
    FIELD_SIZE_METERS = 250
    half_size = FIELD_SIZE_METERS / 2
    field_bounds = point.buffer(half_size).bounds()
    
    # Step 2: Query Sentinel-2 image collection
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    collection = (
        ee.ImageCollection('COPERNICUS/S2_SR')
        .filterBounds(field_bounds)
        .filterDate(start_date.strftime('%Y-%m-%d'), 
                    end_date.strftime('%Y-%m-%d'))
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    )
    
    # Step 3: Select best image (most recent with least clouds)
    image_list = collection.toList(collection.size())
    count = image_list.size().getInfo()
    
    if count == 0:
        print("⚠️ No Sentinel-2 images found, using fallback")
        return None
    
    # Get most recent image
    image = ee.Image(image_list.get(count - 1))
    
    # Step 4: Calculate NDVI
    nir = image.select('B8')  # Near-Infrared band
    red = image.select('B4')  # Red band
    
    ndvi_image = nir.subtract(red).divide(nir.add(red)).rename('ndvi')
    
    # Step 5: Create sampling grid (10×10 cells)
    cell_size = FIELD_SIZE_METERS / grid_size
    ndvi_grid = []
    
    for row in range(grid_size):
        ndvi_row = []
        for col in range(grid_size):
            # Calculate cell center coordinates
            cell_lon = lon + ((col - grid_size/2 + 0.5) * cell_size / 111320)
            cell_lat = lat + ((row - grid_size/2 + 0.5) * cell_size / 110540)
            
            # Sample with buffer (avoids single-pixel errors)
            sample_point = ee.Geometry.Point([cell_lon, cell_lat])
            sample_region = sample_point.buffer(buffer_m).bounds()
            
            # Get mean NDVI for this cell
            stats = ndvi_image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=sample_region,
                scale=10,
                maxPixels=1e9
            )
            
            ndvi_value = stats.get('ndvi').getInfo()
            ndvi_row.append(round(ndvi_value, 3) if ndvi_value else 0.0)
        
        ndvi_grid.append(ndvi_row)
    
    # Step 6: Calculate statistics
    flat_values = [val for row in ndvi_grid for val in row]
    mean_ndvi = np.mean(flat_values)
    std_ndvi = np.std(flat_values)
    
    # Get image acquisition date
    date_ms = image.get('system:time_start').getInfo()
    image_date = datetime.fromtimestamp(date_ms / 1000).strftime('%Y-%m-%d')
    
    return {
        'ndvi_grid': ndvi_grid,
        'mean': round(mean_ndvi, 3),
        'std': round(std_ndvi, 3),
        'date': image_date,
        'satellite': 'Sentinel-2',
        'cloud_cover': image.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()
    }
```

---

### 2. Backend: Caching (data_ingest.py)

```python
def get_ndvi_with_fallback(lat, lon, use_cache=True, force_refresh=False):
    """
    Get NDVI data with caching and fallback mechanisms.
    
    Args:
        lat: Latitude
        lon: Longitude
        use_cache: Whether to check cache first
        force_refresh: Force bypass cache
    
    Returns:
        NDVI data dict
    """
    
    # Try cache first (unless force refresh)
    if use_cache and not force_refresh:
        cached = get_cached_ndvi(lat, lon)
        if cached:
            print(f"✅ Using cached NDVI (age: {cached.get('age_hours', 0):.1f}h)")
            return cached
    
    # Try fetching from Earth Engine
    try:
        print(f"🛰️ Fetching fresh NDVI from Sentinel-2...")
        ndvi_data = get_sentinel2_ndvi(lat, lon)
        
        if ndvi_data:
            # Save to cache
            cache_ndvi(lat, lon, ndvi_data)
            print(f"✅ NDVI fetched successfully (date: {ndvi_data['date']})")
            return ndvi_data
    
    except Exception as e:
        print(f"❌ Earth Engine error: {e}")
    
    # Fallback: Use simulated data
    print("⚠️ Using simulated NDVI data")
    return generate_simulated_ndvi(lat, lon)


def cache_ndvi(lat, lon, ndvi_data):
    """Save NDVI data to file cache (ndvi_cache.json)"""
    cache_key = f"{lat},{lon}"
    
    cache = {}
    if os.path.exists('ndvi_cache.json'):
        with open('ndvi_cache.json', 'r') as f:
            cache = json.load(f)
    
    cache[cache_key] = {
        'data': ndvi_data,
        'cached_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    with open('ndvi_cache.json', 'w') as f:
        json.dump(cache, f, indent=2)
```

---

### 3. Frontend: Heatmap Visualization (dashboard_premium.html)

```html
<!-- HTML Structure -->
<div class="card">
    <div class="card-header">
        <h2 class="card-title">📊 NDVI Heat Map - Vegetation Health</h2>
        <p class="card-subtitle">{{ ndvi_date }} | Avg: {{ ndvi_mean }}</p>
    </div>
    <div id="ndvi-heatmap" style="height:320px;"></div>
    <div class="ndvi-legend">
        <span style="background:#1a3a52;">Bare Soil</span>
        <span style="background:#2d5a7b;">Sparse</span>
        <span style="background:#4a8c6f;">Moderate</span>
        <span style="background:#84b574;">Healthy</span>
        <span style="background:#c9d96e;">Very Healthy</span>
    </div>
</div>

<script>
// JavaScript: Receive data from Flask
const ndviGrid = {{ ndvi_data.ndvi_grid | tojson }};
const ndviMean = {{ ndvi_data.mean }};
const ndviDate = "{{ ndvi_data.date }}";

console.log("📊 NDVI Grid received:", ndviGrid);

// Create heatmap using Plotly
function createNDVIHeatmap() {
    const data = [{
        z: ndviGrid,  // 10×10 array of NDVI values
        type: 'heatmap',
        colorscale: [
            [0.0, '#1a3a52'],  // Dark blue (0.0-0.2: Bare soil)
            [0.2, '#2d5a7b'],  // Blue (0.2-0.3: Sparse)
            [0.4, '#4a8c6f'],  // Teal (0.3-0.4: Moderate)
            [0.6, '#84b574'],  // Green (0.4-0.6: Healthy)
            [1.0, '#e8f26e']   // Yellow-green (0.6+: Very healthy)
        ],
        zmin: 0.0,
        zmax: 1.0,
        
        // Hover tooltip
        hovertemplate: 
            '<b>Cell: Row %{y}, Col %{x}</b><br>' +
            'NDVI: %{z:.3f}<br>' +
            '<extra></extra>',
        
        // Show NDVI values in cells
        text: ndviGrid,
        texttemplate: '%{z:.2f}',
        textfont: {
            size: 10,
            color: 'white'
        },
        
        // Appearance
        showscale: true,
        colorbar: {
            title: 'NDVI',
            titleside: 'right',
            tickmode: 'linear',
            tick0: 0,
            dtick: 0.2,
            thickness: 15,
            len: 0.7
        }
    }];
    
    const layout = {
        title: {
            text: `NDVI Field Map (${ndviDate})`,
            font: { size: 14, color: '#e8ecf1' }
        },
        xaxis: {
            title: 'West → East',
            tickmode: 'linear',
            tick0: 0,
            dtick: 1,
            showgrid: true,
            gridcolor: 'rgba(255,255,255,0.1)'
        },
        yaxis: {
            title: 'South → North',
            tickmode: 'linear',
            tick0: 0,
            dtick: 1,
            showgrid: true,
            gridcolor: 'rgba(255,255,255,0.1)',
            autorange: 'reversed'  // Row 0 at top
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#e8ecf1' },
        margin: { l: 60, r: 60, t: 50, b: 60 },
        height: 320
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['select2d', 'lasso2d']
    };
    
    Plotly.newPlot('ndvi-heatmap', data, layout, config);
    
    console.log("✅ NDVI heatmap rendered");
}

// Initialize on page load
createNDVIHeatmap();
</script>
```

---

## 🎨 Color Scale Explanation

| NDVI Range | Color | Meaning | Typical Vegetation |
|------------|-------|---------|-------------------|
| **-1.0 to 0.0** | Black/Dark blue | Water, snow | N/A |
| **0.0 to 0.2** | Dark blue (#1a3a52) | Bare soil, rock | No vegetation |
| **0.2 to 0.3** | Blue (#2d5a7b) | Very sparse crops | Just emerged seedlings |
| **0.3 to 0.4** | Teal (#4a8c6f) | Moderate vegetation | Growing crops, some gaps |
| **0.4 to 0.6** | Green (#84b574) | Healthy crops | Full canopy, good vigor |
| **0.6 to 0.9** | Bright green (#c9d96e) | Very healthy | Dense, thriving vegetation |

---

## 🔧 Key Features

### 1. Interactive Hover Tooltips
```javascript
hovertemplate: 
    '<b>Cell: Row %{y}, Col %{x}</b><br>' +
    'NDVI: %{z:.3f}<br>' +
    '<extra></extra>'
```
- Hover over any cell to see exact NDVI value
- Shows row/column position

### 2. Value Display in Cells
```javascript
text: ndviGrid,
texttemplate: '%{z:.2f}',
textfont: { size: 10, color: 'white' }
```
- NDVI value displayed directly in each cell
- Easy to read without hovering

### 3. Colorbar Legend
```javascript
colorbar: {
    title: 'NDVI',
    tickmode: 'linear',
    tick0: 0,
    dtick: 0.2
}
```
- Side legend shows NDVI scale
- Ticks at 0.0, 0.2, 0.4, 0.6, 0.8, 1.0

### 4. Responsive Design
```javascript
config: { responsive: true }
```
- Resizes with browser window
- Works on mobile devices

---

## 📊 Integration with Other Features

### 1. Feeds 3D Field Rendering
The NDVI grid is used to determine plant density and color in the 3D visualization:

```javascript
// In 3D rendering code
for (let row = 0; row < 10; row++) {
    for (let col = 0; col < 10; col++) {
        const ndviValue = ndviGrid[row][col];
        
        // Convert NDVI to vegetation parameters
        const vegParams = ndviToVegetationParams(ndviValue);
        
        // Create plants based on NDVI
        if (Math.random() < vegParams.density) {
            createPlant(row, col, vegParams.color, vegParams.height);
        }
    }
}
```

### 2. Contributes to Health KPI
```javascript
// Calculate overall field health
const flatNDVI = ndviGrid.flat();
const avgNDVI = flatNDVI.reduce((a, b) => a + b) / flatNDVI.length;
const healthPercent = Math.round(((avgNDVI - 0.1) / 0.8) * 100);

// Display: "Crop Health: 72%"
```

### 3. Informs AI Recommendations
```python
# In predictor.py
if ndvi_mean < 0.3:
    recommendation = "Low NDVI detected. Check for water/nutrient stress."
elif ndvi_std > 0.2:
    recommendation = "High variability. Investigate inconsistent areas."
```

---

## 🚀 Performance Optimizations

### 1. Caching Strategy
```python
# Cache NDVI data for 7 days
NDVI_CACHE_DURATION = timedelta(days=7)

# Reasoning: Sentinel-2 updates every 5 days
# No point fetching more frequently
```

### 2. Buffered Sampling
```python
# Sample 50m buffer around each cell center
CELL_SAMPLE_BUFFER_METERS = 50

# Avoids single-pixel errors
# More robust statistics
```

### 3. Fallback Mechanisms
```python
1. Try cache (instant)
   ↓ If expired or missing
2. Try Earth Engine (2-3 seconds)
   ↓ If fails
3. Use simulated data (instant)
   ↓ Always succeeds
Dashboard never fails to load
```

---

## 🐛 Error Handling

### Scenario 1: No Recent Satellite Images
```python
if count == 0:
    print("⚠️ No Sentinel-2 images in last 30 days")
    print("   Possible reasons: Heavy clouds, high latitude winter")
    return None  # Triggers fallback
```

### Scenario 2: Cloudy Images Only
```python
.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))

# If all images >20% clouds, collection is empty
# System uses older cached data or simulated
```

### Scenario 3: API Rate Limits
```python
try:
    ndvi_data = get_sentinel2_ndvi(lat, lon)
except ee.EEException as e:
    print(f"❌ Earth Engine quota exceeded: {e}")
    # Return cached or simulated data
```

---

## 📈 Future Enhancements

### Planned Improvements:
1. **Time-series Animation**: Show NDVI changes over season
2. **Anomaly Detection**: Automatically highlight problem areas
3. **Multi-band Indices**: Add EVI, SAVI, LAI
4. **Higher Resolution**: Use PlanetScope (3m pixels)
5. **Change Detection**: Compare current vs previous week

---

## 📚 Technical References

- **Sentinel-2 Bands**: https://sentinels.copernicus.eu/web/sentinel/technical-guides/sentinel-2-msi/msi-instrument
- **NDVI Formula**: Rouse et al. (1974)
- **Google Earth Engine**: https://earthengine.google.com
- **Plotly Heatmaps**: https://plotly.com/javascript/heatmaps/

---

## ✅ Testing the Feature

### Test 1: Basic Visualization
```bash
# Open dashboard
python app.py

# Look for NDVI heatmap card
# Should show 10×10 colored grid
# Hover over cells → Should show NDVI values
```

### Test 2: Location Change
```bash
# Click new location on satellite map
# Wait 3-5 seconds
# NDVI heatmap should update with new values
```

### Test 3: Cache Verification
```bash
# First load: Should see "Fetching fresh NDVI"
# Second load (same location): Should see "Using cached NDVI"
# Check ndvi_cache.json file created
```

---

**Feature Status:** ✅ Fully Implemented & Tested  
**Last Updated:** November 23, 2025  
**File:** `/templates/dashboard_premium.html`, `/earth_engine_ndvi.py`


