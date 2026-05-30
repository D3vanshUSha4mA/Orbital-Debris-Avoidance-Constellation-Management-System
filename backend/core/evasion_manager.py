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

        # 1. Read warnings and trigger new evasions
        for w in warnings:
            if w.get("status") == "CRITICAL":
                sat_id = w.get("obj_1")
                # Only trigger if it isn't already evading
                if sat_id not in self.active_evasions:
                    self.active_evasions[sat_id] = current_time

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