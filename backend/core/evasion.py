# backend/core/evasion.py
import numpy as np
from datetime import datetime, timedelta
import uuid

def get_rtn_rotation_matrix(r_eci: np.ndarray, v_eci: np.ndarray) -> np.ndarray:
    """
    Calculates the rotation matrix to convert from the RTN frame back to the global ECI frame.
    R: Radial (along the position vector)
    N: Normal (perpendicular to the orbital plane)
    T: Transverse (perpendicular to R and N, generally along velocity)
    """
    # 1. Radial Unit Vector
    r_norm = np.linalg.norm(r_eci)
    u_R = r_eci / r_norm
    
    # 2. Normal Unit Vector (Cross product of R and V)
    h_vec = np.cross(r_eci, v_eci)
    h_norm = np.linalg.norm(h_vec)
    u_N = h_vec / h_norm
    
    # 3. Transverse Unit Vector (Cross product of N and R)
    u_T = np.cross(u_N, u_R)
    
    # The rotation matrix columns are the RTN unit vectors in ECI coordinates
    # Q = [u_R | u_T | u_N]
    return np.column_stack((u_R, u_T, u_N))

def calculate_evasion_sequence(sat_id: str, r_eci_dict: dict, v_eci_dict: dict, current_time_iso: str) -> dict:
    """
    Generates a hackathon-compliant automated maneuver sequence.
    Applies a prograde evasion burn, waits for cooldown, and applies a retrograde recovery burn.
    """
    r_eci = np.array([r_eci_dict["x"], r_eci_dict["y"], r_eci_dict["z"]])
    v_eci = np.array([v_eci_dict["x"], v_eci_dict["y"], v_eci_dict["z"]])
    
    # Get the conversion matrix
    rotation_matrix = get_rtn_rotation_matrix(r_eci, v_eci)
    
    # --- BURN 1: EVASION ---
    # We apply a 2.0 m/s burn entirely in the Transverse (T) direction.
    # Note: State vectors are in km/s, so 2.0 m/s = 0.002 km/s
    dv_rtn_evasion = np.array([0.0, 0.002, 0.0])
    
    # Rotate thrust vector back to ECI frame
    dv_eci_evasion = np.dot(rotation_matrix, dv_rtn_evasion)
    
    # Schedule Evasion for T + 15 seconds (Clears the 10-second latency rule)
    current_time = datetime.fromisoformat(current_time_iso.replace('Z', '+00:00'))
    evasion_time = current_time + timedelta(seconds=15)
    
    # --- BURN 2: RECOVERY ---
    # We reverse the burn (-2.0 m/s) to halt the drift and lock back into the station box.
    dv_rtn_recovery = np.array([0.0, -0.002, 0.0])
    dv_eci_recovery = np.dot(rotation_matrix, dv_rtn_recovery)
    
    # Schedule Recovery for T + 615 seconds (Clears the 600-second thermal cooldown rule)
    recovery_time = evasion_time + timedelta(seconds=600)
    
    # Construct the exact JSON payload expected by the maneuver API
    maneuver_payload = {
        "satelliteId": sat_id,
        "maneuver_sequence": [
            {
                "burn_id": f"EVASION_{uuid.uuid4().hex[:6].upper()}",
                "burnTime": evasion_time.isoformat().replace('+00:00', 'Z'),
                "deltaV_vector": {
                    "x": round(dv_eci_evasion[0], 6),
                    "y": round(dv_eci_evasion[1], 6),
                    "z": round(dv_eci_evasion[2], 6)
                }
            },
            {
                "burn_id": f"RECOVERY_{uuid.uuid4().hex[:6].upper()}",
                "burnTime": recovery_time.isoformat().replace('+00:00', 'Z'),
                "deltaV_vector": {
                    "x": round(dv_eci_recovery[0], 6),
                    "y": round(dv_eci_recovery[1], 6),
                    "z": round(dv_eci_recovery[2], 6)
                }
            }
        ]
    }
    
    return maneuver_payload