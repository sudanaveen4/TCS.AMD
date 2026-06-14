import os
import sys
import json
import time

# Ensure we can import from engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engine.ollama_client import get_ollama

def generate_all():
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data')
    incidents_file = os.path.join(docs_dir, 'databases', 'incident_reports.json')
    output_file = os.path.join(docs_dir, 'sops', 'auto_generated_sipocs.json')
    
    with open(incidents_file, 'r', encoding='utf-8') as f:
        incidents = json.load(f)
        
    ollama = get_ollama()
    system = "You are an expert industrial plant orchestrator. Output strictly valid JSON without any markdown formatting."
    
    generated_flows = []
    
    for inc in incidents:
        print(f"Generating SIPOC flow for Incident {inc['incident_id']} - {inc['failure_mode'] if 'failure_mode' in inc else inc.get('category', 'unknown')}...")
        
        prompt = f"""
        Based on the following incident data:
        Incident ID: {inc['incident_id']}
        Machine: {inc.get('machine_id', 'Unknown')}
        Description: {inc['description']}
        Root Cause: {inc['root_cause']}
        Corrective Action: {inc['corrective_action']}
        
        Generate a strict JSON array of resolution tasks (SIPOC DAG) to handle this type of incident if it occurs again.
        Each task must follow this JSON schema exactly:
        {{
            "id": "t1",
            "title": "Task Name",
            "type": "automated" or "manual",
            "status": "pending",
            "depends_on": ["previous_task_id", ...],
            "sipoc": {{
                "Supplier": "...", "Input": "...", "Process": "...", "Output": "...", "Customer": "..."
            }}
        }}
        Return ONLY the raw JSON array.
        """
        
        try:
            raw_tasks = ollama.generate(prompt, system=system, format="json", timeout=60)
            tasks = json.loads(raw_tasks)
            generated_flows.append({
                "incident_type": inc.get('category', 'unknown'),
                "machine_id": inc.get('machine_id', 'Unknown'),
                "description_context": inc['description'],
                "sipoc_tasks": tasks
            })
            print(f" -> Success! Generated {len(tasks)} tasks.")
        except Exception as e:
            print(f" -> Failed: {e}")
            
    print(f"Saving {len(generated_flows)} flows to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(generated_flows, f, indent=2)

if __name__ == "__main__":
    generate_all()
