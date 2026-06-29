import numpy as np
from scipy.spatial import cKDTree
from datetime import datetime, timedelta
from backend.core.physics import rk4_step

# --- PREDICTION CONSTANTS ---
TIME_STEP_SEC = 300.0  # 5 minutes per step
PREDICTION_HOURS = 24
TOTAL_STEPS = int((PREDICTION_HOURS * 3600) / TIME_STEP_SEC)
COLLISION_THRESHOLD_KM = 10.0


def run_predictive_ca(simulation_state):
    """
    Simulates the future using RK4 and KD-Trees to generate
    Conjunction Data Messages (CDMs) for future collisions.
    """
    satellites = simulation_state.get("satellites", {})
    debris = simulation_state.get("debris", {})
    start_time_str = simulation_state.get("last_updated")

    if not satellites or not debris or not start_time_str:
        return []

    try:
        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
    except ValueError:
        start_time = datetime.utcnow()

    sim_sats = {}
    for sid, data in satellites.items():
        sim_sats[sid] = {
            "r": np.array([data["r"]["x"], data["r"]["y"], data["r"]["z"]]),
            "v": np.array([data["v"]["x"], data["v"]["y"], data["v"]["z"]])
        }

    sim_debs = {}
    for did, data in debris.items():
        sim_debs[did] = {
            "r": np.array([data["r"]["x"], data["r"]["y"], data["r"]["z"]]),
            "v": np.array([data["v"]["x"], data["v"]["y"], data["v"]["z"]])
        }

    future_cdms = []

    # Propagation loop
    for step in range(1, TOTAL_STEPS + 1):
        current_sim_time = start_time + timedelta(seconds=step * TIME_STEP_SEC)

        debris_coords = []
        debris_ids = list(sim_debs.keys())

        # --- Propagate debris ---
        for did in debris_ids:
            r_next, v_next = rk4_step(
                sim_debs[did]["r"],
                sim_debs[did]["v"],
                TIME_STEP_SEC
            )
            sim_debs[did]["r"] = r_next
            sim_debs[did]["v"] = v_next
            debris_coords.append(r_next)

        # --- THE FIX: Apply numpy finite masking ---
        debris_coords_arr = np.array(debris_coords)
        valid_mask = np.all(np.isfinite(debris_coords_arr), axis=1)

        clean_debris_coords = debris_coords_arr[valid_mask]
        clean_debris_ids = np.array(debris_ids)[valid_mask]

        # Failsafe: If all debris crashed/corrupted, skip the KD-Tree for this timestep
        if len(clean_debris_coords) == 0:
            continue

        # Build KD-tree for current step using ONLY valid coordinates
        future_tree = cKDTree(clean_debris_coords)

        # --- Propagate satellites and check collisions ---
        for sid, sat_state in sim_sats.items():
            r_next, v_next = rk4_step(
                sat_state["r"],
                sat_state["v"],
                TIME_STEP_SEC
            )
            sim_sats[sid]["r"] = r_next
            sim_sats[sid]["v"] = v_next

            # Failsafe: Skip this satellite if RK4 corrupted its coordinate
            if not np.all(np.isfinite(r_next)):
                continue

            # Query nearby debris safely
            close_indices = future_tree.query_ball_point(
                r_next,
                COLLISION_THRESHOLD_KM
            )

            for idx in close_indices:
                deb_id = clean_debris_ids[idx]
                deb_r = sim_debs[deb_id]["r"]

                distance = np.linalg.norm(r_next - deb_r)

                future_cdms.append({
                    "satellite_id": sid,
                    "debris_id": deb_id,
                    "time_of_closest_approach": current_sim_time.isoformat(),
                    "hours_until_collision": round(
                        (step * TIME_STEP_SEC) / 3600, 2
                    ),
                    "miss_distance_km": round(distance, 3)
                })

    return future_cdms