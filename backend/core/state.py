# This dictionary will act as our server's RAM (Random Access Memory).
# It will hold the latest state vectors for everything in the simulation.

SIMULATION_STATE = {
    "satellites": {},
    "debris": {},
    "active_warnings": [],
    "last_updated": None
}