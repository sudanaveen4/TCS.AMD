import sys
import os
import time
import json
from datetime import datetime

# Attempt to load ML libs
try:
    import pandas as pd
    import xgboost as xgb
    import joblib
    HAS_ML = True
except ImportError:
    HAS_ML = False
    print("Warning: ML libraries (pandas, xgboost, joblib) not found. Falling back to mock simulation.")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.schema import Machine
from database.json_db import JSONDatabase

class DigitalTwinEngine:
    def __init__(self, workspace_dir: str = "d:/amd_tcs_hackathon"):
        self.workspace_dir = workspace_dir
        self.db = JSONDatabase(os.path.join(workspace_dir, "data"))
        self.telemetry_file = os.path.join(workspace_dir, "data", "telemetry.json")
        self.is_running = False
        
        self.models = {}
        if HAS_ML:
            self._load_models()
            
    def _load_models(self):
        print("Loading XGBoost Digital Twin Models...")
        pump_dir = os.path.join(self.workspace_dir, "Pump_Failure")
        comp_dir = os.path.join(self.workspace_dir, "Compressor_failure")
        
        try:
            self.models['pump_prob'] = joblib.load(os.path.join(pump_dir, "pump_failure_probability_model.pkl"))
            self.models['pump_mode'] = joblib.load(os.path.join(pump_dir, "pump_failure_mode_model.pkl"))
            self.models['pump_rul'] = joblib.load(os.path.join(pump_dir, "pump_rul_model.pkl"))
            
            # Load sample CSV data to replay
            self.pump_data = pd.read_csv(os.path.join(pump_dir, "pump_telemetry.csv")).dropna()
            self.pump_idx = 0
            print("Models loaded successfully.")
        except Exception as e:
            print(f"Failed to load models: {e}")
            global HAS_ML
            HAS_ML = False

    def get_next_pump_telemetry(self, machine_id="PUMP-01"):
        # Simulated or Real ML inference
        if HAS_ML and hasattr(self, 'pump_data'):
            if self.pump_idx >= len(self.pump_data):
                self.pump_idx = 0
            
            row = self.pump_data.iloc[[self.pump_idx]]
            self.pump_idx += 1
            
            # Extract features expected by models (dropping non-features if necessary)
            features = row.drop(columns=['timestamp', 'machine_id'], errors='ignore')
            
            prob = float(self.models['pump_prob'].predict_proba(features)[0][1]) * 100
            mode = str(self.models['pump_mode'].predict(features)[0])
            rul = int(self.models['pump_rul'].predict(features)[0])
            
            return {
                "machine_id": machine_id,
                "timestamp": datetime.utcnow().isoformat(),
                "vibration": float(row.get('vibration', 2.0)),
                "bearing_temp": float(row.get('bearing_temp', 45.0)),
                "suction_pressure": float(row.get('suction_pressure', 4.0)),
                "flow_rate": float(row.get('flow_rate', 300.0)),
                "motor_current": float(row.get('motor_current', 110.0)),
                "seal_leakage_rate": float(row.get('seal_leakage_rate', 0.05)),
                "failure_probability": prob,
                "predicted_failure_mode": mode,
                "rul_days": rul
            }
        else:
            # Fallback for hackathon demo without xgboost installed
            return {
                "machine_id": machine_id,
                "timestamp": datetime.utcnow().isoformat(),
                "vibration": 8.5,
                "bearing_temp": 82.0,
                "suction_pressure": 1.5,
                "flow_rate": 180.0,
                "motor_current": 145.0,
                "seal_leakage_rate": 0.05,
                "failure_probability": 92.5,
                "predicted_failure_mode": "Cavitation",
                "rul_days": 8
            }

    def simulate_continuous(self, duration_sec: int, tick_interval: float = 1.0, event_bus=None):
        print(f"Starting Digital Twin simulation for {duration_sec} seconds...")
        self.is_running = True
        start_time = time.time()
        
        while time.time() - start_time < duration_sec and self.is_running:
            # Generate tick
            telemetry_batch = [
                self.get_next_pump_telemetry("PUMP-101")
            ]
            
            # Append to file
            if os.path.exists(self.telemetry_file):
                with open(self.telemetry_file, 'r') as f:
                    try:
                        data = json.load(f)
                    except:
                        data = []
            else:
                data = []
            
            data.extend(telemetry_batch)
            with open(self.telemetry_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            # Publish to event bus
            if event_bus:
                event_bus.publish(telemetry_batch)
                
            time.sleep(tick_interval)
            
        self.is_running = False
        print("Simulation complete.")

if __name__ == "__main__":
    from detectors.rules import RuleEngine, EventBus
    
    engine = DigitalTwinEngine()
    event_bus = EventBus()
    detector = RuleEngine()
    
    event_bus.subscribe(detector.evaluate_telemetry)
    engine.simulate_continuous(duration_sec=5, event_bus=event_bus)
