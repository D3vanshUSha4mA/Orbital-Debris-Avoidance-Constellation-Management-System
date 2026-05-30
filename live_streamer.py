import time
import requests
import random
from datetime import datetime, timezone
from skyfield.api import load

# ==========================================
# CONFIGURATION
# ==========================================
BACKEND_URL = "http://localhost:8000/api/telemetry"
CELESTRAK_STARLINK_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
MAX_STARLINKS = 200     # Limit to 200 real satellites to keep the map clean
DEBRIS_COUNT = 300      # Size of our synthetic fragmentation cloud

print("Initializing Kobayashi Maru Data Streamer...")

# 1. Load the Skyfield timescale and fetch live TLEs
ts = load.timescale()
print("Fetching live Starlink TLEs from Celestrak...")
satellites = load.tle_file(CELESTRAK_STARLINK_URL)
active_starlinks = satellites[:MAX_STARLINKS]
print(f"Loaded {len(active_starlinks)} live Starlink satellites.")

def generate_kobayashi_maru_debris(target_position, target_velocity):
    """
    Creates a synthetic debris cloud targeting a specific satellite's XYZ coordinates.
    """
    debris_list = []
    
    for i in range(DEBRIS_COUNT):
        # Create a fragmentation spread formatted as x,y,z dictionaries
        r_offset = {
            "x": target_position["x"] + random.uniform(-10.0, 10.0),
            "y": target_position["y"] + random.uniform(-10.0, 10.0),
            "z": target_position["z"] + random.uniform(-10.0, 10.0)
        }
        
        # Make the debris retrograde (head-on collision course)
        v_offset = {
            "x": -target_velocity["x"] + random.uniform(-0.5, 0.5),
            "y": -target_velocity["y"] + random.uniform(-0.5, 0.5),
            "z": -target_velocity["z"] + random.uniform(-0.5, 0.5)
        }
        
        debris_list.append({
            "id": f"DEB-KOBAYASHI-{i}",
            "type": "debris",
            "r": r_offset,
            "v": v_offset
        })
        
    return debris_list

# ==========================================
# MAIN EVENT LOOP
# ==========================================
print("Starting real-time propagation engine. Press Ctrl+C to stop.")

try:
    while True:
        current_time = ts.now()
        payload = []
        
        # 1. Propagate REAL Starlink Satellites into {"x", "y", "z"} dictionaries
        for sat in active_starlinks:
            geocentric = sat.at(current_time)
            
            # Extract raw lists
            pos_list = geocentric.position.km.tolist()
            vel_list = geocentric.velocity.km_per_s.tolist()
            
            # Format as strict Pydantic dictionaries
            pos_dict = {"x": pos_list[0], "y": pos_list[1], "z": pos_list[2]}
            vel_dict = {"x": vel_list[0], "y": vel_list[1], "z": vel_list[2]}
            
            payload.append({
                "id": sat.name.strip(),
                "type": "satellite",
                "r": pos_dict,
                "v": vel_dict
            })
            
        # 2. Inject SYNTHETIC Debris Cloud
        target_r = payload[0]["r"]
        target_v = payload[0]["v"]
        
        debris_cloud = generate_kobayashi_maru_debris(target_r, target_v)
        payload.extend(debris_cloud)
        
        # 3. Format and Send to the Docker Backend
        request_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "objects": payload
        }
        
        try:
            response = requests.post(BACKEND_URL, json=request_data, timeout=2)
            
            if response.status_code == 422:
                print("FASTAPI ERROR DETAILS:", response.json())
            else:
                print(f"[{request_data['timestamp']}] Injected {len(payload)} objects -> Server Response: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("ERROR: Could not connect to Docker backend. Is it running on port 8000?")
            
        time.sleep(1)

except KeyboardInterrupt:
    print("\nData stream terminated.")