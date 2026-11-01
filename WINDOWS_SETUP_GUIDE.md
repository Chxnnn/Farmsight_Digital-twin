# 🪟 FarmSight Digital Twin - Windows Setup Guide
## Complete Step-by-Step Instructions for Running on Windows

---

## 📋 Prerequisites

Before starting, ensure you have these installed on your Windows machine:

### **1. Python 3.8 or Higher**

**Check if Python is installed:**
1. Press `Win + R`, type `cmd`, press Enter
2. Type: `python --version`
3. You should see: `Python 3.8.x` or higher

**If Python is NOT installed:**
1. Go to: https://www.python.org/downloads/
2. Download the latest Python 3.x installer (e.g., Python 3.11)
3. **IMPORTANT:** During installation, check the box **"Add Python to PATH"**
4. Click "Install Now"
5. Verify installation by opening a new Command Prompt and typing `python --version`

### **2. Git (Optional, for cloning)**

**Check if Git is installed:**
```cmd
git --version
```

**If Git is NOT installed:**
1. Go to: https://git-scm.com/download/win
2. Download and install Git for Windows
3. Use default settings during installation

---

## 🚀 Step-by-Step Setup

### **Step 1: Get the Project Files**

**Option A: If you have the folder already**
- Navigate to your project folder (e.g., `C:\Users\YourName\Downloads\digitaltwin`)
- Skip to Step 2

**Option B: Clone from repository (if applicable)**
```cmd
cd C:\Users\YourName\Documents
git clone <your-repo-url> digitaltwin
cd digitaltwin
```

**Option C: Download as ZIP**
- Download the project ZIP file
- Extract to `C:\Users\YourName\Documents\digitaltwin`
- Open Command Prompt and navigate:
```cmd
cd C:\Users\YourName\Documents\digitaltwin
```

---

### **Step 2: Create Virtual Environment**

A virtual environment keeps project dependencies isolated.

**Open Command Prompt in your project folder:**
1. Press `Win + E` to open File Explorer
2. Navigate to your `digitaltwin` folder
3. Type `cmd` in the address bar and press Enter

**Create virtual environment:**
```cmd
python -m venv dt_env
```

**Activate the virtual environment:**
```cmd
dt_env\Scripts\activate
```

✅ **Success indicator:** Your command prompt should now show `(dt_env)` at the beginning:
```
(dt_env) C:\Users\YourName\Documents\digitaltwin>
```

---

### **Step 3: Install Dependencies**

**With the virtual environment activated, run:**
```cmd
pip install -r requirements.txt
```

This will install:
- Flask (web server)
- Prophet (AI forecasting)
- Plotly (charts)
- NumPy & Pandas (data processing)
- Requests (API calls)
- earthengine-api (satellite data)

⏱️ **Expected time:** 2-5 minutes depending on internet speed

**If you get SSL errors:**
```cmd
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

**If Prophet installation fails:**
Prophet has C++ dependencies. Install Microsoft Visual C++ Build Tools:
1. Go to: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Download and install "Build Tools for Visual Studio"
3. Select "C++ build tools" during installation
4. Restart Command Prompt and try again

---

### **Step 4: Set Up Google Earth Engine**

**Authenticate with Google Earth Engine:**
```cmd
python setup_earth_engine.py
```

**What will happen:**
1. A browser window will open
2. Sign in with your Google account
3. Click "Allow" to grant access
4. You'll see "Successfully authenticated!"
5. Close the browser and return to Command Prompt

**If authentication succeeds, you'll see:**
```
✅ Earth Engine authenticated successfully!
✅ Test query successful - API is working!
```

**Troubleshooting Earth Engine:**
- If the browser doesn't open automatically, copy the URL from the terminal
- Paste it in your browser manually
- If you get permission errors, use a personal Gmail account (not institutional)

---

### **Step 5: Get API Keys**

#### **5a. OpenWeather API Key (Required)**

1. Go to: https://openweathermap.org/api
2. Click "Sign Up" (free account)
3. After signing up, go to "API keys" tab
4. Copy your API key (looks like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`)

#### **5b. Configure API Keys**

**Open `config.py` in Notepad or any text editor:**
```cmd
notepad config.py
```

**Find and replace:**
```python
WEATHER_API_KEY = "your_openweather_api_key_here"
```

