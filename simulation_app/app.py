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
from engine.vision_engine import get_vision_engine

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize engines
telemetry = TelemetryEngine(data_dir=os.path.join(os.path.dirname(__file__), 'plant_data'))
slm = SLMClient()
ml = MLDetector(slm_client=slm)

# Global state
alerts = []
MAX_ALERTS = 50
alert_history = []
MAX_ALERT_HISTORY = 500
last_shift_time = time.time()

# Load pre-generated ontology flows if available
ONTOLOGY_CACHE = {}
def _load_ontology_cache():
    global ONTOLOGY_CACHE
    sipoc_path = os.path.join(os.path.dirname(__file__), 'plant_data', 'sops', 'auto_generated_sipocs.json')
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
    global alerts, alert_history
    while True:
        telemetry.generate_tick()
        # Evaluate rules/ML
        active = ml.detect_anomalies(telemetry.get_latest_data())
        
        # Simple alert logic
        current_alerts = []
        incident_manager = get_incident_manager()
        
        # detect_anomalies returns a list of dictionaries: [{'machine_id': 'CNC-101A', 'sensor': 'vibration_slitting_head', 'value': 2.12, 'timestamp': 1781...}, ...]
        for a in active:
            m_id = a['machine_id']
            current_alerts.append(a)
            
            # Record to alert history
            alert_history.append({
                "timestamp": a.get("timestamp", time.strftime("%H:%M:%S")),
                "machine_id": m_id,
                "sensor": a.get("sensor"),
                "value": a.get("value"),
                "slm_analysis": a.get("slm_analysis"),
                "timestamp_epoch": time.time()
            })
            if len(alert_history) > MAX_ALERT_HISTORY:
                alert_history.pop(0)
            
            # If we have an injected failure, use it.
            fail_mode = telemetry.active_failures.get(m_id)
            if fail_mode:
                # Create incident if it doesn't exist
                if not any(inc['machine_id'] == m_id and inc['status'] == 'open' for inc in incident_manager.get_all_incidents()):
                    history = telemetry.telemetry_history.get(m_id, [])
                    telemetry_slice = history[-5:] if len(history) >= 5 else history
                    incident_manager.trigger_incident(m_id, fail_mode, telemetry_slice)
        
        alerts = current_alerts
        
        # Check closed incidents and clear their active failures in telemetry and ML status
        for inc in incident_manager.get_all_incidents():
            if inc["status"] == "closed":
                m_id = inc["machine_id"]
                if m_id in telemetry.active_failures:
                    print(f"[Incident Closed] Clearing active telemetry failure for {m_id}")
                    del telemetry.active_failures[m_id]
                    # Also clear ML status for that machine
                    ml.machine_status[m_id] = "running"
        
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
    gpu_name = "CPU"
    try:
        import torch
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                name = torch.cuda.get_device_name(i)
                if any(x in name.lower() for x in ["nvidia", "geforce", "rtx", "gtx", "tesla", "quadro"]):
                    gpu_name = name
                    break
            else:
                gpu_name = torch.cuda.get_device_name(0)
    except Exception as e:
        gpu_name = f"Error: {str(e)}"
    
    return jsonify({
        "status": "running",
        "gpu": gpu_name
    })

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
    active_alerts = list(alerts)
    try:
        incident_manager = get_incident_manager()
        for inc in incident_manager.get_all_incidents():
            if inc["status"] == "open" and inc.get("incident_type") == "safety_ppe":
                already_in = any(a.get("machine_id") == inc["machine_id"] and a.get("sensor") == "PPE Compliance Check" for a in active_alerts)
                if not already_in:
                    active_alerts.append({
                        "timestamp": inc.get("start_time", time.strftime("%H:%M:%S")),
                        "machine_id": inc["machine_id"],
                        "sensor": "PPE Compliance Check",
                        "value": f"{len(inc.get('missing_ppe', []))} violations",
                        "detected_by": "YOLO PPE Safety Model",
                        "slm_analysis": f"PPE violations detected: missing {', '.join(inc.get('missing_ppe', []))}",
                        "timestamp_epoch": time.time()
                    })
    except Exception as e:
        print(f"Error appending safety alerts: {e}")

    return jsonify({
        "telemetry": telemetry.get_latest_data(),
        "alerts": active_alerts,
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
    rca_dir = os.path.join(os.path.dirname(__file__), 'plant_data', 'rca_documents')
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
    
    Generate a strict JSON array of resolution tasks (5-8 tasks) using the Task Generator. Each task must follow this JSON schema:
    {{
        "id": "t1",
        "title": "Task Name",
        "type": "automated" or "manual",
        "status": "pending",
        "depends_on": ["previous_task_id", ...],
        "assigned_to": "Specific Persona (e.g. Maintenance Engineer, Safety Officer) or automated Agent",
        "sipoc": {{
            "Input": "Specify exact JSON database files to query, tools to use, or specific sensory data required.",
            "Process": "Write a 2-3 sentence highly detailed, technical step-by-step procedure of what needs to be performed.",
            "Output": "Specify exactly what logs, database records, or system states will be saved or updated."
        }}
    }}
    Ensure the first task has no dependencies. Include parallel tasks where possible.
    The final task should be an automated 'Root Cause Analysis'.
    Return ONLY the JSON array. No markdown, no explanation.
    """
    
    system = "You are an expert industrial plant orchestrator. Output strictly valid JSON arrays containing detailed Task Generator components (Inputs, Process/Procedure, Outputs)."
    raw_tasks = ollama.generate(prompt, system=system, format="json", timeout=60)
    
    try:
        tasks = json.loads(raw_tasks)
        if isinstance(tasks, dict):
            if "tasks" in tasks and isinstance(tasks["tasks"], list):
                tasks = tasks["tasks"]
            else:
                normalized = []
                for k, v in tasks.items():
                    if isinstance(v, dict):
                        if "id" not in v:
                            v["id"] = k
                        normalized.append(v)
                tasks = normalized
            
        import os
        cache_dir = os.path.join(os.path.dirname(__file__), 'plant_data', 'ontology_cache')
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
        cache_dir = os.path.join(os.path.dirname(__file__), 'plant_data', 'ontology_cache')
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
                
                Generate a strict JSON array of resolution tasks (5-8 tasks) using the Task Generator. Each task must follow this JSON schema:
                {{
                    "id": "t1",
                    "title": "Task Name",
                    "type": "automated" or "manual",
                    "status": "pending",
                    "depends_on": ["previous_task_id", ...],
                    "assigned_to": "Specific Persona",
                    "sipoc": {{
                        "Input": "Specify exact JSON database files to query, tools to use, or specific sensory data required.",
                        "Process": "CRITICAL: Write AT LEAST 50-80 words of highly detailed, technical step-by-step procedures.",
                        "Output": "Specify exactly what logs, database records, or system states will be saved or updated."
                    }}
                }}
                Ensure the first task has no dependencies. Include parallel tasks where possible.
                The final task should be an automated 'Root Cause Analysis'.
                Return ONLY the raw JSON array.
                """
                system = "You are an expert industrial plant orchestrator. Output strictly valid JSON arrays containing detailed Task Generator components (Inputs, Process/Procedure, Outputs)."
                raw_tasks = ollama.generate(prompt, system=system, format="json", timeout=60)
                
                tasks = json.loads(raw_tasks)
                if isinstance(tasks, dict):
                    if "tasks" in tasks and isinstance(tasks["tasks"], list):
                        tasks = tasks["tasks"]
                    else:
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
    db_dir = os.path.join(os.path.dirname(__file__), 'plant_data', 'databases')
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
    db_dir = os.path.join(os.path.dirname(__file__), 'plant_data', 'databases')
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

# Folders to exclude from the general documents listing
_DOC_EXCLUDED_FOLDERS = {'databases', 'OpenCV', 'ontology_cache'}

@app.route('/api/documents', methods=['GET'])
def list_documents():
    docs_dir = os.path.join(os.path.dirname(__file__), 'plant_data')
    if not os.path.exists(docs_dir):
        return jsonify({"documents": []})
        
    docs = []
    for root, dirs, files in os.walk(docs_dir):
        # Skip excluded folders
        rel_root = os.path.relpath(root, docs_dir).replace('\\', '/')
        top_folder = rel_root.split('/')[0]
        if top_folder in _DOC_EXCLUDED_FOLDERS:
            continue
        
        for file in files:
            # Skip model files and non-document extensions
            if file.lower().endswith(('.pt', '.pth', '.onnx', '.bin', '.ipynb')):
                continue
            if file.lower().endswith(('.md', '.txt', '.json', '.png', '.jpg', '.svg')):
                rel_path = os.path.relpath(os.path.join(root, file), docs_dir)
                web_path = rel_path.replace('\\', '/')
                folder = rel_root
                ext = os.path.splitext(file)[1].lower()
                icon = "fa-file-lines"
                if ext == '.json': icon = "fa-database"
                elif ext == '.md': icon = "fa-file-code"
                elif ext in ('.png', '.jpg'): icon = "fa-file-image"
                elif ext == '.svg': icon = "fa-chart-area"
                docs.append({"name": file, "path": web_path, "folder": folder, "icon": icon, "ext": ext})
    return jsonify({"documents": docs})

@app.route('/api/generate_shift_handover', methods=['POST'])
def api_generate_shift_handover():
    global last_shift_time, alert_history
    data = request.json or {}
    shift_name = data.get('shift_name', 'Day Shift')
    supervisor = data.get('supervisor', 'Supervisor (Plant Manager)')
    manual = data.get('manual', False)
    
    current_time = time.time()
    
    # In manual generation, we look back 5 minutes (or since last shift, whichever is greater)
    # In automatic rollover, we look back since last_shift_time
    if manual:
        start_t = max(last_shift_time, current_time - 300)
    else:
        start_t = last_shift_time
        
    end_t = current_time
    
    # Filter alerts since start_t
    shift_alerts = [
        a for a in alert_history 
        if start_t <= a.get('timestamp_epoch', 0) <= end_t
    ]
    
    # If no alerts inside window, but some active alerts, include them as safety
    if not shift_alerts and alerts:
        for a in alerts:
            shift_alerts.append({
                "timestamp": a.get("timestamp", time.strftime("%H:%M:%S")),
                "machine_id": a.get("machine_id"),
                "sensor": a.get("sensor"),
                "value": a.get("value"),
                "slm_analysis": a.get("slm_analysis")
            })
            
    # Gather telemetry history
    tel_history = telemetry.telemetry_history
    
    # Gather incidents
    inc_manager = get_incident_manager()
    all_inc = inc_manager.get_all_incidents()
    
    # Machines config
    machines_config = telemetry.get_machine_config()
    
    # Generate report
    from engine.shift_manager import ShiftHandoverGenerator
    plant_data_dir = os.path.join(os.path.dirname(__file__), 'plant_data')
    generator = ShiftHandoverGenerator(data_dir=plant_data_dir)
    
    try:
        html_file = generator.generate_shift_report(
            shift_name=shift_name,
            supervisor=supervisor,
            start_time=start_t,
            end_time=end_t,
            telemetry_history=tel_history,
            all_incidents=all_inc,
            shift_alerts=shift_alerts,
            machines_config=machines_config
        )
        
        # Update shift time boundary
        last_shift_time = current_time
        
        return jsonify({
            "success": True,
            "filename": html_file,
            "message": f"Successfully generated shift handover report: {html_file}"
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/shift_documents', methods=['GET'])
def api_list_shift_documents():
    shift_docs_dir = os.path.join(os.path.dirname(__file__), 'plant_data', 'shift_documents')
    if not os.path.exists(shift_docs_dir):
        return jsonify({"documents": []})
        
    docs = []
    for f in os.listdir(shift_docs_dir):
        if f.endswith('.html'):
            filepath = os.path.join(shift_docs_dir, f)
            creation_time = os.path.getmtime(filepath)
            
            # Simple metadata extraction from filename
            name_parts = f.replace('_Handover.html', '').split('-')
            date_str = ""
            if len(name_parts) >= 2:
                raw_date = name_parts[1]
                if len(raw_date) == 8:
                    date_str = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
                    
            docs.append({
                "name": f,
                "path": f"shift_documents/{f}",
                "date": date_str or time.strftime("%Y-%m-%d", time.localtime(creation_time)),
                "timestamp": creation_time,
                "size": os.path.getsize(filepath)
            })
            
    # Sort by timestamp desc
    docs.sort(key=lambda x: x["timestamp"], reverse=True)
    return jsonify({"documents": docs})

@app.route('/api/document/<path:filename>', methods=['GET'])
def serve_document(filename):
    docs_dir = os.path.join(os.path.dirname(__file__), 'plant_data')
    return send_from_directory(docs_dir, filename)

# --- VISION / PPE SAFETY ROUTES ---

@app.route('/api/vision/images', methods=['GET'])
def api_vision_images():
    """List available camera images for PPE analysis."""
    ve = get_vision_engine(os.path.join(os.path.dirname(__file__), 'plant_data'))
    return jsonify({"images": ve.list_available_images()})

@app.route('/api/vision/cameras', methods=['GET'])
def api_vision_cameras():
    """Return camera zones from zones_and_cameras.json."""
    cameras_path = os.path.join(os.path.dirname(__file__), 'plant_data', 'databases', 'zones_and_cameras.json')
    cameras = []
    if os.path.exists(cameras_path):
        try:
            with open(cameras_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    zone = item.get('zone_name', item.get('zone_id', 'Unknown Zone'))
                    cameras.append({"zone": zone, "data": item})
        except Exception as e:
            print(f"Camera load error: {e}")
    if not cameras:
        cameras = [
            {"zone": "Zone A - Assembly Line"},
            {"zone": "Zone B - Welding Bay"},
            {"zone": "Zone C - Storage Yard"},
            {"zone": "Zone D - Loading Dock"}
        ]
    return jsonify({"cameras": cameras})

@app.route('/api/vision/analyze', methods=['POST'])
def api_vision_analyze():
    """Run YOLO PPE detection on a selected image."""
    global alert_history
    data = request.json or {}
    image_name = data.get('image_name')
    camera_zone = data.get('camera_zone', 'Zone A')
    
    if not image_name:
        return jsonify({"error": "No image_name provided"}), 400
    
    ve = get_vision_engine(os.path.join(os.path.dirname(__file__), 'plant_data'))
    report = ve.analyze_image(image_name, camera_zone)
    
    if "error" in report:
        return jsonify(report), 404
    
    # If non-compliant, create a safety incident
    if not report.get('compliant', True):
        missing = report.get('missing_ppe', [])
        incident_manager = get_incident_manager()
        
        # Check for existing open PPE incidents to avoid duplicates
        existing = any(
            inc['status'] == 'open' and 'PPE' in inc.get('failure_mode', '')
            for inc in incident_manager.get_all_incidents()
        )
        
        if not existing:
            inc_id = incident_manager.trigger_safety_incident(
                camera_zone=camera_zone,
                missing_ppe=missing,
                original_image=report.get('original_image', ''),
                annotated_image=report.get('annotated_image', ''),
                detections=report.get('detections', [])
            )
            report['incident_id'] = inc_id
            report['incident_created'] = True
            
            # Log to alert history
            alert_history.append({
                "timestamp": time.strftime("%H:%M:%S"),
                "machine_id": f"CAM-{camera_zone}",
                "sensor": "PPE Compliance Check",
                "value": f"{len(missing)} violations",
                "slm_analysis": f"PPE violations detected: missing {', '.join(missing)}",
                "timestamp_epoch": time.time()
            })
        else:
            report['incident_created'] = False
            report['message'] = 'PPE incident already open'
    
    return jsonify(report)

# --- DATABASE CONTENT ROUTE (for table visualization) ---

@app.route('/api/db_content/<db_name>', methods=['GET'])
def get_db_content(db_name):
    """Return full JSON content of a database file for table rendering."""
    db_dir = os.path.join(os.path.dirname(__file__), 'plant_data', 'databases')
    filepath = os.path.join(db_dir, f"{db_name}.json")
    if not os.path.exists(filepath):
        return jsonify({"error": f"Database '{db_name}' not found"}), 404
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({"database": db_name, "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
