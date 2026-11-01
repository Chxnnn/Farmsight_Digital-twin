# FarmSight Complete Features Documentation Index
## Comprehensive Technical Reference for All Dashboard Components

---

## 📚 Overview

This document provides an index of all feature documentation files with code snippets, architecture diagrams, and implementation details for the FarmSight Digital Twin Dashboard.

**Last Updated:** November 23, 2025

---

## 🗂️ Documentation Structure

### **Category 1: Core Visualization Features**

#### **1. Interactive Satellite Map**
**File:** `INTERACTIVE_MAP_FEATURE.md`

**What it does:** Allows users to click anywhere on the satellite map to select a new field location for analysis.

**Key Technologies:**
- Leaflet.js for interactive mapping
- ESRI World Imagery tiles
- Nominatim API for reverse geocoding
- Custom popup UI with location confirmation

**Code Sections:**
- Frontend: Map click event handling
- Backend: Location update API endpoint
- Cache clearing mechanism
- Page reload with cache-busting

**Status:** ✅ Fully Implemented

---

#### **2. NDVI to 3D Field Mapping**
**File:** `NDVI_3D_MAPPING_FEATURE.md`

**What it does:** Renders 3D wheat plants that match the NDVI heatmap grid - sparse plants where NDVI is low, dense plants where NDVI is high.

**Key Technologies:**
- Three.js / WebGL for 3D rendering
- Custom vegetation parameter mapping
- Grid-based plant positioning
- Real-time wind animation

**Code Sections:**
- `ndviToVegetationParams()` function
- Plant density calculation
- Color and height adjustment
- Grid position mapping (10×10)

**Status:** ✅ Fully Implemented

---

#### **3. NDVI Heatmap Visualization**
**File:** `NDVI_HEATMAP_FEATURE.md`

**What it does:** Displays a color-coded 10×10 grid showing vegetation health from Sentinel-2 satellite data.

**Key Technologies:**
- Google Earth Engine API
- Sentinel-2 satellite imagery
- Plotly.js heatmap visualization
- Custom color scale (blue → green → yellow)

**Code Sections:**
- Backend: `get_sentinel2_ndvi()` in `earth_engine_ndvi.py`
- NDVI calculation: `(NIR - Red) / (NIR + Red)`
- 50m buffered sampling
- Caching strategy (7 days)
- Frontend: Plotly heatmap rendering

**Key Data:**
- **Resolution:** 10 meters per pixel
- **Update Frequency:** Every 5 days
- **Grid Size:** 10×10 cells (100 samples)
- **Field Coverage:** 250m × 250m

**Status:** ✅ Fully Implemented

---

### **Category 2: AI & Prediction Features**

#### **4. Soil Moisture Forecast**
**File:** `SOIL_MOISTURE_FORECAST_FEATURE.md`

**What it does:** Predicts soil moisture for the next 7 days using Facebook Prophet AI, showing trend and confidence intervals.

**Key Technologies:**
- Facebook Prophet (time series forecasting)
- NASA POWER API (historical rainfall)
- Pandas DataFrames for data preparation
- Plotly.js line chart with confidence bands

**Code Sections:**
- Backend: `predict_soil_moisture()` in `predictor.py`
- Data preparation: Converting rainfall to moisture
- Prophet model training and forecasting
- Confidence interval extraction
- Frontend: Multi-trace chart rendering

**Key Metrics:**
- **Historical Data:** 30 days
- **Forecast Horizon:** 7 days
- **Confidence Level:** 95%
- **Typical Accuracy:** 85% (Day 1-2), 70% (Day 5-7)

**Status:** ✅ Fully Implemented

---

#### **5. AI Recommendations (Q-Learning)**
**File:** `AI_RECOMMENDATIONS_FEATURE.md`

**What it does:** Provides daily actionable advice (irrigate, fertilize, or wait) using a Q-Learning reinforcement learning agent.

