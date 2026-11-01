# FarmSight Dashboard - 
## What Each Section Does and How It Works

---

## 🎯 Dashboard Overview

The FarmSight dashboard shows you the health and status of your wheat crop field. It collects data from satellites, weather stations, and soil sensors to help you make smart decisions about watering and fertilizing your crops.

---

## 📍 **1. Location Section (Top Header)**

### What It Does:
Shows where your field is located on Earth.

### Data We Collect:
- **Latitude and Longitude**: Exact coordinates of your field (like GPS coordinates)
- **Location Name**: City and state where your field is located

### Where Data Comes From:
- You enter coordinates OR click on the satellite map
- We use a reverse geocoding service (Nominatim API) to find the location name

### How It Works:
1. You either type coordinates (like "12.9716, 77.5946") or click on the map
2. System finds the place name (like "Bangalore, Karnataka, India")
3. Saves this location so all other data is fetched for YOUR field

### Why It Matters:
Everything else on the dashboard is based on this location - weather, satellite images, crop health, etc.

---

## 🛰️ **2. Satellite View (Top-Left Card)**

### What It Does:
Shows an actual photograph of your field taken from space.

### Data We Collect:
- **RGB Satellite Image**: Real photo of your field from satellites

### Where Data Comes From:
- **ESRI World Imagery** service (uses satellites like WorldView, GeoEye, Landsat)
- Updates every 1-6 months

### How It Works:
1. Takes your field coordinates
2. Fetches satellite photo from ESRI
3. Shows you what your field looks like from above
4. You can zoom in/out to see details

### Why It Matters:
Lets you visually confirm you're looking at the right field and see physical features like boundaries, roads, and neighboring fields.

### Special Feature:
**Click anywhere on this map** to change your field location!

---

## 📊 **3. NDVI Heat Map (Top-Middle Card)**

### What It Does:
Shows which parts of your field are healthy (green) and which parts are stressed (blue/yellow).

### Data We Collect:
- **NDVI Values**: A number from 0 to 1 that measures vegetation health
- **Grid Data**: Divides your field into 100 squares (10×10 grid)

### Where Data Comes From:
- **Sentinel-2 Satellite** via Google Earth Engine
- Takes special infrared photos of plants
- Updates every 5 days (when satellite passes overhead)

### How It Works:
1. Satellite takes two types of photos:
   - **Red light** (what our eyes see)
   - **Near-Infrared light** (invisible to humans, but plants reflect it strongly)
2. Healthy plants reflect a lot of infrared light
3. Stressed plants reflect less infrared light
4. Formula: NDVI = (Infrared - Red) / (Infrared + Red)
5. Creates a color-coded map of your field

### Color Meaning:
- 🔵 **Dark Blue** (0.0-0.2): No crops, bare soil
- 🔵 **Blue** (0.2-0.3): Very weak crops, just emerging
- 🟦 **Teal** (0.3-0.4): Moderate crops, growing
- 🟩 **Green** (0.4-0.6): Healthy crops, good condition
- 🟢 **Bright Green** (0.6+): Very healthy crops, excellent

### Why It Matters:
Shows you problem areas that need attention (blue spots = stressed crops = need water/fertilizer).

---

## 🌾 **4. 3D Crop Field (Bottom-Left Card)**

### What It Does:
Shows an animated 3D model of your wheat plants that matches the health shown in the NDVI map.

### Data We Use:
- **NDVI values** from the heat map
- **Growth stage** (based on temperature data)
- **Irrigation level** (how much water plants have)
- **Fertilization level** (how much nutrients plants have)

### How It Works:
1. Creates a 10×10 grid of virtual wheat plants (100 plants total)
2. Each plant matches the health of the NDVI map square
   - **If NDVI map shows blue** → Few plants, short, brownish color
   - **If NDVI map shows green** → Many plants, tall, bright green color
3. Plants sway gently in the "wind" (animation)
4. You can rotate the view with your mouse to see from different angles

