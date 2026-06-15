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
            # Fallback if Task Generator flow hasn't been generated yet
            tasks = [
                {"id": "t1", "title": "Acknowledge Alert", "type": "automated", "status": "pending", "depends_on": [], "assigned_to": "System Agent", "sipoc": {"Input": "Telemetry Sensor Data & Active Alerts", "Process": "Log the alert in the system database and acknowledge the warning code.", "Output": "Alert logged & acknowledged"}},
                {"id": "t2", "title": "Manual Verification", "type": "manual", "status": "pending", "depends_on": ["t1"], "assigned_to": "Maintenance Engineer", "sipoc": {"Input": "Machine location & sensor specifications", "Process": "Conduct visual inspection of the machine to check for wear, heat, or abnormal vibration.", "Output": "Visual inspection verified & logged"}},
                {"id": "t3", "title": "Root Cause Analysis", "type": "automated", "status": "pending", "depends_on": ["t2"], "assigned_to": "AI Agent", "sipoc": {"Input": "Historical data & inspection notes", "Process": "Generate comprehensive Root Cause Analysis detailing findings and recommendations.", "Output": "RCA report generated"}}
            ]
        else:
            # Enforce strict sequential order: each task depends on the previous one
            for i in range(1, len(tasks)):
                tasks[i]["depends_on"] = [tasks[i-1]["id"]]
        
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

    def trigger_safety_incident(self, camera_zone, missing_ppe, original_image, annotated_image, detections=None):
        """Create a PPE safety violation incident from camera/vision analysis."""
        incident_id = f"INC-{int(time.time())}"
        
        failure_mode = f"PPE Safety Violation - Missing: {', '.join(missing_ppe)}"
        
        tasks = [
            {
                "id": "t1", "title": "Log Safety Alert",
                "type": "automated", "status": "pending", "depends_on": [],
                "assigned_to": "System Agent",
                "sipoc": {
                    "Input": f"Camera feed from {camera_zone}, detection report",
                    "Process": "Log the PPE violation alert to the safety incident database. Record the camera zone, timestamp, and list of missing PPE items.",
                    "Output": "Safety alert logged to incident_reports.json"
                }
            },
            {
                "id": "t2", "title": "Visual Verification by Safety Officer",
                "type": "manual", "status": "pending", "depends_on": ["t1"],
                "assigned_to": "Safety Officer",
                "image_path": annotated_image,
                "original_image_path": original_image,
                "sipoc": {
                    "Input": f"Annotated image showing PPE violations. Missing items: {', '.join(missing_ppe)}",
                    "Process": "Review the annotated detection image. Verify that the PPE violations detected by the AI model are accurate. Confirm or override the findings. Write notes about the situation.",
                    "Output": "Verification report with officer's review notes"
                }
            },
            {
                "id": "t3", "title": "Issue PPE to Non-Compliant Personnel",
                "type": "manual", "status": "pending", "depends_on": ["t2"],
                "assigned_to": "Safety Officer",
                "sipoc": {
                    "Input": f"List of missing PPE: {', '.join(missing_ppe)}",
                    "Process": "Identify the non-compliant personnel from the camera image. Issue the required PPE items. Brief personnel on safety requirements. Document the corrective action taken.",
                    "Output": "PPE issued, personnel briefed"
                }
            },
            {
                "id": "t4", "title": "Generate Safety RCA Report",
                "type": "automated", "status": "pending", "depends_on": ["t3"],
                "assigned_to": "AI Agent",
                "sipoc": {
                    "Input": "Detection results, officer review, corrective actions",
                    "Process": "Generate a comprehensive Root Cause Analysis for the PPE safety violation using AI. Include the detection image, officer's notes, and recommendations.",
                    "Output": "RCA report saved to rca_documents/"
                }
            }
        ]
        
        incident = {
            "id": incident_id,
            "machine_id": f"CAM-{camera_zone}",
            "failure_mode": failure_mode,
            "status": "open",
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": None,
            "tasks": tasks,
            "logs": [f"[{time.strftime('%H:%M:%S')}] PPE Safety Incident created from vision analysis."],
            "telemetry_slice": [],
            "original_image": original_image,
            "annotated_image": annotated_image,
            "missing_ppe": missing_ppe,
            "detections": detections or [],
            "camera_zone": camera_zone,
            "incident_type": "safety_ppe"
        }
        
        self.incidents[incident_id] = incident
        print(f"[Safety] Created PPE incident {incident_id} for {camera_zone}")
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
            from engine.agents import get_agents_engine
            agents_engine = get_agents_engine()
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
