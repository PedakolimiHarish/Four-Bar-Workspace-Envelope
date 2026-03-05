"""
dynamics.py

This module computes VELOCITY and ACCELERATION
from position-time data using numerical differentiation.

Important:
Despite the file name "dynamics", this module performs
purely KINEMATIC calculations.

That means it does NOT consider:
- forces
- masses
- torques
- energy
- equations of motion

Instead, it simply differentiates position data with
respect to time.

Input:
    Position array (x, y) for a point over time
    Time array corresponding to each position

Output:
    Velocity components (vx, vy)
    Acceleration components (ax, ay)

These results are typically used for analyzing
coupler-point motion in mechanism simulations.
"""

import numpy as np


# --------------------------------------------------
# Compute velocity using numerical differentiation
#
# Velocity is the time derivative of position:
#
#     v = dx/dt
#
# Since the simulator produces discrete time samples,
# the derivative is approximated using finite differences.
#
# The method used here is:
#
#  • Forward difference for the first point
#  • Central difference for interior points
#  • Backward difference for the final point
#
# Central difference is used whenever possible because
# it provides better numerical accuracy than forward
# or backward difference methods.
# --------------------------------------------------
def compute_velocity(pos, time):
    """
    Computes velocity from position data using
    numerical differentiation.

    Central difference is used for interior points
    Forward/backward difference for boundaries.

    Parameters
    ----------
    pos : numpy.ndarray
        Position array of shape (N, 2)

        pos[:,0] → x coordinate
        pos[:,1] → y coordinate

        Each row corresponds to the position of a point
        at a given time step.

    time : numpy.ndarray
        Time array of shape (N,)

        Each entry represents the time associated
        with the corresponding position sample.

    Returns
    -------
    vel : numpy.ndarray
        Velocity array of shape (N, 2)

        vel[:,0] → vx (x velocity)
        vel[:,1] → vy (y velocity)
    """

    # Total number of time samples
    N = len(time)

    # Create output array for velocity
    vel = np.zeros_like(pos)

    # --------------------------------------------------
    # Forward difference (first sample)
    #
    # v₀ ≈ (x₁ - x₀) / (t₁ - t₀)
    #
    # Only forward information is available at the
    # beginning of the dataset.
    # --------------------------------------------------
    vel[0] = (pos[1] - pos[0]) / (time[1] - time[0])

    # --------------------------------------------------
    # Central difference (interior points)
    #
    # vᵢ ≈ (xᵢ₊₁ - xᵢ₋₁) / (tᵢ₊₁ - tᵢ₋₁)
    #
    # This method uses both neighboring points
    # and provides a better approximation of the
    # derivative.
    # --------------------------------------------------
    for i in range(1, N - 1):
        vel[i] = (pos[i + 1] - pos[i - 1]) / (time[i + 1] - time[i - 1])

    # --------------------------------------------------
    # Backward difference (final sample)
    #
    # vₙ ≈ (xₙ - xₙ₋₁) / (tₙ - tₙ₋₁)
    #
    # Only previous information is available at
    # the end of the dataset.
    # --------------------------------------------------
    vel[-1] = (pos[-1] - pos[-2]) / (time[-1] - time[-2])

    return vel


# --------------------------------------------------
# Compute acceleration using numerical differentiation
#
# Acceleration is the time derivative of velocity:
#
#     a = dv/dt
#
# Since velocity is already discretized, the same
# finite difference approach is applied again.
#
# The same scheme is used:
#
#  • Forward difference at start
#  • Central difference for interior points
#  • Backward difference at end
# --------------------------------------------------
def compute_acceleration(vel, time):
    """
    Computes acceleration from velocity data
    using numerical differentiation.

    Parameters
    ----------
    vel : numpy.ndarray
        Velocity array of shape (N, 2)

        vel[:,0] → vx
        vel[:,1] → vy

    time : numpy.ndarray
        Time array of shape (N,)

    Returns
    -------
    acc : numpy.ndarray
        Acceleration array of shape (N, 2)

        acc[:,0] → ax
        acc[:,1] → ay
    """

    # Number of time samples
    N = len(time)

    # Output acceleration array
    acc = np.zeros_like(vel)

    # --------------------------------------------------
    # Forward difference (first point)
    # --------------------------------------------------
    acc[0] = (vel[1] - vel[0]) / (time[1] - time[0])

    # --------------------------------------------------
    # Central difference (interior points)
    # --------------------------------------------------
    for i in range(1, N - 1):
        acc[i] = (vel[i + 1] - vel[i - 1]) / (time[i + 1] - time[i - 1])

    # --------------------------------------------------
    # Backward difference (final point)
    # --------------------------------------------------
    acc[-1] = (vel[-1] - vel[-2]) / (time[-1] - time[-2])

    return acc


# --------------------------------------------------
# Compute full kinematic derivatives
#
# This is a convenience wrapper that performs both
# velocity and acceleration calculations.
#
# Instead of calling two separate functions,
# the solver can call this single function.
#
# It returns the velocity and acceleration
# components as separate arrays for easy plotting
# and analysis.
# --------------------------------------------------
def compute_kinematics(pos, time):
    """
    Convenience function that computes both
    velocity and acceleration.

    Parameters
    ----------
    pos : numpy.ndarray
        Position array of shape (N, 2)

    time : numpy.ndarray
        Time array of shape (N,)

    Returns
    -------
    kinematics : dict
        Dictionary containing:

        vx → x velocity
        vy → y velocity
        ax → x acceleration
        ay → y acceleration
    """

    # Compute velocity from position data
    vel = compute_velocity(pos, time)

    # Compute acceleration from velocity data
    acc = compute_acceleration(vel, time)

    # Return components separately for convenience
    return {
        "vx": vel[:, 0],
        "vy": vel[:, 1],
        "ax": acc[:, 0],
        "ay": acc[:, 1],
    }