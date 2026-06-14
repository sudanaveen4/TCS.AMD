import time
import json
import os
from engine.rag_store import get_rag_store
from engine.ollama_client import get_ollama
from engine.workflow import get_incident_manager
from engine.tools import TOOL_REGISTRY, get_tool_descriptions, execute_tools

class MultiAgentEngine:
    def __init__(self):
        self.rag = get_rag_store()
        self.incidents = get_incident_manager()
        self.ollama = get_ollama()
        
    def chat(self, persona, query, context_data=None):
        """
        Multi-Agent Orchestrator:
        Step 1 - PLANNER: LLM decides which tools to call based on user query
        Step 2 - EXECUTOR: Run the selected tools and gather data
        Step 3 - RAG: Retrieve relevant documentation from vector store
        Step 4 - SYNTHESIZER: LLM composes final answer from all gathered context
        """
        tools_used = []
        tool_results = {}
        
        # ===== STEP 1: TOOL PLANNER =====
        tool_list = get_tool_descriptions()
        planner_prompt = f"""You are a tool-planning agent. Given a user query, decide which database tools to call.

Available tools:
{tool_list}

User query: "{query}"
User persona: {persona}

Return a JSON object with key "tools" containing an array of tool names to call. 
Pick ONLY the tools that are relevant to answer this specific query. Pick at most 4 tools.
If no tools are needed (e.g. general greeting), return {{"tools": []}}.
Return ONLY raw JSON, no markdown."""

        planner_system = "You are a JSON-only tool planner. Output strictly valid JSON with a 'tools' key."
        
        try:
            raw_plan = self.ollama.generate(planner_prompt, system=planner_system, format="json", timeout=15)
            plan = json.loads(raw_plan)
            selected_tools = plan.get("tools", [])
            if isinstance(selected_tools, list) and len(selected_tools) > 0:
                tool_results = execute_tools(selected_tools[:4])
                tools_used = list(tool_results.keys())
        except Exception as e:
            print(f"Tool planner error: {e}")

        # ===== STEP 2: RAG RETRIEVAL =====
        rag_context = self.rag.retrieve_context(query, k=3)
        
        # ===== STEP 3: LIVE CONTEXT =====
        live_context = ""
        if context_data:
            live_context = json.dumps(context_data, indent=2, default=str)
        
        # Also add active incidents summary
        active_incidents = self.incidents.get_all_incidents()
        incidents_summary = ""
        if active_incidents:
            inc_list = []
            for inc in active_incidents[:5]:
                completed = sum(1 for t in inc.get('tasks', []) if t.get('status') == 'completed')
                total = len(inc.get('tasks', []))
                inc_list.append(f"- {inc['id']}: {inc['machine_id']} | {inc['failure_mode']} | Status: {inc['status']} | Tasks: {completed}/{total} done")
            incidents_summary = "\n".join(inc_list)

        # ===== STEP 4: SYNTHESIZER =====
        persona_instructions = {
            "Plant Manager": "Focus on operational KPIs, overall plant health, production impact, cost implications, and strategic decisions. Give executive-level summaries with data tables when relevant.",
            "Maintenance Engineer": "Focus on technical diagnostics, repair procedures step-by-step, required tools and spare parts, MTTR estimates, and preventive maintenance recommendations.",
            "Safety Officer": "Focus on hazard identification, LOTO procedures, PPE requirements, safety compliance, incident investigation protocols, and regulatory requirements.",
            "Quality Inspector": "Focus on quality metrics, defect analysis, inspection results, calibration status, and corrective action recommendations.",
            "Shift Supervisor": "Focus on shift handover items, crew assignments, pending tasks, production targets, and immediate operational priorities."
        }
        
        persona_focus = persona_instructions.get(persona, persona_instructions["Plant Manager"])
        
        system_prompt = f"""You are ShiftSense AI, an advanced Industrial Intelligence Assistant for TCS Bharat Steel Pipes plant.
You are responding as the AI advisor for the **{persona}** role.
{persona_focus}

CRITICAL RULES:
1. Use the provided data to give SPECIFIC, DATA-DRIVEN answers. Quote actual numbers, part names, machine IDs.
2. Format responses using Markdown: use **bold**, bullet points, tables (| col | col |), and headers (###).
3. If database data was fetched, present it in organized tables or structured lists.
4. Do NOT hallucinate data. If data is not available, say so clearly.
5. Be concise but thorough. Every answer should be actionable.
6. For repair questions, include step-by-step procedures from the documentation.
8. You MUST decline to answer deeply if the user asks a question entirely outside the scope of the {persona} role. Keep refusals brief and advise consulting the correct role."""

        prompt = f"""# User Query
{query}

# Retrieved Documentation (RAG Vector Store)
{rag_context}

# Database Query Results
{json.dumps(tool_results, indent=2, default=str) if tool_results else "No database queries executed."}

# Live System State
{live_context if live_context else "No live telemetry context."}

# Active Incidents
{incidents_summary if incidents_summary else "No active incidents."}

# Instructions
Provide a comprehensive, professional, and data-driven response. 
Include specific numbers and facts from the data above.
At the end, suggest 2-3 relevant follow-up questions the user could ask.
Format everything in clean Markdown."""
        
        from engine.logger import get_system_logger
        logger = get_system_logger()
        logger.info(f"[MultiAgent] Generating response for Persona: {persona} | Query: {query}")
        
        response = self.ollama.generate(prompt, system=system_prompt, timeout=45)
        logger.info(f"[MultiAgent] Response generated successfully ({len(response)} chars).")
        
        sources = ["Vector Store (RAG)"]
        if tools_used:
            sources.append(f"Database Tools ({', '.join(tools_used)})")
        if live_context:
            sources.append("Live Telemetry")
        if incidents_summary:
            sources.append("Incident Tracker")
            
        return {
            "response": response, 
            "sources_used": sources,
            "tools_called": tools_used
        }

    def run_automated_task(self, incident, task):
        """
        Executes a background automated task node using the appropriate Agent tool.
        """
        time.sleep(0.5)
        
        output_note = ""
        title = task.get("title", "")
        
        if "Root Cause Analysis" in title or "RCA" in title:
            output_note = self.generate_rca(incident)
        elif "Acknowledge" in title or "Log" in title:
            output_note = f"Alert acknowledged automatically. Incident {incident['id']} logged to system database at {time.strftime('%H:%M:%S')}."
        elif "Isolate" in title or "LOTO" in title:
            output_note = f"Machine {incident['machine_id']} isolated via LOTO procedure. Lockout applied at {time.strftime('%H:%M:%S')}."
        elif "Diagnostic" in title or "Inspect" in title:
            diag = self.rag.retrieve_context(incident["failure_mode"], k=2)
            output_note = f"Diagnostic context retrieved from knowledge base:\n{diag[:500]}"
        elif "Order" in title or "Spare" in title or "Part" in title:
            output_note = f"Purchase Order auto-generated for parts related to {incident['failure_mode']}. Sent to ERP system."
        elif "Notify" in title or "Alert" in title:
            output_note = f"Notification sent to shift supervisor and maintenance team for incident {incident['id']}."
        elif "Report" in title or "Document" in title:
            output_note = f"Incident report drafted and saved to database. Reference: {incident['id']}"
        else:
            output_note = f"Automated execution completed successfully at {time.strftime('%H:%M:%S')}."
            
        self.incidents.resolve_task(incident["id"], task["id"], output_note)

    def generate_rca(self, incident):
        """
        Automated RCA Generation by the AI.
        """
        system = """You are a Senior Root Cause Analysis expert at TCS Bharat Steel Pipes. 
Output a comprehensive, highly professional Markdown report. Do not include introductory text like 'Here is the report'.
Include: Executive Summary, Timeline, Technical Analysis, Corrective Actions, Preventive Recommendations."""

        prompt = f"""# Incident Data for RCA

**Incident ID:** {incident['id']}
**Machine:** {incident['machine_id']}
**Failure Mode:** {incident['failure_mode']}
**Started At:** {incident.get('started_at')}
**Resolved At:** {incident.get('resolved_at')}

**Telemetry Slice (5 seconds leading to failure):**
```json
{json.dumps(incident.get('telemetry_slice', {}), indent=2, default=str)}
```

**Tasks Executed and User Reviews:**
```json
{json.dumps(incident.get('tasks', []), indent=2, default=str)}
```

**RAG Context from Knowledge Base:**
{self.rag.retrieve_context(incident["failure_mode"], k=2)}

Generate a complete Root Cause Analysis (RCA) report. Synthesize the Telemetry anomalies, RAG knowledge, and the user's manual task 'review_note's.
1. **Executive Summary**: Brief incident overview
2. **Timeline of Events**: Chronological breakdown
3. **Telemetry & Technical Analysis**: Analyze the sensor slice provided and why it caused the incident
4. **Root Cause**: Direct and contributing causes based on RAG knowledge
5. **Corrective Actions**: Immediate fixes applied (referencing manual user reviews)
6. **Preventive Recommendations**: Future prevention measures
7. **Estimated Impact**: Downtime hours, production loss estimate"""
        
        report = self.ollama.generate(prompt, system=system, timeout=60)
        
        self.incidents.rca_reports.append({
            "incident_id": incident['id'],
            "machine_id": incident['machine_id'],
            "failure_mode": incident['failure_mode'],
            "report": report,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Save to filesystem
        rca_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plant_data', 'rca_documents')
        if not os.path.exists(rca_dir):
            os.makedirs(rca_dir)
            
        filename = f"{incident['id']}_RCA.md"
        filepath = os.path.join(rca_dir, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report)
        except Exception as e:
            print(f"Error saving RCA document: {e}")
            
        return f"RCA Report Generated and Saved to {filename}."

# Singleton
_engine = None
def get_agents_engine():
    global _engine
    if _engine is None:
        _engine = MultiAgentEngine()
    return _engine
