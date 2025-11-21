# Data Flow Guide

Complete documentation of how data flows through the FarmSight Digital Twin dashboard, including both real API data and simulated fallbacks.

---

## Overview: End-to-End Data Journey

```
User Opens Dashboard
        ↓
Flask Route (/)
        ↓
Data Ingestion Layer
        ↓
├─ OpenWeather API ──→ Temperature, Humidity, Rain, Wind
├─ Earth Engine ─────→ 10×10 NDVI Grid
├─ NASA POWER ───────→ Soil Moisture (or simulation)
└─ Preprocessing ────→ Clean & validate data
        ↓
Digital Twin Update
        ↓
├─ Update crop state (height, stage, health)
├─ Calculate GDD (Growing Degree Days)
└─ Sync with satellite data
        ↓
Forecasting & AI
        ↓
├─ Prophet: 7-day soil moisture forecast
└─ Q-Learning: Daily action recommendations
        ↓
Flask Context Assembly
        ↓
├─ NDVI → JSON for heatmap
├─ Weather → Real-time card
├─ Forecast → Chart data
├─ Recommendations → AI timeline
└─ Twin state → 3D field + gauges
        ↓
Frontend Rendering
        ↓
├─ Plotly: NDVI Heatmap
├─ Three.js: 3D Wheat Field
├─ Chart.js: Forecast Line Chart
├─ Leaflet: Satellite Basemap
└─ HTML/CSS: Cards, tooltips, controls
```

---

## 1. Data Ingestion Layer

### File: `data_ingest.py`

#### Function: `get_weather(crop_health=0.7)`

**Purpose:** Fetch weather and NDVI data for current location

**Flow:**

```python
def get_weather(crop_health=0.7):
    # 1. Get coordinates from config
    lat = config.LOCATION_COORDS['lat']
    lon = config.LOCATION_COORDS['lon']
    
    # 2. Call OpenWeather API
    try:
        response = requests.get(OPENWEATHER_URL, params={...})
        # Extract: temp, humidity, rain, wind, pressure, conditions
        temperature = response.json()['main']['temp']
        humidity = response.json()['main']['humidity']
        # ... more fields
    except:
        # FALLBACK: Simulate weather
        temperature = random.uniform(15, 30)
        humidity = random.uniform(30, 80)
    
    # 3. Call Earth Engine for NDVI
    try:
        ndvi_data = get_ndvi_with_fallback(lat, lon)
        ndvi_grid = ndvi_data['ndvi_grid']  # 10×10 array
        ndvi_source = ndvi_data['source']   # 'sentinel2' or 'cache'
    except:
        # FALLBACK: Simulate NDVI grid
        ndvi_grid = generate_simulated_ndvi_pattern()
        ndvi_source = 'simulated'
    
    # 4. Return unified weather object
    return {
        'temperature': temperature,
        'humidity': humidity,
        'rainfall': rainfall,
        'ndvi_grid': ndvi_grid,
        'conditions': conditions,
        # ... all fields
    }
```

**Output Structure:**
```json
{
  "temperature": 25.3,
  "humidity": 65,
  "rainfall": 0.5,
  "soil_moisture": 42.1,
  "ndvi_grid": [[0.3, 0.4, ...], ...],
  "conditions": "Clear",
  "wind_speed": 12.5,
  "pressure": 1013
}
```

---

#### Function: `get_soil_moisture()`

**Purpose:** Fetch NASA soil moisture baseline (or simulate)

**Flow:**

```python
def get_soil_moisture():
    # 1. Try NASA POWER precipitation
    try:
        response = requests.get(NASA_POWER_URL, params={
            'parameters': 'PRECTOTCORR',
            'latitude': lat,
            'longitude': lon,
            'start': today,
            'end': today
        })
        
        precip_mm = response.json()[...]
        
        # Convert precipitation to moisture estimate
        moisture = 40.0 + min(precip_mm * 2, 30)
        moisture = clamp(moisture, 25, 70)
        
        return moisture
    except:
        # FALLBACK: Simulate
        return random.uniform(35, 55)
```

**Current Status:**
- NASA POWER returns 422 errors
- **Always uses simulation** (35-55% range)
- Logged as: `⚠️ NASA POWER unavailable, using simulated`

---

### File: `earth_engine_ndvi.py`

#### Function: `get_ndvi_with_fallback(lat, lon)`

**Purpose:** Fetch 10×10 NDVI grid from Sentinel-2

**Flow:**

