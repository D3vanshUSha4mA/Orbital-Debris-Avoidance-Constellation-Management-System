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
        # Using *args failsafe we added earlier just in case
        lat, lon, alt = eci_to_lat_lon_alt(
            data["r"]["x"],
            data["r"]["y"],
            data["r"]["z"],
            timestamp
        )

        is_evading = sat_id in evading_sats
        
        display_alt = alt
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

        formatted_debris.append([
            deb_id,
            round(lat, 3),
            round(lon, 3),
            round(alt, 3)
        ])

    # 3. THE FIX: Pass all warnings directly to the UI
    # We must not filter out evading satellites, otherwise the UI logs will be empty!
    raw_warnings = SIMULATION_STATE.get("active_warnings", [])
    predictive_warnings = SIMULATION_STATE.get("future_cdms", [])

    return {
        "timestamp": timestamp,
        "total_tracked_objects": len(formatted_satellites) + len(formatted_debris),
        
        # Provide both keys to ensure React catches the data regardless of the exact prop name
        "warning_count": len(raw_warnings),
        "warnings": raw_warnings,
        "active_warnings": raw_warnings,
        
        "predictive_warning_count": len(predictive_warnings),
        "predictive_warnings": predictive_warnings,
        "satellites": formatted_satellites,
        "debris_cloud": formatted_debris
    }