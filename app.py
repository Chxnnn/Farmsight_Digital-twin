from flask import Flask, render_template, request, jsonify
from data_ingest import get_weather, get_ndvi_metadata
from crop_model import twin
from predictor import predict_soil_moisture, generate_recommendations
from preprocessing import clean_and_extract
from geocoding import reverse_geocode, decimal_to_dms
import config
import pandas as pd
import datetime
import json
import random
import os

app = Flask(__name__)

# ---------------------------
# Simple in-memory cache
# ---------------------------
_cached = {
    'forecast': None,
    'weather': None,
    'timestamp': None,
}

# ---------------------------
# Simulated historical soil moisture history
# ---------------------------
history_df = pd.DataFrame({
    'ds': pd.date_range(datetime.date.today() - pd.Timedelta(days=30), periods=30),
    'y': [random.uniform(25, 65) for _ in range(30)]
})

# ---------------------------
# Weather summary helper
# ---------------------------
def weather_recommendation(weather):
    rain = weather.get('rainfall', 0)
    humidity = weather.get('humidity', 0)
    temperature = weather.get('temperature', 0)

    if rain > 2:
        return "Rain is expected, which should help with irrigation."
    elif humidity < 30:
        return "Humidity is low, so avoid overwatering and watch for plant stress."
    elif temperature > 30:
        return "It will be quite hot, so keep an eye on soil moisture."
    else:
        return "Weather looks stable and suitable for crop growth."

# ---------------------------
# Turn model recs into farmer-friendly one-liners
# ---------------------------
def humanize_recommendation(rec):
    day = rec.get('day')
    soil = rec.get('pred_soil')
    action = rec.get('action')

    if soil is None:
        soil_text = "soil moisture is not available"
    else:
        soil_text = f"moisture about {soil:.1f}%"

    if action == "irrigate":
        templates = [
            "Day {day}: {soil_text}. Give the field some water.",
            "Day {day}: {soil_text}. Plan to irrigate.",
            "Day {day}: {soil_text}. Water the crop."
        ]
    elif action == "fertilize":
        templates = [
            "Day {day}: {soil_text}. Apply some fertilizer to support growth.",
            "Day {day}: {soil_text}. A light fertilizer dose is a good idea.",
            "Day {day}: {soil_text}. Add fertilizer to help the plants."
        ]
    else:  # wait / monitor
        templates = [
            "Day {day}: {soil_text}. Leave the field as it is and keep an eye on it.",
            "Day {day}: {soil_text}. No work needed, just watch the field.",
            "Day {day}: {soil_text}. You can wait and simply monitor."
        ]
    return random.choice(templates).format(day=day, soil_text=soil_text)

# ---------------------------
# MAIN DASHBOARD (Premium - Only Version)
# ---------------------------
@app.route('/')
def index():
    """Premium dashboard with enhanced UI, dark mode, and better visualizations"""
    refresh = request.args.get('refresh', '0') == '1'

    # Get real NASA soil moisture
    from data_ingest import get_soil_moisture
    nasa_soil_moisture = get_soil_moisture()

    # Get and clean weather data (NDVI will reflect crop health)
    weather_raw = get_weather(crop_health=twin.health)
    weather = clean_and_extract(weather_raw)

    # Update the digital twin state
    twin.update(weather)

    # Load or regenerate forecast
    global _cached
    if _cached['forecast'] is None or refresh:
        forecast_df = predict_soil_moisture(history_df)
        _cached['forecast'] = forecast_df
        _cached['weather'] = weather
        _cached['timestamp'] = datetime.datetime.now().isoformat()
    else:
        forecast_df = _cached['forecast']
        _cached['weather'] = weather

    # Generate RL recommendations
    raw_recommendations, rec_explanation = generate_recommendations(
        forecast_df, recent_weather=weather
    )
    human_recommendations = [
        humanize_recommendation(r) for r in raw_recommendations
    ]

    weather_summary = weather_recommendation(weather)
    ndvi_json = json.dumps(weather.get('ndvi_grid', []))
    
    # Get NDVI metadata for beautiful display
    ndvi_meta = get_ndvi_metadata()
    
    # Calculate NDVI mean from grid for real data sync
    ndvi_grid = weather.get('ndvi_grid', [])
    if ndvi_grid and len(ndvi_grid) > 0:
        import numpy as np
        ndvi_mean = float(np.mean(ndvi_grid))
    else:
        ndvi_mean = None

    # Build farm_data grid for 3D rendering
    farm_data = [[
        {
            "height": twin.height,
            "health": twin.health,
            "stage": twin.stage
        }
    ]]

    crop = {
        "height": twin.height,
        "health": twin.health,
        "stage": twin.stage,
        "soil_moisture": twin.soil_moisture,
        "nitrogen": twin.nitrogen,
        "gdd": twin.gdd,
        "age_days": twin.age_days,
        "rows": 1,
        "cols": 1,
        "stages": [[twin.stage]],
    }

    return render_template(
        'dashboard_premium.html',
        crop=crop,
        farm_data=json.dumps(farm_data),
        weather=weather,
        forecast=forecast_df.to_dict(orient='records'),
        recommendations=human_recommendations,
        recommendations_text=rec_explanation,
        weather_recommendation=weather_summary,
        ndvi_json=ndvi_json,
        ndvi_metadata=ndvi_meta,
        ndvi_mean=ndvi_mean,
        nasa_soil_moisture=nasa_soil_moisture,
        config=config,
        now=datetime.datetime.now()
    )

