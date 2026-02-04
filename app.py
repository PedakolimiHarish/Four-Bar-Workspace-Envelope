from flask import Flask, render_template, request, jsonify

from solver import compute_four_bar
from geometry import compute_geometry
from dynamics import compute_kinematics

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

    params = request.json

    L1 = float(params["L1"])
    L2 = float(params["L2"])
    L3 = float(params["L3"])
    L4 = float(params["L4"])

    step_deg = float(params.get("step_deg", 1))
    rpm = float(params.get("rpm", 30.0))

    # Run kinematic solver
    data = compute_four_bar(L1, L2, L3, L4, step_deg, rpm)

    # Compute geometry
    geom = compute_geometry(data, L1, L2, L3)

    # Compute velocity & acceleration of coupler point
    kin = compute_kinematics(geom["P"], data["time"])

    return jsonify({
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
    })


if __name__ == "__main__":
    app.run(debug=True)