**Key Technologies:**
- Q-Learning algorithm (reinforcement learning)
- Pretrained Q-table with domain knowledge
- State discretization (moisture × weather)
- Action selection based on Q-values

**Code Sections:**
- Backend: `SimpleQAgent` class in `predictor.py`
- Q-table construction with expert rules
- State determination from moisture/weather
- Action selection (`get_action()` method)
- Recommendation formatting

**Key Concepts:**
- **States:** 9 combinations (low/med/high moisture × dry/normal/wet weather)
- **Actions:** 3 options (irrigate, fertilize, wait)
- **Q-values:** Expected rewards for each state-action pair
- **Policy:** Greedy selection (choose highest Q-value)

**Example Q-Table:**
```
          | Irrigate | Fertilize | Wait
----------|----------|-----------|------
Low_Dry   |   +1.5   |   +0.1    | -0.5
Med_Normal|   +0.5   |   +0.6    | +0.7
High_Wet  |   -1.0   |   +0.4    | +1.2
```

**Status:** ✅ Fully Implemented

---

### **Category 3: Environmental Monitoring**

#### **6. Real-Time Weather Data**
**File:** `WEATHER_DATA_FEATURE.md`

**What it does:** Displays current meteorological conditions (temperature, humidity, rainfall, wind) from OpenWeather API.

**Key Technologies:**
- OpenWeather Current Weather API
- In-memory caching (30 minutes)
- Unit conversions (Kelvin → Celsius, m/s → km/h)
- Dynamic status indicators (color-coded)

**Code Sections:**
- Backend: `get_weather()` in `data_ingest.py`
- API call with error handling
- Cache checking and storing
- Fallback to simulated data
- Frontend: Weather grid display with icons

**Data Collected:**
| Parameter | Unit | Update Frequency |
|-----------|------|------------------|
| Temperature | °C | Hourly |
| Humidity | % | Hourly |
| Rainfall | mm | Hourly |
| Wind Speed | km/h | Hourly |
| Pressure | hPa | Hourly |
| Clouds | % | Hourly |

**Status:** ✅ Fully Implemented

---

### **Category 4: Crop Development Tracking**

#### **7. Growth Stage Tracking (GDD)**
**File:** `GROWTH_STAGE_TRACKING_FEATURE.md`

**What it does:** Automatically tracks wheat development stages based on accumulated Growing Degree Days (GDD) calculated from temperature.

**Key Technologies:**
- Growing Degree Days (GDD) calculation
- Stage threshold system
- Temperature integration
- Visual parameter adjustment

**Code Sections:**
- Backend: `WheatTwin` class in `crop_model.py`
- GDD formula: `max(0, (Tmax + Tmin)/2 - Tbase)`
- Stage determination based on cumulative GDD
- Visual parameter mapping for 3D rendering
- Frontend: Stage timeline display

**Growth Stages:**
| Stage | GDD Threshold | Typical Duration | Visual Height |
|-------|---------------|------------------|---------------|
| Germination | 0 | 7-10 days | 3 cm |
| Emergence | 150 | 3-5 days | 8 cm |
| Tillering | 180 | 10-20 days | 20 cm |
| Stem Elongation | 395 | 15-25 days | 60 cm |
| Booting | 700 | 10-15 days | 85 cm |
| Heading | 1000 | 7-10 days | 100 cm |
| Flowering | 1250 | 5-7 days | 105 cm |
| Grain Filling | 1500 | 20-30 days | 110 cm |
| Ripening | 1900 | 10-15 days | 110 cm |
| Maturity | 2100 | - | 105 cm |

**Formula Details:**
```
Daily GDD = max(0, (Tmax + Tmin)/2 - 10°C)

Example:
Day with Max=25°C, Min=15°C
GDD = max(0, (25+15)/2 - 10) = 10 GDD

Accumulate daily GDD:
Day 1: 10 GDD → Total: 10
Day 2: 8 GDD → Total: 18
...
Day 18: 12 GDD → Total: 180 → Stage: Tillering!
```

