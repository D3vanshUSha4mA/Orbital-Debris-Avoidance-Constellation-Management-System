# backend/core/los.py
import math
import numpy as np
from datetime import datetime
from backend.core.coordinates import calculate_gmst
from backend.core.station_loader import ACTIVE_STATIONS

R_E = 6378.137  # Earth equatorial radius in km

def get_gs_ecef(lat_deg: float, lon_deg: float, alt_m: float) -> np.ndarray:
    """
    Converts Ground Station Latitude, Longitude, and Altitude into 
    Earth-Centered, Earth-Fixed (ECEF) 3D coordinates.
    """
    lat_rad = math.radians(lat_deg)
    lon_rad = math.radians(lon_deg)
    alt_km = alt_m / 1000.0

    r_total = R_E + alt_km

    x = r_total * math.cos(lat_rad) * math.cos(lon_rad)
    y = r_total * math.cos(lat_rad) * math.sin(lon_rad)
    z = r_total * math.sin(lat_rad)

    return np.array([x, y, z])

def eci_to_ecef(r_eci: np.ndarray, gmst_rad: float) -> np.ndarray:
    """
    Rotates an ECI vector into the ECEF frame using the Earth's rotation angle (GMST).
    """
    cos_g = math.cos(gmst_rad)
    sin_g = math.sin(gmst_rad)
    
    # Apply the Z-axis rotation matrix
    x_ecef = r_eci[0] * cos_g + r_eci[1] * sin_g
    y_ecef = -r_eci[0] * sin_g + r_eci[1] * cos_g
    z_ecef = r_eci[2]
    
    return np.array([x_ecef, y_ecef, z_ecef])

def calculate_elevation(r_sat_ecef: np.ndarray, r_gs_ecef: np.ndarray) -> float:
    """
    Calculates the elevation angle (in degrees) of the satellite 
    relative to the ground station's local horizon.
    """
    # 1. Vector pointing from Ground Station to Satellite
    range_vector = r_sat_ecef - r_gs_ecef
    range_mag = np.linalg.norm(range_vector)
    
    # 2. The local Zenith (Up) vector of the ground station
    zenith_vector = r_gs_ecef / np.linalg.norm(r_gs_ecef)
    
    # 3. Calculate the angle between the Zenith and Range vectors using the Dot Product
    # dot(A, B) = |A| * |B| * cos(theta)
    dot_product = np.dot(zenith_vector, range_vector)
    
    # Prevent math domain errors due to floating point inaccuracies
    cos_zenith_angle = max(-1.0, min(1.0, dot_product / range_mag))
    
    zenith_angle_rad = math.acos(cos_zenith_angle)
    
    # Elevation is 90 degrees minus the Zenith angle
    elevation_rad = (math.pi / 2.0) - zenith_angle_rad
    
    return math.degrees(elevation_rad)

def validate_line_of_sight(r_sat_eci_dict: dict, timestamp_iso: str) -> bool:
    """
    Checks if the satellite has line-of-sight to ANY active ground station.
    Accepts the satellite dictionary format: {"x": float, "y": float, "z": float}
    """
    if not ACTIVE_STATIONS:
        print("Warning: No ground stations loaded. Failing LOS validation.")
        return False

    r_sat_eci = np.array([r_sat_eci_dict["x"], r_sat_eci_dict["y"], r_sat_eci_dict["z"]])
    
    if not timestamp_iso:
        print("Warning: No timestamp provided. Failing LOS validation.")
        return False

    # Get Earth's rotation angle at this exact moment
    dt = datetime.fromisoformat(timestamp_iso.replace('Z', '+00:00'))
    gmst_rad = calculate_gmst(dt)
    
    # Rotate satellite to match the rotating Earth
    r_sat_ecef = eci_to_ecef(r_sat_eci, gmst_rad)

    # Check against all loaded stations
    for station_id, gs_data in ACTIVE_STATIONS.items():
        r_gs_ecef = get_gs_ecef(gs_data["lat"], gs_data["lon"], gs_data["elevation_m"])
        
        elevation_deg = calculate_elevation(r_sat_ecef, r_gs_ecef)
        
        if elevation_deg >= gs_data["min_elevation_deg"]:
            # Signal is clear!
            return True
            
    # If the loop finishes without returning True, the satellite is in a blackout zone
    return False