```python
def get_ndvi_with_fallback(lat, lon):
    # 1. Check cache first
    cached = get_cached_ndvi(lat, lon)
    if cached and not_expired(cached):
        return cached
    
    # 2. Query Earth Engine
    try:
        # Get Sentinel-2 image
        image = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                  .filterBounds(point)
                  .filterDate(last_30_days)
                  .filter(cloud_cover < 20%)
                  .sort('system:time_start', False)
                  .first()
        
        # Calculate NDVI
        ndvi = (NIR - RED) / (NIR + RED)
        
        # Sample 10×10 grid with 50m buffers
        for i in range(10):
            for j in range(10):
                point = calculate_grid_point(i, j)
                region = point.buffer(50).bounds()
                value = ndvi.reduceRegion(mean, region)
                grid[i][j] = value
        
        # Validate variation
        if max(grid) - min(grid) < 0.05:
            raise FlatGridError()
        
        # Cache and return
        save_to_cache(lat, lon, grid)
        return {
            'ndvi_grid': grid,
            'ndvi_mean': mean(grid),
            'source': 'sentinel2',
            'date': image_date
        }
    except:
        # FALLBACK: Generate simulated NDVI
        return generate_simulated_ndvi(lat, lon)
```

**Simulated NDVI Pattern:**
```python
# Center-healthy, edge-stressed pattern
for i in range(10):
    for j in range(10):
        distance_from_center = sqrt((i-4.5)² + (j-4.5)²)
        base_ndvi = 0.7 * (1 - distance * 0.3)
        
        # Add spatial variation
        value = base_ndvi + sin(i*0.8) * cos(j*0.8) * 0.12
        
        # Edge stress
        if i < 2 or j < 2:
            value -= 0.15
        
        # Center boost
        if 3 <= i <= 6 and 3 <= j <= 6:
            value += 0.15
        
        grid[i][j] = clamp(value, 0.15, 0.95)
```

---

## 2. Preprocessing Layer

### File: `preprocessing.py`

#### Function: `clean_and_extract(weather_data)`

**Purpose:** Ensure all required fields exist with safe defaults

**Flow:**

```python
def clean_and_extract(weather_data):
    if not weather_data:
        # Return complete default object
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
    
    # Fill missing fields
    return {
        'temperature': weather_data.get('temperature', 20.0),
        'humidity': weather_data.get('humidity', 50),
        # ... ensure all fields present
    }
```

**Why This Matters:**
- Frontend never receives incomplete data
- No crashes from missing fields
- Graceful degradation

---

## 3. Digital Twin Layer

### File: `crop_model.py`

#### Class: `WheatDigitalTwin`

**Purpose:** Simulate crop state (height, stage, health, moisture, nitrogen)

**State Variables:**
```python
self.height = 5          # cm
self.stage = "Seedling"
self.health = 100        # 0-100%
self.soil_moisture = 40  # 0-100%
self.nitrogen = 80       # 0-100%
self.gdd = 0             # Growing Degree Days
self.age_days = 0
```

**Update Flow:**

```python
def update(self, weather):
    # 1. Age the crop
    self.age_days += 1
    
    # 2. Calculate GDD from temperature
    gdd_today = max(0, (weather['temperature'] - 0) / 2)
    self.gdd += gdd_today
    
    # 3. Auto-advance growth stage based on GDD
    if self.gdd > 150 and self.stage == "Seedling":
        self.stage = "Tillering"
    elif self.gdd > 350 and self.stage == "Tillering":
        self.stage = "Stem Elongation"
    # ... more stages
    
    # 4. Update height based on stage and GDD
    self.height = calculate_height(self.stage, self.gdd)
    
    # 5. Update health from NDVI
    ndvi_mean = mean(weather['ndvi_grid'])
    self.health = ndvi_mean * 120  # Scale to 0-100
    
    # 6. Update moisture from rainfall
    self.soil_moisture += weather['rainfall'] * 5
    self.soil_moisture = clamp(self.soil_moisture, 20, 70)
    
    # 7. Decay nitrogen over time
    self.nitrogen -= 1
```

**Live Mode Sync:**

```python
def sync_with_real_data(self, nasa_moisture, ndvi_mean):
    # Directly set values from real data
    self.soil_moisture = nasa_moisture
    self.health = ndvi_mean * 120
```

---

## 4. Forecasting Layer

### File: `predictor.py`

#### Function: `predict_soil_moisture(history_df)`

**Purpose:** Generate 7-day soil moisture forecast

**Model:** Prophet-style time series (CmdStanPy)

**Flow:**

