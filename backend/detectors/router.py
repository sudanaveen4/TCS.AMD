import sys
import os
import json
import uuid
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.schema import Incident, Alert, Task, Severity, Status
from database.json_db import JSONDatabase

class AgentRouter:
    def __init__(self, db_dir: str = "data"):
        self.db = JSONDatabase(db_dir)
        
    def process_new_incidents(self):
        incidents = self.db.read_table("incidents", Incident)
        alerts = self.db.read_table("alerts", Alert)
        tasks = self.db.read_table("tasks", Task)
        
        # Keep track of what we've already processed
        processed_incident_ids = {a.incident_id for a in alerts}
        
        for incident in incidents:
            if incident.incident_id not in processed_incident_ids and incident.status == Status.OPEN:
                print(f"Routing Incident {incident.incident_id}...")
                self.route_incident(incident)

    def route_incident(self, incident: Incident):
        # Petrochemical Persona Routing Logic based on AI predicted failure mode
        persona_routing = {
            "bearing_failure": ["maintenance", "reliability"],
            "Cavitation": ["operations", "reliability"],
            "Seal Failure": ["maintenance", "operations"],
            "Advanced Bearing Failure": ["maintenance", "reliability", "supervisor"],
            "none": ["supervisor"]
        }
        
        target_personas = persona_routing.get(incident.incident_type, ["supervisor"])
        
        for persona in target_personas:
            # 1. Create an Alert for the persona
            alert = Alert(
                alert_id=f"ALT-{str(uuid.uuid4())[:8].upper()}",
                persona=persona,
                incident_id=incident.incident_id,
                priority=incident.severity,
                status=Status.OPEN
            )
            self.db.insert("alerts", alert)
            print(f" -> Created Alert for {persona.capitalize()}")
            
            # 2. Create a Task for actionable personas
            if persona in ["maintenance", "safety"]:
                eta = 30 if incident.severity == Severity.HIGH else 60
                
                desc_map = {
                    "bearing_failure": f"Inspect bearing on {incident.machine_id} immediately.",
                    "jam": f"Clear blockage in {incident.machine_id}.",
                    "overheating": f"Check cooling jackets and servos on {incident.machine_id}."
                }
                
                task = Task(
                    task_id=f"TSK-{str(uuid.uuid4())[:8].upper()}",
                    persona=persona,
                    owner=f"{persona.capitalize()} Team",
                    incident_id=incident.incident_id,
                    eta_minutes=eta,
                    status=Status.OPEN,
                    description=desc_map.get(incident.incident_type, f"Investigate {incident.incident_type} anomaly.")
                )
                self.db.insert("tasks", task)
                print(f" -> Created Task for {persona.capitalize()} Team")

if __name__ == "__main__":
    router = AgentRouter()
    print("Checking for unrouted incidents...")
    router.process_new_incidents()
    print("Routing complete.")