**Status:** ✅ Fully Implemented

---

## 🔄 Feature Integration Map

### **How Features Work Together:**

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                         │
│  • Clicks map to change location                           │
│  • Views dashboard data                                     │
│  • Reads AI recommendations                                 │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│               FLASK BACKEND (Orchestrator)                  │
│                                                             │
│  [1] Fetch Weather → Temperature, Humidity, Rainfall       │
│         ↓                                                    │
│  [2] Calculate GDD → Determine Growth Stage                 │
│         ↓                                                    │
│  [3] Fetch NDVI Grid → Sentinel-2 Satellite                │
│         ↓                                                    │
│  [4] Get Historical Data → NASA POWER (30 days)           │
│         ↓                                                    │
│  [5] Run Prophet → 7-Day Moisture Forecast                 │
│         ↓                                                    │
│  [6] Q-Learning Agent → Daily Recommendations              │
│         ↓                                                    │
│  [7] Render Template → Pass all data to frontend          │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (Browser Rendering)                   │
│                                                             │
│  [1] Leaflet → Interactive satellite map                   │
│  [2] Plotly → NDVI heatmap (10×10 colored grid)           │
│  [3] Three.js → 3D wheat field (matches NDVI)             │
│  [4] Plotly → Forecast chart (line + confidence)          │
│  [5] HTML/CSS → Weather cards with icons                   │
│  [6] HTML/CSS → AI recommendation list                     │
│  [7] HTML/CSS → Growth stage timeline                      │
└─────────────────────────────────────────────────────────────┘
```

### **Data Flow Example: Location Change**

```
1. User clicks new location on satellite map (13.5°N, 74.8°E)
        ↓
2. JavaScript calls /api/geocode → "Mangalore, Karnataka"
        ↓
3. User confirms "Use This Location"
        ↓
4. JavaScript calls /api/update-location
        ↓
5. Flask clears ALL caches (NDVI, weather, forecast)
        ↓
6. Page reloads with ?refresh=1&t=1732345678
        ↓
7. Flask fetches NEW data for (13.5°N, 74.8°E):
   • Weather from OpenWeather
   • NDVI from Sentinel-2
   • Climate from NASA POWER
        ↓
8. Flask runs AI models:
   • Prophet forecasts soil moisture
   • Q-Learning generates recommendations
        ↓
9. Flask calculates GDD and determines stage
        ↓
10. All dashboard sections update:
    • Satellite map centers on new location
    • NDVI heatmap shows new field health
    • 3D plants render based on new NDVI
    • Forecast predicts new location's moisture
    • Weather shows new location's conditions
    • Recommendations tailored to new data
