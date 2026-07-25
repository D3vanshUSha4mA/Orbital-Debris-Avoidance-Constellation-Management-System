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

def calculate_evasion_sequence(sat_id: str, r_eci_dict: dict, v_eci_dict: dict, current_time_iso: str, current_mass: float = 50.0) -> dict:
    """
    Generates a hackathon-compliant automated maneuver sequence.
    Applies a prograde evasion burn, waits for cooldown, and applies a retrograde recovery burn.
    """
    r_eci = np.array([r_eci_dict["x"], r_eci_dict["y"], r_eci_dict["z"]])
    v_eci = np.array([v_eci_dict["x"], v_eci_dict["y"], v_eci_dict["z"]])
    
    # Get the conversion matrix
    rotation_matrix = get_rtn_rotation_matrix(r_eci, v_eci)
    
    current_time = datetime.fromisoformat(current_time_iso.replace('Z', '+00:00'))
    evasion_time = current_time + timedelta(seconds=15)
    
    # --- END-OF-LIFE GRAVEYARD ORBIT CHECK ---
    # If fuel is below 5% (2.5 kg), perform a terminal radial burn to clear the orbit
    if current_mass < 2.5:
        dv_rtn_graveyard = np.array([0.015, 0.0, 0.0]) # 15 m/s maximum thrust
        dv_eci_graveyard = np.dot(rotation_matrix, dv_rtn_graveyard)
        return {
            "satelliteId": sat_id,
            "maneuver_sequence": [
                {
                    "burn_id": f"GRAVEYARD_{uuid.uuid4().hex[:6].upper()}",
                    "burnTime": evasion_time.isoformat().replace('+00:00', 'Z'),
                    "deltaV_vector": {
                        "x": round(dv_eci_graveyard[0], 6),
                        "y": round(dv_eci_graveyard[1], 6),
                        "z": round(dv_eci_graveyard[2], 6)
                    }
                }
            ]
        }
    
    # --- STATION-KEEPING PHASING MANEUVER ---
    # Burn 1: EVASION (Prograde)
    # We apply a 2.0 m/s burn in the Transverse (T) direction to dodge the debris.
    dv_rtn_evasion = np.array([0.0, 0.002, 0.0])
    dv_eci_evasion = np.dot(rotation_matrix, dv_rtn_evasion)
    
    # Burn 2: DRIFT REVERSAL (Retrograde)
    # 600 seconds later, we apply -4.0 m/s to drop below the nominal orbit.
    # This halts the backward drift and initiates a forward catch-up trajectory.
    dv_rtn_reversal = np.array([0.0, -0.004, 0.0])
    dv_eci_reversal = np.dot(rotation_matrix, dv_rtn_reversal)
    reversal_time = evasion_time + timedelta(seconds=600)
    
    # Burn 3: STATION CIRCULARIZATION (Prograde)
    # 600 seconds after Reversal, we have caught back up to the nominal slot.
    # Apply +2.0 m/s to match the nominal velocity and lock back into the box.
    dv_rtn_circularize = np.array([0.0, 0.002, 0.0])
    dv_eci_circularize = np.dot(rotation_matrix, dv_rtn_circularize)
    circularize_time = reversal_time + timedelta(seconds=600)
    
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
                "burn_id": f"REVERSAL_{uuid.uuid4().hex[:6].upper()}",
                "burnTime": reversal_time.isoformat().replace('+00:00', 'Z'),
                "deltaV_vector": {
                    "x": round(dv_eci_reversal[0], 6),
                    "y": round(dv_eci_reversal[1], 6),
                    "z": round(dv_eci_reversal[2], 6)
                }
            },
            {
                "burn_id": f"CIRCULARIZE_{uuid.uuid4().hex[:6].upper()}",
                "burnTime": circularize_time.isoformat().replace('+00:00', 'Z'),
                "deltaV_vector": {
                    "x": round(dv_eci_circularize[0], 6),
                    "y": round(dv_eci_circularize[1], 6),
                    "z": round(dv_eci_circularize[2], 6)
                }
            }
        ]
    }
    
    return maneuver_payload