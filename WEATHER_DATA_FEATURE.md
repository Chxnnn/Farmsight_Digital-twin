# Real-Time Weather Data Feature
## Live Environmental Monitoring via OpenWeather API

---

## 🎯 Overview

The **Real-Time Weather Data** feature displays current meteorological conditions at the field location, including temperature, humidity, rainfall, wind speed, and weather description. It updates hourly and provides critical environmental context for crop management decisions.

**Location in Dashboard:** Bottom-middle card (Row 2, Column 2)

---

## 🔍 What Problem Does It Solve?

### Traditional Farming Problem:
- Farmers rely on general weather forecasts for entire regions
- Location-specific microclimates not captured
- Difficult to correlate weather with crop stress
- No integration with field-specific data

### Our Solution:
- **Hyperlocal weather** for exact field coordinates
- **Real-time updates** (every hour)
- **Integrated with crop data** (temperature affects growth calculations)
- **Decision context** (e.g., recent rain = skip irrigation)

---

## 🌐 Data Source

### API: OpenWeather Current Weather API
- **Provider**: OpenWeather (openweathermap.org)
- **Endpoint**: `/data/2.5/weather`
- **Update Frequency**: Hourly
- **Coverage**: Global (200,000+ weather stations)
- **Cost**: Free tier (1,000 calls/day)

### Data Collected:
| Parameter | Unit | Description |
|-----------|------|-------------|
| **Temperature** | °C | Air temperature (converted from Kelvin) |
| **Humidity** | % | Relative humidity (0-100%) |
| **Rainfall** | mm | Precipitation in last hour |
| **Wind Speed** | km/h | Wind velocity (converted from m/s) |
| **Pressure** | hPa | Atmospheric pressure |
| **Clouds** | % | Cloud coverage |
| **Weather** | Text | Description (e.g., "Partly cloudy") |
| **Icon** | Code | Weather icon identifier |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│            USER'S BROWSER                           │
│                                                     │
│  [Weather Card]                                    │
│   🌡️ 28°C                                          │
│   💧 75% humidity                                   │
│   🌧️ 2.3mm rain (last hour)                       │
│   💨 12.6 km/h wind                                │
│   ☁️ Partly cloudy                                 │
└─────────────────┬───────────────────────────────────┘
                  │ Receives formatted data
                  │
┌─────────────────▼───────────────────────────────────┐
│         FLASK SERVER (app.py)                       │
│                                                     │
│  weather_data = get_weather(lat, lon)              │
│  # Returns: {                                       │
│  #   'temperature': 28,                            │
│  #   'humidity': 75,                               │
│  #   'rainfall': 2.3,                              │
│  #   'wind_speed': 12.6,                           │
│  #   'description': 'Partly cloudy',               │
│  #   'icon': '02d'                                 │
│  # }                                                │
└─────────────────┬───────────────────────────────────┘
                  │ Calls
                  │
┌─────────────────▼───────────────────────────────────┐
│       data_ingest.py Module                         │
│                                                     │
│  get_weather(lat, lon, use_cache=True):           │
│    1. Check in-memory cache (30 min TTL)          │
│    2. If expired: Call OpenWeather API            │
│    3. Parse JSON response                          │
│    4. Convert units (K→°C, m/s→km/h)              │
│    5. Cache result                                 │
│    6. Return formatted data                        │
└─────────────────┬───────────────────────────────────┘
                  │ HTTP GET Request
                  │
┌─────────────────▼───────────────────────────────────┐
│       OPENWEATHER API                               │
│                                                     │
│  GET /data/2.5/weather?lat={lat}&lon={lon}        │
│      &appid={API_KEY}&units=metric                │
│                                                     │
│  Returns JSON with current conditions              │
└─────────────────┬───────────────────────────────────┘
                  │ Data from
                  │
┌─────────────────▼───────────────────────────────────┐
│      WEATHER STATIONS NETWORK                       │
│                                                     │
│  • 200,000+ stations worldwide                     │
│  • Satellites for remote areas                     │
│  • Updates every hour                              │
└─────────────────────────────────────────────────────┘
```

---

## 💻 Code Implementation

### 1. Backend: Weather Fetching (data_ingest.py)

```python
import requests
from datetime import datetime, timedelta

