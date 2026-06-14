# System Split: Read-Only Dashboard & Dedicated Simulation Controller

Based on your request, you want the system to be split into two distinct pages:
1. **Live Dashboard (`index.html`)**: The gorgeous "ShiftSense AI" screen. It will become completely read-only (no injection popups). It purely consumes and visualizes the live alerts and metrics.
2. **Simulation Controller (`control.html`)**: A dedicated page for the simulation engineer. It will show live, high-resolution telemetry graphs (e.g., vibration signals deflecting based on thresholds) and house the injection controls.

Additionally, you requested that anomalies be detected by **multiple ML models**.

## User Review Required

> [!IMPORTANT]
> **Ensemble ML Detection Strategy:** I plan to update the backend to train and run both a **One-Class SVM** and an **Isolation Forest** simultaneously on the streaming telemetry. An alert will clearly state which model(s) detected the anomaly. Is this acceptable?

## Proposed Changes

### [MODIFY] `d:\amd_tcs_hackathon\simulation_app\static\index.html`
- Remove the injection modal HTML and the click event listeners from the map markers. The dashboard will now act purely as a "Live View" for plant operators.

### [NEW] `d:\amd_tcs_hackathon\simulation_app\static\control.html`
- Create a new, highly technical UI for simulation control.
- **Features**:
  - A dropdown to select a specific machine.
  - Live, scrolling Chart.js line graphs showing the raw telemetry signals (e.g., vibration, temperature) for the selected machine, complete with threshold lines.
  - The injection dropdowns and buttons. When a failure is injected, you will visually see the raw signal spike past the threshold on the charts.

### [NEW] `d:\amd_tcs_hackathon\simulation_app\static\js\control.js`
- The JS logic to handle the high-frequency telemetry charting and injection API calls for the new `control.html` page.

### [MODIFY] `d:\amd_tcs_hackathon\simulation_app\app.py`
- Add a new Flask route `@app.route('/control')` that serves `control.html`.

### [MODIFY] `d:\amd_tcs_hackathon\simulation_app\engine\ml_detector.py`
- Import and initialize `sklearn.ensemble.IsolationForest`.
- Update `_train_on_fly` to train both SVM and Isolation Forest on the baseline data.
- Update `detect_anomalies` to run predictions from both models. The resulting alert payload will include a `detected_by` field (e.g., `["SVM", "IsolationForest"]`).

## Verification Plan
1. I will implement the backend ensemble ML logic.
2. I will build the new `control.html` and strip the injection logic from `index.html`.
3. I will test the flow: Injecting an error on `/control` should cause the raw graphs to visually spike past thresholds, triggering an ensemble ML alert that is immediately displayed on the `/` Live Dashboard.
