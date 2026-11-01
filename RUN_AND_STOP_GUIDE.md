# 🚀 How to Run and Stop the Digital Twin Server

## ⚡ Quick Start

### 1️⃣ Activate virtual environment:
```bash
source dt_env/bin/activate
```

### 2️⃣ Run the server:
```bash
python app.py
```

### 3️⃣ Access in browser:
```
http://127.0.0.1:5001/
```

---

## 🛑 Stop the Server

### Easiest way: 
Press `Ctrl+C` in the terminal

### If that doesn't work:

**macOS/Linux:**
```bash
kill -9 $(lsof -t -i:5001)
```

**Windows Command Prompt:**
```cmd
netstat -ano | findstr :5001
taskkill /PID <PID> /F
```

**Windows PowerShell:**
```powershell
Get-NetTCPConnection -LocalPort 5001 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
```

---

## 🔧 Complete Setup & Run Instructions

### 1️⃣ **First Time Setup**

#### Activate Virtual Environment

**On macOS/Linux:**
```bash
cd /Users/chethanam/Desktop/digitaltwin
source dt_env/bin/activate
```

**On Windows (Command Prompt):**
```cmd
cd C:\Users\YourUsername\Desktop\digitaltwin
dt_env\Scripts\activate.bat
```

**On Windows (PowerShell):**
```powershell
cd C:\Users\YourUsername\Desktop\digitaltwin
dt_env\Scripts\Activate.ps1
```

#### Install Dependencies (if not already installed)
```bash
pip install -r requirements.txt
```

#### Setup Google Earth Engine (First time only)
```bash
python setup_earth_engine.py
```

#### Configure API Keys
Edit `config.py` and add your OpenWeather API key:
```python
WEATHER_API_KEY = "your_api_key_here"
```

### 2️⃣ **Running the Server**

#### Standard Run
```bash
python app.py
```

The server will start on: **http://127.0.0.1:5001/**

You should see output like:
```
 * Running on http://127.0.0.1:5001
 * Restarting with stat
 * Debugger is active!
```

#### Run in Background (Advanced)

**On macOS/Linux:**
```bash
nohup python app.py > server.log 2>&1 &
```

**On Windows (using pythonw):**
```cmd
start /B pythonw app.py
```

---

## 🛑 How to Stop the Server

### Method 1: Keyboard Interrupt (Simplest)
If the server is running in your terminal:
```
Press: Ctrl+C
```

### Method 2: Find and Kill by Port (If Ctrl+C doesn't work)

#### **On macOS/Linux:**

**Step 1:** Find the process using port 5001
```bash
lsof -i :5001
```

**Step 2:** Kill the process
```bash
kill -9 <PID>
```

**Or in one command:**
```bash
kill -9 $(lsof -t -i:5001)
```

#### **On Windows (Command Prompt):**

**Step 1:** Find the process using port 5001
```cmd
netstat -ano | findstr :5001
```

**Step 2:** Kill the process (replace <PID> with the number from the last column)
```cmd
taskkill /PID <PID> /F
```

#### **On Windows (PowerShell):**
```powershell
# Find and kill in one command
Get-NetTCPConnection -LocalPort 5001 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
```

### Method 3: Kill All Python Processes (Nuclear option)

⚠️ **Warning**: This will stop ALL Python processes, not just your server!

**On macOS/Linux:**
```bash
pkill -9 python
```

**On Windows:**
```cmd
taskkill /IM python.exe /F
```

---

## 🔍 Troubleshooting

### Problem: "Address already in use" error

This means port 5001 is already occupied.

**Solution 1:** Kill the existing process (see Method 2 above)

**Solution 2:** Change the port in `app.py`
```python
# At the bottom of app.py, change:
app.run(debug=True, port=5001)
# To:
app.run(debug=True, port=5002)  # Or any other available port
```

### Problem: Virtual environment not activating

**On Windows PowerShell**, you might need to enable script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: "Module not found" errors

Make sure you're in the virtual environment and dependencies are installed:
```bash
# Check if you're in the virtual environment (should see (dt_env) in prompt)
# If not, activate it first, then:
pip install -r requirements.txt
```

### Problem: Server running but can't access in browser

1. Make sure you're using the correct URL: `http://127.0.0.1:5001/`
2. Try `http://localhost:5001/` instead
3. Check if your firewall is blocking the port
4. Look at the terminal output for any error messages

---

## 📊 Checking if Server is Running

### On macOS/Linux:
```bash
# Check if port 5001 is in use
lsof -i :5001

# Or check all Python processes
ps aux | grep python
```

### On Windows:
```cmd
# Check if port 5001 is in use
netstat -ano | findstr :5001

# Or check all Python processes
tasklist | findstr python
```

---

## 🎯 Quick Command Reference Card

| Task | macOS/Linux | Windows |
|------|-------------|---------|
| **Activate venv** | `source dt_env/bin/activate` | `dt_env\Scripts\activate` |
| **Run server** | `python app.py` | `python app.py` |
| **Stop server** | `Ctrl+C` | `Ctrl+C` |
| **Kill by port** | `kill -9 $(lsof -t -i:5001)` | `netstat -ano \| findstr :5001` then `taskkill /PID <PID> /F` |
| **Check if running** | `lsof -i :5001` | `netstat -ano \| findstr :5001` |

---

## 🎨 Development Mode vs Production

### Development (Current Setup)
- Debug mode enabled
- Auto-reloads on code changes
- Detailed error messages
- Running on `http://127.0.0.1:5001/`

### Production (Future Deployment)
For production deployment, you should:
1. Set `debug=False` in `app.py`
2. Use a production WSGI server (gunicorn, waitress, etc.)
3. Set up proper environment variables
4. Use a reverse proxy (nginx, apache)

---

## 💡 Pro Tips

1. **Keep the terminal open** while the server is running to see real-time logs
2. **Use `Ctrl+C` first** before trying other kill methods
3. **Check the logs** in the terminal if something goes wrong
4. **Restart the server** after making changes to Python files (if not in debug mode)
5. **Virtual environment should always be activated** before running the server

---

**Need more help?** Check the other documentation files:
- `README.md` - Project overview and features
- `API_SETUP_GUIDE.md` - API configuration details
- `PROJECT_STRUCTURE.md` - Code organization

