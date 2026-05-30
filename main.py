# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all the routers we built
from backend.core.evasion_manager import EvasionManager

# Instantiate the manager globally so it remembers state between requests
fleet_evasion_manager = EvasionManager()
from backend.api.telemetry import router as telemetry_router
from backend.api.maneuver import router as maneuver_router
from backend.api.simulate import router as simulate_router
from backend.api.visualization import router as visualization_router
from backend.core.station_loader import load_ground_stations

app = FastAPI(title="Autonomous Constellation Manager (AETHER)")

# Enable CORS for your upcoming Claude-built frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the API Endpoints
app.include_router(telemetry_router, prefix="/api", tags=["Telemetry"])
app.include_router(maneuver_router, prefix="/api", tags=["Maneuver"])
app.include_router(simulate_router, prefix="/api", tags=["Simulation"])
app.include_router(visualization_router, prefix="/api", tags=["Visualization"])

@app.on_event("startup")
async def startup_event():
    print("Initializing Autonomous Constellation Manager...")
    load_ground_stations()
    print("System Ready.")

if __name__ == "__main__":
    import uvicorn
    # Binds to 0.0.0.0 to ensure Docker compatibility
    uvicorn.run(app, host="0.0.0.0", port=8000)