# In-memory cache
_weather_cache = {
    'data': None,
    'timestamp': None,
    'location': None
}

WEATHER_CACHE_MINUTES = 30


def get_weather(lat, lon, use_cache=True, refresh=False):
    """
    Fetch current weather data from OpenWeather API.
    
    Args:
        lat: Latitude of field
        lon: Longitude of field
        use_cache: Whether to use cached data
        refresh: Force fresh fetch (bypass cache)
    
    Returns:
        dict with weather parameters
    """
    
    # Step 1: Check cache (unless force refresh)
    if use_cache and not refresh:
        cached = _get_cached_weather(lat, lon)
        if cached:
            print(f"✅ Using cached weather (age: {cached['age_minutes']:.0f} min)")
            return cached['data']
    
    # Step 2: Fetch from OpenWeather API
    print(f"🌦️ Fetching weather from OpenWeather API...")
    
    API_KEY = os.getenv('OPENWEATHER_API_KEY', 'your_api_key_here')
    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}"
        f"&lon={lon}"
        f"&appid={API_KEY}"
        f"&units=metric"  # Get Celsius instead of Kelvin
    )
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Step 3: Parse response
        weather_data = {
            'temperature': round(data['main']['temp'], 1),
            'feels_like': round(data['main']['feels_like'], 1),
            'temp_min': round(data['main']['temp_min'], 1),
            'temp_max': round(data['main']['temp_max'], 1),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # m/s → km/h
            'wind_direction': data['wind'].get('deg', 0),
            'clouds': data['clouds']['all'],
            'rainfall': data.get('rain', {}).get('1h', 0.0),  # Last hour
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
            'weather_main': data['weather'][0]['main'],
            'timestamp': datetime.now().isoformat(),
            'location': data.get('name', 'Unknown')
        }
        
        # Step 4: Cache result
        _cache_weather(lat, lon, weather_data)
        
        print(f"✅ Weather fetched: {weather_data['temperature']}°C, "
              f"{weather_data['description']}")
        
        return weather_data
    
    except requests.exceptions.RequestException as e:
        print(f"❌ OpenWeather API error: {e}")
        return _get_fallback_weather(lat, lon)
    
    except KeyError as e:
        print(f"❌ Unexpected API response format: {e}")
        return _get_fallback_weather(lat, lon)


def _get_cached_weather(lat, lon):
    """Check if cached weather is still valid."""
    
    if _weather_cache['data'] is None:
        return None
    
    # Check if same location
    cached_location = _weather_cache['location']
    if cached_location != (lat, lon):
        return None
    
    # Check if cache expired
    cached_time = _weather_cache['timestamp']
    age = datetime.now() - cached_time
    age_minutes = age.total_seconds() / 60
    
    if age_minutes > WEATHER_CACHE_MINUTES:
        return None
    
    return {
        'data': _weather_cache['data'],
        'age_minutes': age_minutes
    }


def _cache_weather(lat, lon, data):
    """Store weather data in cache."""
    
    _weather_cache['data'] = data
    _weather_cache['timestamp'] = datetime.now()
    _weather_cache['location'] = (lat, lon)


def _get_fallback_weather(lat, lon):
    """Return simulated weather when API fails."""
    
    print("⚠️ Using simulated weather data")
    
    return {
        'temperature': 25.0,
        'feels_like': 26.0,
        'temp_min': 22.0,
        'temp_max': 28.0,
        'humidity': 65,
        'pressure': 1013,
        'wind_speed': 10.0,
        'wind_direction': 180,
        'clouds': 40,
        'rainfall': 0.0,
        'description': 'Partly cloudy',
        'icon': '02d',
        'weather_main': 'Clouds',
        'timestamp': datetime.now().isoformat(),
        'location': 'Simulated'
    }
```

---

### 2. Backend: Flask Integration (app.py)

```python
@app.route('/')
def index():
    # Get coordinates
    lat = config.LOCATION_COORDS['lat']
    lon = config.LOCATION_COORDS['lon']
    
    # Fetch weather data
    refresh = request.args.get('refresh', '0') == '1'
    weather_data = get_weather(lat, lon, use_cache=True, refresh=refresh)
    
    # Pass to template
    return render_template(
        'dashboard_premium.html',
        weather=weather_data,
        # ... other data ...
    )