### Growth Stages Shown:
1. **Emergence**: Tiny shoots (3-5 cm tall)
2. **Tillering**: Multiple stems growing (15-25 cm)
3. **Stem Elongation**: Getting taller (40-60 cm)
4. **Booting**: Almost full height (70-90 cm)
5. **Heading**: Wheat heads visible (80-100 cm)
6. **Flowering**: Yellow wheat heads
7. **Grain Filling**: Golden grains forming
8. **Maturity**: Ready to harvest, golden brown

### Why It Matters:
Gives you a realistic visual representation of your crop's condition. Easy to understand at a glance - green and dense = good, brown and sparse = problem.

---

## 📈 **5. Soil Moisture Forecast (Top-Right Card)**

### What It Does:
Predicts soil moisture for the next 7 days so you can plan irrigation in advance.

### Data We Collect:
- **Past 30 days** of soil moisture/rainfall data
- **Current weather** conditions

### Where Data Comes From:
- **NASA POWER API**: Provides rainfall/soil moisture data from satellites
- **Historical weather data**: Past month of precipitation

### How It Works:
1. **Collects History**: Gets the last 30 days of rain/moisture data
2. **AI Analysis**: Uses "Facebook Prophet" AI model to find patterns:
   - Is moisture increasing or decreasing?
   - What's the seasonal trend?
   - What day of week patterns exist?
3. **Makes Predictions**: Forecasts next 7 days
4. **Shows Confidence**: Gray shaded area shows uncertainty range

### Chart Explanation:
- **Blue Line**: Predicted moisture level
- **Gray Shaded Area**: Confidence range (95% sure actual value will be in this range)
- **Red Line**: Critical threshold (30% - below this needs irrigation)
- **Green Line**: Optimal threshold (70% - above this is well-watered)

### Why It Matters:
Helps you plan ahead. If forecast shows moisture dropping below 30% in 3 days, you can arrange irrigation NOW instead of waiting for crops to suffer.

---

## 🌦️ **6. Real-Time Weather (Bottom-Middle Card)**

### What It Does:
Shows current weather conditions at your field location RIGHT NOW.

### Data We Collect:
- **Temperature**: Current air temperature (°C)
- **Humidity**: Moisture in the air (%)
- **Rainfall**: How much it rained in last hour (mm)
- **Wind Speed**: How fast wind is blowing (km/h)
- **Weather Condition**: Sunny, cloudy, rainy, etc.

### Where Data Comes From:
- **OpenWeather API**: Real-time weather data from local weather stations
- Updates every hour

### How It Works:
1. Sends your field coordinates to OpenWeather
2. They find the nearest weather station
3. Returns current measurements
4. Displays with easy-to-understand icons

### Why It Matters:
- Current temperature affects crop growth rate
- High humidity means less irrigation needed
- Recent rainfall means soil is already wet
- Strong winds can stress plants

---

## 🤖 **7. AI Recommendations (Bottom-Right Card)**

### What It Does:
Gives you daily advice on whether to irrigate, fertilize, or just monitor your crops.

### Data We Use:
- **7-day moisture forecast**
- **Current weather**
- **Crop growth stage**
- **Historical patterns**

### Where Intelligence Comes From:
Uses **Q-Learning AI** (a type of artificial intelligence that learns from experience):
- Trained on thousands of scenarios
- Knows when irrigation helps vs when it wastes water
- Considers weather, growth stage, and soil conditions

### How It Works:
1. **Analyzes Forecast**: Looks at predicted moisture for each day
2. **Checks Weather**: Considers if rain is coming
3. **Evaluates Stage**: Different growth stages need different care
4. **Makes Decision**:
   - **"Irrigate"**: Moisture too low, plants need water
   - **"Fertilize"**: Nutrients low, plants need feeding
   - **"Wait"**: Conditions OK, save resources

