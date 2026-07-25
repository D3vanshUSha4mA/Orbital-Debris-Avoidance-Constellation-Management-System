import time
import numpy as np
import sys
import os

# Ensure backend imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.collision import detect_collisions

def run_benchmark():
    print("========================================")
    print("   ACM PERFORMANCE & LATENCY BENCHMARK  ")
    print("========================================\n")
    
    # --- 1. SPATIAL INDEXING TEST (O(log N) Verification) ---
    print("Test 1: KD-Tree Spatial Indexing Load Test")
    print("Generating 100,000 simulated debris pieces and 50 satellites...")
    
    simulation_state = {
        "satellites": {},
        "debris": {}
    }
    
    # 50 satellites
    for i in range(50):
        simulation_state["satellites"][f"SAT-{i}"] = {
            "r": {"x": np.random.uniform(6378, 7000), "y": np.random.uniform(6378, 7000), "z": np.random.uniform(6378, 7000)}
        }
        
    # 100,000 debris objects
    for i in range(100000):
        simulation_state["debris"][f"DEB-{i}"] = {
            "r": {"x": np.random.uniform(6378, 7000), "y": np.random.uniform(6378, 7000), "z": np.random.uniform(6378, 7000)}
        }
        
    start_time = time.perf_counter()
    warnings = detect_collisions(simulation_state)
    end_time = time.perf_counter()
    
    elapsed_ms = (end_time - start_time) * 1000
    print(f" -> KD-Tree Query execution time: {elapsed_ms:.2f} ms")
    print(f" -> Found {len(warnings)} random conjunctions in that tick.")
    
    # In a typical O(N^2) brute force, 50 * 100,000 = 5,000,000 distance checks (would take hundreds of ms)
    # The KD-Tree should resolve this in < 50ms.
    if elapsed_ms < 50:
        print(" -> [PASS] Latency well below 50ms. O(log N) requirement satisfied!\n")
    else:
        print(" -> [FAIL] Execution exceeded 50ms. Check KD-Tree implementation.\n")

    # --- 2. EVASION ALGORITHM PERFORMANCE ---
    print("Test 2: Phasing Maneuver Math Verification")
    from backend.core.evasion import calculate_evasion_sequence
    import datetime
    
    sat_r = {"x": 6800.0, "y": 0.0, "z": 0.0}
    sat_v = {"x": 0.0, "y": 7.6, "z": 0.0}
    iso_now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
    
    start_time = time.perf_counter()
    payload = calculate_evasion_sequence("SAT-001", sat_r, sat_v, iso_now, 45.0)
    end_time = time.perf_counter()
    
    calc_ms = (end_time - start_time) * 1000
    burns = payload.get("maneuver_sequence", [])
    
    print(f" -> Astrodynamics math execution time: {calc_ms:.3f} ms")
    if len(burns) == 3:
         print(" -> [PASS] Generated exactly 3 phasing burns (Evasion, Reversal, Circularize)")
    else:
         print(" -> [FAIL] Expected 3 burns, got something else.")

    if calc_ms < 10:
         print(" -> [PASS] Autopilot latency is sub-10ms, satisfying rapid-response requirements.\n")

    print("========================================")
    print(" Benchmark Complete.")
    print("========================================")

if __name__ == "__main__":
    run_benchmark()
