"""
solver.py

This module performs the KINEMATIC ANALYSIS of a planar four-bar linkage.

The solver computes the motion of the mechanism by determining the
link angles for each step of the simulation.

Key responsibilities of this module:

1. Solve the four-bar loop closure using the Freudenstein equation
2. Use Newton–Raphson iteration to compute the output link angle
3. Sweep the input angle through its allowable motion range
4. Maintain configuration continuity using the previous solution
5. Detect singular (change-point / toggle) mechanisms

Important:
This module works purely with link ANGLES.

It does NOT:
- compute joint positions
- compute velocities or accelerations
- plot or animate the mechanism
- interact with the web interface

Input:
    Link lengths (L1, L2, L3, L4)
    Simulation parameters (step size, RPM)

Output:
    Time-indexed arrays of link angles:
        theta2  → input link
        theta3  → coupler
        theta4  → output link
"""

import numpy as np


# --------------------------------------------------
# Solve four-bar linkage for ONE input angle
# --------------------------------------------------
#
# This function computes the unknown angles of the
# coupler (theta3) and output link (theta4) when
# the input angle (theta2) is known.
#
# Instead of solving the full vector loop equations,
# the solver uses the Freudenstein equation, which
# eliminates theta3 and reduces the problem to a
# single nonlinear equation in theta4.
#
# Newton–Raphson iteration is used to solve the
# equation numerically.
#
# The previous solution of theta4 is used as the
# initial guess to maintain branch continuity during
# the simulation sweep.
# --------------------------------------------------

def solve_four_bar(theta2, L1, L2, L3, L4, prev_theta4=None):

    # --------------------------------------------------
    # Special case: Parallelogram linkage
    #
    # If opposite links are equal, the mechanism forms
    # a parallelogram. In this case the input and output
    # links remain parallel and their angles are equal.
    #
    # This configuration has an analytical solution.
    # --------------------------------------------------
    if abs(L1 - L3) < 1e-9 and abs(L2 - L4) < 1e-9:
        theta4 = theta2
        theta3 = theta2
        return theta3, theta4

    # --------------------------------------------------
    # Freudenstein equation constants
    #
    # The Freudenstein equation relates the input and
    # output angles of a four-bar linkage:
    #
    # k1 cos(theta4) − k2 cos(theta2) + k3 − cos(theta4 − theta2) = 0
    #
    # These constants simplify the expression.
    # --------------------------------------------------
    k1 = L1 / L2
    k2 = L1 / L4
    k3 = (L1**2 + L2**2 - L3**2 + L4**2) / (2 * L2 * L4)

    # --------------------------------------------------
    # Initial guess for Newton iteration
    #
    # If this is the first step, use theta2 as the guess.
    # Otherwise use the previous solution to maintain
    # configuration continuity (continuation method).
    # --------------------------------------------------
    theta4 = theta2 if prev_theta4 is None else prev_theta4

    tol = 1e-10       # convergence tolerance
    max_iter = 50     # maximum Newton iterations

    # --------------------------------------------------
    # Newton–Raphson iteration
    #
    # θ_new = θ − f(θ) / f'(θ)
    #
    # Iteratively improves the estimate of theta4
    # until the solution converges.
    # --------------------------------------------------
    for _ in range(max_iter):

        # Freudenstein equation
        f = (
            k1 * np.cos(theta4)
            - k2 * np.cos(theta2)
            + k3
            - np.cos(theta4 - theta2)
        )

        # Derivative of Freudenstein equation
        df = (
            -k1 * np.sin(theta4)
            + np.sin(theta4 - theta2)
        )

        # Avoid division by zero near singularity
        if abs(df) < 1e-12:
            break

        # Newton update step
        theta4_new = theta4 - f / df

        # Check convergence
        if abs(theta4_new - theta4) < tol:
            theta4 = theta4_new
            break

        theta4 = theta4_new

    # --------------------------------------------------
    # Compute coupler angle (theta3)
    #
    # Once theta4 is known, theta3 can be obtained
    # geometrically from the loop equation.
    #
    # Vector form:
    # L2 + L3 = L1 + L4
    # --------------------------------------------------
    x = L1 + L4*np.cos(theta4) - L2*np.cos(theta2)
    y = L4*np.sin(theta4) - L2*np.sin(theta2)

    theta3 = np.arctan2(y, x)

    return theta3, theta4


