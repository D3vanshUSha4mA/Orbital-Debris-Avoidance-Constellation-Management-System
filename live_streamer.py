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

def generate_kobayashi_maru_debris(current_payload, total_debris=300, target_count=5):
    """
    Distributes a synthetic debris cloud across multiple target satellites
    so the UI shows various conjunction warnings.
    """
    debris_list = []
    
    # Use a fixed slice of satellites so the debris clouds follow 
    # the same targets frame-by-frame and don't teleport randomly.
    threatened_sats = current_payload[:target_count]
    
    # Safely handle cases where we have fewer satellites than target_count
    actual_target_count = len(threatened_sats)
    if actual_target_count == 0:
        return debris_list
        
    debris_per_target = total_debris // actual_target_count
    
    debris_id = 0
    for sat in threatened_sats:
        for _ in range(debris_per_target):
            # Create a fragmentation spread localized around the target satellite
            r_offset = {
                "x": sat["r"]["x"] + random.uniform(-10.0, 10.0),
                "y": sat["r"]["y"] + random.uniform(-10.0, 10.0),
                "z": sat["r"]["z"] + random.uniform(-10.0, 10.0)
            }
            
            # Retrograde collision course relative to target
            v_offset = {
                "x": -sat["v"]["x"] + random.uniform(-0.5, 0.5),
                "y": -sat["v"]["y"] + random.uniform(-0.5, 0.5),
                "z": -sat["v"]["z"] + random.uniform(-0.5, 0.5)
            }
            
            debris_list.append({
                "id": f"DEB-KOBAYASHI-{debris_id}",
                "type": "debris",
                "r": r_offset,
                "v": v_offset
            })
            debris_id += 1
            
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
            
        # 2. Inject SYNTHETIC Debris Cloud across 5 different satellites
        if payload:
            debris_cloud = generate_kobayashi_maru_debris(payload, DEBRIS_COUNT, target_count=5)
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