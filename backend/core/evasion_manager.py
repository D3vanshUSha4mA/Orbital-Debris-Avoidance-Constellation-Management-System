import time
import math

class EvasionManager:
    def __init__(self):
        # Dictionary to track which satellites are actively dodging
        # Format: { "SAT_ID": start_time_float }
        self.active_evasions = {}
        
        # Hackathon tuning parameters
        self.EVASION_DURATION = 15.0  # How many seconds the dodge maneuver lasts
        self.DODGE_DISTANCE = 50.0    # Peak displacement in km (large enough to see on UI)

    def process_telemetry(self, objects, warnings):
        """
        Intercepts the telemetry stream, triggers evasions based on warnings,
        and mathematically overrides the coordinates of evading satellites.
        """
        current_time = time.time()
        from backend.core.state import SIMULATION_STATE
        from backend.core.evasion import calculate_evasion_sequence
        import requests
        import threading
        
        current_iso = SIMULATION_STATE.get("last_updated")

        # 1. Read warnings and trigger new evasions
        for w in warnings:
            if w.get("status") in ["CRITICAL", "PREDICTED"]:
                sat_id = w.get("obj_1")
                # Only trigger if it isn't already evading
                if sat_id and sat_id not in self.active_evasions:
                    self.active_evasions[sat_id] = current_time
                    
                    # AUTOPILOT LOGIC: Trigger Evasion and Graveyard sequences
                    sat_data = SIMULATION_STATE.get("satellites", {}).get(sat_id)
                    if sat_data and current_iso:
                        
                        # --- BLACKOUT ZONE FORECASTING ---
                        if w.get("status") == "PREDICTED":
                            from backend.core.physics import rk4_step
                            from backend.core.los import validate_line_of_sight
                            from datetime import datetime, timedelta
                            import numpy as np
                            
                            tca_str = w.get("time_of_closest_approach")
                            if tca_str:
                                try:
                                    tca = datetime.fromisoformat(tca_str.replace('Z', '+00:00'))
                                    curr = datetime.fromisoformat(current_iso.replace('Z', '+00:00'))
                                    time_to_tca = (tca - curr).total_seconds()
                                    
                                    # If TCA is > 20 mins away, check LOS at TCA - 15 mins
                                    if time_to_tca > 1200:
                                        check_time = time_to_tca - 900
                                        r_pred, _ = rk4_step(
                                            np.array([sat_data["r"]["x"], sat_data["r"]["y"], sat_data["r"]["z"]]),
                                            np.array([sat_data["v"]["x"], sat_data["v"]["y"], sat_data["v"]["z"]]),
                                            check_time
                                        )
                                        pred_iso = (curr + timedelta(seconds=check_time)).isoformat().replace('+00:00', 'Z')
                                        r_pred_dict = {"x": r_pred[0], "y": r_pred[1], "z": r_pred[2]}
                                        if not validate_line_of_sight(r_pred_dict, pred_iso):
                                            print(f"📡 BLACKOUT ZONE FORECASTED for {sat_id} at {pred_iso}. Uplinking Evasion Sequence EARLY.")
                                except Exception as e:
                                    print(f"Blackout forecast error: {e}")

                        payload = calculate_evasion_sequence(
                            sat_id, 
                            sat_data["r"], 
                            sat_data["v"], 
                            current_iso,
                            sat_data.get("mass", 50.0)
                        )
                        
                        # Dispatch to API asynchronously so we don't block telemetry
                        def schedule_burn():
                            try:
                                requests.post("http://127.0.0.1:8000/api/maneuver/schedule", json=payload, timeout=2)
                            except Exception:
                                pass
                        threading.Thread(target=schedule_burn).start()

        # 2. Apply mathematical overrides to the live objects
        for obj in objects:
            sat_id = obj.get("id")
            
            if sat_id in self.active_evasions:
                elapsed = current_time - self.active_evasions[sat_id]

                # Check if the maneuver is finished
                if elapsed > self.EVASION_DURATION:
                    del self.active_evasions[sat_id]
                    obj["status"] = "NOMINAL"
                    continue

                # Calculate the smooth arc using a sine wave
                arc_factor = math.sin(math.pi * (elapsed / self.EVASION_DURATION))
                offset = arc_factor * self.DODGE_DISTANCE

                # Apply the spatial displacement (Push radially outward to raise altitude)
                r_x = obj["r"]["x"]
                r_y = obj["r"]["y"]
                r_z = obj["r"]["z"]
                
                # Calculate vector magnitude
                magnitude = math.sqrt(r_x**2 + r_y**2 + r_z**2)
                if magnitude > 0:
                    obj["r"]["x"] += (r_x / magnitude) * offset
                    obj["r"]["y"] += (r_y / magnitude) * offset
                    obj["r"]["z"] += (r_z / magnitude) * offset

                # Tag the object for the UI to change its color to Yellow/Orange
                obj["status"] = "EVADING"

        return objects