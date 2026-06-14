import os
import json
import glob
from datetime import datetime, timedelta
import random

def get_image_for_machine(machine_prefix):
    images = glob.glob(f"data/documents/images/{machine_prefix}*.png")
    return images[0] if images else ""

def generate_documents():
    docs = []
    doc_id_counter = 1
    
    manuals_data = [
        {
            "machine_id": "M1",
            "title": "Buhler Mixer X-2000 Maintenance Manual",
            "prefix": "buhler",
            "chunks": [
                "Section 1.2: General Overview. The Buhler Industrial Mixer X-2000 is designed for high-capacity continuous mixing.",
                "Section 3.1: Bearing Maintenance. If vibration exceeds 3.0 mm/s, inspect the main shaft bearings. If vibration exceeds 4.5 mm/s, immediate replacement of the front-end bearing is required to prevent shaft misalignment.",
                "Section 4.5: Cleaning Procedure. Ensure the mixer is fully powered down before entering the drum. PPE requirement: Hard hat, safety glasses, harness."
            ]
        },
        {
            "machine_id": "M2",
            "title": "Coperion Twin-Screw Extruder TE-90 Service Guide",
            "prefix": "coperion",
            "chunks": [
                "Section 2.1: Screw Assembly. The twin screws are co-rotating. Ensure proper alignment during reassembly.",
                "Section 5.4: Temperature Control. Normal operating temperature is between 45C and 65C. If the temperature spikes above 80C combined with high vibration (> 10 mm/s), this strongly indicates a bearing failure or screw jam.",
                "Section 7.1: Flow Optimization. If upstream bottlenecks occur, reduce throughput by 10% to prevent barrel overloading."
            ]
        },
        {
            "machine_id": "M3",
            "title": "CryoCool Tunnel C-40 Operations Manual",
            "prefix": "cryocool",
            "chunks": [
                "Section 1.1: System Layout. The cooling tunnel uses liquid nitrogen spray combined with high-velocity fans.",
                "Section 6.2: Belt Tracking. If the conveyor belt slips, check the tensioner pneumatics. Belt slippage usually causes a sudden drop in RPM without a spike in motor current.",
                "Section 8.0: Safety. Cryogenic burns are a high risk. Gloves and face shields are mandatory in Zone Z3."
            ]
        },
        {
            "machine_id": "M4",
            "title": "Urschel Precision Cutter R-5 Manual",
            "prefix": "urschel",
            "chunks": [
                "Section 3.2: Blade Replacement. Blades must be replaced every 500 hours or if vibration exceeds 3.5 mm/s due to imbalance.",
                "Section 4.1: Jam Recovery. In case of a product jam, the motor current will spike above 12 Amps. Immediately stop the feed, open the impeller cover, and manually clear the obstruction.",
                "Section 5.5: Routine Lubrication. Lubricate the main drive spindle weekly using food-grade grease."
            ]
        },
        {
            "machine_id": "M5",
            "title": "ABB Robotic Palletizer Pro Guide",
            "prefix": "abb",
            "chunks": [
                "Section 1.0: Kinematics. The palletizer uses a 4-axis robotic arm with a vacuum gripper.",
                "Section 4.3: Servo Overload. If the wrist servo temperature exceeds 55C, it indicates a payload overload or a failing servo brake.",
                "Section 9.1: Zone Entry. The palletizer operates in a restricted safety cell. Any entry into Zone Z5 without breaking the light curtain correctly will trigger an emergency stop."
            ]
        }
    ]

    for m in manuals_data:
        img_path = get_image_for_machine(m['prefix'])
        img_markdown = f"\n\n![{m['title']} Diagram](/{img_path.replace(chr(92), '/')})" if img_path else ""
        
        for i, chunk_text in enumerate(m['chunks']):
            # Attach image to the first chunk
            final_text = chunk_text + img_markdown if i == 0 else chunk_text
            docs.append({
                "document_id": f"DOC-{doc_id_counter:04d}",
                "machine_id": m["machine_id"],
                "title": m["title"],
                "chunk_text": final_text,
                "metadata": {"type": "manual", "section_index": i}
            })
            doc_id_counter += 1

    os.makedirs("data", exist_ok=True)
    with open("data/documents.json", "w") as f:
        json.dump(docs, f, indent=4)

def generate_historical_incidents():
    history = [
        {
            "incident_id": "HIST-001",
            "machine_id": "M2",
            "zone_id": "Z2",
            "severity": "high",
            "incident_type": "bearing_failure",
            "status": "resolved",
            "timestamp": (datetime.utcnow() - timedelta(days=19)).isoformat(),
            "root_cause": "The front main bearing failed due to lack of lubrication, causing vibration to spike to 13 mm/s and temperature to reach 85C.",
            "evidence_links": []
        },
        {
            "incident_id": "HIST-002",
            "machine_id": "M4",
            "zone_id": "Z4",
            "severity": "medium",
            "incident_type": "jam",
            "status": "resolved",
            "timestamp": (datetime.utcnow() - timedelta(days=4)).isoformat(),
            "root_cause": "Foreign object jammed the rotary cutter, causing motor current to spike to 14A. Cleared manually by maintenance.",
            "evidence_links": []
        }
    ]
    with open("data/historical_incidents.json", "w") as f:
        json.dump(history, f, indent=4)

if __name__ == "__main__":
    generate_documents()
    generate_historical_incidents()
    print("Documents and historical incidents generated.")
