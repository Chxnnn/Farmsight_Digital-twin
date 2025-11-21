# API Setup Guide

Complete guide for configuring all external data sources in the FarmSight Digital Twin dashboard.

---

## 1. Google Earth Engine (Sentinel-2 NDVI)

### What It Provides
- 10×10 grid of NDVI values (vegetation health)
- 10 m resolution satellite imagery
- Filtered by date, cloud cover, and location

### Setup Steps

1. **Create Google Cloud Project:**
   ```bash
   # Visit https://console.cloud.google.com
   # Create a new project (e.g., "digitaltwin-farming")
   # Enable Earth Engine API
   ```

2. **Authenticate Earth Engine:**
   ```bash
   cd /Users/chethanam/Downloads/digitaltwin
   source dt_env/bin/activate
   
   # Authenticate
   earthengine authenticate
   
   # Set your project
   earthengine set_project digitaltwin-farming
   ```

3. **Verify Setup:**
   ```bash
   python -c "import ee; ee.Initialize(); print('✅ Earth Engine ready!')"
   ```

### Files Involved
- `earth_engine_ndvi.py` - Main integration
- `ndvi_cache.json` - Cached NDVI grids (auto-generated)

### Troubleshooting
- **Error: "Element.get: Parameter 'object' is required"**  
  → Uses buffered sampling to avoid masked pixels
  
- **Error: "Not authenticated"**  
  → Run `earthengine authenticate --force`

- **Deprecated dataset warning**  
  → Now uses `COPERNICUS/S2_SR_HARMONIZED` (updated)

---

## 2. OpenWeather API

### What It Provides
- Live temperature, humidity, pressure
- Rainfall, wind speed, weather conditions
- Updated every request

### Setup Steps

1. **Get API Key:**
   ```bash
   # Visit https://openweathermap.org/api
   # Sign up for free account
   # Get API key from dashboard
   ```

2. **Configure in Project:**
   ```python
   # Edit config.py
   WEATHER_API_KEY = "your_openweather_api_key_here"
   ```

3. **Verify Setup:**
   - Restart Flask app
   - Check console for: `🌦️ Weather source: OpenWeather`
   - If you see `⚠️ OpenWeather fetch failed`, check your key

### Files Involved
- `config.py` - API key storage
- `data_ingest.py` - API calls in `get_weather()`

### API Endpoint
```
GET https://api.openweathermap.org/data/2.5/weather
Parameters:
  - lat: latitude
  - lon: longitude
  - appid: your API key
  - units: metric
```

### Response Example
```json
{
  "main": {
    "temp": 25.3,
    "humidity": 65,
    "pressure": 1013
  },
  "wind": {
    "speed": 4.5
  },
  "rain": {
    "1h": 0.5
  },
  "weather": [{
    "description": "light rain"
  }]
}
```

### Fallback Behavior
If OpenWeather fails:
- Logs error message
- Uses simulated weather (15-30°C temp, 30-80% humidity)
- Dashboard remains functional

---

## 3. NASA POWER (Soil Moisture Baseline)

### What It Provides
- Precipitation data (PRECTOTCORR parameter)
- Converted to soil moisture estimate
- Global coverage, agricultural community

### Setup Steps

**No API key required** - NASA POWER is free and open.

### Current Status
- **Attempted:** SOILM (soil moisture) - returned 422 errors
- **Attempted:** PRECTOTCORR (precipitation) - returned 422 errors
- **Active:** Simulated fallback (35-55% moisture range)

### Why It's Not Working
NASA POWER may return 422 for:
1. Data not yet processed for recent dates
2. Parameter not available for specific lat/lon
3. Regional coverage limitations

### Files Involved
- `data_ingest.py` - `get_soil_moisture()` function

### API Endpoint (Ready to Use)
```
GET https://power.larc.nasa.gov/api/temporal/daily/point
Parameters:
  - parameters: PRECTOTCORR or SOILM
  - community: AG
  - latitude: field latitude
  - longitude: field longitude
  - start: YYYYMMDD
  - end: YYYYMMDD
  - format: JSON
```

### Fallback Behavior
When NASA POWER is unavailable:
- Logs warning message
- Uses simulated soil moisture (35-55%)
- Dashboard displays data normally
- Digital twin uses simulated baseline

### Future Options
1. Wait for NASA POWER date processing
2. Use different parameter (e.g., evapotranspiration)
3. Switch to SMAP satellite data (requires NASA Earthdata account)
4. Keep current simulated approach

---

## 4. ESRI World Imagery (Satellite Basemap)

### What It Provides
- High-resolution satellite tiles
- Visual context for field location
- Updated every 1-6 months

### Setup Steps

**No setup required** - loaded via Leaflet CDN in browser.

### Files Involved
- `templates/dashboard_premium.html` - Leaflet map initialization
- `static/premium-style.css` - Map styling

### How It Works
```javascript
// Frontend loads ESRI tiles directly
var esriSatellite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    { attribution: 'ESRI' }
);
```

### No Backend Calls
This is purely client-side; the browser fetches tiles directly from ESRI servers.