```python
def predict_soil_moisture(history_df):
    # 1. Prepare historical data
    # history_df has columns: ['ds', 'y']
    # ds = dates, y = moisture values
    
    # 2. Fit Prophet model
    model = Prophet()
    model.fit(history_df)
    
    # 3. Create future dataframe (7 days)
    future = model.make_future_dataframe(periods=7)
    
    # 4. Generate forecast
    forecast = model.predict(future)
    
    # 5. Extract predictions
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
```

**Output Example:**
```python
[
    {'ds': '2025-11-22', 'yhat': 45.2, 'yhat_lower': 40.1, 'yhat_upper': 50.3},
    {'ds': '2025-11-23', 'yhat': 43.8, 'yhat_lower': 38.7, 'yhat_upper': 48.9},
    # ... 7 days total
]
```

---

#### Function: `generate_recommendations(forecast_df, recent_weather)`

**Purpose:** Use Q-learning to generate daily actions

**Model:** Pre-trained Q-learning agent (`q_agent.pkl`)

**Flow:**

```python
def generate_recommendations(forecast_df, recent_weather):
    # 1. Load Q-learning agent
    with open('q_agent.pkl', 'rb') as f:
        agent = pickle.load(f)
    
    # 2. For each forecast day
    recommendations = []
    for day in forecast_df:
        # 3. Build state representation
        state = (
            day['yhat'],           # Predicted moisture
            recent_weather['temp'],
            crop_stage
        )
        
        # 4. Agent selects best action
        action = agent.select_action(state)
        # action ∈ {'irrigate', 'fertilize', 'wait'}
        
        # 5. Store recommendation
        recommendations.append({
            'day': day['ds'],
            'pred_soil': day['yhat'],
            'action': action
        })
    
    return recommendations
```

**Humanization:**

```python
def humanize_recommendation(rec):
    if rec['action'] == 'irrigate':
        return f"Day {rec['day']}: Moisture {rec['pred_soil']:.1f}%. Water the field."
    elif rec['action'] == 'fertilize':
        return f"Day {rec['day']}: Moisture {rec['pred_soil']:.1f}%. Apply fertilizer."
    else:
        return f"Day {rec['day']}: Moisture {rec['pred_soil']:.1f}%. Monitor only."
```

---

## 5. Flask Context Assembly

### File: `app.py`

#### Route: `@app.route('/')`

**Purpose:** Orchestrate all data and render dashboard

**Flow:**

```python
@app.route('/')
def index():
    # 1. Get weather + NDVI
    weather_raw = get_weather(crop_health=twin.health)
    weather = clean_and_extract(weather_raw)
    
    # 2. Update digital twin
    twin.update(weather)
    
    # 3. Get NASA soil moisture
    nasa_soil_moisture = get_soil_moisture()
    
    # 4. Generate forecast
    forecast_df = predict_soil_moisture(history_df)
    
    # 5. Generate AI recommendations
    recommendations, explanation = generate_recommendations(
        forecast_df,
        weather
    )
    
    # 6. Calculate NDVI stats
    ndvi_grid = weather['ndvi_grid']
    ndvi_mean = mean(ndvi_grid)
    ndvi_json = json.dumps(ndvi_grid)
    
    # 7. Get metadata
    ndvi_metadata = get_ndvi_metadata()
    
    # 8. Build farm data for 3D field
    farm_data = [[{
        "height": twin.height,
        "health": twin.health,
        "stage": twin.stage
    }]]
    
    # 9. Render template with all context
    return render_template(
        'dashboard_premium.html',
        crop=twin.to_dict(),
        farm_data=json.dumps(farm_data),
        weather=weather,
        forecast=forecast_df.to_dict(orient='records'),
        recommendations=humanize_all(recommendations),
        ndvi_json=ndvi_json,
        ndvi_mean=ndvi_mean,
        ndvi_metadata=ndvi_metadata,
        nasa_soil_moisture=nasa_soil_moisture,
        config=config,
        now=datetime.now()
    )
```

---

## 6. Frontend Rendering

### File: `templates/dashboard_premium.html`

#### JavaScript Data Flow

**1. Parse Flask Context:**

```javascript
const cropData = {{ crop | tojson }};
const weatherData = {{ weather | tojson }};
const forecastData = {{ forecast | tojson }};
const ndviData = {{ ndvi_json | safe }};
const ndviMean = {{ ndvi_mean }};
const nasaSoilMoisture = {{ nasa_soil_moisture }};
```

**2. Initialize Visualizations:**