# --------------------------------------------------
# Compute allowable input angle limits
# --------------------------------------------------
#
# Non-Grashof mechanisms cannot rotate fully.
# Their motion is limited by toggle configurations
# where three joints become collinear.
#
# These limits are determined using the law of
# cosines applied to the four-bar geometry.
# --------------------------------------------------

def compute_theta2_limits(L1, L2, L3, L4):

    # --------------------------------------------------
    # Assembly validity check
    #
    # A four-bar linkage cannot exist if the largest
    # link is longer than the sum of the other three.
    # --------------------------------------------------
    if max(L1, L2, L3, L4) > (L1 + L2 + L3 + L4 - max(L1, L2, L3, L4)):
        raise ValueError("Invalid linkage: cannot form closed four-bar chain.")

    # --------------------------------------------------
    # Compute toggle positions using law of cosines
    # --------------------------------------------------
    term1 = (L1**2 + L2**2 - (L3 + L4)**2) / (2 * L1 * L2)
    term2 = (L1**2 + L2**2 - (L3 - L4)**2) / (2 * L1 * L2)

    # Clip to valid acos range
    term1 = np.clip(term1, -1.0, 1.0)
    term2 = np.clip(term2, -1.0, 1.0)

    theta1 = np.arccos(term1)
    theta2 = np.arccos(term2)

    theta_limit = max(theta1, theta2)

    return -theta_limit, +theta_limit


# --------------------------------------------------
# Main simulation routine
# --------------------------------------------------
#
# Performs a full kinematic simulation of the
# four-bar linkage.
#
# Steps:
# 1) Detect change-point mechanism
# 2) Determine allowable input motion
# 3) Sweep the input angle
# 4) Solve linkage configuration each step
# 5) Store time and angle history
# --------------------------------------------------

def compute_four_bar(L1, L2, L3, L4, step_deg=2.0, rpm=30.0):

    # --------------------------------------------------
    # Detect change-point mechanism
    #
    # Occurs when:
    # shortest + longest = other two
    #
    # At this condition the mechanism passes through
    # a singular configuration where branches merge.
    # --------------------------------------------------
    links = sorted([L1, L2, L3, L4])
    s, p, q, l = links

    grashof_index = (p + q) - (s + l)

    is_change_point = abs(grashof_index) < 1e-8

    if is_change_point:
        print("WARNING: Change-point mechanism detected.")

    # --------------------------------------------------
    # Convert simulation parameters
    # --------------------------------------------------
    step = np.deg2rad(step_deg)             # input step size
    omega = rpm * 2.0 * np.pi / 60.0        # rad/s
    dt = step / omega                       # time step

    # Storage arrays
    time_vals = []
    theta2_vals = []
    theta3_vals = []
    theta4_vals = []

    # --------------------------------------------------
    # Determine if input link is a crank
    # --------------------------------------------------
    links = [L1, L2, L3, L4]

    s = min(links)
    l = max(links)

    temp = links.copy()
    temp.remove(s)
    temp.remove(l)
    p, q = temp

    grashof = (s + l) <= (p + q)

    if not grashof:
        input_is_crank = False
    else:
        input_is_crank = abs(L2 - s) < 1e-6 or abs(L1 - s) < 1e-6

    # --------------------------------------------------
    # Set input motion limits
    # --------------------------------------------------
    if input_is_crank:
        theta2_min = 0.0
        theta2_max = 2.0 * np.pi
    else:
        theta_a, theta_b = compute_theta2_limits(L1, L2, L3, L4)
        theta2_min = min(theta_a, theta_b)
        theta2_max = max(theta_a, theta_b)

    # Simulation time
    t = 0.0

    prev_theta4 = None

    # --------------------------------------------------
    # Forward sweep
    # --------------------------------------------------
    theta2 = theta2_min + 1e-4

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

    # --------------------------------------------------
    # Backward sweep (for rocker mechanisms)
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Convert results to numpy arrays
    # --------------------------------------------------
    theta2_array = np.array(theta2_vals)
    theta3_array = np.array(theta3_vals)
    theta4_array = np.array(theta4_vals)

    return {
        "time": np.array(time_vals),
        "theta2": theta2_array,
        "theta3": theta3_array,
        "theta4": theta4_array,
        "is_change_point": is_change_point
    }