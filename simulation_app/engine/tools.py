"""
Multi-Agent Tool Registry
Each tool is a callable that fetches data from the plant databases, live telemetry,
or the RAG vector store. The AI planner decides which tools to invoke based on the query.
"""

import os
import json

PLANT_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'plant_data')
DB_DIR = os.path.join(PLANT_DATA_DIR, 'databases')


def _load_json_db(filename):
    """Helper to load a JSON database file from plant_data/databases/"""
    path = os.path.join(DB_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"Failed to load {filename}: {str(e)}"}


# ========== DATABASE QUERY TOOLS ==========

def tool_get_inventory():
    """Get raw materials inventory levels, stock, and reorder status."""
    return _load_json_db('raw_materials_inventory.json')

def tool_get_spare_parts():
    """Get spare parts inventory with stock levels, reorder points, and costs."""
    return _load_json_db('spare_parts_inventory.json')

def tool_get_machines_master():
    """Get master list of all machines with specifications, zones, and status."""
    return _load_json_db('machines_master.json')

def tool_get_workers():
    """Get all worker records: names, roles, skills, certifications, shifts."""
    return _load_json_db('workers.json')

def tool_get_maintenance_history():
    """Get maintenance history: past repairs, PM schedules, downtime records."""
    return _load_json_db('maintenance_history.json')

def tool_get_incident_reports():
    """Get historical incident reports with root causes and corrective actions."""
    return _load_json_db('incident_reports.json')

def tool_get_alarm_events():
    """Get alarm event log: timestamps, severity, machine, acknowledgment status."""
    return _load_json_db('alarm_events.json')

def tool_get_downtime_logs():
    """Get downtime logs: planned vs unplanned, duration, reason codes."""
    return _load_json_db('downtime_logs.json')

def tool_get_production_records():
    """Get production records: output quantities, reject rates, batch tracking."""
    return _load_json_db('production_records.json')

def tool_get_quality_inspections():
    """Get quality inspection results: pass/fail, dimensions, defect types."""
    return _load_json_db('quality_inspections.json')

def tool_get_calibration_records():
    """Get calibration records: instruments, due dates, results."""
    return _load_json_db('calibration_records.json')

def tool_get_training_records():
    """Get training records: employee skills matrix, certifications, expiry."""
    return _load_json_db('training_records.json')

def tool_get_vendor_database():
    """Get vendor database: supplier names, contacts, lead times, ratings."""
    return _load_json_db('vendor_database.json')

def tool_get_shifts_and_crews():
    """Get shift schedules and crew assignments."""
    return _load_json_db('shifts_and_crews.json')

def tool_get_shift_handover_history():
    """Get shift handover notes and pending items from previous shifts."""
    return _load_json_db('shift_handover_history.json')

def tool_get_audit_logs():
    """Get audit trail: who changed what, when, system access logs."""
    return _load_json_db('audit_logs.json')

def tool_get_zones_and_cameras():
    """Get zone layout and CCTV camera positions with coverage areas."""
    return _load_json_db('zones_and_cameras.json')


# ========== DOCUMENT TOOLS ==========

def tool_get_machine_manual(machine_folder=None):
    """Read a machine user manual. Pass machine folder name like 'CNC-101_Slitting_Machine'."""
    machines_dir = os.path.join(PLANT_DATA_DIR, 'machines')
    if machine_folder:
        manual_path = os.path.join(machines_dir, machine_folder, 'user_manual.md')
        if os.path.exists(manual_path):
            with open(manual_path, 'r', encoding='utf-8') as f:
                return f.read()[:3000]  # Truncate for LLM context
        return f"Manual not found for {machine_folder}"
    # List available manuals
    result = []
    if os.path.exists(machines_dir):
        for folder in os.listdir(machines_dir):
            manual = os.path.join(machines_dir, folder, 'user_manual.md')
            if os.path.exists(manual):
                result.append(folder)
    return {"available_manuals": result}

