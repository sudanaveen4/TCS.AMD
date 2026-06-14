import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# Cell 1: Description
text_1 = """# TCS Bharat Steel Pipes: Digital Twin & ML Anomaly Detection Engine
This notebook provides a complete 2-tab interface using **Gradio**:
1. **Live Monitoring**: Displays plant status, interactive blueprint, and live telemetry.
2. **Simulation Controller**: Allows injecting simulated failures.

An underlying **One-Class SVM** detects anomalies in the synthetic telemetry, and a **Local SLM (Ollama)** is used to generate alerts and RCA recommendations."""

# Cell 2: Imports
code_2 = """import gradio as gr
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import threading
import requests
import json
import os
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from PIL import Image
import warnings
warnings.filterwarnings('ignore')"""

# Cell 3: Data Loading
code_3 = """# Load Plant Blueprint Image
blueprint_path = r"d:\\amd_tcs_hackathon\\plant_data\\plant_overview\\images\\plant_blueprint.png"
if os.path.exists(blueprint_path):
    bg_image = Image.open(blueprint_path)
else:
    bg_image = None
    print("Blueprint image not found. Ensure it exists at:", blueprint_path)

# Simulated Machine Coordinates (for plotting on the blueprint)
# X, Y coordinates relative to the image size
machine_locations = {
    "CNC-101A": {"x": 200, "y": 150, "zone": "Z2", "status": "running"},
    "FRM-201A": {"x": 400, "y": 150, "zone": "Z3", "status": "running"},
    "WLD-301A": {"x": 600, "y": 150, "zone": "Z4", "status": "running"},
    "HTR-401A": {"x": 800, "y": 150, "zone": "Z5", "status": "running"},
    "PKG-501A": {"x": 1000, "y": 150, "zone": "Z6", "status": "running"},
}

# Failure Modes Dictionary (from manuals)
failure_modes = {
    "CNC-101A": ["FM-001 Arbor Bearing Wear", "FM-002 Hydraulic Pressure Drop"],
    "FRM-201A": ["FM-101 Motor Bearing Failure", "FM-103 UJ Shaft Spider Wear"],
    "WLD-301A": ["FM-201 IGBT Short Circuit", "FM-204 Squeeze Roller Vibration"],
    "HTR-401A": ["FM-301 Induction Coil Breakdown", "FM-305 Cooling Bed Roller Seize"],
    "PKG-501A": ["FM-401 Hydro Test Pump Failure", "FM-406 Bundling Jam"]
}

# Global State for Telemetry and Alerts
telemetry_data = {m: [] for m in machine_locations.keys()}
live_alerts = []
current_injected_failure = {"machine": None, "failure": None, "active": False}
"""

# Cell 4: SLM Integration
code_4 = """# ==============================================================================
# SLM / LLM INTEGRATION LAYER
# ==============================================================================

def generate_alert_summary(machine_id, telemetry_feature, value, status):
    \"\"\"
    Uses a local SLM (e.g., <2B model like qwen2:1.5b via Ollama) to generate 
    a contextual alert description.
    \"\"\"
    prompt = f"Machine {machine_id} triggered a {status} alert. Sensor: {telemetry_feature}, Value: {value:.2f}. Briefly describe the operational risk in 1 sentence."
    
    # -------------------------------------------------------------------------
    # LOCAL SLM (< 2B) SETUP - OLLAMA (Local PC Environment)
    # -------------------------------------------------------------------------
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "qwen2:1.5b", # Replace with your local SLM
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(url, json=payload, timeout=2)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except Exception:
        pass
        
    # Fallback if SLM is unreachable
    return f"Anomaly detected on {machine_id} for {telemetry_feature}."

# -------------------------------------------------------------------------
# FUTURE MI300X SETUP (Large Models >70B Parameters) - COMMENTED
# -------------------------------------------------------------------------
# When moving to AMD Instinct MI300X infrastructure, use a vLLM or TGI endpoint
# suitable for massive models (e.g., Llama-3-70B-Instruct).
#
# def generate_alert_summary_mi300x(machine_id, telemetry_feature, value, status):
#     import openai
#     client = openai.Client(
#         base_url="http://<MI300X_VLLM_SERVER_IP>:8000/v1",
#         api_key="empty"
#     )
#     prompt = f"You are an industrial AI agent. Machine {machine_id}..."
#     response = client.chat.completions.create(
#         model="meta-llama/Meta-Llama-3-70B-Instruct",
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=50
#     )
#     return response.choices[0].message.content
"""

