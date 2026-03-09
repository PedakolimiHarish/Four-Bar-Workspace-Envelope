"""
geometry.py

Converts four-bar linkage angles into Cartesian joint positions.

This module handles geometry only.
It does not perform solving, numerical iteration, or plotting.

Inputs
------
theta2, theta3, theta4 : link angles (radians)
L1, L2, L3, L4         : link lengths

Outputs
-------
Joint coordinates A, B, C, D and a coupler point P.

Coordinate system
-----------------
A = (0, 0)
D = (L1, 0)
Ground link is horizontal.
"""

import numpy as np


# --------------------------------------------------
# Joint positions for one configuration
# --------------------------------------------------

def joint_positions(theta2, theta3, theta4, L1, L2, L3, L4):
    """
    Compute joint coordinates for a single mechanism state.
    """

    # Ground joints
    A = np.array([0.0, 0.0])
    D = np.array([L1, 0.0])

    # Input crank position
    B = np.array([
        L2 * np.cos(theta2),
        L2 * np.sin(theta2)
    ])

    # Distance between B and D
    dx = D[0] - B[0]
    dy = D[1] - B[1]
    d = np.sqrt(dx**2 + dy**2)

    # Solve triangle B-C-D
    a = (L3**2 - L4**2 + d**2) / (2 * d)
    h_sq = L3**2 - a**2
    h = np.sqrt(max(h_sq, 0))

    xm = B[0] + a * dx / d
    ym = B[1] + a * dy / d

    # Two possible intersection points for C
    xs1 = xm + h * (-dy) / d
    ys1 = ym + h * dx / d

    xs2 = xm - h * (-dy) / d
    ys2 = ym - h * dx / d

    # Choose the solution closest to the solver's predicted position
    C_guess = D + np.array([
        L4 * np.cos(theta4),
        L4 * np.sin(theta4)
    ])

    if np.linalg.norm([xs1 - C_guess[0], ys1 - C_guess[1]]) < \
       np.linalg.norm([xs2 - C_guess[0], ys2 - C_guess[1]]):
        C = np.array([xs1, ys1])
    else:
        C = np.array([xs2, ys2])

    return A, B, C, D


# --------------------------------------------------
# Point on the coupler link
# --------------------------------------------------

def coupler_point(B, C, ratio=1.0):
    """
    Returns a point along the coupler BC.

    ratio = 0 → B
    ratio = 1 → C
    """

    BC = C - B
    return B + ratio * BC


# --------------------------------------------------
# Convert simulation angles to geometry arrays
# --------------------------------------------------

def compute_geometry(data, L1, L2, L3, L4, coupler_ratio=1.0):
    """
    Generate joint coordinate arrays for the full simulation.
    """

    A_list = []
    B_list = []
    C_list = []
    D_list = []
    P_list = []

    for theta2, theta3, theta4 in zip(
        data["theta2"],
        data["theta3"],
        data["theta4"]
    ):

        A, B, C, D = joint_positions(
            theta2, theta3, theta4,
            L1, L2, L3, L4
        )

        P = coupler_point(B, C, ratio=coupler_ratio)

        A_list.append(A)
        B_list.append(B)
        C_list.append(C)
        D_list.append(D)
        P_list.append(P)

    return {
        "A": np.array(A_list),
        "B": np.array(B_list),
        "C": np.array(C_list),
        "D": np.array(D_list),
        "P": np.array(P_list),
    }