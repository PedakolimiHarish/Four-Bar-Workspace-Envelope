"""
solver.py

Kinematic solver for a planar four-bar linkage.

Inputs
------
L1, L2, L3, L4 : link lengths
step_deg       : input angle step size
rpm            : crank speed

Outputs
-------
time, theta2, theta3, theta4 arrays
"""

import numpy as np


# --------------------------------------------------
# Basic assembly check
# --------------------------------------------------

def check_assembly(L1, L2, L3, L4):
    """
    Verifies that the links can form a closed chain.
    """
    longest = max(L1, L2, L3, L4)
    return longest < (L1 + L2 + L3 + L4 - longest)


# --------------------------------------------------
# Solve linkage for one input angle
# --------------------------------------------------

def solve_four_bar(theta2, L1, L2, L3, L4, prev_theta4=None):
    """
    Computes theta3 and theta4 for a given input angle.
    Uses Newton–Raphson on the Freudenstein equation.
    """

    # Parallelogram case has a direct analytical solution
    if abs(L1 - L3) < 1e-9 and abs(L2 - L4) < 1e-9:
        return theta2, theta2

    # Freudenstein constants
    k1 = L1 / L2
    k2 = L1 / L4
    k3 = (L1**2 + L2**2 - L3**2 + L4**2) / (2 * L2 * L4)

    # First step needs a guess.
    # After that we reuse the previous solution to stay on the same branch.
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

        # Near toggle positions df becomes very small.
        # Newton step would explode, so we stop iterating.
        if abs(df) < 1e-12:
            break

        step = -f / df

        # Limit the update step so Newton does not jump branches
        step = np.clip(step, -0.25, 0.25)

        theta4_new = theta4 + step

        # Simple continuity guard to prevent sudden branch flips
        if prev_theta4 is not None:
            if abs(theta4_new - prev_theta4) > 0.8:
                theta4_new = prev_theta4

        if abs(theta4_new - theta4) < tol:
            theta4 = theta4_new
            break

        theta4 = theta4_new

    # Once theta4 is known we can compute theta3 from geometry
    x = L1 + L4*np.cos(theta4) - L2*np.cos(theta2)
    y = L4*np.sin(theta4) - L2*np.sin(theta2)

    theta3 = np.arctan2(y, x)

    return theta3, theta4


# --------------------------------------------------
# Find feasible theta2 range (rocker mechanisms)
# --------------------------------------------------

def compute_theta2_limits(L1, L2, L3, L4):
    """
    Finds the range of input angles where the linkage can assemble.
    Done by scanning and checking triangle feasibility.
    """

    theta_scan = np.linspace(0, 2*np.pi, 2000)

    valid = []

    for theta2 in theta_scan:

        Bx = L2 * np.cos(theta2)
        By = L2 * np.sin(theta2)

        BD = np.sqrt((L1 - Bx)**2 + By**2)

        # Triangle inequality for triangle B-C-D
        if abs(L3 - L4) <= BD <= (L3 + L4):
            valid.append(theta2)

    if not valid:
        raise ValueError("No valid configuration found")

    valid = np.array(valid)

    # Detect if the valid region splits into two arcs
    gaps = np.where(np.diff(valid) > 0.05)[0]

    if len(gaps) == 0:
        return valid.min(), valid.max()

    start = valid[0]
    end = valid[gaps[0]]

    return start, end


# --------------------------------------------------
# Main simulation routine
# --------------------------------------------------

def compute_four_bar(L1, L2, L3, L4, step_deg=2.0, rpm=30.0):
    """
    Sweeps the input angle and computes the linkage motion.
    """

    if not check_assembly(L1, L2, L3, L4):
        raise ValueError("Invalid linkage: cannot assemble")

    step = np.deg2rad(step_deg)
    omega = rpm * 2*np.pi / 60
    dt = step / omega

    time_vals = []
    theta2_vals = []
    theta3_vals = []
    theta4_vals = []

    links = [L1, L2, L3, L4]

    s = min(links)
    l = max(links)

    temp = links.copy()
    temp.remove(s)
    temp.remove(l)

    p, q = temp

    # Standard Grashof condition
    grashof = (s + l) <= (p + q)

    # Input can rotate fully only if driver or ground is shortest
    if not grashof:
        input_is_crank = False
    else:
        input_is_crank = abs(L2 - s) < 1e-6 or abs(L1 - s) < 1e-6

    # Choose input angle sweep limits
    if input_is_crank:
        theta2_min = 0.0
        theta2_max = 2*np.pi
    else:
        theta_a, theta_b = compute_theta2_limits(L1, L2, L3, L4)
        theta2_min = min(theta_a, theta_b)
        theta2_max = max(theta_a, theta_b)

    t = 0
    prev_theta4 = None

    # Avoid starting exactly at the singular limit
    theta2 = theta2_min + 1e-4

    # Forward sweep
    while theta2 <= theta2_max:

        theta3, theta4 = solve_four_bar(
            theta2,
            L1, L2, L3, L4,
            prev_theta4
        )

        prev_theta4 = theta4

        time_vals.append(t)
        theta2_vals.append(theta2)
        theta3_vals.append(theta3)
        theta4_vals.append(theta4)

        theta2 += step
        t += dt

    # For rocker mechanisms we sweep back to complete the cycle
    if not input_is_crank:

        theta2 = theta2_max - step

        while theta2 >= theta2_min:

            theta3, theta4 = solve_four_bar(
                theta2,
                L1, L2, L3, L4,
                prev_theta4
            )

            prev_theta4 = theta4

            time_vals.append(t)
            theta2_vals.append(theta2)
            theta3_vals.append(theta3)
            theta4_vals.append(theta4)

            theta2 -= step
            t += dt

    theta2_array = np.array(theta2_vals)
    theta3_array = np.array(theta3_vals)
    theta4_array = np.array(theta4_vals)

    """ print("L1 L2 L3 L4:", L1, L2, L3, L4)
    print("theta4 range:", theta4_array.min(), theta4_array.max())
    print("rotation:", theta4_array[-1] - theta4_array[0])
    print("shortest link:", s)
    print("input is crank:", input_is_crank) """

    return {
        "time": np.array(time_vals),
        "theta2": theta2_array,
        "theta3": theta3_array,
        "theta4": theta4_array
    }