# Cell 5: Telemetry Generator
code_5 = """# ==============================================================================
# SYNTHETIC TELEMETRY GENERATOR
# ==============================================================================
# This simulates normal operating parameters and injects anomalies based on the controller.

def generate_sensor_data(machine_id):
    # Base normal values
    base_values = {
        "CNC-101A": {"vibration": 1.5, "pressure": 150},
        "FRM-201A": {"vibration": 2.0, "current": 160},
        "WLD-301A": {"vibration": 1.2, "temperature": 85},
        "HTR-401A": {"temperature": 900, "current": 140},
        "PKG-501A": {"pressure": 50, "vibration": 1.5}
    }
    
    sensors = base_values[machine_id].copy()
    
    # Add normal random noise
    for k in sensors:
        sensors[k] += np.random.normal(0, sensors[k]*0.05)
        
    # Inject Failure if active
    if current_injected_failure["active"] and current_injected_failure["machine"] == machine_id:
        failure = current_injected_failure["failure"]
        if "Bearing" in failure or "Spider" in failure or "Squeeze" in failure:
            sensors["vibration"] += np.random.normal(3.5, 0.5) # Spike vibration
        if "Pressure" in failure or "Pump" in failure:
            sensors["pressure"] -= np.random.normal(40, 5) # Drop pressure
        if "Coil" in failure or "IGBT" in failure:
            sensors.get("temperature", 0)
            if "temperature" in sensors:
                sensors["temperature"] += np.random.normal(150, 20) # Spike temp
                
    return sensors

def background_telemetry_loop():
    \"\"\"Continuously generates data for all machines in a background thread.\"\"\"
    while True:
        for m_id in machine_locations.keys():
            data = generate_sensor_data(m_id)
            data["timestamp"] = time.time()
            telemetry_data[m_id].append(data)
            # Keep only last 100 points
            if len(telemetry_data[m_id]) > 100:
                telemetry_data[m_id].pop(0)
        time.sleep(1) # 1 update per second

# Start background thread
bg_thread = threading.Thread(target=background_telemetry_loop, daemon=True)
bg_thread.start()
"""

# Cell 6: ML Detection Layer
code_6 = """# ==============================================================================
# ML DETECTION LAYER (One-Class SVM)
# ==============================================================================

# We will instantiate a simple SVM for demonstration. 
# In a real app, this would be trained on historical normal data.
models = {}
scalers = {}

# Dummy pre-training on synthetic normal data
for m_id in machine_locations.keys():
    normal_data = []
    for _ in range(200):
        current_injected_failure["active"] = False
        normal_data.append(list(generate_sensor_data(m_id).values()))
        
    df = pd.DataFrame(normal_data)
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)
    
    svm = OneClassSVM(nu=0.05, kernel="rbf", gamma=0.1)
    svm.fit(scaled_data)
    
    models[m_id] = svm
    scalers[m_id] = scaler

def run_ml_detection():
    \"\"\"Runs detection on the latest telemetry point.\"\"\"
    for m_id, svm in models.items():
        if len(telemetry_data[m_id]) < 1:
            continue
            
        latest = telemetry_data[m_id][-1]
        features = [v for k, v in latest.items() if k != "timestamp"]
        
        # Transform and Predict
        scaled = scalers[m_id].transform([features])
        prediction = svm.predict(scaled)[0] # 1 is normal, -1 is anomaly
        
        if prediction == -1:
            machine_locations[m_id]["status"] = "alert"
            # Get the sensor that is most deviated
            sensor_keys = [k for k in latest.keys() if k != "timestamp"]
            deviations = np.abs(scaled[0])
            worst_sensor_idx = np.argmax(deviations)
            worst_sensor = sensor_keys[worst_sensor_idx]
            val = latest[worst_sensor]
            
            # Use SLM to generate alert
            slm_msg = generate_alert_summary(m_id, worst_sensor, val, "CRITICAL")
            
            msg = f"[{time.strftime('%H:%M:%S')}] {m_id} ANOMALY: {worst_sensor.upper()} = {val:.2f}. {slm_msg}"
            if msg not in live_alerts:
                live_alerts.insert(0, msg)
                if len(live_alerts) > 10:
                    live_alerts.pop()
        else:
            if not (current_injected_failure["active"] and current_injected_failure["machine"] == m_id):
                machine_locations[m_id]["status"] = "running"
"""

