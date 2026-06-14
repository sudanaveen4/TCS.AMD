import sys
import os
import json
import random
import time
from datetime import datetime, timedelta
import threading

# Add backend to path so we can import models and database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.json_db import JSONDatabase
from models.schema import Machine

class SimulationEngine:
    def __init__(self, db_dir: str = "data"):
        self.db = JSONDatabase(db_dir)
        self.machines = self.db.read_table("machines", Machine)
        self.is_running = False
        self.telemetry_file = os.path.join(db_dir, "telemetry.json")
        self.events_file = os.path.join(db_dir, "events.json")
        
        # Initialize empty files if they don't exist
        if not os.path.exists(self.telemetry_file):
            with open(self.telemetry_file, 'w') as f: json.dump([], f)
        if not os.path.exists(self.events_file):
            with open(self.events_file, 'w') as f: json.dump([], f)

    def generate_normal_telemetry(self, machine: Machine):
        # Baseline normal values
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "machine_id": machine.machine_id,
            "vibration": round(random.uniform(1.0, 3.5), 2),  # mm/s
            "temperature": round(random.uniform(40.0, 60.0), 1), # Celsius
            "current": round(random.uniform(5.0, 15.0), 2), # Amps
            "rpm": round(random.uniform(1400, 1500), 0),
            "throughput": round(random.uniform(machine.throughput * 0.9, machine.throughput * 1.0), 1),
            "status": "normal"
        }

    def generate_fault_telemetry(self, machine: Machine, fault_type: str):
        # Specific simulated faults
        data = self.generate_normal_telemetry(machine)
        data["status"] = "fault"
        data["fault_type"] = fault_type
        
        if fault_type == "bearing_failure":
            data["vibration"] = round(random.uniform(8.0, 15.0), 2)
            data["temperature"] = round(random.uniform(75.0, 95.0), 1)
        elif fault_type == "jam":
            data["rpm"] = round(random.uniform(0, 100), 0)
            data["current"] = round(random.uniform(30.0, 50.0), 2)
            data["throughput"] = 0.0
        elif fault_type == "overheating":
            data["temperature"] = round(random.uniform(90.0, 120.0), 1)
            data["current"] = round(random.uniform(20.0, 25.0), 2)
            
        return data

    def _append_json_list(self, file_path, new_items):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data = []
        data.extend(new_items)
        # Keep only last 1000 records to prevent massive files during demo
        data = data[-1000:]
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def run_step(self, active_faults: dict = None, event_bus=None):
        if active_faults is None:
            active_faults = {}
            
        current_telemetry = []
        for machine in self.machines:
            fault = active_faults.get(machine.machine_id)
            if fault:
                current_telemetry.append(self.generate_fault_telemetry(machine, fault))
            else:
                current_telemetry.append(self.generate_normal_telemetry(machine))
                
        self._append_json_list(self.telemetry_file, current_telemetry)
        
        # Publish to event bus for real-time detection
        if event_bus:
            event_bus.publish(current_telemetry)
            
        return current_telemetry

    def simulate_continuous(self, duration_sec: int, tick_interval: float = 1.0, event_bus=None):
        print(f"Starting simulation for {duration_sec} seconds...")
        self.is_running = True
        start_time = time.time()
        
        fault_time = duration_sec / 2
        active_faults = {}
        
        while time.time() - start_time < duration_sec and self.is_running:
            elapsed = time.time() - start_time
            if elapsed > fault_time and "M2" not in active_faults:
                print("Injecting bearing_failure fault into M2...")
                active_faults["M2"] = "bearing_failure"
                
            self.run_step(active_faults, event_bus)
            time.sleep(tick_interval)
            
        self.is_running = False
        print("Simulation complete.")

if __name__ == "__main__":
    from detectors.rules import RuleEngine, EventBus
    
    engine = SimulationEngine()
    event_bus = EventBus()
    detector = RuleEngine()
    
    event_bus.subscribe(detector.evaluate_telemetry)
    engine.simulate_continuous(duration_sec=10, tick_interval=1.0, event_bus=event_bus)