**With your actual key:**
```python
WEATHER_API_KEY = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

**Save the file** (`Ctrl + S`) and close Notepad.

---

### **Step 6: Configure Your Location (Optional)**

**If you want to monitor a specific field:**

1. Open `config.py` again:
```cmd
notepad config.py
```

2. Find the location configuration:
```python
LOCATION_COORDS = {
    "lat": 12.9716,
    "lon": 77.5946
}
LOCATION_NAME = "Bangalore, Karnataka, India"
```

3. Replace with your field coordinates:
```python
LOCATION_COORDS = {
    "lat": 28.6139,  # Your latitude
    "lon": 77.2090   # Your longitude
}
LOCATION_NAME = "New Delhi, India"
```

4. Save and close

**Tip:** You can also change location later using the interactive map in the dashboard!

---

### **Step 7: Run the Application**

**With virtual environment activated, run:**
```cmd
python app.py
```

✅ **Success! You should see:**
```
 * Running on http://127.0.0.1:5001
 * Press CTRL+C to quit
🌱 Wheat digital twin initialized
✅ Flask server started successfully!
```

---

### **Step 8: Access the Dashboard**

**Open your web browser and go to:**
```
http://127.0.0.1:5001
```

Or:
```
http://localhost:5001
```

🎉 **You should see the FarmSight dashboard with:**
- 🛰️ Satellite view (interactive map)
- 📊 NDVI heatmap (vegetation health)
- 🌾 3D wheat field visualization
- 📈 7-day soil moisture forecast
- 🌦️ Real-time weather data
- 🤖 AI recommendations

---

### **Step 9: Stopping the Application**

**To stop the Flask server:**
1. Go back to the Command Prompt window
2. Press `Ctrl + C`
3. Type `Y` if asked to confirm
4. Deactivate virtual environment:
```cmd
deactivate
```

---

## 🔄 Running the Project Again (Next Time)

**Every time you want to run the project:**

1. **Open Command Prompt in project folder:**
   - Navigate to `digitaltwin` folder in File Explorer
   - Type `cmd` in the address bar

2. **Activate virtual environment:**
   ```cmd
   dt_env\Scripts\activate
   ```

3. **Run the app:**
   ```cmd
   python app.py
   ```

4. **Open browser:**
   ```
   http://127.0.0.1:5001
   ```

**That's it!** No need to reinstall dependencies or reconfigure API keys.

---

## 🐛 Common Windows Issues & Solutions

### **Issue 1: "python is not recognized"**

**Problem:** Python not in PATH

**Solution:**
1. Find Python installation path (usually `C:\Python311\` or `C:\Users\YourName\AppData\Local\Programs\Python\Python311\`)
2. Add to PATH:
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Go to "Advanced" tab → "Environment Variables"
   - Under "System variables", find "Path", click "Edit"
   - Click "New" and add Python path
   - Click "New" again and add `C:\Python311\Scripts\`
   - Click OK, restart Command Prompt

### **Issue 2: "pip is not recognized"**

**Solution:**
```cmd
python -m pip install --upgrade pip
```

### **Issue 3: "Cannot activate virtual environment"**

**Problem:** Execution policy restriction

**Solution (Run Command Prompt as Administrator):**
```cmd
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again:
```cmd
dt_env\Scripts\activate
```

### **Issue 4: Port 5001 already in use**

**Problem:** Another application is using port 5001

**Solution 1 - Find and kill process:**
```cmd
netstat -ano | findstr :5001
taskkill /PID <PID_NUMBER> /F
```

**Solution 2 - Use different port:**
Open `app.py` and change:
```python
app.run(debug=True, port=5001)
```
To:
```python
app.run(debug=True, port=5002)
```
Then access: `http://127.0.0.1:5002`

### **Issue 5: Firewall blocking Flask**

**Problem:** Windows Firewall blocks local server

**Solution:**
1. Click "Allow access" when Windows Firewall prompt appears
2. Or manually add exception:
   - Windows Security → Firewall & network protection
   - Allow an app through firewall
   - Add Python.exe

### **Issue 6: Prophet installation fails**

**Problem:** Missing C++ compiler

**Solution:**
```cmd
pip install pystan==2.19.1.1
pip install prophet
```

If that fails, install precompiled version:
```cmd
pip install prophet --no-build-isolation
```

### **Issue 7: Earth Engine authentication stuck**

**Problem:** Browser doesn't open or authentication loops

**Solution:**
1. Copy the authentication URL from terminal
2. Open in browser manually
3. Complete authentication
4. Copy the authorization code
5. Paste back in terminal

### **Issue 8: Dashboard shows "Simulated data" everywhere**

**Problem:** API keys not configured or APIs unreachable

**Solution:**
1. Verify API keys in `config.py`
2. Check internet connection
3. Verify Earth Engine authentication:
   ```cmd
   python -c "import ee; ee.Initialize(); print('✅ Earth Engine OK')"
   ```

---

## 🎯 Quick Command Reference

### **Essential Commands:**