---

## 5. OpenStreetMap Nominatim (Geocoding)

### What It Provides
- Reverse geocoding (coordinates → location name)
- City, state, country information
- DMS coordinate formatting

### Setup Steps

**No API key required** - Nominatim is free, but rate-limited.

### Rate Limits
- 1 request per second
- Must include User-Agent header
- Already configured in `geocoding.py`

### Files Involved
- `geocoding.py` - Reverse geocoding functions
- `app.py` - `/api/geocode` and `/api/update-location` endpoints

### API Endpoint
```
GET https://nominatim.openstreetmap.org/reverse
Parameters:
  - lat: latitude
  - lon: longitude
  - format: json
  - addressdetails: 1
  - zoom: 10
Headers:
  - User-Agent: DigitalTwinDashboard/1.0
```

### Response Example
```json
{
  "address": {
    "city": "Bengaluru",
    "state": "Karnataka",
    "country": "India"
  },
  "display_name": "Bengaluru, Karnataka, India"
}
```

### Usage in Dashboard
1. User enters coordinates
2. Frontend calls `/api/geocode`
3. Backend queries Nominatim
4. Returns formatted location name
5. Updates `location_config.json`
6. Dashboard reloads with new location

---

## API Summary Table

| API | Setup Required | Cost | Current Status | Fallback |
|-----|----------------|------|----------------|----------|
| **Earth Engine** | ✅ Auth required | Free | ✅ Working | Simulated NDVI |
| **OpenWeather** | ✅ API key | Free tier | ✅ Working | Simulated weather |
| **NASA POWER** | ❌ None | Free | ⚠️ 422 errors | Simulated moisture |
| **ESRI Imagery** | ❌ None | Free | ✅ Working | N/A |
| **Nominatim** | ❌ None | Free | ✅ Working | N/A |

---

## Configuration Files

### `config.py`
```python
WEATHER_API_KEY = "your_openweather_key_here"
LOCATION_COORDS = {"lat": 12.9719, "lon": 77.5937}
LOCATION_COORDS_DISPLAY = {"lat": "12°58′18.8″N", "lon": "77°35′37.3″E"}
LOCATION_NAME = "Bengaluru, Karnataka, India"
```

### `location_config.json` (Auto-generated)
```json
{
  "coords": {"lat": 12.9719, "lon": 77.5937},
  "coords_display": {"lat": "12°58′18.8″N", "lon": "77°35′37.3″E"},
  "name": "Bengaluru, Karnataka, India"
}
```

### `ndvi_cache.json` (Auto-generated)
```json
{
  "12.9719,77.5937": {
    "ndvi_grid": [[0.3, 0.4, ...], ...],
    "ndvi_mean": 0.306,
    "date": "2025-11-10",
    "source": "sentinel2"
  }
}
```

---

## Quick Start Checklist

- [ ] Create Google Cloud project
- [ ] Run `earthengine authenticate`
- [ ] Set Earth Engine project ID
- [ ] Get OpenWeather API key
- [ ] Update `config.py` with API key
- [ ] Update coordinates in `config.py`
- [ ] Run `python app.py`
- [ ] Visit http://127.0.0.1:5001
- [ ] Check console for API status messages

---

## Console Log Examples

### Successful Setup
```
✅ Earth Engine NDVI module loaded
🌦️ Weather source: OpenWeather (lat=12.9719, lon=77.5937)
🛰️ Fetching REAL NDVI data for 12.9719, 77.5937...
📅 Found image from 2025-11-10, cloud cover: 10.4%
✅ Retrieved 10x10 NDVI grid | mean: 0.306
📊 NDVI source: sentinel2 (mean: 0.306)
```

### With Fallbacks
```
✅ Earth Engine NDVI module loaded
🌦️ Weather source: OpenWeather (lat=12.9719, lon=77.5937)
🛰️ Fetching REAL NDVI data for 12.9719, 77.5937...
✅ Using cached NDVI from 2025-11-10
⚠️ NASA POWER HTTP 422 for date 20251121
⚠️ NASA POWER unavailable after retry, using simulated soil moisture
```

---

## Troubleshooting Common Issues

### Earth Engine "Not Authenticated"
```bash
earthengine authenticate --force
earthengine set_project YOUR_PROJECT_ID
```

### OpenWeather 401 Error
- Check API key is correct in `config.py`
- Verify key is active on OpenWeather dashboard
- Restart Flask app after changing key

### NASA POWER 422 Error
- This is expected for recent dates
- System automatically falls back to simulation
- Dashboard remains fully functional

### Nominatim Rate Limit
- Wait 1 second between location searches
- Already enforced by console debouncing
- If blocked, wait a few minutes

---

## Next Steps

1. **Monitor Console Logs:** Watch for API status messages
2. **Test Location Changes:** Use search bar to verify geocoding
3. **Check Cache Files:** Verify `ndvi_cache.json` and `location_config.json` are created
4. **Review Dashboard:** Ensure all cards display data correctly

---

**Last Updated:** November 22, 2024  
**Version:** 1.0

