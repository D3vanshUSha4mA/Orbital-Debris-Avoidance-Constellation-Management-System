from fastapi import APIRouter, status
from backend.core.state import SIMULATION_STATE
from backend.core.coordinates import eci_to_lat_lon_alt

router = APIRouter()

@router.get("/visualization/snapshot", status_code=status.HTTP_200_OK)
async def get_visualization_snapshot():
    
    timestamp = SIMULATION_STATE.get("last_updated", "2026-03-12T08:00:00.000Z")

    # 1. Format Satellites (Convert to Map Coordinates)
    formatted_satellites = []
    for sat_id, data in SIMULATION_STATE.get("satellites", {}).items():
        lat, lon, alt = eci_to_lat_lon_alt(
            data["r"]["x"],
            data["r"]["y"],
            data["r"]["z"],
            timestamp
        )

        formatted_satellites.append({
            "id": sat_id,
            "lat": round(lat, 3),
            "lon": round(lon, 3),
            "alt_km": round(alt, 3),
            "fuel_kg": data.get("mass", 50.0),
            "status": "NOMINAL"
        })

    # 2. Format Debris (Convert to Map Coordinates)
    formatted_debris = []
    for deb_id, data in SIMULATION_STATE.get("debris", {}).items():
        lat, lon, alt = eci_to_lat_lon_alt(
            data["r"]["x"],
            data["r"]["y"],
            data["r"]["z"],
            timestamp
        )

        formatted_debris.append({
            "id": deb_id,
            "lat": round(lat, 3),
            "lon": round(lon, 3),
            "alt_km": round(alt, 3)
        })

    # 3. Pull the warnings that the K-D Tree already calculated safely in the background
    active_warnings = SIMULATION_STATE.get("active_warnings", [])
    predictive_warnings = SIMULATION_STATE.get("future_cdms", [])

    return {
        "timestamp": timestamp,
        "total_tracked_objects": len(formatted_satellites) + len(formatted_debris),
        
        "warning_count": len(active_warnings),
        "active_warnings": active_warnings,       # Instantly calculated by KD-Tree
        
        "predictive_warning_count": len(predictive_warnings),
        "predictive_warnings": predictive_warnings, # 24-hr Future calculated by RK4
        
        "satellites": formatted_satellites,
        "debris_cloud": formatted_debris
    }