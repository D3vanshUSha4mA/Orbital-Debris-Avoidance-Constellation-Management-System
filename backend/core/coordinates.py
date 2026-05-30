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

def eci_to_lat_lon_alt(x: float, y: float, z: float, timestamp_iso: str):
    """
    Converts 3D ECI coordinates (km) to Latitude, Longitude, and Altitude.
    """
    # Parse the JSON timestamp string into a Python datetime object
    # Format expected: "2026-03-15T11:17:24.600Z" or similar
    dt = datetime.fromisoformat(timestamp_iso.replace('Z', '+00:00'))
    
    # Get Earth's rotation angle
    gmst = calculate_gmst(dt)
    
    # 1. Calculate Longitude (and wrap it between -180 and 180 degrees)
    lon_rad = math.atan2(y, x) - gmst
    lon_rad = (lon_rad + math.pi) % (2 * math.pi) - math.pi
    longitude = math.degrees(lon_rad)
    
    # 2. Calculate Latitude
    # Euclidean distance from center of the earth: r = sqrt(x^2 + y^2 + z^2)
    r = math.sqrt(x**2 + y**2 + z**2)
    latitude = math.degrees(math.asin(z / r))
    
    # 3. Calculate Altitude (Distance from center minus Earth's radius)
    altitude = r - EARTH_RADIUS_KM
    
    return latitude, longitude, altitude