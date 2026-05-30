import csv
import os

# Global dictionary to hold the station data in memory
ACTIVE_STATIONS = {}

def load_ground_stations():
    """
    Loads the ground station network from the CSV file into memory.
    The path navigates up one directory since the script runs from /backend.
    """
    filepath = os.path.join(os.path.dirname(__file__), "../../data/ground_stations.csv")
    
    try:
        with open(filepath, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                station_id = row["Station_ID"]
                ACTIVE_STATIONS[station_id] = {
                    "name": row["Station_Name"],
                    "lat": float(row["Latitude"]),
                    "lon": float(row["Longitude"]),
                    "elevation_m": float(row["Elevation_m"]),
                    "min_elevation_deg": float(row["Min_Elevation_Angle_deg"])
                }
        print(f"Loaded {len(ACTIVE_STATIONS)} ground stations into memory.")
    except FileNotFoundError:
        print(f"Warning: Could not find ground stations data at {filepath}")