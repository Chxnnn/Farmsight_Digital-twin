# 🌾 Crop Digital Twin MVP

## 🛰️ Now with Real Satellite NDVI from Google Earth Engine!

### Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Authenticate with Google Earth Engine:**
   ```bash
   python setup_earth_engine.py
   ```
   
   This beautiful setup wizard will:
   - ✅ Install Earth Engine API
   - ✅ Authenticate with Google
   - ✅ Test real satellite data
   - ✅ Verify everything works!

3. **Add your OpenWeather API key in `config.py`:**
   ```python
   WEATHER_API_KEY = "YOUR_OPENWEATHER_KEY"
   ```
   (Get a free key at https://openweathermap.org/api)

4. **Update your field location in `config.py`:**
   ```python
   LOCATION_COORDS = {"lat": YOUR_LAT, "lon": YOUR_LON}
   ```

5. **Run the app:**
   ```bash
   python app.py
   ```

6. **Visit** http://127.0.0.1:5001/ **in your browser**

---

## 📚 Documentation

- **`SETUP_COMPLETE.md`** - What was built and why it's beautiful
- **`SATELLITE_SYNC_GUIDE.md`** - How satellite data drives your 3D plant! ✨
- **`EARTH_ENGINE_QUICKSTART.md`** - Complete Earth Engine integration guide
- **`NDVI_INTEGRATION_GUIDE.md`** - All NDVI data source options
- **`WHATS_NEW.md`** - Recent improvements

---

## ✨ Features

- 🛰️ **Real Satellite NDVI** from Sentinel-2 (10m resolution)
- 🔄 **Satellite-Synced Digital Twin** - 3D plant reflects real field conditions!
- 📊 **Visual NDVI Interpretation** - Color-coded health bars (no manual interpretation!)
- 🤖 **AI Recommendations** using Q-learning
- 📈 **Prophet Forecasting** for soil moisture
- 🌦️ **Live Weather via OpenWeather** (auto fallback if offline)
- 🌍 **NASA POWER Soil Moisture** with graceful fallback
- 🌾 **Interactive 3D Crop Visualization** with growth simulation
- 🎯 **Contextual Guidance** - Clear action recommendations for every reading
- 💾 **Smart Caching** for offline capability
- 🎨 **Beautiful Dashboard** with satellite metadata and health indicators

**Your digital twin now mirrors your real field from space!** 🚀🌍
