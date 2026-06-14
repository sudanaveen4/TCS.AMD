import sys
import os
import json
import requests
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.schema import Incident, Status
from database.json_db import JSONDatabase

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

class RCAEngine:
    def __init__(self, db_dir: str = "data"):
        self.db = JSONDatabase(db_dir)
        self.docs_dir = os.path.join(db_dir, "documents")

    def _get_machine_manual(self, machine_id: str) -> str:
        # Match machine ID to manual file
        prefix_map = {
            "M1": "M1_Buhler_Mixer_Manual.md",
            "M2": "M2_Coperion_Extruder_Manual.md",
            "M3": "M3_CryoCool_Tunnel_Manual.md",
            "M4": "M4_Urschel_Cutter_Manual.md",
            "M5": "M5_ABB_Palletizer_Manual.md"
        }
        filename = prefix_map.get(machine_id)
        if not filename: return ""
        
        filepath = os.path.join(self.docs_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def _get_historical_logs(self) -> str:
        filepath = os.path.join(self.docs_dir, "Historical_Maintenance_Logs.md")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def generate_rca(self, incident: Incident) -> str:
        manual_context = self._get_machine_manual(incident.machine_id)
        historical_context = self._get_historical_logs()

        prompt = f"""You are the Root Cause Analysis (RCA) Copilot for a Petrochemical Plant.
An AI Digital Twin model has flagged a high probability of failure for a machine.
Analyze the incident based on the provided machine troubleshooting guide.
Keep your answer under 100 words, highly technical, and suggest a specific root cause and action.

INCIDENT DETAILS:
Machine: {incident.machine_id}
Type: {incident.incident_type}
Severity: {incident.severity}
AI Failure Probability: {incident.failure_probability}%
Remaining Useful Life: {incident.rul_days} Days

TROUBLESHOOTING GUIDE EXCERPT:
{manual_context[:1500]}...

Based on the evidence and the troubleshooting matrix, what is the most likely root cause and recommended action?"""

        print(f"Requesting RCA from Ollama ({MODEL_NAME}) for {incident.incident_id}...")
        try:
            response = requests.post(OLLAMA_URL, json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }, timeout=10)
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                return result
            else:
                print(f"Ollama Error: {response.status_code}")
                return "Root Cause Analysis failed: Ollama model returned an error."
                
        except requests.exceptions.RequestException as e:
            print(f"Ollama Connection Error: Ensure Ollama is running and {MODEL_NAME} is pulled.")
            # Fallback mock for hackathon testing if Ollama is off
            return f"Simulated RCA: Based on the {incident.machine_id} diagnostic guide, '{incident.incident_type}' indicates a failing subsystem. Probability is {incident.failure_probability}%. Schedule maintenance immediately."

    def process_unresolved_incidents(self):
        incidents = self.db.read_table("incidents", Incident)
        updated = False
        
        for incident in incidents:
            # We run RCA for OPEN incidents that don't have a root_cause yet
            if incident.status == Status.OPEN and not incident.root_cause:
                rca_result = self.generate_rca(incident)
                incident.root_cause = rca_result
                self.db.update("incidents", "incident_id", incident.incident_id, incident)
                print(f"RCA completed for {incident.incident_id}: {rca_result}")
                updated = True
                
        if not updated:
            print("No new incidents required RCA.")

if __name__ == "__main__":
    engine = RCAEngine()
    engine.process_unresolved_incidents()
