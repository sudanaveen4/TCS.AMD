import json
import os
import time
import numpy as np

class TelemetryEngine:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.machines = {}
        self.failure_modes = {}
        self.telemetry_history = {}
        self.active_failures = {}
        
        self._load_data()
        
    def _load_data(self):
        # 1. Load Machines
        machines_file = os.path.join(self.data_dir, 'databases', 'machines_master.json')
        if os.path.exists(machines_file):
            with open(machines_file, 'r') as f:
                machines_list = json.load(f)
                for m in machines_list:
                    # Filter out idle machines for the simulation to keep it clean, 
                    # or just load running ones.
                    if m.get('status') == 'running':
                        m['x'] = 50
                        m['y'] = 50
                        self.machines[m['machine_id']] = m
                        self.telemetry_history[m['machine_id']] = []
        else:
            print("WARNING: machines_master.json not found!")

        # 2. Add M1-M5 aliases and coordinates to the machines
        # We will map:
        # CNC-101A -> M1 (Conveyor A)
        # FRM-201A -> M2 (Motor Unit)
        # WLD-301A -> M3 (Pump Unit)
        # HTR-401A -> M4 (Compressor)
        # PKG-501A -> M5 (Packaging)
        alias_map = {
            "CNC-101A": {"alias": "M1", "label": "Conveyor A", "x": 15, "y": 60},
            "FRM-201A": {"alias": "M2", "label": "Motor Unit", "x": 32, "y": 60},
            "WLD-301A": {"alias": "M3", "label": "Pump Unit", "x": 50, "y": 60},
            "HTR-401A": {"alias": "M4", "label": "Compressor", "x": 68, "y": 60},
            "PKG-501A": {"alias": "M5", "label": "Packaging", "x": 85, "y": 60}
        }
        
        for m_id, m in self.machines.items():
            if m_id in alias_map:
                m['alias'] = alias_map[m_id]['alias']
                m['label'] = alias_map[m_id]['label']
                m['x'] = alias_map[m_id]['x']
                m['y'] = alias_map[m_id]['y']
        
        # 3. Hardcode some failure modes based on manuals for simulation
        self.failure_modes = {
            "CNC-101A": ["FM-002 Hydraulic Pressure Drop", "FM-001 Arbor Bearing Wear"],
            "FRM-201A": ["FM-101 Motor Bearing Failure", "FM-103 UJ Shaft Spider Wear"],
            "WLD-301A": ["FM-201 IGBT Short Circuit", "FM-204 Squeeze Roller Vibration"],
            "HTR-401A": ["FM-301 Induction Coil Breakdown", "FM-305 Cooling Bed Roller Seize"],
            "PKG-501A": ["FM-401 Hydro Test Pump Failure", "FM-406 Bundling Jam"]
        }
        
    def get_machine_config(self):
        return list(self.machines.values())
        
    def get_failure_modes(self):
        return self.failure_modes
        
    def inject_failure(self, machine_id, failure_mode):
        self.active_failures[machine_id] = failure_mode
        
    def resolve_all_failures(self):
        self.active_failures.clear()
        
    def _generate_normal_sensor(self, machine_id):
        base_values = {
            "CNC-101A": {"vibration_slitting_head": 1.5, "hydraulic_pressure": 150},
            "FRM-201A": {"vibration_main_drive": 2.0, "main_motor_current": 160},
            "WLD-301A": {"vibration_squeeze_stand": 1.2, "weld_temperature": 1200},
            "HTR-401A": {"pipe_exit_temperature": 900, "coil_power": 140},
            "PKG-501A": {"hydro_test_pressure": 50, "vibration_test_pump": 1.5}
        }
        
        sensors = base_values.get(machine_id, {"sensor_1": 100}).copy()
        for k in sensors:
            # Gaussian noise
            sensors[k] += np.random.normal(0, sensors[k] * 0.02)
        return sensors
        
    def generate_tick(self):
        timestamp = int(time.time() * 1000) # JS timestamp
        
        for m_id in self.machines:
            sensors = self._generate_normal_sensor(m_id)
            
            # Apply failure modifications if active
            if m_id in self.active_failures:
                failure = self.active_failures[m_id]
                fl = failure.lower()
                
                # Simple heuristic modifications based on failure string (case-insensitive)
                if "bearing" in fl or "spider" in fl or "vibration" in fl or "wear" in fl:
                    for k in sensors:
                        if "vibration" in k:
                            sensors[k] += np.random.normal(3.0, 0.5) # Spike vibration
                            
                if "pressure" in fl or "pump" in fl or "hydraulic" in fl:
                    for k in sensors:
                        if "pressure" in k:
                            sensors[k] -= np.random.normal(40, 5) # Drop pressure
                            
                if "coil" in fl or "igbt" in fl or "temperature" in fl or "seize" in fl or "heat" in fl or "fire" in fl or "arc" in fl:
                    for k in sensors:
                        if "temperature" in k:
                            sensors[k] += np.random.normal(150, 20) # Spike temp
                            
                if "jam" in fl or "block" in fl:
                    for k in sensors:
                        if "pressure" in k:
                            sensors[k] += np.random.normal(30, 5) # Spike pressure
                        if "vibration" in k:
                            sensors[k] += np.random.normal(2.0, 0.5)
                            
            # Add to history
            record = {"timestamp": timestamp, "sensors": sensors}
            self.telemetry_history[m_id].append(record)
            
            # Truncate
            if len(self.telemetry_history[m_id]) > 60: # Keep 1 minute of data
                self.telemetry_history[m_id].pop(0)
                
    def get_latest_data(self):
        latest = {}
        for m_id, history in self.telemetry_history.items():
            if history:
                latest[m_id] = history[-1]
        return latest
