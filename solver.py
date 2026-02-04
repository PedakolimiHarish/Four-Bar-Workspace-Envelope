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
from scipy.optimize import fsolve


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
def solve_four_bar(theta2, L1, L2, L3, L4, prev_solution=None):
    """
    Solves the four-bar linkage for a single input angle.

    Uses numerical root finding (fsolve).

    Parameters:
    ----------
    theta2 : float
        Input crank angle (radians)

    prev_solution : list or None
        Previous [theta3, theta4] solution
        Used to maintain branch consistency

    Returns:
    -------
    theta3, theta4 : float
        Coupler and output angles (radians)
    """

    # Initial guess strategy
    if prev_solution is None:
        # First step: use input angle as rough guess
        guess = [theta2, theta2]
    else:
        # Subsequent steps: use previous solution
        # This prevents jumping between open/crossed configurations
        guess = prev_solution

    # Call nonlinear solver
    solution, info, ier, msg = fsolve(
        four_bar_equations,
        guess,
        args=(theta2, L1, L2, L3, L4),
        full_output=True,
        maxfev=200
    )

    # Check convergence
    if ier != 1:
        # Solver failed (usually near singular positions)
        raise RuntimeError("Four-bar solver did not converge")

    # Return solved angles
    return solution[0], solution[1]


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

    # For branch continuity
    prev_solution = None

    # Start slightly away from zero to avoid toggle singularity
    theta2 = 1e-3
    t = 0.0

    # Sweep input crank angle for one full revolution
    while theta2 <= 2.0 * np.pi:

        try:
            # Solve for coupler and output angles
            theta3, theta4 = solve_four_bar(
                theta2, L1, L2, L3, L4, prev_solution
            )

            # Store solution for next iteration
            prev_solution = [theta3, theta4]

        except RuntimeError:
            # Solver failed (singular position)
            # Skip this step safely
            theta2 += step
            t += dt
            continue

        # Store results
        time_vals.append(t)
        theta2_vals.append(theta2)
        theta3_vals.append(theta3)
        theta4_vals.append(theta4)

        # Increment input angle and time
        theta2 += step
        t += dt

    # Convert lists to NumPy arrays
    return {
        "time": np.array(time_vals),
        "theta2": np.array(theta2_vals),
        "theta3": np.array(theta3_vals),
        "theta4": np.array(theta4_vals),
    }


# --------------------------------------------------
# Standalone test (for debugging and learning)
# --------------------------------------------------
if __name__ == "__main__":
    """
    This block runs only when solver.py is executed directly.
    It is useful for quick validation without web integration.
    """

    data = compute_four_bar(
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
    )