# ---------------------------
# Force-refresh endpoint
# ---------------------------
@app.route('/refresh', methods=['POST'])
def refresh():
    global _cached
    forecast_df = predict_soil_moisture(history_df)
    weather_raw = get_weather(crop_health=twin.health)
    weather = clean_and_extract(weather_raw)

    generate_recommendations(forecast_df, recent_weather=weather)

    _cached['forecast'] = forecast_df
    _cached['weather'] = weather
    _cached['timestamp'] = datetime.datetime.now().isoformat()
    return jsonify({'status': 'ok', 'timestamp': _cached['timestamp']})

# ---------------------------
# Control actions (buttons)
# ---------------------------
@app.route('/control', methods=['POST'])
def control():
    action = request.json.get('action')
    mode = request.json.get('mode', 'simulation')
    
    if mode == 'simulation':
        # Simulation mode: manual control
        irrigation = request.json.get('irrigation')
        fertilization = request.json.get('fertilization')
        
        if irrigation is not None or fertilization is not None:
            twin.set_manual_levels(irrigation, fertilization)
        elif action:
            twin.process_action(action)
    else:
        # Live mode: sync with real data
        nasa_moisture = request.json.get('nasa_soil_moisture')
        ndvi_mean = request.json.get('ndvi_mean')
        twin.sync_with_real_data(nasa_moisture, ndvi_mean)
    
    return jsonify({
        "stage": twin.stage,
        "height": twin.height,
        "health": twin.health,
        "soil_moisture": twin.soil_moisture,
        "nitrogen": twin.nitrogen
    })

# ---------------------------
# Admin page (Q-values + logs)
# ---------------------------
@app.route('/admin')
def admin():
    qvals = {}
    logs = {}

    try:
        import pickle
        p = os.path.join(os.path.dirname(__file__), 'q_agent.pkl')
        with open(p, 'rb') as f:
            agent = pickle.load(f)
        qvals = {str(k): agent.q[k] for k in agent.q}
    except Exception as e:
        qvals = {'error': str(e)}

    try:
        lpath = os.path.join(os.path.dirname(__file__), 'agent_logs.json')
        with open(lpath, 'r') as f:
            logs = json.load(f)
    except Exception as e:
        logs = {'error': str(e)}

    return render_template('admin.html', q_vals=qvals, logs=logs)

