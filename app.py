# --------------------------------------------------
# app.py
#
# This file implements the backend web server for the
# four-bar linkage simulator using Flask.
#
# Responsibilities of this file:
# • Receive user inputs from the web interface
# • Validate linkage parameters
# • Call the simulation modules
# • Return simulation results to the frontend
#
# This file acts as the **controller layer** that
# connects the frontend UI with the numerical solver.
#
# Simulation pipeline executed here:
#
#   User Input (UI)
#        ↓
#   Linkage Classification
#        ↓
#   Kinematic Solver
#        ↓
#   Geometry Calculation
#        ↓
#   Velocity & Acceleration
#        ↓
#   JSON Response to UI
# --------------------------------------------------

from flask import Flask, render_template, request, jsonify
import numpy as np

# Import core simulation modules
from solver import compute_four_bar
from geometry import compute_geometry
from dynamics import compute_kinematics
from linkage_properties import compute_linkage_properties


# --------------------------------------------------
# Create Flask application instance
#
# This object represents the web application and
# manages routing, request handling, and responses.
# --------------------------------------------------
app = Flask(__name__)


# --------------------------------------------------
# Main page route
#
# When a user opens the website root URL "/",
# Flask renders the HTML interface.
#
# The returned file is:
#    templates/index.html
#
# This file contains the user interface where link
# lengths and simulation parameters are entered.
# --------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------
# Solve four-bar linkage
#
# This endpoint is called by the frontend JavaScript
# using a POST request.
#
# It receives:
#    Link lengths
#    Driver link selection
#    Simulation parameters
#
# It then runs the entire simulation pipeline and
# returns results as JSON.
#
# URL endpoint:
#    /solve
# --------------------------------------------------
@app.route("/solve", methods=["POST"])
def solve():

    try:

        # --------------------------------------------------
        # Read parameters sent from the frontend
        #
        # The frontend sends JSON containing link lengths
        # and simulation parameters.
        #
        # Example JSON received:
        #
        # {
        #   "L1": 4,
        #   "L2": 5,
        #   "L3": 5,
        #   "L4": 5,
        #   "driver": 2
        # }
        # --------------------------------------------------
        params = request.json


        # --------------------------------------------------
        # Extract user input values
        #
        # Link naming convention:
        #
        # L1 → ground link
        # L2 → input link
        # L3 → coupler link
        # L4 → output link
        # --------------------------------------------------
        L1 = float(params["L1"])
        L2 = float(params["L2"])
        L3 = float(params["L3"])
        L4 = float(params["L4"])


        # --------------------------------------------------
        # Optional simulation parameters
        #
        # step_deg → angular resolution of simulation
        # rpm      → input angular velocity
        # driver   → which link acts as input driver
        # --------------------------------------------------
        step_deg = float(params.get("step_deg", 2))
        rpm = float(params.get("rpm", 30.0))
        driver = int(params.get("driver", 2))


        # --------------------------------------------------
        # Step 1: Linkage classification
        #
        # Determine mechanism type based on link lengths.
        #
        # This includes:
        #   • assembly validity
        #   • Grashof classification
        #   • mechanism type
        #   • expected motion types
        # --------------------------------------------------
        properties = compute_linkage_properties(L1, L2, L3, L4)


        # --------------------------------------------------
        # Stop simulation if mechanism cannot assemble
        #
        # A four-bar linkage cannot exist if the longest
        # link is longer than the sum of the other three.
        #
        # If this condition occurs, return an error
        # message to the UI instead of running the solver.
        # --------------------------------------------------
        if properties["Assembly"] == "Invalid":
            return jsonify({
                "success": False,
                "error": "Invalid linkage: cannot form closed four-bar chain.",
                "properties": properties
            })


        # --------------------------------------------------
        # Step 2: Driver link rotation handling
        #
        # The solver always assumes the input link is L2.
        #
        # If the user chooses another driver (e.g., L4),
        # the link list is rotated so that the chosen
        # driver becomes L2 internally.
        #
        # Example:
        #
        # Original:
        #   [L1, L2, L3, L4]
        #
        # If driver = 4
        #   shift = 2
        #
        # Rotated:
        #   [L3, L4, L1, L2]
        #
        # This allows a single solver implementation
        # to support multiple driver selections.
        # --------------------------------------------------
        lengths = [L1, L2, L3, L4]

        shift = (driver - 2) % 4

        rotated = lengths[shift:] + lengths[:shift]

        L1_int, L2_int, L3_int, L4_int = rotated


        # --------------------------------------------------
        # Step 3: Run the kinematic solver
        #
        # This computes the angular motion of the linkage
        # over time.
        #
        # Output arrays:
        #
        #   theta2 → input angle
        #   theta3 → coupler angle
        #   theta4 → output angle
        #
        # plus time array
        # --------------------------------------------------
        data = compute_four_bar(
            L1_int,
            L2_int,
            L3_int,
            L4_int,
            step_deg,
            rpm
        )


        # --------------------------------------------------
        # Step 4: Convert angles to joint coordinates
        #
        # The geometry module converts link angles into
        # physical joint positions (A, B, C, D).
        # --------------------------------------------------
        geom = compute_geometry(
            data,
            L1_int,
            L2_int,
            L3_int,
            L4_int
        )


        # --------------------------------------------------
        # Step 5: Compute velocity and acceleration
        #
        # These are computed for the coupler point P.
        #
        # Velocity and acceleration are obtained using
        # numerical differentiation of position data.
        # --------------------------------------------------
        kin = compute_kinematics(
            geom["P"],
            data["time"]
        )


        # --------------------------------------------------
        # Step 6: Send simulation results back to UI
        #
        # NumPy arrays are converted to Python lists
        # because JSON cannot directly transmit NumPy
        # data structures.
        # --------------------------------------------------
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


    # --------------------------------------------------
    # Error handling
    #
    # If any error occurs during the simulation,
    # the backend sends the error message back
    # to the frontend so it can be displayed.
    # --------------------------------------------------
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


# --------------------------------------------------
# Run the Flask development server
#
# debug=True enables:
# • automatic reload when code changes
# • detailed error messages in browser
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)