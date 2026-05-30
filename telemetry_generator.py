import requests
import time
import math
import random
from datetime import datetime, timezone
from sgp4.api import Satrec, jday

# --- Configuration ---
API_URL = "http://localhost:8000/api/telemetry"
URL_ACTIVE = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"

TARGET_SATELLITES = 50
TARGET_BACKGROUND_DEBRIS = 3000   # random load
DEBRIS_PER_SAT = 5               # collision debris per satellite

# --- Fetch TLE ---
def fetch_tle_data(url, limit):
    print(f"Fetching TLE data from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text.strip().split("\n")
        
        objects = []
        for i in range(0, min(len(data), limit * 3), 3):
            if i + 2 < len(data):
                objects.append({
                    "name": data[i].strip(),
                    "satrec": Satrec.twoline2rv(data[i+1].strip(), data[i+2].strip())
                })
        return objects
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

# --- Propagation ---
def propagate_sat(sat, jd, fr):
    e, r, v = sat.sgp4(jd, fr)
    return (r, v) if e == 0 else (None, None)

# --- Dangerous Debris (FOR COLLISIONS) ---
def generate_collision_debris(active_tles, jd, fr):
    debris = []

    for i, tle in enumerate(active_tles):
        r, v = propagate_sat(tle["satrec"], jd, fr)
        if not r or not v:
            continue

        for j in range(DEBRIS_PER_SAT):
            # VERY CLOSE → guaranteed conjunction
            r_offset = [
                r[0] + random.uniform(-0.05, 0.05),  # ~50m
                r[1] + random.uniform(-0.05, 0.05),
                r[2] + random.uniform(-0.05, 0.05)
            ]

            v_offset = [
                v[0] + random.uniform(-0.005, 0.005),
                v[1] + random.uniform(-0.005, 0.005),
                v[2] + random.uniform(-0.005, 0.005)
            ]

            debris.append({
                "id": f"DEB-COLL-{i:03d}-{j:02d}",
                "type": "DEBRIS",
                "r": {"x": r_offset[0], "y": r_offset[1], "z": r_offset[2]},
                "v": {"x": v_offset[0], "y": v_offset[1], "z": v_offset[2]}
            })

    return debris

# --- Background Debris (FOR LOAD) ---
def generate_background_debris(n):
    debris = []
    for i in range(n):
        r_mag = random.uniform(6578, 8378)
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(-math.pi/2, math.pi/2)

        x = r_mag * math.cos(phi) * math.cos(theta)
        y = r_mag * math.cos(phi) * math.sin(theta)
        z = r_mag * math.sin(phi)

        v_mag = random.uniform(6.5, 7.8)

        vx = -v_mag * math.sin(theta)
        vy = v_mag * math.cos(theta)
        vz = random.uniform(-1, 1)

        debris.append({
            "id": f"DEB-RAND-{i:05d}",
            "type": "DEBRIS",
            "r": {"x": x, "y": y, "z": z},
            "v": {"x": vx, "y": vy, "z": vz}
        })

    return debris

# --- JSON Formatter ---
def build_telemetry_object(r, v, obj_id, obj_type):
    return {
        "id": obj_id,
        "type": obj_type,
        "r": {"x": r[0], "y": r[1], "z": r[2]},
        "v": {"x": v[0], "y": v[1], "z": v[2]}
    }

# --- Chunking (IMPORTANT for large data) ---
def chunk_data(data, size=500):
    for i in range(0, len(data), size):
        yield data[i:i+size]

# --- API Sender ---
def send_telemetry_batch(objects):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "objects": objects
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            print(f"[{payload['timestamp']}] Sent {len(objects)} objects")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        print("FastAPI server not running")

# --- Main Loop ---
def run_simulation():
    print("--- Initializing Space Environment ---")
    
    active_tles = fetch_tle_data(URL_ACTIVE, TARGET_SATELLITES)
    print(f"Loaded {len(active_tles)} real satellites")

    # Generate background debris once
    background_debris = generate_background_debris(TARGET_BACKGROUND_DEBRIS)
    print(f"Generated {len(background_debris)} background debris")

    print("Starting telemetry stream...")

    while True:
        telemetry_objects = []

        now = datetime.now(timezone.utc)
        jd, fr = jday(now.year, now.month, now.day,
                      now.hour, now.minute, now.second)

        # --- Satellites ---
        for i, tle in enumerate(active_tles):
            r, v = propagate_sat(tle["satrec"], jd, fr)
            if r and v:
                telemetry_objects.append(
                    build_telemetry_object(r, v, f"SAT-{i:03d}", "SATELLITE")
                )

        # --- Collision debris (dynamic every step) ---
        collision_debris = generate_collision_debris(active_tles, jd, fr)

        telemetry_objects.extend(collision_debris)
        telemetry_objects.extend(background_debris)

        print(f"Total objects this step: {len(telemetry_objects)}")

        # --- Send in chunks ---
        for chunk in chunk_data(telemetry_objects, 500):
            send_telemetry_batch(chunk)

        time.sleep(2)

if __name__ == "__main__":
    run_simulation()