import sys
import os
import json
import requests
import uuid
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.schema import Incident, Task, ShiftReport, Status
from database.json_db import JSONDatabase

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

class HandoverGenerator:
    def __init__(self, db_dir: str = "data"):
        self.db = JSONDatabase(db_dir)
        self.reports_dir = os.path.join(db_dir, "generated_reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_global_shift_report(self):
        incidents = self.db.read_table("incidents", Incident)
        tasks = self.db.read_table("tasks", Task)
        
        # Filter for current shift (mock logic: all records for demo)
        open_incidents = [i for i in incidents if i.status == Status.OPEN]
        resolved_incidents = [i for i in incidents if i.status == Status.RESOLVED]
        open_tasks = [t for t in tasks if t.status == Status.OPEN]
        
        # Prepare context for the LLM
        incident_summaries = "\n".join([f"- [{i.severity.name}] {i.incident_type} on {i.machine_id}: {i.root_cause or 'Under Investigation'}" for i in open_incidents])
        task_summaries = "\n".join([f"- {t.owner}: {t.description} (ETA: {t.eta_minutes}m)" for t in open_tasks])
        
        prompt = f"""You are the Shift Supervisor AI for a High-Moisture Extrusion Plant. 
Generate a professional, structured shift handover report in Markdown.
Keep it concise. Do NOT hallucinate data.

CURRENT OPEN INCIDENTS:
{incident_summaries if incident_summaries else 'None'}

PENDING TASKS:
{task_summaries if task_summaries else 'None'}

RESOLVED INCIDENTS TODAY: {len(resolved_incidents)}

Format the report with headings:
- Executive Summary
- Unresolved Risks & Incidents
- Pending Tasks for Next Shift
- Recommendations
"""

        print("Requesting Shift Report from Ollama...")
        try:
            response = requests.post(OLLAMA_URL, json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }, timeout=15)
            
            if response.status_code == 200:
                report_content = response.json().get("response", "").strip()
            else:
                report_content = "Error generating report: Ollama returned non-200 status."
        except requests.exceptions.RequestException:
            report_content = f"# Shift Handover Report\n\n## Unresolved Risks\n{incident_summaries}\n\n## Pending Tasks\n{task_summaries}\n\n*Note: Generated using fallback mode (Ollama unreachable).*"

        # Save to DB and File
        report_id = f"RPT-{str(uuid.uuid4())[:8].upper()}"
        filename = f"{report_id}_Handover.md"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        report = ShiftReport(
            report_id=report_id,
            shift_id=datetime.utcnow().strftime("%Y-%m-%d_Shift1"),
            persona="supervisor",
            content=report_content,
            report_path=filepath
        )
        self.db.insert("shift_reports", report)
        print(f"Shift report {report_id} generated successfully at {filepath}")

if __name__ == "__main__":
    generator = HandoverGenerator()
    generator.generate_global_shift_report()
