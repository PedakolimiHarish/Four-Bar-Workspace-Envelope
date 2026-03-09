"""
app.py

Flask backend for the four-bar linkage simulator.

This file connects the web interface to the simulation modules.
It receives user inputs, runs the kinematic solver, and returns
the results to the UI for visualization.

Simulation pipeline
-------------------
User input → solver → geometry → kinematics → workspace analysis
"""

from flask import Flask, render_template, request, jsonify
import numpy as np

from solver import compute_four_bar
from geometry import compute_geometry
from dynamics import compute_kinematics
from linkage_properties import compute_linkage_properties, compute_workspace_area

app = Flask(__name__)


@app.route("/")
def index():
    """Render main interface."""
    return render_template("index.html")


@app.route("/solve", methods=["POST"])
def solve():
    """
    Run the four-bar simulation based on parameters received from the UI.
    """

    try:
        params = request.json

        # Read user inputs
        L1 = float(params["L1"])
        L2 = float(params["L2"])
        L3 = float(params["L3"])
        L4 = float(params["L4"])

        step_deg = float(params.get("step_deg", 2.0))
        rpm = float(params.get("rpm", 90.0))
        driver = int(params.get("driver", 2))

        # First classify the linkage
        properties = compute_linkage_properties(L1, L2, L3, L4, driver=driver)

        if properties["Assembly"] == "Invalid":
            return jsonify({
                "success": False,
                "error": "Invalid linkage: cannot form closed four-bar chain.",
                "properties": properties
            })

        # Rotate links so the solver's internal convention (L2 as driver)
        # matches the driver selected in the UI.
        lengths = [L1, L2, L3, L4]
        shift = (driver - 2) % 4
        rotated = lengths[shift:] + lengths[:shift]

        L1_int, L2_int, L3_int, L4_int = rotated

        # Run kinematic solver
        data = compute_four_bar(
            L1_int,
            L2_int,
            L3_int,
            L4_int,
            step_deg,
            rpm
        )

        # Convert angles to joint coordinates
        geom = compute_geometry(
            data,
            L1_int,
            L2_int,
            L3_int,
            L4_int
        )

        # Workspace area from coupler trajectory
        try:
            workspace_area = compute_workspace_area(geom["P"])
            properties["Workspace Area"] = round(workspace_area, 3)
        except Exception:
            properties["Workspace Area"] = "-"

        # Compute velocity and acceleration of coupler point
        kin = compute_kinematics(
            geom["P"],
            data["time"]
        )

        return jsonify({
            "success": True,

            "time": data["time"].tolist(),

            "A": geom["A"].tolist(),
            "B": geom["B"].tolist(),
            "C": geom["C"].tolist(),
            "D": geom["D"].tolist(),
            "P": geom["P"].tolist(),

            "vx": kin["vx"].tolist(),
            "vy": kin["vy"].tolist(),
            "ax": kin["ax"].tolist(),
            "ay": kin["ay"].tolist(),

            "properties": properties
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(debug=True)