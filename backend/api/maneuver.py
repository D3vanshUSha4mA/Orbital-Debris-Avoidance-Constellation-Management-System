# backend/api/maneuver.py
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from typing import List

from backend.core.state import SIMULATION_STATE
from backend.core.los import validate_line_of_sight
from backend.core.propulsion import calculate_mass_depletion, validate_thrust, check_cooldown

router = APIRouter()

# Global dictionary to track cooldowns
# Format: {"SAT-Alpha-04": "2026-03-12T14:15:30.000Z"}
SATELLITE_LAST_BURN = {}

# --- Pydantic Models ---
class Vector3D(BaseModel):
    x: float
    y: float
    z: float

class ManeuverBurn(BaseModel):
    burn_id: str
    burnTime: str
    deltaV_vector: Vector3D

class ManeuverSchedulePayload(BaseModel):
    satelliteId: str
    maneuver_sequence: List[ManeuverBurn]

# --- Endpoint ---
@router.post("/maneuver/schedule", status_code=status.HTTP_202_ACCEPTED)
async def schedule_maneuver(payload: ManeuverSchedulePayload):
    sat_id = payload.satelliteId
    
    if sat_id not in SIMULATION_STATE["satellites"]:
        raise HTTPException(status_code=404, detail="Satellite ID not found in telemetry.")
        
    sat_data = SIMULATION_STATE["satellites"][sat_id]
    current_mass = sat_data.get("mass", 50.0) # Start with 50.0 kg payload fuel [cite: 157]
    projected_mass = current_mass
    
    # 1. Validate Ground Station Line-of-Sight [cite: 185]
    has_los = validate_line_of_sight(sat_data["r"], SIMULATION_STATE["last_updated"])
    if not has_los:
        raise HTTPException(status_code=400, detail="Maneuver rejected: Satellite is in a blackout zone (No LOS).")

    # Process each burn in the sequence
    for burn in payload.maneuver_sequence:
        
        # 2. Validate Maximum Thrust [cite: 159]
        try:
            dv_mag_m_s = validate_thrust(burn.deltaV_vector.dict())
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
        # 3. Validate Thermal Cooldown [cite: 160]
        last_burn = SATELLITE_LAST_BURN.get(sat_id)
        if not check_cooldown(last_burn, burn.burnTime):
            raise HTTPException(status_code=400, detail=f"Maneuver rejected: 600s thermal cooldown active for {sat_id}.")
            
        # 4. Calculate Mass Depletion [cite: 162]
        mass_consumed = calculate_mass_depletion(projected_mass, dv_mag_m_s)
        projected_mass -= mass_consumed
        
        if projected_mass <= 0:
             raise HTTPException(status_code=400, detail="Maneuver rejected: Insufficient fuel.")
             
        # Update cooldown tracker
        SATELLITE_LAST_BURN[sat_id] = burn.burnTime

    # --- INSTANTANEOUS APPLICATION --- [cite: 154]
    # Apply the final Delta V to the state vector and update the actual mass
    final_burn = payload.maneuver_sequence[-1].deltaV_vector
    SIMULATION_STATE["satellites"][sat_id]["v"]["x"] += final_burn.x
    SIMULATION_STATE["satellites"][sat_id]["v"]["y"] += final_burn.y
    SIMULATION_STATE["satellites"][sat_id]["v"]["z"] += final_burn.z
    SIMULATION_STATE["satellites"][sat_id]["mass"] = projected_mass

    return {
    "status": "SCHEDULED",
    "validation": {
        "ground_station_los": True,
        "sufficient_fuel": True,
        "projected_mass_remaining_kg": round(projected_mass + 500.0, 4)
    }
}