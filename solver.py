"""
solver.py

This module performs the KINEMATIC ANALYSIS of a planar four-bar linkage.

Responsibilities:
- Check Grashof condition
- Solve nonlinear vector-loop equations
- Sweep input crank angle over one full revolution
- Maintain branch consistency (open configuration)
- Handle singular (toggle) positions safely

This file DOES NOT:
- Compute geometry (positions)
- Plot anything
- Handle web or UI logic

Input  : Link lengths + simulation parameters
Output : Time-indexed arrays of link angles
"""

import numpy as np

# --------------------------------------------------
# Grashof condition check
# --------------------------------------------------
def check_grashof(L1, L2, L3, L4):
    """
    Checks whether the given four-bar linkage satisfies
    the Grashof condition.

    Grashof condition:
        shortest + longest <= sum of other two

    If true:
        At least one link can rotate fully.

    Parameters:
    ----------
    L1, L2, L3, L4 : float
        Link lengths

    Returns:
    -------
    bool
        True  -> Grashof mechanism
        False -> Non-Grashof (no full rotation)
    """

    # Sort link lengths from smallest to largest
    links = sorted([L1, L2, L3, L4])

    # Assign shortest, middle, and longest
    s, p, q, l = links

    return (s + l) <= (p + q)

# --------------------------------------------------
# Vector loop equations (nonlinear equations)
# --------------------------------------------------
def four_bar_equations(vars, theta2, L1, L2, L3, L4):
    """
    Defines the vector loop equations for the four-bar linkage.

    Unknowns:
        theta3 -> coupler angle
        theta4 -> output link angle

    Known:
        theta2 -> input crank angle

    These equations come from:
        L2 + L3 = L1 + L4

    resolved in X and Y directions.
    """

    # Unpack unknown variables
    theta3, theta4 = vars

    # X-direction loop equation
    eq1 = (
        L2 * np.cos(theta2)
        + L3 * np.cos(theta3)
        - L1
        - L4 * np.cos(theta4)
    )

    # Y-direction loop equation
    eq2 = (
        L2 * np.sin(theta2)
        + L3 * np.sin(theta3)
        - L4 * np.sin(theta4)
    )

    # fsolve expects equations in the form f(x) = 0
    return [eq1, eq2]

# --------------------------------------------------
# Solve four-bar linkage for ONE input angle
# --------------------------------------------------
def solve_four_bar(theta2, L1, L2, L3, L4, prev_theta4=None):
    # newton-raphson method for solving nonlinear equations

    k1 = L1 / L2
    k2 = L1 / L4
    k3 = (L1**2 + L2**2 - L3**2 + L4**2) / (2 * L2 * L4)

    if abs(L1-L3) < 1e-9 and abs(L2-L4) < 1e-9:
        theta4 = theta2
        
    theta4 = theta2 if prev_theta4 is None else prev_theta4

    tol = 1e-10
    max_iter = 50

    for _ in range(max_iter):

        f = (
            k1 * np.cos(theta4)
            - k2 * np.cos(theta2)
            + k3
            - np.cos(theta4 - theta2)
        )

        df = (
            -k1 * np.sin(theta4)
            + np.sin(theta4 - theta2)
        )

        if abs(df) < 1e-12:
            break

        theta4_new = theta4 - f / df

        if abs(theta4_new - theta4) < tol:
            theta4 = theta4_new
            break

        theta4 = theta4_new

    x = L1 + L4*np.cos(theta4) - L2*np.cos(theta2)
    y = L4*np.sin(theta4) - L2*np.sin(theta2)

    theta3 = np.arctan2(y, x)

    return theta3, theta4

def compute_theta2_limits(L1, L2, L3, L4):

    # Toggle when L3 and L4 align
    term1 = (L1**2 + L2**2 - (L3 + L4)**2) / (2 * L1 * L2)
    term2 = (L1**2 + L2**2 - (L3 - L4)**2) / (2 * L1 * L2)

    # Clip numerical noise
    term1 = np.clip(term1, -1.0, 1.0)
    term2 = np.clip(term2, -1.0, 1.0)

    theta1 = np.arccos(term1)
    theta2 = np.arccos(term2)

    return min(theta1, theta2), max(theta1, theta2)

