"""
linkage_properties.py

Utility functions for analyzing a four-bar linkage.

This module does NOT solve the mechanism motion.  
Instead it provides high-level properties of the linkage such as:

- Assembly validity
- Grashof classification
- Mechanism type (crank-rocker, double crank, etc.)
- Input/output motion type
- Workspace area of the coupler trajectory

The workspace area is computed from the convex hull of the coupler
point path generated during simulation.
"""

from scipy.spatial import ConvexHull
import numpy as np


def compute_workspace_area(points):
    """
    Compute workspace area from a set of trajectory points.

    The convex hull is used so the outer reachable region is measured
    even if the trajectory crosses itself.
    """

    if len(points) < 3:
        return 0.0

    hull = ConvexHull(points)

    # In 2D scipy stores the area in the "volume" field
    return hull.volume


def compute_linkage_properties(L1, L2, L3, L4, driver=2, geometry=None):
    """
    Classify the linkage and optionally compute workspace area.
    """

    # Rotate links so the solver's internal convention (L2 as driver)
    # matches the driver selected in the UI.
    links = [L1, L2, L3, L4]
    shift = (driver - 2) % 4
    links = links[shift:] + links[:shift]

    L1, L2, L3, L4 = links

    tol = 1e-6
    links = [L1, L2, L3, L4]

    # Basic assembly check
    if max(links) > sum(links) - max(links):
        return {
            "Assembly": "Invalid",
            "Grashof Class": "-",
            "Mechanism Type": "Cannot Assemble",
            "Input Type": "-",
            "Output Type": "-"
        }

    # Detect symmetric special cases
    special = None

    if abs(L1 - L3) < tol and abs(L2 - L4) < tol:
        special = "Parallelogram"

    elif abs(L1 - L2) < tol and abs(L3 - L4) < tol:
        special = "Kite Linkage"

    elif abs(L1 - L4) < tol and abs(L2 - L3) < tol:
        special = "Rhomboid (Galloway)"

    # Grashof classification
    s = min(links)
    l = max(links)

    temp = links.copy()
    temp.remove(s)
    temp.remove(l)
    p, q = temp

    GI = (p + q) - (s + l)

    if GI > tol:
        grashof_class = "Grashof"
    elif GI < -tol:
        grashof_class = "Non-Grashof"
    else:
        grashof_class = "Change-Point"

    mechanism = "-"
    input_type = "-"
    output_type = "-"

    if special:
        mechanism = special
        input_type = "Crank"
        output_type = "Crank"

    elif grashof_class == "Non-Grashof":
        mechanism = "Double Rocker"
        input_type = "Rocker"
        output_type = "Rocker"

    else:
        # Mechanism type depends on which link is shortest
        if abs(L1 - s) < tol:
            mechanism = "Double Crank"
            input_type = "Crank"
            output_type = "Crank"

        elif abs(L2 - s) < tol:
            mechanism = "Crank-Rocker"
            input_type = "Crank"
            output_type = "Rocker"

        elif abs(L4 - s) < tol:
            mechanism = "Rocker-Crank"
            input_type = "Rocker"
            output_type = "Crank"

        else:
            mechanism = "Double Rocker"
            input_type = "Rocker"
            output_type = "Rocker"

        if grashof_class == "Change-Point":
            mechanism += " (Change-Point)"

    # Compute workspace area if geometry data is provided
    workspace_area = "-"

    if geometry is not None:
        try:
            workspace_area = round(
                compute_workspace_area(geometry["P"]), 3
            )
        except Exception:
            workspace_area = "-"

    return {
        "Assembly": "Valid",
        "Grashof Class": grashof_class,
        "Mechanism Type": mechanism,
        "Input Type": input_type,
        "Output Type": output_type,
        "Workspace Area": workspace_area
    }