```javascript
document.addEventListener('DOMContentLoaded', function() {
    initNDVIHeatmap();      // Plotly
    init3DWheatField();      // Three.js
    initForecastChart();     // Chart.js
    loadSatelliteImage();    // Leaflet
});
```

---

#### NDVI Heatmap (Plotly)

```javascript
function initNDVIHeatmap() {
    // Calculate stats
    let minNDVI = Math.min(...ndviData.flat());
    let maxNDVI = Math.max(...ndviData.flat());
    
    // Plot with fixed scale
    Plotly.newPlot('ndvi-heatmap', [{
        z: ndviData,
        type: 'heatmap',
        colorscale: [
            [0.0, '#1a3a52'],    // Dark blue
            [0.2, '#2d5a7b'],    // Blue
            [0.4, '#4a8c6f'],    // Teal
            [0.6, '#84b574'],    // Green
            [1.0, '#e8f26e']     // Yellow-green
        ],
        zmin: 0.0,  // Fixed minimum
        zmax: 1.0   // Fixed maximum
    }], layout);
}
```

**Why Fixed Scale Matters:**
- Same NDVI value = same color everywhere
- 0.4 always shows as teal (moderate vegetation)
- 0.7 always shows as bright green (very healthy)
- Prevents misleading auto-scaling

---

#### 3D Wheat Field (Three.js)

```javascript
function createRealisticWheatField(stageName, tier) {
    const gridSize = 10;
    const spacing = 1.8;
    
    // For each plant position in 10×10 grid
    for (let i = 0; i < gridSize; i++) {
        for (let j = 0; j < gridSize; j++) {
            // 1. Get NDVI value for this cell
            const ndviValue = ndviData[i][j];
            const localHealth = Math.max(0.3, Math.min(1.0, ndviValue));
            
            // 2. Calculate plant density
            const plantDensity = baseDensity * localHealth;
            
            // Skip plant randomly based on density
            if (Math.random() > plantDensity) continue;
            
            // 3. Create plant geometry
            const plant = new THREE.Group();
            
            // 4. Color based on NDVI
            const stressedColor = 0xDAA520;  // Gold (stressed)
            const healthyColor = 0x4a8c6f;   // Green (healthy)
            const plantColor = interpolateColor(
                stressedColor,
                healthyColor,
                localHealth
            );
            
            // 5. Height from crop stage
            const heightMultiplier = GROWTH_STAGES[stageName].height;
            const stemHeight = avgHeight * heightMultiplier;
            
            // 6. Build stem, leaves, head
            const stem = createStem(stemHeight, plantColor);
            const leaves = createLeaves(stemHeight, plantColor);
            const head = createHead(stageName, plantColor);
            
            plant.add(stem, leaves, head);
            plant.position.set(x, 0, z);
            
            field.add(plant);
        }
    }
}
```

**NDVI → 3D Field Mapping:**

| NDVI Range | Heat Map Color | 3D Field Result |
|------------|----------------|-----------------|
| 0.2 - 0.3 | Dark Blue | Very sparse plants, brown/gold color |
| 0.3 - 0.4 | Blue-Teal | Sparse plants, yellowish-green |
| 0.4 - 0.6 | Teal-Green | Moderate density, green |
| 0.6 - 0.8 | Bright Green | Dense plants, vibrant green |
| 0.8 - 1.0 | Yellow-Green | Very dense, peak health |

---

#### Forecast Chart (Chart.js)

```javascript
function initForecastChart() {
    const dayLabels = forecastData.map((f, i) => `Day ${i + 1}`);
    const values = forecastData.map(f => f.yhat);
    const lower = forecastData.map(f => f.yhat_lower);
    const upper = forecastData.map(f => f.yhat_upper);
    
    new Chart('forecast-chart', {
        type: 'line',
        data: {
            labels: dayLabels,
            datasets: [
                {
                    label: 'Predicted Moisture',
                    data: values,
                    borderColor: '#52c196',
                    backgroundColor: 'rgba(82, 193, 150, 0.1)'
                },
                {
                    label: 'Confidence Interval',
                    data: upper,
                    borderColor: 'rgba(82, 193, 150, 0.3)',
                    fill: '+1'
                }
            ]
        }
    });
}
```

---

#### Satellite Map (Leaflet)

```javascript
function loadSatelliteImage() {
    const map = L.map('satellite-rgb-image').setView(
        [config.LOCATION_COORDS.lat, config.LOCATION_COORDS.lon],
        15
    );
    
    L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        { attribution: 'ESRI' }
    ).addTo(map);
    
    // Add marker for field center
    L.marker([lat, lon]).addTo(map);
}
```