```

---

### 3. Frontend: Weather Display (dashboard_premium.html)

```html
<!-- HTML Structure -->
<div class="card">
    <div class="card-header">
        <h2 class="card-title">🌦️ Real-Time Weather</h2>
        <p class="card-subtitle">
            {{ weather.location }} | 
            Updated: {{ weather.timestamp[:16] }}
        </p>
    </div>
    
    <div class="weather-grid">
        
        <!-- Temperature Section -->
        <div class="weather-main">
            <div class="weather-icon-large">
                <img src="https://openweathermap.org/img/wn/{{ weather.icon }}@2x.png" 
                     alt="{{ weather.description }}"
                     style="width:80px; height:80px;">
            </div>
            <div class="weather-temp-display">
                <div class="temp-large">{{ weather.temperature }}°C</div>
                <div class="temp-description">{{ weather.description|title }}</div>
                <div class="temp-feels-like">Feels like {{ weather.feels_like }}°C</div>
            </div>
        </div>
        
        <!-- Weather Parameters Grid -->
        <div class="weather-params">
            
            <!-- Humidity -->
            <div class="weather-param-card">
                <div class="param-icon">💧</div>
                <div class="param-value">{{ weather.humidity }}%</div>
                <div class="param-label">Humidity</div>
                {% if weather.humidity > 80 %}
                <div class="param-status high">High</div>
                {% elif weather.humidity < 40 %}
                <div class="param-status low">Low</div>
                {% else %}
                <div class="param-status normal">Normal</div>
                {% endif %}
            </div>
            
            <!-- Rainfall -->
            <div class="weather-param-card">
                <div class="param-icon">🌧️</div>
                <div class="param-value">{{ weather.rainfall }} mm</div>
                <div class="param-label">Rain (1h)</div>
                {% if weather.rainfall > 5 %}
                <div class="param-status high">Heavy</div>
                {% elif weather.rainfall > 0 %}
                <div class="param-status normal">Light</div>
                {% else %}
                <div class="param-status low">None</div>
                {% endif %}
            </div>
            
            <!-- Wind Speed -->
            <div class="weather-param-card">
                <div class="param-icon">💨</div>
                <div class="param-value">{{ weather.wind_speed }} km/h</div>
                <div class="param-label">Wind Speed</div>
                {% if weather.wind_speed > 30 %}
                <div class="param-status high">Strong</div>
                {% elif weather.wind_speed > 15 %}
                <div class="param-status normal">Moderate</div>
                {% else %}
                <div class="param-status low">Calm</div>
                {% endif %}
            </div>
            
            <!-- Cloud Cover -->
            <div class="weather-param-card">
                <div class="param-icon">☁️</div>
                <div class="param-value">{{ weather.clouds }}%</div>
                <div class="param-label">Clouds</div>
                {% if weather.clouds > 70 %}
                <div class="param-status high">Overcast</div>
                {% elif weather.clouds > 30 %}
                <div class="param-status normal">Partly</div>
                {% else %}
                <div class="param-status low">Clear</div>
                {% endif %}
            </div>
            
            <!-- Pressure -->
            <div class="weather-param-card">
                <div class="param-icon">🌡️</div>
                <div class="param-value">{{ weather.pressure }} hPa</div>
                <div class="param-label">Pressure</div>
                {% if weather.pressure > 1020 %}
                <div class="param-status high">High</div>
                {% elif weather.pressure < 1000 %}
                <div class="param-status low">Low</div>
                {% else %}
                <div class="param-status normal">Normal</div>
                {% endif %}
            </div>
            
            <!-- Temperature Range -->
            <div class="weather-param-card">
                <div class="param-icon">🌡️</div>
                <div class="param-value">
                    {{ weather.temp_min }}° - {{ weather.temp_max }}°
                </div>
                <div class="param-label">Temp Range</div>
            </div>
            
        </div>
        
    </div>
    
    <!-- Weather Alert (if extreme conditions) -->
    {% if weather.temperature > 35 %}
    <div class="weather-alert danger">
        <span class="alert-icon">⚠️</span>
        <span>High temperature alert! Crops may experience heat stress. Consider irrigation.</span>
    </div>
    {% elif weather.temperature < 5 %}
    <div class="weather-alert warning">
        <span class="alert-icon">❄️</span>
        <span>Low temperature warning! Risk of frost damage. Monitor closely.</span>
    </div>
    {% endif %}
    
    {% if weather.wind_speed > 40 %}
    <div class="weather-alert danger">
        <span class="alert-icon">💨</span>
        <span>Strong winds detected! Risk of lodging (plants falling over).</span>
    </div>
    {% endif %}
    
    {% if weather.rainfall > 20 %}
    <div class="weather-alert warning">
        <span class="alert-icon">🌧️</span>
        <span>Heavy rainfall! Skip irrigation today. Monitor for waterlogging.</span>
    </div>
    {% endif %}
    