def tool_get_failure_modes(machine_folder=None):
    """Read failure modes document for a machine."""
    machines_dir = os.path.join(PLANT_DATA_DIR, 'machines')
    if machine_folder:
        fm_path = os.path.join(machines_dir, machine_folder, 'failure_modes.md')
        if os.path.exists(fm_path):
            with open(fm_path, 'r', encoding='utf-8') as f:
                return f.read()[:3000]
        return f"Failure modes document not found for {machine_folder}"
    return {"available": [f for f in os.listdir(machines_dir) if os.path.isdir(os.path.join(machines_dir, f))]}

def tool_get_safety_guidelines():
    """Get plant safety guidelines and procedures."""
    path = os.path.join(PLANT_DATA_DIR, 'safety', 'safety_guidelines.md')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()[:3000]
    return "Safety guidelines not found."

def tool_get_sop(sop_name=None):
    """Get Standard Operating Procedures. Pass SOP filename or None to list all."""
    sops_dir = os.path.join(PLANT_DATA_DIR, 'sops')
    if sop_name:
        path = os.path.join(sops_dir, sop_name)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()[:3000]
        return f"SOP {sop_name} not found."
    if os.path.exists(sops_dir):
        return {"available_sops": [f for f in os.listdir(sops_dir) if f.endswith('.md')]}
    return {"available_sops": []}

def tool_get_plant_profile():
    """Get the plant profile including capacity, location, and specifications."""
    path = os.path.join(PLANT_DATA_DIR, 'plant_overview', 'plant_profile.md')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()[:3000]
    return "Plant profile not found."


# ========== ANALYSIS TOOLS ==========

def tool_analyze_inventory_status():
    """Analyze inventory levels and flag items below reorder point."""
    data = tool_get_spare_parts()
    if isinstance(data, dict) and "error" in data:
        return data
    low_stock = []
    if isinstance(data, list):
        for item in data:
            qty = item.get('quantity_in_stock', item.get('current_stock', 0))
            reorder = item.get('reorder_level', item.get('reorder_point', 0))
            if isinstance(qty, (int, float)) and isinstance(reorder, (int, float)):
                if qty <= reorder:
                    low_stock.append({
                        "part": item.get('part_name', item.get('name', 'Unknown')),
                        "stock": qty,
                        "reorder_level": reorder,
                        "status": "CRITICAL" if qty == 0 else "LOW"
                    })
    return {"low_stock_items": low_stock, "total_parts_checked": len(data) if isinstance(data, list) else 0}

def tool_analyze_downtime():
    """Analyze downtime patterns: total hours, top reasons, machine ranking."""
    data = tool_get_downtime_logs()
    if isinstance(data, dict) and "error" in data:
        return data
    if not isinstance(data, list):
        return {"error": "Unexpected data format"}
    total_hours = 0
    by_machine = {}
    by_reason = {}
    for entry in data:
        dur = entry.get('duration_hours', entry.get('duration_minutes', 0) / 60)
        machine = entry.get('machine_id', 'Unknown')
        reason = entry.get('reason', entry.get('failure_type', 'Unknown'))
        total_hours += dur
        by_machine[machine] = by_machine.get(machine, 0) + dur
        by_reason[reason] = by_reason.get(reason, 0) + dur
    return {
        "total_downtime_hours": round(total_hours, 1),
        "by_machine": dict(sorted(by_machine.items(), key=lambda x: -x[1])[:5]),
        "by_reason": dict(sorted(by_reason.items(), key=lambda x: -x[1])[:5])
    }

def tool_analyze_production():
    """Analyze production metrics: output totals, efficiency, reject rates."""
    data = tool_get_production_records()
    if isinstance(data, dict) and "error" in data:
        return data
    if not isinstance(data, list):
        return {"error": "Unexpected data format"}
    total_output = 0
    total_reject = 0
    by_machine = {}
    for entry in data:
        output = entry.get('quantity_produced', entry.get('output', 0))
        reject = entry.get('rejected', entry.get('reject_count', 0))
        machine = entry.get('machine_id', 'Unknown')
        total_output += output
        total_reject += reject
        if machine not in by_machine:
            by_machine[machine] = {"output": 0, "rejected": 0}
        by_machine[machine]["output"] += output
        by_machine[machine]["rejected"] += reject
    return {
        "total_output": total_output,
        "total_rejected": total_reject,
        "reject_rate_pct": round(total_reject / max(total_output, 1) * 100, 2),
        "by_machine": by_machine
    }