# --------------------------------------------------
# Main kinematic sweep (entire simulation)
# --------------------------------------------------
def compute_four_bar(
    L1,
    L2,
    L3,
    L4,
    step_deg=2.0,
    rpm=30.0
):
    """
    Computes the full kinematic motion of the four-bar linkage
    over one complete input crank revolution.

    Parameters:
    ----------
    L1, L2, L3, L4 : float
        Link lengths

    step_deg : float
        Input angle step size (degrees)

    rpm : float
        Input crank speed (revolutions per minute)

    Returns:
    -------
    data : dict
        Dictionary containing NumPy arrays:
        - time
        - theta2
        - theta3
        - theta4
    """

    # Validate mechanism type
    if not check_grashof(L1, L2, L3, L4):
        raise ValueError("Grashof condition not satisfied")

    # --------------------------------------------------
    # Detect change-point (singular) mechanism
    # --------------------------------------------------

    links = sorted([L1, L2, L3, L4])
    s, p, q, l = links

    grashof_index = (p + q) - (s + l)

    is_change_point = abs(grashof_index) < 1e-8

    if is_change_point:
        print("WARNING: Change-point mechanism detected.")

        
    # Convert step size to radians
    step = np.deg2rad(step_deg)

    # Convert RPM to angular velocity (rad/s)
    omega = rpm * 2.0 * np.pi / 60.0

    # Time step corresponding to angular step
    dt = step / omega

    # Storage lists (converted to arrays later)
    time_vals = []
    theta2_vals = []
    theta3_vals = []
    theta4_vals = []

    # ----------------------------------------
    # Determine motion type of driver (L2)
    # ----------------------------------------

    links = [L1, L2, L3, L4]
    s = min(links)
    l = max(links)

    # remaining two
    temp = links.copy()
    temp.remove(s)
    temp.remove(l)
    p, q = temp

    grashof = (s + l) <= (p + q)

    # Input is crank ONLY if:
    # 1) Grashof mechanism
    # 2) Driver (L2) is shortest link

    if not grashof:
        input_is_crank = False
    else:
        input_is_crank = abs(L2 - s) < 1e-6 or abs(L1 - s) < 1e-6

    # ----------------------------------------
    # Set theta2 limits
    # ----------------------------------------
    if input_is_crank:
        theta2_min = 0.0
        theta2_max = 2.0 * np.pi
    else:
        theta_a, theta_b = compute_theta2_limits(L1, L2, L3, L4)
        theta2_min = min(theta_a, theta_b)
        theta2_max = max(theta_a, theta_b)

    t = 0.0
    # Initialize continuity variable
    prev_theta4 = None

    # -----------------------------------------
    # Forward sweep
    # -----------------------------------------
    theta2 = theta2_min + 1e-4

    while theta2 <= theta2_max:

        try:
            theta3, theta4 = solve_four_bar(
                theta2,
                L1, L2, L3, L4,
                prev_theta4
            )

            #theta4 = np.arctan2(np.sin(theta4), np.cos(theta4))
            prev_theta4 = theta4

        except RuntimeError:
            break

        time_vals.append(t)
        theta2_vals.append(theta2)
        theta3_vals.append(theta3)
        theta4_vals.append(theta4)

        theta2 += step
        t += dt

    # -----------------------------------------
    # Backward sweep (rocker only)
    # -----------------------------------------
    if not input_is_crank:

        theta2 = theta2_max - step

        while theta2 >= theta2_min:

            try:
                theta3, theta4 = solve_four_bar(
                    theta2,
                    L1, L2, L3, L4,
                    prev_theta4
                )

                #theta4 = np.arctan2(np.sin(theta4), np.cos(theta4))
                prev_theta4 = theta4

            except RuntimeError:
                break

            time_vals.append(t)
            theta2_vals.append(theta2)
            theta3_vals.append(theta3)
            theta4_vals.append(theta4)

            theta2 -= step
            t += dt

    # -----------------------------------------
    # Convert and unwrap
    # -----------------------------------------
    theta2_array = np.array(theta2_vals)
    theta3_array = np.array(theta3_vals)
    # theta4_array = np.unwrap(np.array(theta4_vals))
    theta4_array = np.array(theta4_vals)

    print("L1, L2, L3, L4:", L1, L2, L3, L4)
    print("theta4 min/max:", theta4_array.min(), theta4_array.max())
    print("theta4 total rotation:", theta4_array[-1] - theta4_array[0])
    print("Shortest link:", s)
    print("Input is crank:", input_is_crank)

    return {
        "time": np.array(time_vals),
        "theta2": theta2_array,
        "theta3": theta3_array,
        "theta4": theta4_array,
        "is_change_point": is_change_point
    }
    
# --------------------------------------------------
# Standalone test (for debugging and learning)
# --------------------------------------------------
if __name__ == "__main__":
    """
    This block runs only when solver.py is executed directly.
    It is useful for quick validation without web integration.
    """

    """ data = compute_four_bar(
        L1=1.0,
        L2=0.3,
        L3=0.9,
        L4=0.8,
        step_deg=2.0,
        rpm=30.0
    )

    print("Number of steps:", len(data["theta2"]))
    print(
        "Input angle range (deg):",
        np.rad2deg([data["theta2"][0], data["theta2"][-1]])
    ) """
