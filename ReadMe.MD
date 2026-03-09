# Four-Bar Workspace Envelope Simulator

A web-based simulator for analyzing planar **four-bar linkages**.

This tool computes and visualizes the motion of a four-bar mechanism, including joint trajectories, coupler motion, workspace envelope, and basic kinematic properties.

The backend performs the kinematic calculations while the frontend visualizes the motion interactively.

---

## Features

- Interactive four-bar linkage animation
- Automatic mechanism classification
- Support for different driver links
- Coupler point trajectory tracking
- Workspace envelope visualization
- Velocity and acceleration computation
- Numerical kinematic solver using the Freudenstein equation

---

## Project Structure

```
four_bar_workspace/
│
├── app.py
│   Flask server connecting UI and simulation modules
│
├── solver.py
│   Four-bar kinematic solver
│
├── geometry.py
│   Converts link angles to joint coordinates
│
├── dynamics.py
│   Computes velocity and acceleration
│
├── linkage_properties.py
│   Mechanism classification and workspace analysis
│
├── templates/
│   index.html
│
├── static/
│   plot.js
│
├── requirements.txt
└── README.md
```

---

## Simulation Pipeline

```
User Input
   ↓
Mechanism Classification
   ↓
Kinematic Solver
   ↓
Geometry Conversion
   ↓
Coupler Trajectory
   ↓
Velocity / Acceleration
   ↓
Workspace Envelope
   ↓
Visualization
```

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone git@github.com:PedakolimiHarish/Four-Bar-Workspace-Envelope.git
cd Four-Bar-Workspace-Envelope
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Server

```bash
python app.py
```

### 4. Open in Browser

```
http://127.0.0.1:5000
```

---

## Inputs

The simulator requires the following parameters:

| Parameter | Description |
|----------|-------------|
| L1 | Ground link length |
| L2 | Input link |
| L3 | Coupler link |
| L4 | Output link |
| Driver | Selected driving link |

---

## Outputs

The system computes:

- Joint coordinates (A, B, C, D)
- Coupler point trajectory
- Workspace envelope
- Velocity and acceleration
- Mechanism classification (Grashof type)

---

## Numerical Methods Used

The kinematic solver uses:

- Freudenstein equation
- Newton–Raphson iteration
- Branch continuity control
- Finite-difference differentiation
- Convex hull workspace estimation

---

## Dependencies

The project requires the following Python packages:

- Flask
- NumPy
- SciPy
- Plotly

Install them with:

```bash
pip install -r requirements.txt
```

---