# Cell 7: Gradio UI
code_7 = """# ==============================================================================
# GRADIO INTERFACE
# ==============================================================================

def update_dashboard():
    \"\"\"Updates the visual map, the telemetry plots, and the alert logs.\"\"\"
    
    # 1. Blueprint Map using Plotly
    fig = go.Figure()
    
    # Add background image if available
    if bg_image:
        fig.add_layout_image(
            dict(
                source=bg_image,
                xref="x", yref="y",
                x=0, y=bg_image.height,
                sizex=bg_image.width, sizey=bg_image.height,
                sizing="stretch",
                opacity=0.8,
                layer="below")
        )
        fig.update_xaxes(range=[0, bg_image.width], showgrid=False, visible=False)
        fig.update_yaxes(range=[0, bg_image.height], scaleanchor="x", showgrid=False, visible=False)
    else:
        fig.update_xaxes(range=[0, 1200])
        fig.update_yaxes(range=[0, 600])
        
    # Plot Machines
    x_coords = []
    y_coords = []
    colors = []
    texts = []
    
    for m_id, info in machine_locations.items():
        x_coords.append(info["x"])
        y_coords.append(info["y"])
        colors.append("green" if info["status"] == "running" else "red")
        texts.append(m_id)
        
    fig.add_trace(go.Scatter(
        x=x_coords, y=y_coords,
        mode="markers+text",
        marker=dict(size=25, color=colors, line=dict(width=2, color="white")),
        text=texts,
        textposition="top center",
        textfont=dict(color="white", size=14)
    ))
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="black",
        paper_bgcolor="black",
        height=400
    )
    
    # Run ML Detection
    run_ml_detection()
    
    # 2. Format Alerts
    alerts_text = "\\n".join(live_alerts) if live_alerts else "System Normal. No alerts."
    
    # 3. Telemetry Plot (Show the first machine as an example, or the one with anomaly)
    target_m = current_injected_failure["machine"] if current_injected_failure["active"] else "FRM-201A"
    df = pd.DataFrame(telemetry_data[target_m])
    
    plot_fig = go.Figure()
    if not df.empty:
        sensor_keys = [c for c in df.columns if c != "timestamp"]
        for col in sensor_keys:
            plot_fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col, mode='lines'))
            
    plot_fig.update_layout(title=f"Live Telemetry: {target_m}", height=300, margin=dict(l=20, r=20, t=40, b=20))
    
    return fig, plot_fig, alerts_text

def update_failure_dropdown(machine):
    \"\"\"Update the failure modes dropdown based on machine selection.\"\"\"
    return gr.Dropdown(choices=failure_modes.get(machine, []), value=None)

def inject_failure(machine, failure):
    \"\"\"Trigger the anomaly generation.\"\"\"
    if not machine or not failure:
        return "Please select both a machine and a failure mode."
    
    current_injected_failure["machine"] = machine
    current_injected_failure["failure"] = failure
    current_injected_failure["active"] = True
    
    return f"Injected '{failure}' into {machine} telemetry stream. Watch ML detection!"

def resolve_failure():
    \"\"\"Clear the anomaly.\"\"\"
    current_injected_failure["active"] = False
    return "Anomalies resolved. Returning to normal telemetry."


# BUILD THE UI
with gr.Blocks(theme=gr.themes.Monochrome()) as app:
    gr.Markdown("# 🏭 TCS Bharat Steel Pipes: Digital Twin & ML Intelligence")
    
    with gr.Tabs():
        # TAB 1: LIVE MONITORING
        with gr.Tab("Live Monitoring"):
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### Live Plant Blueprint (Animated)")
                    plant_map = gr.Plot()
                
                with gr.Column(scale=1):
                    gr.Markdown("### Real-Time Alerts & ML Detection")
                    alert_box = gr.Textbox(lines=15, label="Alert Stream (Powered by SVM + SLM)")
            
            with gr.Row():
                gr.Markdown("### Live Machine Telemetry")
                telemetry_plot = gr.Plot()
                
        # TAB 2: SIMULATION CONTROLLER
        with gr.Tab("Simulation Controller"):
            gr.Markdown("### Inject Digital Failures")
            gr.Markdown("Use this panel to simulate failures on the plant floor. The synthetic data engine will alter the telemetry stream, triggering the ML Anomaly Detection layer in real-time.")
            
            with gr.Row():
                m_dropdown = gr.Dropdown(choices=list(machine_locations.keys()), label="Select Target Machine")
                f_dropdown = gr.Dropdown(choices=[], label="Select Failure Mode")
            
            m_dropdown.change(fn=update_failure_dropdown, inputs=m_dropdown, outputs=f_dropdown)
            
            with gr.Row():
                inject_btn = gr.Button("🚨 Trigger Anomaly", variant="stop")
                resolve_btn = gr.Button("✅ Resolve Issues", variant="primary")
            
            status_text = gr.Textbox(label="Injection Status")
            
            inject_btn.click(fn=inject_failure, inputs=[m_dropdown, f_dropdown], outputs=status_text)
            resolve_btn.click(fn=resolve_failure, inputs=[], outputs=status_text)

    # Timer to update Tab 1 automatically every second
    timer = gr.Timer(1)
    timer.tick(fn=update_dashboard, inputs=[], outputs=[plant_map, telemetry_plot, alert_box])

# Launch the app inline
app.launch(inline=True, share=False)
"""

nb.cells = [
    nbf.v4.new_markdown_cell(text_1),
    nbf.v4.new_code_cell(code_2),
    nbf.v4.new_code_cell(code_3),
    nbf.v4.new_code_cell(code_4),
    nbf.v4.new_code_cell(code_5),
    nbf.v4.new_code_cell(code_6),
    nbf.v4.new_code_cell(code_7)
]

with open(r"d:\\amd_tcs_hackathon\\plant_simulation_engine.ipynb", 'w', encoding="utf-8") as f:
    nbf.write(nb, f)