---

## 7. User Interactions

### Location Search Flow

```
User enters "19.07, 72.87"
        ↓
JavaScript validates format
        ↓
POST /api/geocode {lat: 19.07, lon: 72.87}
        ↓
Backend calls Nominatim
        ↓
Returns: "Mumbai, Maharashtra, India"
        ↓
Display confirmation to user
        ↓
POST /api/update-location {lat, lon, name, dms}
        ↓
Save to location_config.json
        ↓
Clear cache (_cached = {})
        ↓
Page reload (window.location.reload())
        ↓
New dashboard render with Mumbai data
```

---

### Refresh Button Flow

```
User clicks "🔄 Refresh"
        ↓
POST /refresh
        ↓
Clear _cached dict
        ↓
Re-run get_weather()
        ↓
Re-run predict_soil_moisture()
        ↓
Re-run generate_recommendations()
        ↓
Return {status: 'ok', timestamp}
        ↓
Page reload
        ↓
Fresh data displayed
```

---

### Live/Simulation Mode Toggle

```
User toggles switch
        ↓
JavaScript calls toggleTwinMode(isSimulation)
        ↓
if Live Mode:
    - Use NASA soil moisture
    - Use NDVI mean for health
    - Disable manual controls
    twin.sync_with_real_data(nasa, ndvi)
else:
    - Use simulated values
    - Enable sliders
    - Allow manual irrigation/fertilization
    twin.set_manual_levels(irrigation, fertilization)
        ↓
POST /control {mode, action, levels}
        ↓
Update twin state
        ↓
Return new state JSON
        ↓
Update 3D field colors
```

---

## 8. Caching Strategy

### NDVI Cache (`ndvi_cache.json`)

**Storage:**
```json
{
  "12.9719,77.5937": {
    "ndvi_grid": [[0.3, ...], ...],
    "ndvi_mean": 0.306,
    "ndvi_min": -0.002,
    "ndvi_max": 0.652,
    "ndvi_std": 0.168,
    "date": "2025-11-10",
    "satellite": "Sentinel-2",
    "source": "sentinel2"
  }
}
```

**Cache Logic:**
```python
def get_cached_ndvi(lat, lon):
    key = f"{lat:.4f},{lon:.4f}"
    if key in cache:
        age = (now - cache[key]['date']).days
        if age <= 7:
            # Check variation
            if max - min >= 0.05:
                return cache[key]
    return None
```

**Why Cache?**
- Earth Engine has rate limits
- Satellite data doesn't change daily
- Faster dashboard loads
- Offline capability

---

### Flask Memory Cache (`_cached`)

**Storage:**
```python
_cached = {
    'forecast': forecast_df,
    'weather': weather,
    'timestamp': '2025-11-22T01:33:03'
}
```

**Invalidation:**
- User clicks Refresh
- Location changes
- Server restarts

---

## 9. Fallback Decision Tree

```
┌─────────────────────────┐
│   Get Weather Data      │
└────────┬────────────────┘
         │
    ┌────▼────┐
    │OpenWeather API│
    └────┬────┘
         │
    ┌────▼────────────────┐
    │Success?             │
    └─┬─────────────────┬─┘
      │YES              │NO
      │                 │
┌─────▼─────┐    ┌──────▼──────┐
│Use Live   │    │Use Simulated│
│Weather    │    │Weather      │
└─────┬─────┘    └──────┬──────┘
      │                 │
      └─────────┬───────┘
                │
       ┌────────▼────────┐
       │   Get NDVI      │
       └────────┬────────┘
                │
           ┌────▼────┐
           │Cache?   │
           └────┬────┘
                │
           ┌────▼────────────┐
           │Valid & Fresh?   │
           └─┬─────────────┬─┘
             │YES          │NO
             │             │
      ┌──────▼──────┐  ┌──▼─────────┐
      │Use Cached   │  │Query Earth │
      │NDVI         │  │Engine      │
      └──────┬──────┘  └──┬─────────┘
             │             │
             │        ┌────▼────────┐
             │        │Success &    │
             │        │Has Variation│
             │        └─┬─────────┬─┘
             │          │YES      │NO
             │    ┌─────▼────┐ ┌──▼────────┐
             │    │Use Real  │ │Simulate   │
             │    │NDVI      │ │NDVI       │
             │    └─────┬────┘ └──┬────────┘
             │          │         │
             └──────────┴─────────┘
                        │
              ┌─────────▼─────────┐
              │  Get Soil Moisture│
              └─────────┬─────────┘
                        │
                   ┌────▼────┐
                   │NASA API │
                   └────┬────┘
                        │
                   ┌────▼─────────┐
                   │Success?      │
                   └─┬──────────┬─┘
                     │YES       │NO
              ┌──────▼──┐   ┌───▼────────┐
              │Use NASA │   │Simulate    │
              │Moisture │   │Moisture    │
              └──────┬──┘   └───┬────────┘
                     │          │
                     └────┬─────┘
                          │
                 ┌────────▼────────┐
                 │All Data Ready   │
                 └────────┬────────┘
                          │
                 ┌────────▼────────┐
                 │Render Dashboard │
                 └─────────────────┘
```

