import requests
import time
import math
import numpy as np
from datetime import datetime, timezone
from sgp4.api import Satrec, jday

# --- Configuration ---
API_URL = "http://localhost:8000/api/telemetry"
URL_ACTIVE = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
URL_DEBRIS = "https://celestrak.org/NORAD/elements/gp.php?GROUP=iridium-33-debris&FORMAT=tle"

TARGET_SATELLITES = 50
TARGET_REAL_DEBRIS = 1000

# Earth constants for RK4
MU_EARTH = 398600.4418
J2 = 0.0010826267
R_EARTH = 6378.137

import os

def fetch_tle_data(url, limit, fallback_file=None):
    print(f"Fetching TLE data from {url}...")
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        if "GP data has not updated" in response.text:
            raise Exception("Celestrak rate limit block (updated recently).")
        data = response.text.strip().split("\n")
    except Exception as e:
        print(f"Error fetching data: {e}")
        if fallback_file and os.path.exists(fallback_file):
            print(f"Using local fallback file: {fallback_file}")
            with open(fallback_file, "r") as f:
                data = f.read().strip().split("\n")
        else:
            return []

    objects = []
    for i in range(0, min(len(data), limit * 3), 3):
        if i + 2 < len(data):
            try:
                objects.append({
                    "name": data[i].strip(),
                    "satrec": Satrec.twoline2rv(data[i+1].strip(), data[i+2].strip())
                })
            except:
                pass
    return objects

def propagate_sat(sat, jd, fr):
    e, r, v = sat.sgp4(jd, fr)
    return (r, v) if e == 0 else (None, None)

# Fast RK4 for custom intersecting debris
def compute_acceleration(r):
    r_norm = np.linalg.norm(r)
    if r_norm == 0: return np.zeros(3)
    
    a_g = -MU_EARTH / (r_norm**3) * r
    
    z2_r2 = (r[2] / r_norm)**2
    j2_coeff = 1.5 * J2 * (R_EARTH / r_norm)**2
    
    a_j2_x = a_g[0] * j2_coeff * (5 * z2_r2 - 1)
    a_j2_y = a_g[1] * j2_coeff * (5 * z2_r2 - 1)
    a_j2_z = a_g[2] * j2_coeff * (5 * z2_r2 - 3)
    
    return a_g + np.array([a_j2_x, a_j2_y, a_j2_z])

def rk4_step(r, v, dt):
    k1_v = compute_acceleration(r)
    k1_r = v
    k2_v = compute_acceleration(r + 0.5 * dt * k1_r)
    k2_r = v + 0.5 * dt * k1_v
    k3_v = compute_acceleration(r + 0.5 * dt * k2_r)
    k3_r = v + 0.5 * dt * k2_v
    k4_v = compute_acceleration(r + dt * k3_r)
    k4_r = v + dt * k3_v
    
    r_new = r + (dt / 6.0) * (k1_r + 2*k2_r + 2*k3_r + k4_r)
    v_new = v + (dt / 6.0) * (k1_v + 2*k2_v + 2*k3_v + k4_v)
    return r_new, v_new

def build_telemetry_object(r, v, obj_id, obj_type):
    return {
        "id": obj_id,
        "type": obj_type,
        "r": {"x": r[0], "y": r[1], "z": r[2]},
        "v": {"x": v[0], "y": v[1], "z": v[2]}
    }

def chunk_data(data, size=500):
    for i in range(0, len(data), size):
        yield data[i:i+size]

def send_telemetry_batch(objects):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "objects": objects
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=2)
        if response.status_code == 200:
            print(f"[{payload['timestamp']}] Sent {len(objects)} objects")
    except requests.exceptions.ConnectionError:
        print("FastAPI server not running")
    except requests.exceptions.Timeout:
        print("API timeout")

def run_simulation():
    print("--- Initializing Space Environment ---")
    active_tles = fetch_tle_data(URL_ACTIVE, TARGET_SATELLITES, fallback_file="gp.php")
    debris_tles = fetch_tle_data(URL_DEBRIS, TARGET_REAL_DEBRIS, fallback_file="gp.php")
    print(f"Loaded {len(active_tles)} satellites and {len(debris_tles)} real debris pieces.")

    # Generate "Rogue" Debris that guarantees intersections for the demo
    rogue_debris = []
    now = datetime.now(timezone.utc)
    jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute, now.second)
    
    for i, tle in enumerate(active_tles[:5]): # Target first 5 satellites
        r, v = propagate_sat(tle["satrec"], jd, fr)
        if r and v:
            r_vec = np.array(r)
            v_vec = np.array(v)
            
            # Place the rogue debris 50km behind the satellite
            v_norm = v_vec / np.linalg.norm(v_vec)
            r_rogue = r_vec - (v_norm * 50.0) 
            
            # Give it a higher velocity so it catches up gradually (creating a realistic conjunction)
            v_rogue = v_vec + (v_norm * 0.05) # 50 m/s faster
            
            rogue_debris.append({
                "id": f"DEB-ROGUE-{i:03d}",
                "r": r_rogue,
                "v": v_rogue
            })

    print("Starting telemetry stream...")
    last_time = time.time()
    
    while True:
        telemetry_objects = []
        current_now = datetime.now(timezone.utc)
        jd, fr = jday(current_now.year, current_now.month, current_now.day, current_now.hour, current_now.minute, current_now.second)
        
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # Failsafe for large dt pauses
        if dt > 5.0: dt = 2.0

        # Satellites
        for i, tle in enumerate(active_tles):
            r, v = propagate_sat(tle["satrec"], jd, fr)
            if r and v:
                telemetry_objects.append(build_telemetry_object(r, v, f"SAT-{i:03d}", "SATELLITE"))

        # Real Debris (SGP4 propagated)
        for i, tle in enumerate(debris_tles):
            r, v = propagate_sat(tle["satrec"], jd, fr)
            if r and v:
                telemetry_objects.append(build_telemetry_object(r, v, f"DEB-REAL-{i:04d}", "DEBRIS"))
                
        # Rogue Debris (Physics Propagated)
        for rogue in rogue_debris:
            r_new, v_new = rk4_step(rogue["r"], rogue["v"], dt)
            rogue["r"] = r_new
            rogue["v"] = v_new
            telemetry_objects.append(build_telemetry_object(r_new, v_new, rogue["id"], "DEBRIS"))

        for chunk in chunk_data(telemetry_objects, 500):
            send_telemetry_batch(chunk)

        time.sleep(2)

if __name__ == "__main__":
    run_simulation()