```cmd
# Navigate to project
cd C:\Users\YourName\Documents\digitaltwin

# Activate environment
dt_env\Scripts\activate

# Run application
python app.py

# Stop application
Ctrl + C

# Deactivate environment
deactivate

# Update dependencies
pip install -r requirements.txt --upgrade

# Check Python version
python --version

# Check installed packages
pip list

# Clear Python cache (if weird errors)
del /s /q __pycache__
```

---

## 📁 Project Structure on Windows

```
C:\Users\YourName\Documents\digitaltwin\
│
├── dt_env\                          # Virtual environment (DON'T touch)
│   ├── Scripts\
│   │   ├── activate.bat            # Activation script
│   │   └── python.exe              # Isolated Python
│   └── Lib\                        # Installed packages
│
├── app.py                          # Main Flask server
├── config.py                       # Configuration (API keys, location)
├── requirements.txt                # Dependencies list
│
├── crop_model.py                   # Growth stage tracking
├── predictor.py                    # AI forecasting & Q-Learning
├── data_ingest.py                  # API data fetching
├── earth_engine_ndvi.py            # Satellite NDVI data
│
├── templates\
│   └── dashboard_premium.html      # Main dashboard UI
│
├── static\
│   └── premium-style.css           # Styling
│
└── Documentation files...
```

---

## 🌐 Browser Compatibility

**Recommended browsers:**
- ✅ **Google Chrome** (best performance)
- ✅ **Microsoft Edge** (Chromium-based)
- ✅ **Firefox**
- ⚠️ **Internet Explorer** (NOT supported - use Edge instead)

**For best experience:**
- Use latest browser version
- Enable JavaScript
- Allow location services (optional)
- Disable ad blockers (may interfere with map tiles)

---

## 🔒 Security Notes

**Firewall:**
- Flask runs on localhost (127.0.0.1) only
- Not accessible from other computers on network
- Safe for local development

**API Keys:**
- Never commit `config.py` with real API keys to public repositories
- OpenWeather free tier has usage limits (1,000 calls/day)
- Google Earth Engine is free for research/education

---

## 📊 Performance on Windows

**Expected load times:**
- First load: 3-5 seconds (fetching fresh data)
- Cached load: 0.5-1 second
- Location change: 2-3 seconds
- NDVI refresh: 2-3 seconds (Google Earth Engine)

**System requirements:**
- **RAM:** 2GB minimum, 4GB recommended
- **Storage:** 500MB for project + dependencies
- **Internet:** Stable connection (APIs need ~1-2 Mbps)
- **CPU:** Any modern processor (AI models are lightweight)

---

## 🎓 Next Steps

After successful setup:

1. **Explore the dashboard:**
   - Click around the satellite map
   - Hover over NDVI heatmap cells
   - Rotate the 3D wheat field
   - Check AI recommendations

2. **Change location:**
   - Click anywhere on the satellite map
   - Click "Use This Location"
   - Wait for dashboard to refresh

3. **Read documentation:**
   - `COMPLETE_FEATURES_INDEX.md` - Overview of all features
   - `DASHBOARD_SECTIONS_EXPLAINED.md` - Plain English guide
   - Feature-specific `.md` files for deep dives

4. **Customize:**
   - Modify `config.py` for your field
   - Adjust growth stage parameters in `crop_model.py`
   - Customize 3D visualization in `dashboard_premium.html`

---

## 🆘 Getting Help

**If you encounter issues:**

1. **Check this guide** - Most common issues covered above
2. **Check terminal output** - Error messages are helpful
3. **Verify prerequisites** - Python version, API keys, internet
4. **Try fresh install:**
   ```cmd
   deactivate
   rmdir /s dt_env
   python -m venv dt_env
   dt_env\Scripts\activate
   pip install -r requirements.txt
   ```

---

## ✅ Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Project files downloaded/extracted
- [ ] Virtual environment created (`dt_env`)
- [ ] Virtual environment activated (`(dt_env)` shown)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Google Earth Engine authenticated (`python setup_earth_engine.py`)
- [ ] OpenWeather API key added to `config.py`
- [ ] Flask server running (`python app.py`)
- [ ] Dashboard accessible in browser (`http://127.0.0.1:5001`)
- [ ] All features loading (satellite, NDVI, forecast, weather)

---

## 🎉 Success!

If you can see the dashboard with live data, **congratulations!** 🌾

You now have a fully functional **digital twin** of a wheat crop field powered by:
- 🛰️ Real satellite data (Sentinel-2)
- 🤖 AI predictions (Prophet + Q-Learning)
- 🌦️ Live weather monitoring (OpenWeather)
- 🌍 Global climate data (NASA POWER)
- 🎨 Interactive 3D visualization (Three.js)

**Enjoy exploring your digital farm!** 🚀

---

**Guide Version:** 1.0  
**Last Updated:** November 23, 2025  
**Platform:** Windows 10/11  
**Python:** 3.8 - 3.11 tested