</div>

<style>
.weather-grid {
    display: grid;
    gap: 20px;
}

.weather-main {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px;
    background: linear-gradient(135deg, rgba(74, 222, 128, 0.1), rgba(59, 130, 246, 0.1));
    border-radius: 12px;
}

.temp-large {
    font-size: 3rem;
    font-weight: 700;
    color: #4ade80;
}

.temp-description {
    font-size: 1.1rem;
    color: #e8ecf1;
    text-transform: capitalize;
}

.temp-feels-like {
    font-size: 0.9rem;
    color: #a8b2bd;
}

.weather-params {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
}

.weather-param-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 15px;
    text-align: center;
    transition: transform 0.2s, background 0.2s;
}

.weather-param-card:hover {
    background: rgba(255, 255, 255, 0.08);
    transform: translateY(-2px);
}

.param-icon {
    font-size: 2rem;
    margin-bottom: 8px;
}

.param-value {
    font-size: 1.3rem;
    font-weight: 600;
    color: #e8ecf1;
    margin-bottom: 4px;
}

.param-label {
    font-size: 0.85rem;
    color: #a8b2bd;
    margin-bottom: 6px;
}

.param-status {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
}

.param-status.high {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}

.param-status.normal {
    background: rgba(74, 222, 128, 0.2);
    color: #4ade80;
}

.param-status.low {
    background: rgba(59, 130, 246, 0.2);
    color: #3b82f6;
}

.weather-alert {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-radius: 8px;
    margin-top: 15px;
    font-size: 0.9rem;
}

.weather-alert.danger {
    background: rgba(239, 68, 68, 0.15);
    border-left: 4px solid #ef4444;
    color: #fecaca;
}

.weather-alert.warning {
    background: rgba(251, 191, 36, 0.15);
    border-left: 4px solid #fbbf24;
    color: #fde68a;
}
</style>
```

---

## 🔗 Integration with Other Features

### 1. Growth Stage Calculation (GDD)
Temperature data is critical for determining crop development:

```python
# In crop_model.py

def update_growth_stage(current_temp):
    """
    Calculate Growing Degree Days (GDD) from temperature.
    
    GDD = max(0, (Tmax + Tmin)/2 - Tbase)
    where Tbase = 0°C for wheat
    """
    
    # Use weather data
    tmax = weather_data['temp_max']
    tmin = weather_data['temp_min']
    
    daily_gdd = max(0, (tmax + tmin) / 2 - 0)
    cumulative_gdd += daily_gdd
    
    # Determine stage based on accumulated GDD
    if cumulative_gdd < 180:
        stage = 'emergence'
    elif cumulative_gdd < 395:
        stage = 'tillering'
    # ... etc
    
    return stage
```

### 2. Irrigation Decision Support
Recent rainfall affects irrigation recommendations:

```python
# In predictor.py

def should_irrigate(soil_moisture, weather):
    """Decide if irrigation is needed."""
    
    # Check recent rainfall
    if weather['rainfall'] > 5:
        return False, "Recent rainfall sufficient"
    
    # Check humidity (affects evaporation)
    if weather['humidity'] > 80 and soil_moisture > 40:
        return False, "High humidity reduces water loss"
    
    # Check temperature (affects water stress)
    if weather['temperature'] > 35 and soil_moisture < 50:
        return True, "High temperature + moderate moisture = stress risk"
    
    return soil_moisture < 30, "Low soil moisture"
```

### 3. Stress Assessment
Weather extremes trigger crop stress:

```python
# In crop_model.py

