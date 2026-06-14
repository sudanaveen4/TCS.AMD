import os
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import time

# Import our custom engines
from engine.telemetry import TelemetryEngine
from engine.ml_detector import MLDetector
from engine.slm_client import SLMClient
from engine.workflow import get_incident_manager
from engine.agents import get_agents_engine
from engine.rag_store import get_rag_store
from engine.tools import TOOL_REGISTRY, execute_tools

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize engines
telemetry = TelemetryEngine(data_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data'))
slm = SLMClient()
ml = MLDetector(slm_client=slm)

# Global state
alerts = []
MAX_ALERTS = 50

# Load pre-generated ontology flows if available
ONTOLOGY_CACHE = {}
def _load_ontology_cache():
    global ONTOLOGY_CACHE
    sipoc_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data', 'sops', 'auto_generated_sipocs.json')
    if os.path.exists(sipoc_path):
        try:
            with open(sipoc_path, 'r', encoding='utf-8') as f:
                flows = json.load(f)
                for flow in flows:
                    key = flow.get('incident_type', 'unknown')
                    ONTOLOGY_CACHE[key] = flow
                print(f"Loaded {len(flows)} pre-generated ontology flows.")
        except Exception as e:
            print(f"Failed to load ontology cache: {e}")

_load_ontology_cache()

def background_polling():
    while True:
        telemetry.generate_tick()
        # Evaluate rules/ML
        active = ml.detect_anomalies(telemetry.get_latest_data())
        
        global alerts
        # Simple alert logic
        current_alerts = []
        incident_manager = get_incident_manager()
        
        # detect_anomalies returns a list of dictionaries: [{'machine_id': 'CNC-101A', 'sensor': 'vibration_slitting_head', 'value': 2.12, 'timestamp': 1781...}, ...]
        for a in active:
            m_id = a['machine_id']
            current_alerts.append(a)
            
            # If we have an injected failure, use it.
            fail_mode = telemetry.active_failures.get(m_id)
            if fail_mode:
                # Create incident if it doesn't exist
                if not any(inc['machine_id'] == m_id and inc['status'] == 'open' for inc in incident_manager.get_all_incidents()):
                    history = telemetry.telemetry_history.get(m_id, [])
                    telemetry_slice = history[-5:] if len(history) >= 5 else history
                    incident_manager.trigger_incident(m_id, fail_mode, telemetry_slice)
        
        alerts = current_alerts
        
        # Continuously tick automation
        try:
            from engine.agents import get_agents_engine
            incident_manager.tick_automation(get_agents_engine())
        except Exception as e:
            print(f"Automation tick error: {e}")
            
        time.sleep(1)

# Start background telemetry & ML loop
bg_thread = threading.Thread(target=background_polling, daemon=True)
bg_thread.start()

# --- API ROUTES ---

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/control')
def control_panel():
    return send_from_directory('static', 'control.html')

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "running"})

@app.route('/api/plant_config', methods=['GET'])
def get_plant_config():
    """Returns machine data for rendering the UI map"""
    return jsonify({
        "machines": telemetry.get_machine_config(),
        "failure_modes": telemetry.get_failure_modes()
    })

@app.route('/api/live_data', methods=['GET'])
def get_live_data():
    """Returns the latest telemetry and alerts for polling"""
    return jsonify({
        "telemetry": telemetry.get_latest_data(),
        "alerts": alerts,
        "machine_status": ml.get_machine_status()
    })

@app.route('/api/inject_failure', methods=['POST'])
def inject_failure():
    data = request.json
    machine_id = data.get('machine_id')
    failure_mode = data.get('failure_mode')
    
    if machine_id and failure_mode:
        telemetry.inject_failure(machine_id, failure_mode)
        return jsonify({"success": True, "message": f"Injected {failure_mode} on {machine_id}"})
    return jsonify({"success": False, "message": "Missing parameters"}), 400

@app.route('/api/resolve_failures', methods=['POST'])
def resolve_failures():
    telemetry.resolve_all_failures()
    ml.clear_status()
    global alerts
    alerts = []
    return jsonify({"success": True, "message": "All failures resolved. Returning to normal telemetry."})

# --- MULTI-AGENT & SIPOC ROUTES ---

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    persona = data.get('persona', 'Plant Manager')
    query = data.get('query', '')
    
    # Pass live alerts, status, and telemetry as context
    context = {
        "active_alerts_count": len(alerts),
        "machine_status": ml.get_machine_status(),
        "latest_telemetry_summary": {m_id: {k: round(v, 2) for k, v in sensors.get("sensors", {}).items()} 
                                     for m_id, sensors in telemetry.get_latest_data().items()}
    }
    
    agent_engine = get_agents_engine()
    result = agent_engine.chat(persona, query, context)
    return jsonify(result)