# ---------------------------
# Location Search (Reverse Geocoding)
# ---------------------------
@app.route('/api/geocode', methods=['POST'])
def geocode_location():
    """
    Reverse geocode coordinates to get location name
    Expects JSON: {"lat": 26.974583, "lon": 83.529583}
    """
    try:
        data = request.get_json()
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))
        
        # Validate India bounds (approximate)
        india_bounds = {
            'lat_min': 6.0,   # Southernmost point (Indira Point)
            'lat_max': 37.0,  # Northernmost point (Kashmir)
            'lon_min': 68.0,  # Westernmost point (Gujarat)
            'lon_max': 98.0   # Easternmost point (Arunachal Pradesh)
        }
        
        is_in_india = (india_bounds['lat_min'] <= lat <= india_bounds['lat_max'] and
                      india_bounds['lon_min'] <= lon <= india_bounds['lon_max'])
        
        # Perform reverse geocoding
        location = reverse_geocode(lat, lon)
        
        if location:
            # Convert to DMS for display
            dms_lat = decimal_to_dms(lat, is_latitude=True)
            dms_lon = decimal_to_dms(lon, is_latitude=False)
            
            return jsonify({
                'success': True,
                'location': {
                    'name': location['display_name'],
                    'city': location['city'],
                    'state': location['state'],
                    'country': location['country'],
                    'full_address': location['full_address']
                },
                'coordinates': {
                    'decimal': {'lat': lat, 'lon': lon},
                    'dms': {'lat': dms_lat, 'lon': dms_lon}
                },
                'validation': {
                    'is_in_india': is_in_india,
                    'warning': None if is_in_india else '⚠️ These coordinates are outside India. Satellite data is still available globally.'
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not find location for these coordinates. Please check if they are valid.'
            }), 404
            
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid coordinates. Please enter numeric decimal values (e.g., 26.974583, 83.529583)'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500

# ---------------------------
# Update Location Configuration
# ---------------------------
@app.route('/api/update-location', methods=['POST'])
def update_location_config():
    """
    Update location configuration and trigger page reload
    Expects JSON: {
        "lat": 26.974583,
        "lon": 83.529583,
        "location_name": "City, State, Country",
        "dms_lat": "26°58′28.5″N",
        "dms_lon": "83°31′46.5″E"
    }
    """
    try:
        data = request.get_json()
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))
        location_name = data.get('location_name')
        dms_lat = data.get('dms_lat')
        dms_lon = data.get('dms_lon')
        
        if not location_name:
            return jsonify({
                'success': False,
                'error': 'Location name is required'
            }), 400
        
        # Update config
        if config.update_location(lat, lon, location_name, dms_lat, dms_lon):
            # Clear ALL cached data to force refresh with new location
            global _cached, history_df
            _cached = {
                'forecast': None,
                'weather': None,
                'timestamp': None,
            }
            
            # Clear NDVI cache file for new location
            ndvi_cache_path = os.path.join(os.path.dirname(__file__), 'ndvi_cache.json')
            if os.path.exists(ndvi_cache_path):
                try:
                    with open(ndvi_cache_path, 'r') as f:
                        cache = json.load(f)
                    # Remove old location cache entries (keep only last 3 locations)
                    if len(cache) > 3:
                        # Keep only most recent 3 entries
                        sorted_keys = sorted(cache.keys(), 
                                           key=lambda k: cache[k].get('date', '2000-01-01'), 
                                           reverse=True)
                        new_cache = {k: cache[k] for k in sorted_keys[:3]}
                        with open(ndvi_cache_path, 'w') as f:
                            json.dump(new_cache, f, indent=2)
                    print(f"🗑️ Cleared old NDVI cache entries")
                except Exception as e:
                    print(f"⚠️ Could not clean NDVI cache: {e}")
            
            # Regenerate historical data for new location
            history_df = pd.DataFrame({
                'ds': pd.date_range(datetime.date.today() - pd.Timedelta(days=30), periods=30),
                'y': [random.uniform(25, 65) for _ in range(30)]
            })
            
            print(f"✅ Location updated to: {location_name} ({lat}, {lon})")
            print(f"🔄 All caches cleared, ready for fresh data")
            
            return jsonify({
                'success': True,
                'message': 'Location updated successfully',
                'location': {
                    'name': location_name,
                    'coords': {'lat': lat, 'lon': lon},
                    'coords_display': {'lat': dms_lat, 'lon': dms_lon}
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save location configuration'
            }), 500
            
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid coordinate values'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error updating location: {str(e)}'
        }), 500

# ---------------------------
# Run app
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
