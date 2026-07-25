from backend.core.evasion_manager import EvasionManager

# This dictionary will act as our server's RAM (Random Access Memory).
# It will hold the latest state vectors for everything in the simulation.

SIMULATION_STATE = {
    "satellites": {},
    "debris": {},
    "active_warnings": [],
    "last_updated": None
}

# Instantiate the manager globally so it remembers state between requests
fleet_evasion_manager = EvasionManager()