@app.route('/api/incidents', methods=['GET'])
def get_all_incidents():
    return jsonify({"incidents": get_incident_manager().get_all_incidents()})

@app.route('/api/incident/<incident_id>', methods=['GET'])
def get_incident_details(incident_id):
    inc = get_incident_manager().get_incident(incident_id)
    if inc: return jsonify(inc)
    return jsonify({"error": "Not found"}), 404

@app.route('/api/resolve_task', methods=['POST'])
def resolve_task():
    data = request.json
    inc_id = data.get('incident_id')
    task_id = data.get('task_id')
    notes = data.get('notes')
    review_note = data.get('review_note')
    
    incident_manager = get_incident_manager()
    success = incident_manager.resolve_task(inc_id, task_id, notes, review_note)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"error": "Failed to resolve"}), 400

@app.route('/api/rca_reports', methods=['GET'])
def get_rca_reports():
    rca_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data', 'rca_documents')
    reports = []
    if os.path.exists(rca_dir):
        for f in os.listdir(rca_dir):
            if f.endswith('.md'):
                try:
                    with open(os.path.join(rca_dir, f), 'r', encoding='utf-8') as file:
                        content = file.read()
                        
                    # Extract basic info from the markdown (we can parse INC ID)
                    inc_id = f.replace('_RCA.md', '')
                    
                    reports.append({
                        "incident_id": inc_id,
                        "machine_id": "Unknown", # We'd have to parse the file or rely on the filename
                        "failure_mode": "See Document",
                        "report": content,
                        "timestamp": os.path.getmtime(os.path.join(rca_dir, f))
                    })
                except Exception as e:
                    print(f"Error loading RCA: {e}")
                    
    # Sort by timestamp desc
    reports.sort(key=lambda x: x["timestamp"], reverse=True)
    return jsonify({"reports": reports})

@app.route('/api/generate_ontology', methods=['POST'])
def api_generate_ontology():
    data = request.json
    failure_mode = data.get('failure_mode', 'Unknown')
    
    # RAG lookup
    rag = get_rag_store()
    docs = rag.retrieve_context(failure_mode, k=3)
    
    # Ollama call
    from engine.ollama_client import get_ollama
    ollama = get_ollama()
    prompt = f"""
    Based on the following plant documentation for failure mode '{failure_mode}':
    {docs}
    
    Generate a strict JSON array of resolution tasks (5-8 tasks). Each task must follow this JSON schema:
    {{
        "id": "t1",
        "title": "Task Name",
        "type": "automated" or "manual",
        "status": "pending",
        "depends_on": ["previous_task_id", ...],
        "assigned_to": "Specific Persona (e.g. Maintenance Engineer, Safety Officer) or automated Agent",
        "sipoc": {{
            "Supplier": "Persona, role, or App Feature providing the input.",
            "Input": "Specify exact JSON database files to query, tools to use, or specific sensory data required.",
            "Process": "Write a 2-3 sentence highly detailed, step-by-step procedure of what needs to be performed.",
            "Output": "Specify exactly what logs, database records, or system states will be saved or updated.",
            "Customer": "Persona or downstream system receiving the output."
        }}
    }}
    Ensure the first task has no dependencies. Include parallel tasks where possible.
    The final task should be an automated 'Root Cause Analysis'.
    Return ONLY the JSON array. No markdown, no explanation.
    """
    
    system = "You are an expert industrial plant orchestrator. Output strictly valid JSON arrays containing detailed SIPOC components."
    raw_tasks = ollama.generate(prompt, system=system, format="json", timeout=60)
    
    try:
        tasks = json.loads(raw_tasks)
        if isinstance(tasks, dict):
            normalized = []
            for k, v in tasks.items():
                if isinstance(v, dict):
                    if "id" not in v:
                        v["id"] = k
                    normalized.append(v)
            tasks = normalized
            
        import os
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data', 'ontology_cache')
        os.makedirs(cache_dir, exist_ok=True)
        safe_name = failure_mode.replace(" ", "_").replace("/", "_") + ".json"
        
        with open(os.path.join(cache_dir, safe_name), 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=4)
            
        return jsonify({"tasks": tasks, "failure_mode": failure_mode})
    except Exception as e:
        return jsonify({"error": str(e), "raw": raw_tasks}), 500