### Example Recommendations:
- "Day 1: moisture about 35%. Leave field as it is and keep an eye on it."
- "Day 3: moisture about 28%. Give the field some water."
- "Day 5: moisture about 45%. Apply some fertilizer to support growth."

### Why It Matters:
Takes the guesswork out of farming. Tells you exactly what to do each day to keep crops healthy while saving water and fertilizer.

---

## 🎮 **8. Control Panel (Simulation Mode)**

### What It Does:
Lets you experiment with "what-if" scenarios without affecting your real field.

### Controls Available:
- **Mode Toggle**: Switch between Live Data (real field) and Simulation (practice)
- **Irrigation Slider**: Adjust water level from 0% to 100%
- **Fertilization Slider**: Adjust nutrient level from 0% to 100%
- **Growth Stage Selector**: Jump to different growth stages

### How It Works:
1. Switch to Simulation Mode
2. Move sliders to try different irrigation/fertilization levels
3. **3D field instantly updates** to show how crops would look
4. See stress effects immediately:
   - Too little water → Plants turn brown, become sparse
   - Too much water → Wasted resources (no extra benefit)
   - Optimal water → Plants bright green, dense, tall

### Why It Matters:
- **Training**: Learn how plants respond to different conditions
- **Testing**: Try strategies before applying to real field
- **Education**: Understand crop needs at different stages

---

## 📊 **9. Key Performance Indicators (KPIs)**

### What They Show:

#### **Crop Health** (0-100%)
- **Source**: Calculated from NDVI values
- **Formula**: Health = (NDVI - 0.1) × 125
- **Meaning**: 
  - 80-100% = Excellent (bright green)
  - 60-80% = Good (green)
  - 40-60% = Fair (yellow-green)
  - Below 40% = Poor (brown/stressed)

#### **Current Growth Stage**
- **Source**: Calculated from accumulated temperature
- **Method**: Growing Degree Days (GDD)
  - Every day, add: max(0, temperature - 0°C)
  - When total reaches 180 GDD → Tillering stage
  - When total reaches 395 GDD → Stem elongation
  - And so on...
- **Why**: Warmer weather = faster growth

#### **Field Age** (days)
- **Source**: Days since planting (or simulation start)
- **Meaning**: Shows how long crop has been growing

#### **Soil Moisture** (%)
- **Source**: NASA satellite data or forecast
- **Meaning**:
  - 70-100% = Well watered
  - 40-70% = Adequate
  - 20-40% = Getting dry
  - Below 20% = Critically dry

#### **Nitrogen Level** (0-100)
- **Source**: Fertilization applications tracked
- **Meaning**: 
  - 80-100 = Plenty of nutrients
  - 60-80 = Adequate
  - Below 60 = Needs fertilizer

### Why KPIs Matter:
Give you quick status check. Glance at dashboard and immediately know if field is healthy or needs attention.

---

## 🔄 **How Everything Works Together**

### The Complete Data Flow:

```
1. YOU → Enter location coordinates
   ↓
2. SYSTEM → Fetches satellite image of that location
   ↓
3. SATELLITE → Provides NDVI health data (10×10 grid)
   ↓
4. SYSTEM → Colors NDVI heatmap (blue = unhealthy, green = healthy)
   ↓
5. SYSTEM → Creates 3D plants matching each heatmap cell
   ↓
6. WEATHER API → Provides current temperature, humidity, rain
   ↓
7. NASA → Provides soil moisture history (30 days)
   ↓
8. AI MODEL → Analyzes history, forecasts next 7 days
   ↓
9. AI AGENT → Generates daily recommendations
   ↓
10. DASHBOARD → Shows everything to you in one screen
```

### What Happens When You Change Location:

```
1. You click new spot on satellite map
   ↓
2. System gets coordinates (e.g., 13.356, 74.694)
   ↓
3. Finds location name: "Udupi, Karnataka"
   ↓
4. Clears all old data (cache reset)
   ↓
5. Fetches NEW satellite image
   ↓
6. Fetches NEW NDVI data for that spot
   ↓
7. Fetches NEW weather for that location
   ↓
8. Fetches NEW soil data for that location
   ↓
9. Regenerates NEW forecast
   ↓
10. Updates ALL dashboard sections
   ↓
11. Page reloads with fresh data (1.5 seconds)
```

---

## 💡 **Simple Explanations of Technical Terms**

### **NDVI (Normalized Difference Vegetation Index)**
- **Simple English**: A health score for plants (0 = dead, 1 = super healthy)
- **How we get it**: Special satellite cameras see how plants reflect invisible light
- **Why it works**: Healthy plants reflect lots of invisible "infrared" light that our eyes can't see

### **Growing Degree Days (GDD)**
- **Simple English**: A way to measure crop age based on warmth, not calendar days
- **Why**: Plants grow faster when it's warm, slower when it's cold
- **Example**: 20°C day = 20 GDD added. 5°C day = 5 GDD added. Crop reaches next stage at specific GDD total.

### **Soil Moisture Forecast**
- **Simple English**: Prediction of how wet the soil will be in coming days
- **How**: AI looks at past patterns and predicts future
- **Like**: Weather forecast, but for soil moisture instead of rain

### **Q-Learning / AI Agent**
- **Simple English**: Computer learns from experience what actions work best
- **How**: Tries different strategies, remembers what worked, gets smarter over time
- **Like**: Learning to play a game - the more you play, the better your decisions

### **Digital Twin**
- **Simple English**: A computer copy of your real field that updates with real data
- **Purpose**: See field status without visiting physically
- **Advantage**: Can test "what-if" scenarios without risking real crops

---

## 🎯 **Summary: Why Each Section Matters**

| Section | What It Shows | Why You Need It |
|---------|---------------|-----------------|
| **Location** | Where your field is | Ensures data is for YOUR field |
| **Satellite View** | Photo of your field | Visual confirmation of location |
| **NDVI Heatmap** | Health map (color-coded) | Find problem areas quickly |
| **3D Field** | Realistic crop visualization | Understand crop condition at glance |
| **Moisture Forecast** | Next 7 days prediction | Plan irrigation in advance |
| **Weather** | Current conditions | Know what's happening now |
| **AI Recommendations** | Daily action advice | Know what to do each day |
| **Controls** | Practice mode | Learn without risk |

---

## 🚀 **How Farmers Use This Dashboard**

### **Morning Routine:**
1. Open dashboard
2. Check **Crop Health KPI** - Is it above 60%? Good!
3. Look at **NDVI Heatmap** - Any blue spots? Those need attention
4. Read **AI Recommendations** - What to do today?
5. Check **Moisture Forecast** - Will I need to irrigate this week?

### **Decision Making:**
1. **AI says "Irrigate Day 3"** → Schedule irrigation for day after tomorrow
2. **Heatmap shows blue corner** → Focus irrigation on that specific area
3. **Forecast shows rain coming** → Skip irrigation, save water
4. **3D field looks brown** → Increase irrigation level

### **Problem Solving:**
1. **Crop health dropped to 40%** → Check heatmap for problem areas
2. **Blue patches in heatmap** → Soil might be compacted or drainage issue
3. **Forecast shows consistent drying** → Plan for increased irrigation
4. **AI recommends fertilize** → Nitrogen levels low, time to feed crops

---

## ✅ **Key Takeaway**

The FarmSight dashboard is like having:
- A **satellite** watching your field 24/7
- A **weather station** on your field
- An **agricultural expert** giving daily advice
- A **crystal ball** predicting moisture for next week
- A **3D model** showing crop condition in real-time

All in one simple screen, updating automatically, helping you make smart farming decisions every day.

---

**Last Updated:** November 22, 2025  
**Purpose:** Plain English explanation of dashboard sections  
**Audience:** Farmers, students, non-technical users

