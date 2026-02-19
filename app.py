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
        L1 = float(params["L1"])  # Ground
        L2 = float(params["L2"])  # Input
        L3 = float(params["L3"])  # Coupler
        L4 = float(params["L4"])  # Output

        step_deg = float(params.get("step_deg", 2))
        rpm = float(params.get("rpm", 30.0))
        driver = int(params.get("driver", 2))  # default L2

        lengths = [L1, L2, L3, L4]

        # Rotate so selected driver becomes L2
        # Index positions:
        # 0=L1, 1=L2, 2=L3, 3=L4

        # We want driver index to map to position 1
        shift = (driver - 2) % 4

        rotated = lengths[shift:] + lengths[:shift]

        L1_int, L2_int, L3_int, L4_int = rotated

        # -----------------------------
        # Run solver (NO ROTATION)
        # -----------------------------
        data = compute_four_bar(L1_int, L2_int, L3_int, L4_int, step_deg, rpm)

        is_change_point = data.get("is_change_point", False)

        # -----------------------------
        # Geometry
        # -----------------------------
        geom = compute_geometry(data, L1_int, L2_int, L3_int, L4_int)


        # -----------------------------
        # Kinematics
        # -----------------------------
        kin = compute_kinematics(geom["P"], data["time"])

        # -----------------------------
        # Linkage Properties
        # -----------------------------
        properties = compute_linkage_properties(L1_int, L2_int, L3_int, L4_int)

        print("Linkage Properties:", properties)

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
            "properties": properties,
            "change_point": is_change_point
        })


    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })



if __name__ == "__main__":
    app.run(debug=True)
