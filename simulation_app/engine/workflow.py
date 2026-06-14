import time
import json
from uuid import uuid4
from engine.ollama_client import get_ollama
from engine.rag_store import get_rag_store
from engine.logger import get_system_logger

class IncidentManager:
    def __init__(self):
        self.incidents = {} # incident_id -> {details, tasks, status}
        self.rca_reports = []

    def trigger_incident(self, machine_id, failure_mode, initial_telemetry):
        incident_id = f"INC-{int(time.time())}"
        
        # Load pre-generated ontology from disk
        import os
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data', 'ontology_cache')
        safe_name = failure_mode.replace(" ", "_").replace("/", "_") + ".json"
        cache_path = os.path.join(cache_dir, safe_name)
        
        tasks = []
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
            except:
                pass
                
        if not tasks:
            # Fallback if ontology hasn't been generated yet
            tasks = [
                {"id": "t1", "title": "Acknowledge Alert", "type": "automated", "status": "pending", "depends_on": [], "sipoc": {"Supplier": "Telemetry", "Input": "Alert", "Process": "Log", "Output": "Ack", "Customer": "System"}},
                {"id": "t2", "title": "Manual Verification", "type": "manual", "status": "pending", "depends_on": ["t1"], "sipoc": {"Supplier": "Operator", "Input": "Sight", "Process": "Verify", "Output": "Clearance", "Customer": "Manager"}},
                {"id": "t3", "title": "Root Cause Analysis", "type": "automated", "status": "pending", "depends_on": ["t2"], "sipoc": {"Supplier": "Logs", "Input": "Data", "Process": "Analyze", "Output": "RCA", "Customer": "DB"}}
            ]
        
        incident = {
            "id": incident_id,
            "machine_id": machine_id,
            "failure_mode": failure_mode,
            "status": "open",
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": None,
            "tasks": tasks,
            "logs": [],
            "telemetry_slice": initial_telemetry
        }
        
        self.incidents[incident_id] = incident
        return incident_id
        
    def get_incident(self, incident_id):
        return self.incidents.get(incident_id)
        
    def get_all_incidents(self):
        return list(self.incidents.values())
        
    def resolve_task(self, inc_id, task_id, notes=None, review_note=None):
        if inc_id in self.incidents:
            for t in self.incidents[inc_id]["tasks"]:
                if t["id"] == task_id:
                    t["status"] = "completed"
                    if notes:
                        t["notes"] = notes
                    if review_note:
                        t["review_note"] = review_note
                    self.incidents[inc_id]["logs"].append(f"[{time.strftime('%H:%M:%S')}] Task '{t['title']}' manually completed. Review: {review_note}")
                    
                    self._check_incident_completion(inc_id)
                    return True
        return False

    def _check_incident_completion(self, incident_id):
        incident = self.incidents[incident_id]
        all_complete = all(t["status"] == "completed" for t in incident["tasks"])
        if all_complete and incident["status"] != "closed":
            incident["status"] = "closed"
            incident["resolved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            incident["logs"].append(f"[{time.strftime('%H:%M:%S')}] Incident Closed. Triggering Agentic RCA...")
            
            # Guarantee RCA is generated
            from engine.agents import MultiAgentEngine
            agents_engine = MultiAgentEngine(self)
            import threading
            threading.Thread(target=agents_engine.generate_rca, args=(incident,), daemon=True).start()

    def tick_automation(self, agents_engine):
        """
        Called periodically. Finds 'pending' automated tasks whose dependencies are met,
        and runs them via the multi-agent engine.
        """
        logger = get_system_logger()
        for inc_id, inc in self.incidents.items():
            if inc["status"] != "open":
                continue
                
            for t in inc["tasks"]:
                if t["status"] == "pending" and t["type"] == "automated":
                    # Check dependencies
                    deps_met = True
                    for dep_id in t["depends_on"]:
                        dep_task = next((dt for dt in inc["tasks"] if dt["id"] == dep_id), None)
                        if dep_task and dep_task["status"] != "completed":
                            deps_met = False
                            break
                            
                    if deps_met:
                        t["status"] = "in_progress"
                        logger.info(f"[Automation] Executing task '{t['title']}' for Incident {inc_id}")
                        self.incidents[inc_id]["logs"].append(f"[{time.strftime('%H:%M:%S')}] Auto-Task '{t['title']}' started.")
                        
                        # Execute in background so it doesn't block
                        import threading
                        threading.Thread(target=agents_engine.run_automated_task, args=(inc, t), daemon=True).start()

# Singleton
_manager = IncidentManager()
def get_incident_manager():
    return _manager