@app.route('/api/generate_all_ontologies', methods=['POST'])
def api_generate_all_ontologies():
    def _bg_generate():
        fmodes = telemetry.get_failure_modes()
        all_failures = []
        for m_id, f_list in fmodes.items():
            for f in f_list:
                all_failures.append((m_id, f))
                
        import os
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data', 'ontology_cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        rag = get_rag_store()
        from engine.ollama_client import get_ollama
        ollama = get_ollama()
        
        for m_id, failure_mode in all_failures:
            print(f"Background generating ontology for: {failure_mode}")
            try:
                docs = rag.retrieve_context(failure_mode, k=3)
                prompt = f"""
                Based on the following plant documentation for failure mode '{failure_mode}':
                {docs}
                
                Generate a strict JSON array of resolution tasks (5-8 tasks). Each task must follow this JSON schema:
                {{
                    "id": "t1",
                    "title": "Task Name",
                    "type": "automated" or "manual",
                    "status": "pending",
                    "depends_on": ["previous_task_id", ...],
                    "assigned_to": "Specific Persona",
                    "sipoc": {{
                        "Supplier": "Persona, role, or App Feature providing the input.",
                        "Input": "Specify exact JSON database files to query, tools to use, or specific sensory data required.",
                        "Process": "CRITICAL: Write AT LEAST 50-80 words of highly detailed, technical step-by-step procedures.",
                        "Output": "Specify exactly what logs, database records, or system states will be saved or updated.",
                        "Customer": "Persona or downstream system receiving the output."
                    }}
                }}
                Ensure the first task has no dependencies. Include parallel tasks where possible.
                The final task should be an automated 'Root Cause Analysis'.
                Return ONLY the raw JSON array.
                """
                system = "You are an expert industrial plant orchestrator. Output strictly valid JSON arrays containing detailed SIPOC components."
                raw_tasks = ollama.generate(prompt, system=system, format="json", timeout=60)
                
                tasks = json.loads(raw_tasks)
                if isinstance(tasks, dict):
                    normalized = []
                    for k, v in tasks.items():
                        if isinstance(v, dict):
                            if "id" not in v:
                                v["id"] = k
                            normalized.append(v)
                    tasks = normalized
                
                safe_name = failure_mode.replace(" ", "_").replace("/", "_") + ".json"
                with open(os.path.join(cache_dir, safe_name), 'w', encoding='utf-8') as f:
                    json.dump(tasks, f, indent=4)
                    
            except Exception as e:
                print(f"Failed to generate ontology for {failure_mode}: {e}")
                
    threading.Thread(target=_bg_generate, daemon=True).start()
    return jsonify({"success": True, "message": "Background generation started for all ontologies. Check Incidents tab."})

@app.route('/api/ontology_cache', methods=['GET'])
def get_ontology_cache():
    """Return all pre-generated ontology flows."""
    return jsonify({"flows": list(ONTOLOGY_CACHE.values())})

# --- DATABASE QUERY ROUTES ---

@app.route('/api/db/<db_name>', methods=['GET'])
def query_database(db_name):
    """Generic database query endpoint. Reads JSON files from plant_data/databases/"""
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data', 'databases')
    filename = f"{db_name}.json"
    filepath = os.path.join(db_dir, filename)
    
    if not os.path.exists(filepath):
        available = [f.replace('.json', '') for f in os.listdir(db_dir) if f.endswith('.json')]
        return jsonify({"error": f"Database '{db_name}' not found", "available": available}), 404
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({"database": db_name, "records": data, "count": len(data) if isinstance(data, list) else 1})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/databases', methods=['GET'])
def list_databases():
    """List all available database files."""
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data', 'databases')
    if not os.path.exists(db_dir):
        return jsonify({"databases": []})
    
    dbs = []
    for f in os.listdir(db_dir):
        if f.endswith('.json'):
            filepath = os.path.join(db_dir, f)
            try:
                with open(filepath, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                    count = len(data) if isinstance(data, list) else 1
            except:
                count = 0
            dbs.append({"name": f.replace('.json', ''), "filename": f, "record_count": count})
    return jsonify({"databases": dbs})

# --- DOCUMENT & VIEWER ROUTES ---

@app.route('/api/documents', methods=['GET'])
def list_documents():
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data')
    if not os.path.exists(docs_dir):
        return jsonify({"documents": []})
        
    docs = []
    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.lower().endswith(('.md', '.txt', '.json', '.png', '.jpg')):
                rel_path = os.path.relpath(os.path.join(root, file), docs_dir)
                web_path = rel_path.replace('\\', '/')
                folder = os.path.relpath(root, docs_dir).replace('\\', '/')
                ext = os.path.splitext(file)[1].lower()
                icon = "fa-file-lines"
                if ext == '.json': icon = "fa-database"
                elif ext == '.md': icon = "fa-file-code"
                elif ext in ('.png', '.jpg'): icon = "fa-file-image"
                docs.append({"name": file, "path": web_path, "folder": folder, "icon": icon, "ext": ext})
    return jsonify({"documents": docs})

@app.route('/api/document/<path:filename>', methods=['GET'])
def serve_document(filename):
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data')
    return send_from_directory(docs_dir, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