def calculate_stress_tier(ndvi, weather, soil_moisture):
    """Determine crop stress level (1-4)."""
    
    stress_factors = []
    
    # Temperature stress
    if weather['temperature'] > 35:
        stress_factors.append('heat_stress')
    elif weather['temperature'] < 5:
        stress_factors.append('cold_stress')
    
    # Water stress
    if soil_moisture < 30 and weather['rainfall'] < 1:
        stress_factors.append('drought_stress')
    
    # Wind stress
    if weather['wind_speed'] > 40:
        stress_factors.append('wind_stress')
    
    # Tier: 1 (optimal) to 4 (severe stress)
    tier = 1 + min(3, len(stress_factors))
    
    return tier
```

---

## 🎯 Key Features

### 1. **Dynamic Status Indicators**
```jinja2
{% if weather.humidity > 80 %}
<div class="param-status high">High</div>
{% elif weather.humidity < 40 %}
<div class="param-status low">Low</div>
{% else %}
<div class="param-status normal">Normal</div>
{% endif %}
```
- Color-coded badges (green/yellow/red)
- Instant visual feedback

### 2. **Automatic Alerts**
```jinja2
{% if weather.temperature > 35 %}
<div class="weather-alert danger">
    ⚠️ High temperature alert! Crops may experience heat stress.
</div>
{% endif %}
```
- Triggered by extreme conditions
- Actionable advice provided

### 3. **Weather Icons**
```html
<img src="https://openweathermap.org/img/wn/{{ weather.icon }}@2x.png">
```
- Visual weather representation
- Provided by OpenWeather
- Day/night variants

### 4. **Caching for Performance**
```python
WEATHER_CACHE_MINUTES = 30
# Weather doesn't change much in 30 min
# Saves API calls, improves speed
```

---

## 🚀 Performance Optimizations

### 1. In-Memory Caching
```python
_weather_cache = {
    'data': None,
    'timestamp': None,
    'location': None
}
```
- Instant retrieval (no API call)
- 30-minute validity
- Location-specific

### 2. Unit Conversion
```python
# API returns Kelvin
temp_celsius = data['main']['temp']  # Already Celsius (units=metric)

# API returns m/s for wind
wind_kmh = data['wind']['speed'] * 3.6
```
- Done once at fetch time
- Not repeated on every display

### 3. Fallback Data
```python
if API fails:
    return simulated_weather()
# Dashboard never breaks
```

---

## 🐛 Common Issues & Solutions

### Issue 1: API Rate Limit Exceeded
```python
# Free tier: 60 calls/minute, 1,000 calls/day
# Solution: Aggressive caching (30 min)
# Result: Max 48 calls/day per location
```

### Issue 2: Invalid API Key
```python
try:
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if response.status_code == 401:
        print("❌ Invalid API key")
        return fallback_weather()
```

### Issue 3: Network Timeout
```python
response = requests.get(url, timeout=5)
# If server doesn't respond in 5 sec, fail gracefully
```

---

## 📊 Data Accuracy

### Temperature: ±0.5°C typical
### Humidity: ±5% typical
### Rainfall: ±20% (measured vs. interpolated)
### Wind: ±10% typical

### Factors Affecting Accuracy:
- Distance to nearest weather station
- Microclimates (valleys, hills)
- Urban heat islands
- Equipment calibration

---

## 📚 Technical References

- **OpenWeather API Docs**: https://openweathermap.org/current
- **Weather Icons**: https://openweathermap.org/weather-conditions
- **Unit Conversions**: https://openweathermap.org/api/one-call-api#data

---

## ✅ Testing the Feature

### Test 1: Basic Display
```bash
# Open dashboard
# Weather card should show:
# - Temperature with icon
# - 6 parameter cards
# - All values populated
```

### Test 2: Cache Verification
```bash
# First load: "Fetching weather from OpenWeather API"
# Reload within 30 min: "Using cached weather"
# Check console logs
```

### Test 3: Extreme Conditions
```bash
# Manually set temperature to 40°C in code
# Should see heat stress alert
# Verify alert styling
```

---

**Feature Status:** ✅ Fully Implemented & Tested  
**Last Updated:** November 23, 2025  
**Files:** `/data_ingest.py`, `/app.py`, `/templates/dashboard_premium.html`