# ========== TOOL REGISTRY ==========

TOOL_REGISTRY = {
    "get_inventory": {
        "fn": tool_get_inventory,
        "description": "Get raw materials inventory levels, stock quantities, and reorder status"
    },
    "get_spare_parts": {
        "fn": tool_get_spare_parts,
        "description": "Get spare parts inventory with stock levels, reorder points, costs"
    },
    "get_machines_master": {
        "fn": tool_get_machines_master,
        "description": "Get master list of all machines with specs, zones, status"
    },
    "get_workers": {
        "fn": tool_get_workers,
        "description": "Get worker records: names, roles, skills, certifications, shifts"
    },
    "get_maintenance_history": {
        "fn": tool_get_maintenance_history,
        "description": "Get maintenance history: past repairs, PM schedules, downtime"
    },
    "get_incident_reports": {
        "fn": tool_get_incident_reports,
        "description": "Get historical incident reports with root causes and corrective actions"
    },
    "get_alarm_events": {
        "fn": tool_get_alarm_events,
        "description": "Get alarm event log with timestamps, severity, acknowledgment"
    },
    "get_downtime_logs": {
        "fn": tool_get_downtime_logs,
        "description": "Get downtime logs: planned vs unplanned, duration, reasons"
    },
    "get_production_records": {
        "fn": tool_get_production_records,
        "description": "Get production records: quantities, reject rates, batch data"
    },
    "get_quality_inspections": {
        "fn": tool_get_quality_inspections,
        "description": "Get quality inspection results: pass/fail, dimensions, defects"
    },
    "get_calibration_records": {
        "fn": tool_get_calibration_records,
        "description": "Get calibration records: instruments, due dates, results"
    },
    "get_training_records": {
        "fn": tool_get_training_records,
        "description": "Get training records: employee skills, certifications, expiry"
    },
    "get_vendor_database": {
        "fn": tool_get_vendor_database,
        "description": "Get vendor/supplier database: contacts, lead times, ratings"
    },
    "get_shifts_and_crews": {
        "fn": tool_get_shifts_and_crews,
        "description": "Get shift schedules and crew assignments"
    },
    "get_shift_handover_history": {
        "fn": tool_get_shift_handover_history,
        "description": "Get shift handover notes and pending items"
    },
    "get_audit_logs": {
        "fn": tool_get_audit_logs,
        "description": "Get audit trail: who changed what, when"
    },
    "get_zones_and_cameras": {
        "fn": tool_get_zones_and_cameras,
        "description": "Get zone layout and CCTV camera positions"
    },
    "get_safety_guidelines": {
        "fn": tool_get_safety_guidelines,
        "description": "Get plant safety guidelines and procedures"
    },
    "get_plant_profile": {
        "fn": tool_get_plant_profile,
        "description": "Get plant profile: capacity, location, specifications"
    },
    "analyze_inventory_status": {
        "fn": tool_analyze_inventory_status,
        "description": "Analyze spare parts inventory and flag low-stock items"
    },
    "analyze_downtime": {
        "fn": tool_analyze_downtime,
        "description": "Analyze downtime patterns: total hours, top reasons, rankings"
    },
    "analyze_production": {
        "fn": tool_analyze_production,
        "description": "Analyze production metrics: output, efficiency, reject rates"
    },
}


def get_tool_descriptions():
    """Return a formatted string of all available tools for the LLM planner."""
    lines = []
    for name, info in TOOL_REGISTRY.items():
        lines.append(f"- {name}: {info['description']}")
    return "\n".join(lines)


def execute_tools(tool_names):
    """Execute a list of tool names and return their combined results."""
    results = {}
    for name in tool_names:
        name = name.strip()
        if name in TOOL_REGISTRY:
            try:
                result = TOOL_REGISTRY[name]["fn"]()
                # Truncate large results
                result_str = json.dumps(result, indent=2, default=str)
                if len(result_str) > 4000:
                    result_str = result_str[:4000] + "\n... [truncated]"
                results[name] = result_str
            except Exception as e:
                results[name] = f"Error: {str(e)}"
        else:
            results[name] = f"Unknown tool: {name}"
    return results
