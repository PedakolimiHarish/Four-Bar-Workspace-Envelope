"""
dynamics.py

This module computes VELOCITY and ACCELERATION
from position-time data using numerical differentiation.

This is purely kinematic:
- No forces
- No masses
- No dynamics equations

Input  : Position arrays (x, y) and time array
Output : Velocity (vx, vy) and acceleration (ax, ay)

This module is OS-independent and safe on Windows 11.
"""

import numpy as np


# --------------------------------------------------
# Compute velocity using central difference
# --------------------------------------------------
def compute_velocity(pos, time):
    """
    Computes velocity from position data using
    numerical differentiation.

    Central difference is used for interior points
    Forward/backward difference for boundaries.

    Parameters:
    ----------
    pos : numpy.ndarray
        Position array of shape (N, 2)
        pos[:,0] -> x
        pos[:,1] -> y

    time : numpy.ndarray
        Time array of shape (N,)

    Returns:
    -------
    vel : numpy.ndarray
        Velocity array of shape (N, 2)
    """

    N = len(time)
    vel = np.zeros_like(pos)

    # Forward difference (first point)
    vel[0] = (pos[1] - pos[0]) / (time[1] - time[0])

    # Central difference (interior points)
    for i in range(1, N - 1):
        vel[i] = (pos[i + 1] - pos[i - 1]) / (time[i + 1] - time[i - 1])

    # Backward difference (last point)
    vel[-1] = (pos[-1] - pos[-2]) / (time[-1] - time[-2])

    return vel


# --------------------------------------------------
# Compute acceleration using central difference
# --------------------------------------------------
def compute_acceleration(vel, time):
    """
    Computes acceleration from velocity data
    using numerical differentiation.

    Parameters:
    ----------
    vel : numpy.ndarray
        Velocity array of shape (N, 2)

    time : numpy.ndarray
        Time array of shape (N,)

    Returns:
    -------
    acc : numpy.ndarray
        Acceleration array of shape (N, 2)
    """

    N = len(time)
    acc = np.zeros_like(vel)

    # Forward difference (first point)
    acc[0] = (vel[1] - vel[0]) / (time[1] - time[0])

    # Central difference (interior points)
    for i in range(1, N - 1):
        acc[i] = (vel[i + 1] - vel[i - 1]) / (time[i + 1] - time[i - 1])

    # Backward difference (last point)
    acc[-1] = (vel[-1] - vel[-2]) / (time[-1] - time[-2])

    return acc


# --------------------------------------------------
# Compute full kinematic derivatives
# --------------------------------------------------
def compute_kinematics(pos, time):
    """
    Convenience function that computes both
    velocity and acceleration.

    Parameters:
    ----------
    pos : numpy.ndarray
        Position array (N, 2)

    time : numpy.ndarray
        Time array (N,)

    Returns:
    -------
    kinematics : dict
        Dictionary containing:
        - vx, vy
        - ax, ay
    """

    vel = compute_velocity(pos, time)
    acc = compute_acceleration(vel, time)

    return {
        "vx": vel[:, 0],
        "vy": vel[:, 1],
        "ax": acc[:, 0],
        "ay": acc[:, 1],
    }