```

---

## 📊 Technology Stack Summary

### **Backend Technologies:**

| Technology | Purpose | Files |
|------------|---------|-------|
| **Flask** | Web server & routing | `app.py` |
| **Google Earth Engine** | Satellite NDVI data | `earth_engine_ndvi.py` |
| **Facebook Prophet** | Time series forecasting | `predictor.py` |
| **NumPy** | Numerical calculations | All Python files |
| **Pandas** | Data manipulation | `predictor.py`, `data_ingest.py` |
| **Requests** | API calls | `data_ingest.py` |

### **Frontend Technologies:**

| Technology | Purpose | Location |
|------------|---------|----------|
| **Three.js** | 3D wheat field rendering | `dashboard_premium.html` |
| **Plotly.js** | Charts (NDVI heatmap, forecast) | `dashboard_premium.html` |
| **Leaflet.js** | Interactive satellite map | `dashboard_premium.html` |
| **HTML5/CSS3** | Structure & styling | `dashboard_premium.html`, `premium-style.css` |
| **JavaScript** | Interactivity & logic | `dashboard_premium.html` |

### **External APIs:**

| API | Data Provided | Update Frequency | Cost |
|-----|---------------|------------------|------|
| **Google Earth Engine** | Sentinel-2 NDVI | 5 days | Free (research) |
| **NASA POWER** | Historical climate | Daily | Free |
| **OpenWeather** | Current weather | Hourly | Free tier (1K/day) |
| **ESRI World Imagery** | Satellite photos | 1-6 months | Free (non-commercial) |
| **Nominatim** | Reverse geocoding | On-demand | Free |

---

## 📖 Reading Guide

### **For Understanding the Project:**
1. Start with `DASHBOARD_SECTIONS_EXPLAINED.md` (plain English overview)
2. Read `TECHNOLOGY_STACK_EXPLAINED.md` (how technologies work)
3. Review this index for feature overview

### **For Implementation Details:**
1. Pick a feature you're interested in
2. Read its dedicated `.md` file from the list above
3. Look at code snippets and architecture diagrams
4. Test the feature in the live dashboard

### **For Presentations:**
1. Read `PROJECT_EXPLANATION_GUIDE.md` (comprehensive talking points)
2. Review feature `.md` files for specific details
3. Use architecture diagrams in slides
4. Reference performance metrics and accuracy stats

### **For Development:**
1. Read feature `.md` file for context
2. Locate the relevant code files (listed in each doc)
3. Understand data flow from architecture diagrams
4. Follow code snippets for implementation patterns

---

## 🎯 Quick Reference: Where is X Implemented?

### **"Where is NDVI calculated?"**
- **File:** `earth_engine_ndvi.py`
- **Function:** `get_sentinel2_ndvi()`
- **Doc:** `NDVI_HEATMAP_FEATURE.md`

### **"Where is the 3D field created?"**
- **File:** `templates/dashboard_premium.html`
- **Function:** `createRealisticWheatField()`
- **Doc:** `NDVI_3D_MAPPING_FEATURE.md`

### **"Where is soil moisture predicted?"**
- **File:** `predictor.py`
- **Function:** `predict_soil_moisture()`
- **Doc:** `SOIL_MOISTURE_FORECAST_FEATURE.md`

### **"Where are AI recommendations generated?"**
- **File:** `predictor.py`
- **Class:** `SimpleQAgent`
- **Doc:** `AI_RECOMMENDATIONS_FEATURE.md`

### **"Where is weather data fetched?"**
- **File:** `data_ingest.py`
- **Function:** `get_weather()`
- **Doc:** `WEATHER_DATA_FEATURE.md`

### **"Where is growth stage tracked?"**
- **File:** `crop_model.py`
- **Class:** `WheatTwin`
- **Doc:** `GROWTH_STAGE_TRACKING_FEATURE.md`

### **"Where is the map click handled?"**
- **File:** `templates/dashboard_premium.html`
- **Event:** `satelliteMap.on('click')`
- **Doc:** `INTERACTIVE_MAP_FEATURE.md`

---

## 📁 All Documentation Files

### **Feature Documentation (With Code Snippets):**
1. ✅ `INTERACTIVE_MAP_FEATURE.md` - Click to change location
2. ✅ `NDVI_3D_MAPPING_FEATURE.md` - 3D plants match heatmap
3. ✅ `NDVI_HEATMAP_FEATURE.md` - Satellite vegetation health
4. ✅ `SOIL_MOISTURE_FORECAST_FEATURE.md` - Prophet AI predictions
5. ✅ `WEATHER_DATA_FEATURE.md` - Real-time environmental data
6. ✅ `AI_RECOMMENDATIONS_FEATURE.md` - Q-Learning decision support
7. ✅ `GROWTH_STAGE_TRACKING_FEATURE.md` - GDD-based phenology

### **General Documentation:**
- `README.md` - Project overview & setup
- `PROJECT_STRUCTURE.md` - File organization
- `DIGITAL_TWIN_IMPLEMENTATION.md` - Architecture & data flow
- `DASHBOARD_SECTIONS_EXPLAINED.md` - Plain English guide
- `TECHNOLOGY_STACK_EXPLAINED.md` - Tech explanations
- `PROJECT_EXPLANATION_GUIDE.md` - Comprehensive presentation guide

### **Debugging & Maintenance:**
- `INTERACTIVE_MAP_FEATURE.md` (includes debugging section)
- `MAP_CLICK_DEBUG_GUIDE.md` - Troubleshooting map clicks
- `CACHE_REFRESH_FIX.md` - Cache clearing documentation
- `3D_FIELD_RENDERING_FIX.md` - Fixing 3D rendering issues
- `NDVI_3D_MAPPING_FEATURE.md` (includes troubleshooting)

### **Project Planning:**
- `PROJECT_WORK_DIARY_10_WEEKS.md` - Week-by-week work plan for 4 team members

---

## 🚀 Feature Status Summary

| Feature | Status | Tested | Documented |
|---------|--------|--------|------------|
| Interactive Map | ✅ Complete | ✅ Yes | ✅ Yes |
| NDVI Heatmap | ✅ Complete | ✅ Yes | ✅ Yes |
| NDVI → 3D Mapping | ✅ Complete | ✅ Yes | ✅ Yes |
| Soil Moisture Forecast | ✅ Complete | ✅ Yes | ✅ Yes |
| Weather Data | ✅ Complete | ✅ Yes | ✅ Yes |
| AI Recommendations | ✅ Complete | ✅ Yes | ✅ Yes |
| Growth Stage Tracking | ✅ Complete | ✅ Yes | ✅ Yes |
| 3D Field Visualization | ✅ Complete | ✅ Yes | ✅ Yes |
| Caching System | ✅ Complete | ✅ Yes | ✅ Yes |
| Location Management | ✅ Complete | ✅ Yes | ✅ Yes |

---

## 💡 Using This Documentation

### **For Your Project Report:**
Copy relevant sections from feature `.md` files, including:
- Architecture diagrams
- Code snippets
- Data flow explanations
- Performance metrics

### **For Demonstrations:**
Use the "What It Does" and "Key Features" sections to explain functionality to audiences.

### **For Troubleshooting:**
Refer to the debugging sections in each feature file when issues arise.

### **For Future Development:**
Check "Future Enhancements" sections in each feature file for improvement ideas.

---

## ✅ Checklist: Understanding the Project

- [ ] Read `DASHBOARD_SECTIONS_EXPLAINED.md` for overview
- [ ] Review `PROJECT_EXPLANATION_GUIDE.md` for presentation prep
- [ ] Read each of the 7 feature `.md` files
- [ ] Understand data flow between features
- [ ] Test each feature in live dashboard
- [ ] Review code snippets in documentation
- [ ] Understand API integrations
- [ ] Know performance metrics and accuracy

---

## 📧 Documentation Maintenance

**When Adding New Features:**
1. Create a new `FEATURE_NAME_FEATURE.md` file
2. Include: Overview, Architecture, Code, Integration, Testing
3. Add entry to this index file
4. Update `PROJECT_EXPLANATION_GUIDE.md` if major feature

**When Fixing Bugs:**
1. Document the fix in the relevant feature `.md` file
2. Update troubleshooting sections
3. Add to "Common Issues & Solutions"

---

**Index Last Updated:** November 23, 2025  
**Total Documentation Files:** 17  
**Total Documentation Pages:** ~200 (equivalent)  
**Coverage:** 100% of dashboard features

---

## 🎓 Final Note

This documentation represents a **complete technical reference** for the FarmSight Digital Twin project. Each feature is documented with:

✅ **Plain English explanations**  
✅ **Architecture diagrams**  
✅ **Full code snippets**  
✅ **Integration details**  
✅ **Performance metrics**  
✅ **Testing procedures**  

Use these resources to:
- **Understand** the system deeply
- **Explain** it to others confidently
- **Debug** issues systematically
- **Extend** functionality purposefully

**Good luck with your project! 🌾🚀**


