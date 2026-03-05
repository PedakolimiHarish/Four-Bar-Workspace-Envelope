"""
geometry.py

This module converts four-bar linkage angles into actual 2D Cartesian positions.

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

# Convert link angles into Cartesian joint coordinates.
# This defines the actual physical geometry of the mechanism.

# --------------------------------------------------
def joint_positions(theta2, theta3, theta4, L1, L2, L3, L4):
    """
    Computes positions of all joints for a single time step.

    Parameters:
    ----------
    theta2 : float
        Input crank angle (radians)

    theta3 : float
        Coupler link angle (radians)

    theta4 : float
        Output link angle (radians)

    L1 : float
        Length of fixed (ground) link

    L2 : float
        Length of input link

    L3 : float
        Length of coupler link

    L4 : float
        Length of output link
        
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

     # --------------------------------
    # Output link (D → C)
    # --------------------------------

    # Instead of computing C from B using theta3,
    # we compute C from D using theta4.
    # This ensures correct output rotation behavior.
    C = D + np.array([
        L4 * np.cos(theta4),
        L4 * np.sin(theta4)
    ])

    return A, B, C, D

# --------------------------------------------------
# Compute a point on the coupler link

# Compute a point located along the coupler link BC.
# Useful for tracking coupler curves or workspace envelopes.

# --------------------------------------------------
def coupler_point(B, C, ratio=1.0):
    """
    Computes a point along the coupler link BC.

    ratio = 1.0 → point at C
    ratio = 0.5 → midpoint
    ratio = 0.0 → point at B
    """

    # Vector from B to C
    BC = C - B

    # Point along BC
    P = B + ratio * BC

    return P

# --------------------------------------------------
# Compute geometry for entire simulation

# Convert the full set of link angles into arrays of joint positions.
# This produces the geometry used for animation and plotting.

# --------------------------------------------------
def compute_geometry(data, L1, L2, L3, L4, coupler_ratio=1.0):
    """
    Converts angle arrays into joint position arrays.

    Parameters:
    ----------
    data : dict
        Contains theta2, theta3, theta4 arrays

    L1, L2, L3, L4 : float
        Link lengths

    coupler_ratio : float
        Location of point along BC (default = 1 → at C)

    Returns:
    -------
    geometry : dict
        Contains arrays:
        A, B, C, D, P
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

        # Compute joint positions
        A, B, C, D = joint_positions(
            theta2, theta3, theta4,
            L1, L2, L3, L4
        )

        # Compute coupler point along BC
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