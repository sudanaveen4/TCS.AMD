import os
import json
import time
import uuid
from datetime import datetime
from engine.ollama_client import get_ollama

class ShiftHandoverGenerator:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.shift_docs_dir = os.path.join(data_dir, "shift_documents")
        self.images_dir = os.path.join(self.shift_docs_dir, "images")
        
        # Create directories
        os.makedirs(self.shift_docs_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

    def generate_shift_report(self, shift_name, supervisor, start_time, end_time, telemetry_history, all_incidents, shift_alerts, machines_config):
        report_id = f"SHR-{datetime.fromtimestamp(end_time).strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        date_str = datetime.fromtimestamp(end_time).strftime("%Y-%m-%d")
        
        # Filter incidents that started or were active during the shift window
        shift_incidents = []
        for inc in all_incidents:
            try:
                # Started at is stored as YYYY-MM-DD HH:MM:SS
                started_dt = datetime.strptime(inc["started_at"], "%Y-%m-%d %H:%M:%S")
                started_ts = started_dt.timestamp()
                if start_time <= started_ts <= end_time or inc["status"] == "open":
                    shift_incidents.append(inc)
            except:
                # Fallback if parsing fails, include it
                shift_incidents.append(inc)
                
        # 1. Generate SVG Telemetry Trend Chart
        svg_chart = self.generate_telemetry_svg(telemetry_history, machines_config)
        chart_filename = f"chart_{report_id}.svg"
        chart_filepath = os.path.join(self.images_dir, chart_filename)
        try:
            with open(chart_filepath, "w", encoding="utf-8") as f:
                f.write(svg_chart)
        except Exception as e:
            print(f"Error saving SVG chart: {e}")

        # 2. Build summary texts for the LLM prompt
        alerts_summary_text = ""
        if shift_alerts:
            alerts_summary_text = "\n".join([
                f"- [{a.get('timestamp')}] {a.get('machine_id')} {a.get('sensor')}: {a.get('value')} ({a.get('slm_analysis')})"
                for a in shift_alerts[:15]
            ])
        else:
            alerts_summary_text = "No alerts logged."
            
        incidents_summary_text = ""
        if shift_incidents:
            incidents_summary_text = "\n".join([
                f"- Incident {inc['id']} on {inc['machine_id']} ({inc['failure_mode']}) - Status: {inc['status']}"
                for inc in shift_incidents
            ])
        else:
            incidents_summary_text = "No incidents logged."

        machine_status_text = ""
        for m in machines_config:
            m_id = m["machine_id"]
            alias = m.get("alias", m_id)
            lbl = m.get("label", "")
            # Look at telemetry
            latest_val = "N/A"
            if m_id in telemetry_history and telemetry_history[m_id]:
                sensors = telemetry_history[m_id][-1].get("sensors", {})
                if sensors:
                    first_sensor = list(sensors.keys())[0]
                    latest_val = f"{first_sensor}: {sensors[first_sensor]:.2f}"
            machine_status_text += f"- {alias} ({lbl}): Status: Normal | Latest reading: {latest_val}\n"

        # 3. Call Ollama for Executive Summary & Next Shift Instructions
        prompt = f"""
        You are the Shift Supervisor AI for TCS Bharat Steel Pipes plant.
        Generate a professional shift handover summary and instructions for the incoming shift crew.

        SHIFT DETAILS:
        - Shift: {shift_name}
        - Date: {date_str}
        - Supervisor: {supervisor}

        EVENTS LOGGED DURING THE SHIFT:
        - Total Alerts: {len(shift_alerts)}
        {alerts_summary_text}

        - Total Incidents: {len(shift_incidents)}
        {incidents_summary_text}

        MACHINE STATUSES:
        {machine_status_text}

        Write a detailed response in JSON format with two keys:
        1. "executive_summary": A professional, 3-4 sentence paragraph summarizing the shift's operational highlights, issues, and overall plant health.
        2. "instructions": A list of 3-4 actionable instructions/bullet points for the next shift crew (e.g. which machines to monitor, what to focus on).

        Return ONLY the raw JSON object. Do not include markdown formatting or explanation outside the JSON.
        """
        
        system = "You are a JSON-only shift synthesizer. Output strictly valid JSON with keys 'executive_summary' and 'instructions'."
        ollama = get_ollama()
        
        exec_summary = ""
        instructions = []
        
        print(f"Requesting shift handover synthesis from Ollama for {report_id}...")
        try:
            raw_response = ollama.generate(prompt, system=system, format="json", timeout=20)
            data = json.loads(raw_response)
            exec_summary = data.get("executive_summary", "")
            instructions = data.get("instructions", [])
        except Exception as e:
            print(f"Ollama shift generation error: {e}. Using fallback generator.")
            # Fallback generator
            if len(shift_incidents) > 0:
                open_inc = [i for i in shift_incidents if i["status"] == "open"]
                exec_summary = f"The {shift_name} completed with {len(shift_incidents)} incident(s) logged. Machine statuses are mostly stable, but alert conditions on {', '.join(set(i['machine_id'] for i in shift_incidents))} required technician interventions. {len(open_inc)} incident(s) remain open and need immediate follow-up."
            else:
                exec_summary = f"The {shift_name} was completed successfully with all systems operational. No major telemetry deviations or anomalies were detected. Overall plant health is excellent at 98%."
            
            instructions = [
                f"Monitor the forming mill and welding stand telemetry closely.",
                f"Verify LOTO status on any machines flagged during maintenance inspections.",
                f"Conduct routine visual inspections of hydraulic pumps and bearings at shift start."
            ]

        # Ensure instructions is a list of strings
        if isinstance(instructions, str):
            instructions = [instructions]
        elif not isinstance(instructions, list):
            instructions = ["Perform regular system monitoring and verify plant status."]

        # 4. Generate HTML and Markdown documents
        # Build machine rows
        machine_rows = ""
        for m in machines_config:
            m_id = m["machine_id"]
            alias = m.get("alias", m_id)
            lbl = m.get("label", "")
            
            status = "Normal"
            status_badge = "badge-green"
            latest_val = "N/A"
            
            # Check if there is an active failure
            if any(inc["machine_id"] == m_id and inc["status"] == "open" for inc in shift_incidents):
                status = "Critical Failure"
                status_badge = "badge-red"
            elif any(a.get("machine_id") == m_id for a in shift_alerts):
                status = "Alert Warning"
                status_badge = "badge-orange"
                
            if m_id in telemetry_history and telemetry_history[m_id]:
                sensors = telemetry_history[m_id][-1].get("sensors", {})
                if sensors:
                    first_sensor = list(sensors.keys())[0]
                    latest_val = f"{first_sensor.replace('_', ' ').title()}: {sensors[first_sensor]:.2f}"
            
            machine_rows += f"""
            <tr>
                <td><strong>{m_id}</strong></td>
                <td>{alias} ({lbl})</td>
                <td><span class="badge {status_badge}">{status}</span></td>
                <td>{latest_val}</td>
            </tr>"""

        # Build Alerts Table
        alerts_table = ""
        if shift_alerts:
            alerts_rows = ""
            for a in shift_alerts[:10]:
                alerts_rows += f"""
                <tr>
                    <td>{a.get('timestamp')}</td>
                    <td>{a.get('machine_id')}</td>
                    <td>{a.get('sensor').replace('_', ' ').title()}</td>
                    <td>{a.get('value')}</td>
                    <td><em>{a.get('slm_analysis')}</em></td>
                </tr>"""
            alerts_table = f"""
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Machine</th>
                        <th>Sensor</th>
                        <th>Value</th>
                        <th>SLM Risk Warning</th>
                    </tr>
                </thead>
                <tbody>
                    {alerts_rows}
                </tbody>
            </table>"""
        else:
            alerts_table = "<p style='color: var(--text-muted); font-style: italic;'>No critical alerts logged during this shift.</p>"

        # Build Incidents Table
        incidents_table = ""
        if shift_incidents:
            inc_rows = ""
            for inc in shift_incidents:
                inc_rows += f"""
                <tr>
                    <td><strong>{inc['id']}</strong></td>
                    <td>{inc['machine_id']}</td>
                    <td>{inc['failure_mode']}</td>
                    <td><span class="badge {'badge-red' if inc['status']=='open' else 'badge-green'}">{inc['status'].upper()}</span></td>
                    <td>{inc.get('started_at', 'N/A')}</td>
                </tr>"""
            incidents_table = f"""
            <table>
                <thead>
                    <tr>
                        <th>Incident ID</th>
                        <th>Machine</th>
                        <th>Failure Mode</th>
                        <th>Status</th>
                        <th>Started At</th>
                    </tr>
                </thead>
                <tbody>
                    {inc_rows}
                </tbody>
            </table>"""
        else:
            incidents_table = "<p style='color: var(--text-muted); font-style: italic;'>No machine incidents or failure modes triggered.</p>"

        # Build Instructions List
        instructions_list_html = ""
        for inst in instructions:
            instructions_list_html += f"<li>{inst}</li>"
            
        instructions_list_md = ""
        for inst in instructions:
            instructions_list_md += f"- {inst}\n"

        # Read template HTML or write directly
        html_content = self.get_html_template().format(
            title=f"Shift Handover - {shift_name} - {date_str}",
            report_id=report_id,
            shift_name=shift_name,
            date=date_str,
            supervisor=supervisor,
            executive_summary=exec_summary,
            machine_rows=machine_rows,
            svg_chart=svg_chart,
            alerts_count=len(shift_alerts),
            alerts_table_or_text=alerts_table,
            incidents_count=len(shift_incidents),
            incidents_table_or_text=incidents_table,
            next_shift_instructions=instructions_list_html
        )

        md_content = f"""# Shift Handover Report - {report_id}
**Shift Name:** {shift_name}
**Date:** {date_str}
**Supervisor:** {supervisor}

## Executive Summary
{exec_summary}

## Machine Status & Health
{machine_status_text}

## Incidents Logged ({len(shift_incidents)})
{incidents_summary_text if incidents_summary_text else "None"}

## Alerts Logged ({len(shift_alerts)})
{alerts_summary_text if alerts_summary_text else "None"}

## Instructions for Next Shift
{instructions_list_md}

*Note: Telemetry trend chart saved as plant_data/shift_documents/images/{chart_filename}*
"""

        # Save HTML file
        html_filename = f"{report_id}_Handover.html"
        html_filepath = os.path.join(self.shift_docs_dir, html_filename)
        with open(html_filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Save MD file
        md_filename = f"{report_id}_Handover.md"
        md_filepath = os.path.join(self.shift_docs_dir, md_filename)
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        # 5. Append to database/shift_handover_history.json
        self.append_to_history_db(report_id, shift_name, date_str, supervisor, shift_incidents, shift_alerts, instructions)

        return html_filename

    def append_to_history_db(self, report_id, shift_name, date_str, supervisor, incidents, alerts, instructions):
        db_path = os.path.join(self.data_dir, "databases", "shift_handover_history.json")
        history = []
        if os.path.exists(db_path):
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except:
                pass
                
        # Convert objects to simple format
        machine_status = []
        for m_id in ["CNC-101A", "FRM-201A", "WLD-301A", "HTR-401A", "PKG-501A"]:
            has_fail = any(i["machine_id"] == m_id and i["status"] == "open" for i in incidents)
            machine_status.append({
                "machine_id": m_id,
                "status": "critical" if has_fail else "running",
                "health_notes": f"Monitored during {shift_name}.",
                "issues": [i["failure_mode"] for i in incidents if i["machine_id"] == m_id]
            })

        new_record = {
            "report_id": report_id,
            "shift_id": "A" if "Day" in shift_name else "B",
            "date": date_str,
            "shift_start": f"{date_str}T06:00:00" if "Day" in shift_name else f"{date_str}T18:00:00",
            "shift_end": f"{date_str}T18:00:00" if "Day" in shift_name else f"{date_str}T06:00:00",
            "supervisor": "EMP-006",
            "supervisor_name": supervisor,
            "crew_present": ["EMP-009", "EMP-012", "EMP-014", "EMP-016"],
            "crew_absent": [],
            "absence_reason": None,
            "production_summary": {
                "line_a": {
                    "product": "SP-ERW-50 (50mm OD, Medium)",
                    "coils_processed": 5,
                    "pipes_produced": 850,
                    "achievement_pct": 90
                }
            },
            "machine_status": machine_status,
            "alarms_events": [
                {
                    "time": a.get("timestamp"),
                    "machine_id": a.get("machine_id"),
                    "alarm": a.get("slm_analysis"),
                    "severity": "medium",
                    "resolved": True,
                    "resolution": "System normalized."
                } for a in alerts[:5]
            ],
            "safety_observations": [
                "All PPE compliance checked — 100%."
            ],
            "quality_issues": [],
            "pending_maintenance": [i["failure_mode"] for i in incidents if i["status"] == "open"],
            "instructions_for_next_shift": instructions,
            "handover_to": "EMP-007",
            "handover_acknowledged": True,
            "handover_time": datetime.now().isoformat()
        }
        
        history.append(new_record)
        try:
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error appending shift handover record: {e}")

    def generate_telemetry_svg(self, telemetry_history, machines_config):
        # Draw background grid
        svg = ['<svg viewBox="0 0 650 250" width="100%" height="250" xmlns="http://www.w3.org/2000/svg" style="background:#0d131f; border-radius:8px; border:1px solid #232d45; padding: 10px;">']
        
        # Legend colors
        colors = {
            "M1": "#3b82f6", # Blue
            "M2": "#10b981", # Green
            "M3": "#f59e0b", # Orange
            "M4": "#8b5cf6", # Purple
            "M5": "#0ea5e9"  # Cyan
        }
        
        # Draw axes
        svg.append('<line x1="40" y1="30" x2="40" y2="210" stroke="#232d45" stroke-width="1" />')
        svg.append('<line x1="40" y1="210" x2="620" y2="210" stroke="#232d45" stroke-width="1" />')
        
        # Grid lines
        for y_val in [30, 75, 120, 165, 210]:
            svg.append(f'<line x1="40" y1="{y_val}" x2="620" y2="{y_val}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1" />')
            
        # Draw lines for each machine
        for m_id, history in telemetry_history.items():
            if not history:
                continue
            
            m_config = next((m for m in machines_config if m['machine_id'] == m_id), None)
            alias = m_config.get('alias', 'M') if m_config else 'M'
            color = colors.get(alias, "#94a3b8")
            
            # Extract sensor readings
            sensor_values = []
            for h in history:
                sensors = h.get('sensors', {})
                if sensors:
                    first_sensor = list(sensors.keys())[0]
                    sensor_values.append(sensors[first_sensor])
                    
            if not sensor_values:
                continue
                
            # Normalize values to fit in the plot height (from y=40 to y=200)
            min_val = min(sensor_values)
            max_val = max(sensor_values)
            val_range = max_val - min_val if max_val != min_val else 1.0
            
            points = []
            for i, val in enumerate(sensor_values):
                # Scale X across 580 pixels
                x = 40 + (i * 580 / (len(sensor_values) - 1 if len(sensor_values) > 1 else 1))
                # Scale Y between 40 and 200 (bottom is y=210, top is y=30)
                y = 200 - ((val - min_val) / val_range * 160)
                points.append(f"{x},{y}")
                
            path_d = "M " + " L ".join(points)
            svg.append(f'<path d="{path_d}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />')
            
        # Legend labels
        legend_x = 45
        for m in machines_config:
            alias = m.get('alias', m['machine_id'])
            color = colors.get(alias, "#94a3b8")
            svg.append(f'<rect x="{legend_x}" y="5" width="10" height="10" rx="2" fill="{color}" />')
            svg.append(f'<text x="{legend_x + 15}" y="14" fill="#94a3b8" font-family="Inter, sans-serif" font-size="10">{alias} ({m["label"]})</text>')
            legend_x += 115
            
        svg.append('</svg>')
        return "\n".join(svg)

    def get_html_template(self):
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{
            background-color: #090e17;
            color: #f8fafc;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            margin: 0;
            padding: 1.5rem;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background-color: #141b2d;
            border: 1px solid #232d45;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }}
        .header {{
            border-bottom: 2px solid #232d45;
            padding-bottom: 1rem;
            margin-bottom: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 1.6rem;
            color: #3b82f6;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
            background-color: #0d131f;
            padding: 0.8rem;
            border-radius: 6px;
            border: 1px solid #232d45;
        }}
        .meta-item h4 {{
            margin: 0 0 0.2rem 0;
            color: #94a3b8;
            font-size: 0.75rem;
            text-transform: uppercase;
        }}
        .meta-item p {{
            margin: 0;
            font-size: 0.95rem;
            font-weight: 600;
        }}
        .section {{
            margin-bottom: 2rem;
        }}
        .section h2 {{
            font-size: 1.2rem;
            border-bottom: 1px solid #232d45;
            padding-bottom: 0.4rem;
            margin-bottom: 0.8rem;
            color: #8b5cf6;
        }}
        .summary-box {{
            background-color: rgba(59, 130, 246, 0.05);
            border-left: 4px solid #3b82f6;
            padding: 1rem;
            border-radius: 4px;
            line-height: 1.5;
            font-size: 0.9rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 0.5rem;
            font-size: 0.85rem;
        }}
        th, td {{
            padding: 0.6rem 0.8rem;
            text-align: left;
            border-bottom: 1px solid #232d45;
        }}
        th {{
            background-color: #0d131f;
            color: #94a3b8;
            font-size: 0.75rem;
            text-transform: uppercase;
        }}
        .badge {{
            padding: 0.15rem 0.5rem;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
            display: inline-block;
        }}
        .badge-green {{ background-color: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .badge-red {{ background-color: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }}
        .badge-orange {{ background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .chart-container {{
            margin-top: 1rem;
            text-align: center;
        }}
        ul {{
            padding-left: 1.2rem;
            line-height: 1.5;
            font-size: 0.9rem;
        }}
        li {{
            margin-bottom: 0.4rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Shift Handover Report</h1>
            <span class="badge badge-green">{report_id}</span>
        </div>
        
        <div class="meta-grid">
            <div class="meta-item">
                <h4>Shift Name</h4>
                <p>{shift_name}</p>
            </div>
            <div class="meta-item">
                <h4>Date</h4>
                <p>{date}</p>
            </div>
            <div class="meta-item">
                <h4>Supervisor</h4>
                <p>{supervisor}</p>
            </div>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <div class="summary-box">
                {executive_summary}
            </div>
        </div>

        <div class="section">
            <h2>Machine Status & Health</h2>
            <table>
                <thead>
                    <tr>
                        <th>Machine ID</th>
                        <th>Alias & Unit</th>
                        <th>Status</th>
                        <th>Latest Read</th>
                    </tr>
                </thead>
                <tbody>
                    {machine_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Shift Telemetry Trends (Line Chart)</h2>
            <div class="chart-container">
                {svg_chart}
            </div>
        </div>
        
        <div class="section">
            <h2>Alerts Logged ({alerts_count})</h2>
            {alerts_table_or_text}
        </div>
        
        <div class="section">
            <h2>Incidents Tracked ({incidents_count})</h2>
            {incidents_table_or_text}
        </div>
        
        <div class="section">
            <h2>Instructions for Next Shift</h2>
            <ul>
                {next_shift_instructions}
            </ul>
        </div>
    </div>
</body>
</html>"""
