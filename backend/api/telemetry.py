import copy
from fastapi import APIRouter, status, BackgroundTasks
from pydantic import BaseModel
from typing import List

from backend.core.state import SIMULATION_STATE
from backend.core.collision import detect_collisions
from backend.core.conjunction_service import run_predictive_ca
from backend.core.evasion_manager import EvasionManager  # <-- NEW IMPORT

router = APIRouter()

# Instantiate the evasion manager globally so it remembers maneuvers between seconds
fleet_evasion_manager = EvasionManager()

# --- PYDANTIC MODELS ---
class Vector3D(BaseModel):
    x: float
    y: float
    z: float

class TelemetryObject(BaseModel):
    id: str
    type: str
    r: Vector3D
    v: Vector3D

class TelemetryPayload(BaseModel):
    timestamp: str
    objects: List[TelemetryObject]

# --- BACKGROUND TASK ---
def process_future_cdms(state_snapshot: dict):
    """
    Runs the heavy 24-hour RK4 propagation in the background.
    Takes a snapshot of the state so incoming live data doesn't corrupt the loop.
    """
    cdms = run_predictive_ca(state_snapshot)
    
    # Save the generated Conjunction Data Messages to the main memory
    SIMULATION_STATE["future_cdms"] = cdms
    
    if cdms:
        print(f"🔮 PREDICTION: {len(cdms)} future collisions detected in the next 24 hours!")


# --- MAIN ENDPOINT ---
@router.post("/telemetry", status_code=status.HTTP_200_OK)
async def ingest_telemetry(payload: TelemetryPayload, background_tasks: BackgroundTasks):
    
    SIMULATION_STATE["last_updated"] = payload.timestamp
    
    # 1. Convert incoming Pydantic payload to standard dictionaries
    raw_objects = []
    for obj in payload.objects:
        raw_objects.append({
            "id": obj.id,
            "type": obj.type.upper(),  # Normalize to uppercase
            "r": obj.r.dict(),
            "v": obj.v.dict(),
            "status": "NOMINAL"
        })

    # 2. Update Memory with REAL data to accurately detect collisions
    for obj in raw_objects:
        if obj["type"] == "SATELLITE":
            SIMULATION_STATE["satellites"][obj["id"]] = obj
        elif obj["type"] == "DEBRIS":
            SIMULATION_STATE["debris"][obj["id"]] = obj

    # 3. IMMEDIATE RADAR: Check for collisions happening right now (Instantly)
    immediate_warnings = detect_collisions(SIMULATION_STATE)
    SIMULATION_STATE["active_warnings"] = immediate_warnings
    
    if immediate_warnings:
        print(f"⚠️ CRITICAL: {len(immediate_warnings)} immediate collisions occurring!")

    # 4. EVASION OVERRIDE: Pass real data through the Evasion Manager
    # It bends the coordinates of any satellite in danger so the UI sees the dodge
    modified_objects = fleet_evasion_manager.process_telemetry(raw_objects, immediate_warnings)

    # 5. Overwrite the state with the visually modified coordinates
    for obj in modified_objects:
        if obj["type"] == "SATELLITE":
            SIMULATION_STATE["satellites"][obj["id"]] = obj

    # 6. FUTURE RADAR: Trigger the 24-hour CA prediction
    # We must deepcopy the state so the background loop has a stable set of numbers
    state_snapshot = copy.deepcopy(SIMULATION_STATE)
    background_tasks.add_task(process_future_cdms, state_snapshot)

    # 7. Respond instantly to keep the data flowing
    return {
        "status": "ACK",
        "processed_count": len(payload.objects),
        "active_cdm_warnings": len(immediate_warnings),
        "prediction_status": "Calculating next 24 hours in background..."
    }