---

## 10. Data Flow Summary

### Real Data Path (Ideal)

```
OpenWeather → Live Weather
Earth Engine → Real NDVI Grid
NASA POWER → (Currently 422, falls back to simulation)
    ↓
Digital Twin syncs with real values
    ↓
3D field colors match satellite NDVI
    ↓
Forecast uses real baseline
    ↓
AI recommends based on real conditions
```

### Current Actual Path

```
OpenWeather → ✅ Live Weather
Earth Engine → ✅ Real NDVI Grid (cached)
NASA POWER → ⚠️ Simulated Moisture (API returning 422)
    ↓
Digital Twin uses real NDVI, simulated moisture
    ↓
3D field PRIMARILY driven by NDVI (real data)
    ↓
Forecast uses simulated moisture baseline
    ↓
AI uses real weather + simulated moisture
```

---

## 11. Key Insights

### What's Real vs. Simulated

| Component | Status | Source |
|-----------|--------|--------|
| **Weather** | ✅ Real | OpenWeather API |
| **NDVI Grid** | ✅ Real | Sentinel-2 via Earth Engine |
| **Soil Moisture** | ⚠️ Simulated | NASA POWER unavailable |
| **3D Field Colors** | ✅ Real | Driven by NDVI grid |
| **3D Field Density** | ✅ Real | Driven by NDVI grid |
| **Forecast** | 🟡 Mixed | Real weather + simulated moisture baseline |
| **AI Recommendations** | 🟡 Mixed | Real conditions + forecast |

### Why 3D Field is Accurate

Even though soil moisture is simulated, the 3D field is **95% driven by NDVI**:

```javascript
// For each plant
const localHealth = ndviData[i][j];  // ← Real satellite data
const plantColor = interpolate(stressed, healthy, localHealth);
const plantDensity = baseDensity * localHealth;
```

Soil moisture only affects:
- Live mode sync (minor adjustment)
- Forecast baseline (not visual)

The visual representation (colors, density, health) comes from **real NDVI**.

---

## 12. Console Log Interpretation

### Successful Real Data Flow
```
🌦️ Weather source: OpenWeather (lat=12.9719, lon=77.5937)
🛰️ Fetching REAL NDVI data for 12.9719, 77.5937...
✅ Retrieved 10x10 NDVI grid | mean: 0.306 | min/max: -0.002/0.652
📊 NDVI source: sentinel2 (mean: 0.306)
⚠️ NASA POWER HTTP 422 for date 20251121
⚠️ NASA POWER unavailable, using simulated soil moisture
```

**Interpretation:**
- ✅ Weather: Live from OpenWeather
- ✅ NDVI: Real from Sentinel-2
- ⚠️ Moisture: Simulated (NASA API failed)
- **Result:** Dashboard functional with primarily real data

---

## Files Reference

| File | Purpose | Data Flow Role |
|------|---------|----------------|
| `app.py` | Flask routes | Orchestration layer |
| `data_ingest.py` | API calls | External data fetching |
| `earth_engine_ndvi.py` | NDVI fetching | Satellite data integration |
| `preprocessing.py` | Data cleaning | Safety layer |
| `crop_model.py` | Digital twin | State simulation |
| `predictor.py` | Forecasting | ML predictions |
| `geocoding.py` | Location services | Coordinate conversion |
| `templates/dashboard_premium.html` | Frontend | Visualization rendering |
| `static/premium-style.css` | Styling | UI presentation |
| `config.py` | Configuration | Settings & API keys |
| `location_config.json` | Dynamic location | Persistent coordinates |
| `ndvi_cache.json` | NDVI cache | Performance optimization |

---

**Last Updated:** November 22, 2024  
**Version:** 1.0

