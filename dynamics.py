"""
dynamics.py

Computes velocity and acceleration from position–time data
using numerical differentiation.

This module performs kinematic post-processing only.
It does not include forces, masses, or dynamic equations.

Input
-----
pos  : position array (N, 2)
time : time array (N)

Output
------
vx, vy : velocity components
ax, ay : acceleration components
"""

import numpy as np


# --------------------------------------------------
# Velocity computation
# --------------------------------------------------

def compute_velocity(pos, time):
    """
    Estimate velocity using finite differences.

    Central difference is used for interior points,
    with forward/backward differences at the boundaries.
    """

    N = len(time)
    vel = np.zeros_like(pos)

    # forward difference at start
    vel[0] = (pos[1] - pos[0]) / (time[1] - time[0])

    # central difference for interior points
    for i in range(1, N - 1):
        vel[i] = (pos[i + 1] - pos[i - 1]) / (time[i + 1] - time[i - 1])

    # backward difference at end
    vel[-1] = (pos[-1] - pos[-2]) / (time[-1] - time[-2])

    return vel


# --------------------------------------------------
# Acceleration computation
# --------------------------------------------------

def compute_acceleration(vel, time):
    """
    Estimate acceleration by differentiating velocity.
    """

    N = len(time)
    acc = np.zeros_like(vel)

    acc[0] = (vel[1] - vel[0]) / (time[1] - time[0])

    for i in range(1, N - 1):
        acc[i] = (vel[i + 1] - vel[i - 1]) / (time[i + 1] - time[i - 1])

    acc[-1] = (vel[-1] - vel[-2]) / (time[-1] - time[-2])

    return acc


# --------------------------------------------------
# Convenience wrapper
# --------------------------------------------------

def compute_kinematics(pos, time):
    """
    Compute velocity and acceleration from position data.
    """

    vel = compute_velocity(pos, time)
    acc = compute_acceleration(vel, time)

    return {
        "vx": vel[:, 0],
        "vy": vel[:, 1],
        "ax": acc[:, 0],
        "ay": acc[:, 1],
    }