from flask import Flask, render_template, request, jsonify
import numpy as np

from solver import compute_four_bar
from geometry import compute_geometry
from dynamics import compute_kinematics
from linkage_properties import compute_linkage_properties

app = Flask(__name__)

# -------------------------------------------
# Main page
# -------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------------------------------
# Solve four-bar and return data
# -------------------------------------------

@app.route("/solve", methods=["POST"])
def solve():

    try:

        params = request.json

        # User inputs
        L1 = float(params["L1"])
        L2 = float(params["L2"])
        L3 = float(params["L3"])
        L4 = float(params["L4"])

        step_deg = float(params.get("step_deg", 2))
        rpm = float(params.get("rpm", 30.0))
        driver = int(params.get("driver", 2))

        # -----------------------------
        # Linkage Properties (NO rotation)
        # -----------------------------
        properties = compute_linkage_properties(L1, L2, L3, L4)

        if properties["Assembly"] == "Invalid":
            return jsonify({
                "success": False,
                "error": "Invalid linkage: cannot form closed four-bar chain.",
                "properties": properties
            })

        # -----------------------------
        # Rotate for solver only
        # -----------------------------
        lengths = [L1, L2, L3, L4]
        shift = (driver - 2) % 4
        rotated = lengths[shift:] + lengths[:shift]
        L1_int, L2_int, L3_int, L4_int = rotated

        # -----------------------------
        # Solve motion
        # -----------------------------
        data = compute_four_bar(L1_int, L2_int, L3_int, L4_int, step_deg, rpm)

        geom = compute_geometry(data, L1_int, L2_int, L3_int, L4_int)
        kin = compute_kinematics(geom["P"], data["time"])

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


    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })



if __name__ == "__main__":
    app.run(debug=True)
