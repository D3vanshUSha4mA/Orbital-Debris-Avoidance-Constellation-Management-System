import numpy as np

# --- STRICT CONSTANTS DEFINED BY THE HACKATHON ---
MU = 398600.4418           # Earth's standard gravitational parameter (km^3/s^2) [cite: 65]
R_E = 6378.137             # Earth equatorial radius (km) [cite: 67]
J2 = 1.08263e-3            # J2 Perturbation constant [cite: 67]

def calculate_acceleration(r_vec: np.ndarray) -> np.ndarray:
    """
    Calculates the total acceleration vector (Keplerian gravity + J2 Perturbation).
    r_vec is a 3D position vector [x, y, z] in km.
    """
    x, y, z = r_vec[0], r_vec[1], r_vec[2]
    r_mag = np.linalg.norm(r_vec)
    
    # 1. Standard Two-Body Gravity Acceleration [cite: 64]
    a_gravity = -(MU / (r_mag**3)) * r_vec
    
    # 2. J2 Perturbation Acceleration [cite: 66]
    # Using the standard Cartesian expansion of the J2 potential
    z2_over_r2 = (z / r_mag)**2
    j2_coeff = (1.5 * J2 * MU * (R_E**2)) / (r_mag**5)
    
    a_j2 = np.zeros(3)
    a_j2[0] = j2_coeff * x * (5 * z2_over_r2 - 1)
    a_j2[1] = j2_coeff * y * (5 * z2_over_r2 - 1)
    a_j2[2] = j2_coeff * z * (5 * z2_over_r2 - 3)
    
    # Total acceleration
    return a_gravity + a_j2

def rk4_step(r_vec: np.ndarray, v_vec: np.ndarray, dt_seconds: float):
    """
    Propagates the state vector forward by dt_seconds using 
    Runge-Kutta 4th Order numerical integration[cite: 67].
    """
    # k1 
    k1_v = calculate_acceleration(r_vec)
    k1_r = v_vec
    
    # k2
    k2_v = calculate_acceleration(r_vec + 0.5 * dt_seconds * k1_r)
    k2_r = v_vec + 0.5 * dt_seconds * k1_v
    
    # k3
    k3_v = calculate_acceleration(r_vec + 0.5 * dt_seconds * k2_r)
    k3_r = v_vec + 0.5 * dt_seconds * k2_v
    
    # k4
    k4_v = calculate_acceleration(r_vec + dt_seconds * k3_r)
    k4_r = v_vec + dt_seconds * k3_v
    
    # Calculate next state
    r_next = r_vec + (dt_seconds / 6.0) * (k1_r + 2*k2_r + 2*k3_r + k4_r)
    v_next = v_vec + (dt_seconds / 6.0) * (k1_v + 2*k2_v + 2*k3_v + k4_v)
    
    return r_next, v_next