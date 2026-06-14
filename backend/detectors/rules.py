import sys
import os
import json
from datetime import datetime
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.schema import Incident, Severity, Status
from database.json_db import JSONDatabase

class RuleEngine:
    def __init__(self, db_dir: str = "data"):
        self.db = JSONDatabase(db_dir)
        self.incidents_file = os.path.join(db_dir, "incidents.json")
        self.active_incidents = {}  # Track ongoing incidents to avoid spamming

        if not os.path.exists(self.incidents_file):
            with open(self.incidents_file, 'w') as f: json.dump([], f)

    def evaluate_telemetry(self, telemetry: dict):
        prob = telemetry.get("failure_probability", 0.0)
        rul = telemetry.get("rul_days", 999)
        mode = telemetry.get("predicted_failure_mode", "none")
        machine_id = telemetry.get("machine_id", "UNKNOWN")

        # PUMP TROUBLESHOOTING GUIDE - Copilot Escalation Logic
        if prob > 95.0 and rul < 10:
            self._trigger_incident(telemetry, mode, Severity.CRITICAL, 
                                   f"EMERGENCY: Probability {prob}%, RUL {rul} Days")
        elif prob >= 90.0:
            self._trigger_incident(telemetry, mode, Severity.HIGH, 
                                   f"Reliability Engineer Review Required: Probability {prob}%")
        elif prob >= 80.0:
            self._trigger_incident(telemetry, mode, Severity.MEDIUM, 
                                   f"Schedule Maintenance: Probability {prob}%")
        elif prob >= 50.0:
            self._trigger_incident(telemetry, mode, Severity.LOW, 
                                   f"Maintenance Notification: Probability {prob}%")

    def _trigger_incident(self, telemetry: dict, incident_type: str, severity: Severity, desc: str):
        machine_id = telemetry["machine_id"]
        
        # Don't create duplicate open incidents for the same machine and type
        incident_key = f"{machine_id}_{incident_type}_{severity.name}"
        if incident_key in self.active_incidents:
            return

        incident = Incident(
            incident_id=f"INC-{str(uuid.uuid4())[:8].upper()}",
            machine_id=machine_id,
            zone_id="Z1", # General zone
            severity=severity,
            incident_type=incident_type,
            status=Status.OPEN,
            timestamp=datetime.utcnow(),
            failure_probability=telemetry.get("failure_probability", 0.0),
            rul_days=telemetry.get("rul_days", 999)
        )
        
        self.active_incidents[incident_key] = incident.incident_id
        self.db.insert("incidents", incident)
        print(f"[AI COPILOT ALERT] {severity.name}: '{incident_type}' detected on {machine_id}! {desc}")

class EventBus:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def publish(self, telemetry_data_list):
        for data in telemetry_data_list:
            for sub in self.subscribers:
                sub(data)
