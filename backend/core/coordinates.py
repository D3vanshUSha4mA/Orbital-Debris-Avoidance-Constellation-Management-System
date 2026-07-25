import math
from datetime import datetime

# Earth Constants
EARTH_RADIUS_KM = 6371.0

def calculate_gmst(dt: datetime) -> float:
    """
    Calculates Greenwich Mean Sidereal Time (GMST) in radians.
    This tells us exactly how much the Earth has rotated on its axis.
    """
    # 1. Extract time components
    year, month, day = dt.year, dt.month, dt.day
    hour, minute, second = dt.hour, dt.minute, dt.second

    # 2. Adjust for Astronomical Julian Date calculations
    if month <= 2:
        year -= 1
        month += 12

    A = math.floor(year / 100.0)
    B = 2 - A + math.floor(A / 4.0)
    
    # 3. Calculate Julian Date (JD)
    JD = math.floor(365.25 * (year + 4716.0)) + math.floor(30.6001 * (month + 1.0)) + day + B - 1524.5
    JD += (hour + minute / 60.0 + second / 3600.0) / 24.0

    # 4. Calculate centuries past the year 2000 epoch
    T = (JD - 2451545.0) / 36525.0
    
    # 5. Calculate GMST in seconds, then convert to radians
    GMST_seconds = 24110.54841 + 8640184.812866 * T + 0.093104 * T**2 - 6.2e-6 * T**3
    GMST_rad = (GMST_seconds % 86400.0) * (2 * math.pi / 86400.0)
    
    return GMST_rad

import math

import math

def eci_to_lat_lon_alt(x, y, z, timestamp_iso=None, *args):
    # Calculate the radial distance
    r = math.sqrt(x**2 + y**2 + z**2)
    
    # --- The Core Failsafe ---
    if r == 0.0:
        return 0.0, 0.0, 0.0 
        
    latitude = math.degrees(math.asin(z / r))
    
    gmst_rad = 0.0
    if timestamp_iso:
        try:
            dt = datetime.fromisoformat(timestamp_iso.replace('Z', '+00:00'))
            gmst_rad = calculate_gmst(dt)
        except Exception:
            pass

    lon_rad = math.atan2(y, x) - gmst_rad
    # Normalize longitude to [-180, 180]
    lon_rad = (lon_rad + math.pi) % (2 * math.pi) - math.pi
    longitude = math.degrees(lon_rad)
    
    # Calculate altitude using standardized equatorial radius
    EARTH_RADIUS_KM = 6378.137
    altitude = r - EARTH_RADIUS_KM
    
    return latitude, longitude, altitude