from fastapi import APIRouter, status
from backend.core.state import SIMULATION_STATE
from backend.core.coordinates import eci_to_lat_lon_alt

router = APIRouter()

@router.get("/visualization/snapshot", status_code=status.HTTP_200_OK)
async def get_visualization_snapshot():
    
    timestamp = SIMULATION_STATE.get("last_updated", "2026-03-12T08:00:00.000Z")
    evading_sats = SIMULATION_STATE.get("evading_sats", set())

    # 1. Format Satellites
    formatted_satellites = []
    for sat_id, data in SIMULATION_STATE.get("satellites", {}).items():
        lat, lon, alt = eci_to_lat_lon_alt(
            data["r"]["x"],
            data["r"]["y"],
            data["r"]["z"],
            timestamp
        )

        is_evading = sat_id in evading_sats
        
        # Keep the +1500km altitude applied globally once the maneuver triggers
        display_alt = alt + 1500.0 if is_evading else alt
        status_text = "EVADING" if is_evading else "NOMINAL"

        formatted_satellites.append({
            "id": sat_id,
            "lat": round(lat, 3),
            "lon": round(lon, 3),
            "alt_km": round(display_alt, 3),
            "fuel_kg": round(data.get("mass", 50.0), 2),
            "status": status_text
        })

    # 2. Format Debris 
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

    # 3. Suppress active warnings for satellites currently evading
    raw_warnings = SIMULATION_STATE.get("active_warnings", [])
    active_warnings = [w for w in raw_warnings if w["satellite_id"] not in evading_sats]
    
    predictive_warnings = SIMULATION_STATE.get("future_cdms", [])

    return {
        "timestamp": timestamp,
        "total_tracked_objects": len(formatted_satellites) + len(formatted_debris),
        "warning_count": len(active_warnings),
        "active_warnings": active_warnings,
        "predictive_warning_count": len(predictive_warnings),
        "predictive_warnings": predictive_warnings,
        "satellites": formatted_satellites,
        "debris_cloud": formatted_debris
    }