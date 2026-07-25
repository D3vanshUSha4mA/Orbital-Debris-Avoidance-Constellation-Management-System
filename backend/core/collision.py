import numpy as np
from scipy.spatial import cKDTree

# The hackathon will define a minimum safe distance. We will use 10 km.
WARNING_RADIUS_KM = 10.0
CRITICAL_THRESHOLD_KM = 10.0 

def detect_collisions(simulation_state):
    """
    Builds a C++ optimized K-D Tree of all debris and queries it against 
    satellite positions to find imminent collisions in milliseconds.
    """
    satellites = simulation_state.get("satellites", {})
    debris = simulation_state.get("debris", {})

    if not satellites or not debris:
        return []

    # 1. Extract all debris coordinates into a fast NumPy array
    debris_ids = list(debris.keys())
    debris_coords = np.array([
        [d["r"]["x"], d["r"]["y"], d["r"]["z"]] for d in debris.values()
    ])

    # 2. Build the K-D Tree (The Spatial Index)
    # This organizes all debris into a searchable 3D grid
    tree = cKDTree(debris_coords)

    active_warnings = []

    # 3. Query the tree for each satellite
    for sat_id, sat_data in satellites.items():
        sat_coord = [sat_data["r"]["x"], sat_data["r"]["y"], sat_data["r"]["z"]]

        # query_ball_point instantly returns the indices of all debris 
        # that fall within the specified radius of the satellite
        close_debris_indices = tree.query_ball_point(sat_coord, WARNING_RADIUS_KM)

        for idx in close_debris_indices:
            deb_id = debris_ids[idx]
            
            # Calculate the exact Euclidean distance for the warning report
            deb_coord = debris_coords[idx]
            distance = np.linalg.norm(np.array(sat_coord) - deb_coord)

            active_warnings.append({
                "obj_1": sat_id,
                "obj_2": deb_id,
                "distance_km": round(distance, 3),
                "status": "CRITICAL" if distance < CRITICAL_THRESHOLD_KM else "WARNING"
            })

    return active_warnings