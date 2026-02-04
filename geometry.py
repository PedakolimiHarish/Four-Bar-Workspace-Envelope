"""
geometry.py

This module converts four-bar linkage angles into
actual 2D Cartesian positions.

It contains ONLY geometry.
- No solvers
- No numerical iteration
- No plotting
- No web logic

Input  : Angles (theta2, theta3)
Output : Joint positions (A, B, C, D) and coupler point (P)

Coordinate System:
- Ground link is horizontal
- Left ground joint A is at origin (0, 0)
- Right ground joint D is at (L1, 0)
- Motion is in the XY plane
"""

import numpy as np


# --------------------------------------------------
# Compute joint positions for ONE configuration
# --------------------------------------------------
def joint_positions(theta2, theta3, L1, L2, L3):
    """
    Computes positions of all joints for a single time step.

    Parameters:
    ----------
    theta2 : float
        Input crank angle (radians)

    theta3 : float
        Coupler link angle (radians)

    L1 : float
        Length of fixed (ground) link

    L2 : float
        Length of input link

    L3 : float
        Length of coupler link

    Returns:
    -------
    A, B, C, D : numpy.ndarray
        Cartesian coordinates of joints:
        A -> left ground joint
        B -> input-coupler joint
        C -> coupler-output joint
        D -> right ground joint
    """

    # -------------------------------
    # Ground joints (fixed in space)
    # -------------------------------

    # Left ground joint (origin)
    A = np.array([0.0, 0.0])

    # Right ground joint (on X-axis)
    D = np.array([L1, 0.0])

    # -------------------------------
    # Input link (A -> B)
    # -------------------------------

    # Input link rotates about point A
    # Polar-to-Cartesian conversion
    B = np.array([
        L2 * np.cos(theta2),
        L2 * np.sin(theta2)
    ])

    # -------------------------------
    # Coupler link (B -> C)
    # -------------------------------

    # Coupler link extends from joint B
    # Orientation given by theta3
    C = B + np.array([
        L3 * np.cos(theta3),
        L3 * np.sin(theta3)
    ])

    return A, B, C, D


# --------------------------------------------------
# Compute an arbitrary point on the coupler link
# --------------------------------------------------
def coupler_point(B, theta3, r, phi=0.0):
    """
    Computes a point located on the coupler link.

    This is useful for workspace envelope calculation.

    Parameters:
    ----------
    B : numpy.ndarray
        Position of joint B (input-coupler joint)

    theta3 : float
        Coupler angle (radians)

    r : float
        Distance from joint B along the coupler link

    phi : float, optional
        Angular offset from coupler link direction (radians)

    Returns:
    -------
    P : numpy.ndarray
        Cartesian coordinates of the coupler point
    """

    # Coupler point position relative to joint B
    P = B + np.array([
        r * np.cos(theta3 + phi),
        r * np.sin(theta3 + phi)
    ])

    return P


# --------------------------------------------------
# Compute geometry for the ENTIRE simulation
# --------------------------------------------------
def compute_geometry(data, L1, L2, L3, coupler_ratio=1.0):
    """
    Converts angle arrays into joint position arrays.

    This function is typically called once per simulation
    after kinematic angles are computed.

    Parameters:
    ----------
    data : dict
        Output dictionary from solver.py containing:
        - data["theta2"]
        - data["theta3"]

    L1, L2, L3 : float
        Link lengths (ground, input, coupler)

    coupler_ratio : float, optional
        Location of the coupler point as a fraction of L3
        (1.0 -> point at joint C)

    Returns:
    -------
    geometry : dict
        Dictionary containing position arrays:
        - A : (N, 2)
        - B : (N, 2)
        - C : (N, 2)
        - D : (N, 2)
        - P : (N, 2)  coupler point
    """

    # Lists are used first for efficiency,
    # converted to NumPy arrays at the end
    A_list = []
    B_list = []
    C_list = []
    D_list = []
    P_list = []

    # Loop over every time step
    for theta2, theta3 in zip(data["theta2"], data["theta3"]):

        # Compute joint positions
        A, B, C, D = joint_positions(
            theta2, theta3, L1, L2, L3
        )

        # Compute coupler point position
        # Default is at joint C
        P = coupler_point(
            B,
            theta3,
            r=coupler_ratio * L3,
            phi=0.0
        )

        # Store results
        A_list.append(A)
        B_list.append(B)
        C_list.append(C)
        D_list.append(D)
        P_list.append(P)

    # Convert lists to NumPy arrays
    return {
        "A": np.array(A_list),
        "B": np.array(B_list),
        "C": np.array(C_list),
        "D": np.array(D_list),
        "P": np.array(P_list),
    }
