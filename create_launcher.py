import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# Cell 1: Description
text_1 = """# 🏭 Start: TCS Bharat Steel Pipes - Full Stack Simulation
Run the cells below to install all necessary dependencies and launch the real-time simulation backend. 
Once the backend is running, you will be provided with a link to open the Live Digital Twin Dashboard."""

# Cell 2: Install dependencies
code_2 = """!pip install -r requirements.txt"""

# Cell 3: Start Flask Backend
code_3 = """import os
import subprocess
import time
import urllib.request

print("Starting Flask Backend Server...")
# Start the Flask app as a background process
process = subprocess.Popen(
    ["python", "app.py"], 
    cwd="simulation_app", 
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE
)

# Wait for server to boot
time.sleep(3)

# Check if it's running
try:
    urllib.request.urlopen("http://127.0.0.1:5000/api/status", timeout=2)
    print("\\n✅ SUCCESS! The Simulation Backend is running.")
    print("\\n➡️ CLICK HERE TO OPEN THE DASHBOARD: http://127.0.0.1:5000/")
    print("\\nKeep this notebook running. To stop the simulation, stop this cell.")
    process.wait()
except Exception as e:
    print("❌ ERROR: Could not connect to the backend.")
    stdout, stderr = process.communicate()
    print("STDOUT:", stdout.decode())
    print("STDERR:", stderr.decode())
"""

nb.cells = [
    nbf.v4.new_markdown_cell(text_1),
    nbf.v4.new_code_cell(code_2),
    nbf.v4.new_code_cell(code_3)
]

with open(r"d:\\amd_tcs_hackathon\\start_simulation.ipynb", 'w', encoding="utf-8") as f:
    nbf.write(nb, f)
