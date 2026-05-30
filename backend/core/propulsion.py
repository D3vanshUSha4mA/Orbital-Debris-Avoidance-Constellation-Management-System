# backend/core/propulsion.py
import numpy as np
import math
from datetime import datetime

# --- Spacecraft Propulsion Constants ---
ISP = 300.0          # Specific Impulse in seconds [cite: 158]
G0 = 9.80665         # Standard gravity in m/s^2 [cite: 164]
MAX_THRUST = 15.0    # Maximum delta-v per burn in m/s [cite: 159]
COOLDOWN_SEC = 600.0 # Mandatory rest period between burns [cite: 160]

def calculate_mass_depletion(current_mass_kg: float, delta_v_mag_m_s: float) -> float:
    """
    Calculates the mass consumed during a maneuver using the Tsiolkovsky rocket equation[cite: 162].
    Formula: Delta_m = m_current * (1 - e^(-Delta_V / (Isp * g0))) [cite: 163]
    """
    exponent = -delta_v_mag_m_s / (ISP * G0)
    mass_consumed = current_mass_kg * (1.0 - math.exp(exponent))
    return mass_consumed

def validate_thrust(delta_v_km_s: dict) -> float:
    """
    Ensures the requested thrust does not exceed the hardware limit[cite: 159].
    Returns the magnitude of the thrust in m/s if valid, or raises a ValueError.
    """
    dv = np.array([delta_v_km_s["x"], delta_v_km_s["y"], delta_v_km_s["z"]])
    
    # State vectors are in km/s, so we multiply by 1000 for m/s
    dv_mag_m_s = np.linalg.norm(dv) * 1000.0
    
    if dv_mag_m_s > MAX_THRUST:
        raise ValueError(f"Requested thrust {dv_mag_m_s:.2f} m/s exceeds the {MAX_THRUST} m/s limit.")
        
    return dv_mag_m_s

def check_cooldown(last_burn_time_iso: str, new_burn_time_iso: str) -> bool:
    """
    Validates the 600-second mandatory thermal cooldown period[cite: 160].
    """
    if not last_burn_time_iso:
        return True
        
    last_time = datetime.fromisoformat(last_burn_time_iso.replace('Z', '+00:00'))
    new_time = datetime.fromisoformat(new_burn_time_iso.replace('Z', '+00:00'))
    
    time_diff = (new_time - last_time).total_seconds()
    return time_diff >= COOLDOWN_SEC