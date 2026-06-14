import requests
import time
import json
import sys

BASE_URL = "http://127.0.0.1:5000/api"

def print_step(msg):
    print(f"\n[{time.strftime('%H:%M:%S')}] \033[96m=== {msg} ===\033[0m")

def check_res(res, context=""):
    if res.status_code == 200:
        print(f"  \033[92mPASS\033[0m: {context}")
        return res.json()
    else:
        print(f"  \033[91mFAIL\033[0m: {context} (Status {res.status_code})")
        print(f"  Response: {res.text}")
        return None

print_step("1. Testing Base Endpoints")
check_res(requests.get(f"{BASE_URL}/status"), "Status Endpoint")
config = check_res(requests.get(f"{BASE_URL}/plant_config"), "Plant Config")
if config:
    print(f"  - Loaded {len(config.get('machines', []))} machines")

docs = check_res(requests.get(f"{BASE_URL}/documents"), "Document Tree")
if docs:
    print(f"  - Found {len(docs.get('documents', []))} documents in plant_data")

dbs = check_res(requests.get(f"{BASE_URL}/databases"), "Databases List")
if dbs:
    print(f"  - Found {len(dbs.get('databases', []))} database tables")

print_step("2. Testing Inject Failure & Detection Pipeline")
machine_to_fail = "FRM-201A"
failure_to_inject = "FM-101 Motor Bearing Failure"

# Clear existing
requests.post(f"{BASE_URL}/resolve_failures")
print("  - Cleared all existing failures")

res = requests.post(f"{BASE_URL}/inject_failure", json={
    "machine_id": machine_to_fail,
    "failure_mode": failure_to_inject
})
check_res(res, f"Injecting {failure_to_inject} on {machine_to_fail}")

print("  - Waiting up to 45 seconds for ML detection and Ollama Task Generation...")
found_incident = None
for i in range(15):
    time.sleep(3)
    inc_res = requests.get(f"{BASE_URL}/incidents")
    if inc_res.status_code == 200:
        data = inc_res.json()
        incidents = data.get("incidents", [])
        if any(inc["machine_id"] == machine_to_fail and inc["failure_mode"] == failure_to_inject for inc in incidents):
            found_incident = next(inc for inc in incidents if inc["machine_id"] == machine_to_fail)
            break
    print("  - Still waiting...")

if found_incident:
    print(f"  \033[92mPASS\033[0m: Incident Created! ID: {found_incident['id']}")
    tasks = found_incident.get("tasks", [])
    print(f"  - Generated {len(tasks)} tasks")
    if isinstance(tasks, list) and len(tasks) > 0:
        print(f"  - First task: {tasks[0].get('title', 'Unknown')}")
        print(f"  - Tasks are correctly formatted as a LIST!")
    else:
        print("  \033[91mFAIL\033[0m: Tasks are not a list or are empty!")
else:
    print("  \033[91mFAIL\033[0m: Incident was never created. Check ML detector or Ollama.")

print_step("3. Testing Multi-Agent Tool Chatbot")
chat_query = "Can you check the spare parts inventory for any bearings?"
print(f"  - Asking: '{chat_query}'")
chat_res = requests.post(f"{BASE_URL}/chat", json={
    "persona": "Maintenance Engineer",
    "query": chat_query
})
chat_data = check_res(chat_res, "Chatbot Endpoint")
if chat_data:
    print(f"  - Tools Used: {chat_data.get('tools_called', [])}")
    print(f"  - Sources: {chat_data.get('sources_used', [])}")
    print("  - Response Snippet:")
    print("    " + "\n    ".join(chat_data.get('response', '')[:200].splitlines()) + "...\n")

print_step("4. Testing Agentic Ontology Lab")
fail_mode = "FM-003 Decoiler Motor Drive Fault"
print(f"  - Generating SIPOC DAG for '{fail_mode}'...")
ont_res = requests.post(f"{BASE_URL}/generate_ontology", json={
    "failure_mode": fail_mode
})
ont_data = check_res(ont_res, "Ontology Generation")
if ont_data:
    tasks = ont_data.get("tasks", [])
    print(f"  - Generated {len(tasks)} DAG tasks")
    if isinstance(tasks, list) and len(tasks) > 0:
        print("  \033[92mPASS\033[0m: Ontology formatting is correct")
    else:
        print("  \033[91mFAIL\033[0m: Ontology tasks missing or malformed")

print_step("E2E API Test Complete!")
