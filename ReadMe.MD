# Four-Bar Workspace Envelope

## Project Overview

**Four-Bar Workspace Envelope** is a web-based application for the **kinematic analysis and workspace visualization** of a planar four-bar linkage mechanism.

The project focuses on **physically correct kinematics**, continuous motion visualization, and clear geometric interpretation.  
All numerical computations are performed in Python, while visualization is handled in the web browser using real-time animation.

The system is designed for **educational, academic, and demonstration purposes**, with a clean separation between computation and visualization.



## Key Capabilities

- Numerical kinematic analysis of a planar four-bar linkage
- Full input crank rotation (when physically valid)
- Branch-consistent solver (prevents configuration jumping)
- Continuous, automatic animation
- Visualization of joint motion (A–B–C–D)
- Workspace envelope visualization by tracking output joint motion
- Centered and scaled visualization for clear interpretation
- Modular and team-friendly project structure



## Technology Stack

### Backend
- **Python 3**
- **Flask** — Web server and API
- **NumPy** — Numerical computation
- **SciPy** — Nonlinear equation solving

### Frontend
- **HTML / CSS**
- **JavaScript**
- **Plotly.js** — Real-time animation and visualization


## Project Structure & File Responsibilities

### `app.py` — Web Server & Controller
- Entry point of the application
- Handles browser requests
- Receives user-defined link lengths
- Executes kinematic analysis
- Sends computed results to the frontend as JSON
- No visualization or solver logic

---

### `solver.py` — Kinematic Solver (Core Logic)
- Implements four-bar linkage kinematics
- Checks Grashof condition
- Solves vector loop equations numerically
- Computes:
  - Input, coupler, and output link angles
  - Time-indexed motion data
- Maintains configuration continuity
- Handles singular (toggle) positions safely

---

### `geometry.py` — Geometric Computation
- Converts link angles into Cartesian joint positions
- Computes positions of joints A, B, C, and D
- Provides geometric data required for animation
- No numerical solving or visualization logic

---

### `dynamics.py` — Velocity & Acceleration Computation
- Computes velocity and acceleration using numerical differentiation
- Operates on position–time data
- Purely kinematic (no forces or masses)

---

### `templates/index.html` — Web Interface
- Displays the simulation interface
- Provides input fields for link lengths
- Includes a single **Run** button
- Centers all UI elements and visualization
- Contains no computational logic

---

### `static/plot.js` — Animation & Visualization
- Receives computed data from the backend
- Animates the four-bar mechanism continuously
- Labels joints A, B, C, and D
- Tracks output joint motion to show workspace envelope
- Ensures centered, equal-scale visualization
- Visualization-only (no kinematics or math)

---

### `requirements.txt`
Lists all required Python dependencies.

Example:
```txt
flask
numpy
scipy
```
## System Workflow (High-Level)
```txt
User Input (Browser)
        ↓
Flask Web Server (app.py)
        ↓
Kinematic Solver (solver.py)
        ↓
Geometry Computation (geometry.py)
        ↓
JSON Response
        ↓
Live Browser Animation (plot.js)
```
## Installation & Setup
### 1. Clone the Repository
```bash
git clone git@github.com:PedakolimiHarish/Four-Bar-Workspace-Envelope.git
cd four_bar_workspace
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
```bash
http://127.0.0.1:5000
```
---
### Inputs
- Link lengths:
	 - L1 — Ground link
	 - L2 — Input link
	 - L3 — Coupler link
	 - L4 — Output link
---
#### Outputs
 - Continuous animated four-bar motion 
 - Labeled joint positions (A, B, C,D) 
 - Workspace envelope of the output joint 
 - Centered and scaled visualization
----
#### Coordinate System
A standard planar four-bar coordinate system is used:
- Ground link is horizontal
- Left ground joint at origin
- Right ground joint on the positive X-axis
```txt
								A -------- D
								|          |
								|          |
								B -------- C
```
---
### Joint Definitions
| Symbol	| Description |
|:--:|:--:|
| A | Left ground joint |
| D | Right ground joint|	
| B	| Input–coupler joint|
| C | Coupler–output joint|
---
### Notes on Physical Validity
- Continuous output motion depends on the link length configuration
- Change-point (toggle) mechanisms may not produce continuous output rotation
- The simulator intentionally follows physically correct kinematics
- No artificial branch switching or non-physical motion is used

### Planned Improvements
- Input validation and user-friendly error messages
- Warnings for non-Grashof and change-point mechanisms
- Improved user feedback for solver limitations

## Linkage Properties

The following properties describe the kinematic characteristics of the current four-bar linkage configuration.

| Property | Value |
|--------|-------|
| Input Type | Crank |
| Output Type | Crank |
| Linkage Type | Grashof |
| Validity Index | 80 |
| Grashof Index | 0 |

### Notes
- The **input type** indicates the nature of motion of the driving link.
- The **output type** describes the motion behavior of the driven link.
- The **linkage type** is determined using the Grashof condition.
- The **validity index** represents the percentage of the input cycle over which the solver produces physically valid configurations.
- The **Grashof index** is defined as:  
```txt
  (s + l) - (p + q)
  ```
  where `s` is the shortest link, `l` the longest link, and `p`, `q` the remaining links.