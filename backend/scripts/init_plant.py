import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.schema import Machine, Zone
from database.json_db import JSONDatabase

def init_cdu_plant(db_dir: str = "data"):
    print("Initializing Crude Distillation Unit (CDU) Blueprint...")
    db = JSONDatabase(db_dir)

    # Clean existing data
    for table in ["machines", "zones", "incidents", "alerts", "tasks", "shift_reports"]:
        filepath = os.path.join(db_dir, f"{table}.json")
        with open(filepath, 'w') as f:
            json.dump([], f)

    zones = [
        Zone(zone_id="Z1", name="Pre-Heat Train (HEN)", risk_score=15.0),
        Zone(zone_id="Z2", name="Desalter Unit", risk_score=20.0),
        Zone(zone_id="Z3", name="Fired Heater (Furnace)", risk_score=85.0),
        Zone(zone_id="Z4", name="Atmospheric Distillation", risk_score=60.0),
        Zone(zone_id="Z5", name="Overhead Recovery", risk_score=45.0)
    ]

    for z in zones:
        db.insert("zones", z)

    machines = [
        Machine(
            machine_id="PUMP-101",
            name="Main Crude Charge Pump",
            manufacturer="Flowserve",
            machine_type="Centrifugal Pump",
            zone_id="Z1"
        ),
        Machine(
            machine_id="HEX-201",
            name="Crude/Residue Heat Exchanger",
            manufacturer="Alfa Laval",
            machine_type="Shell and Tube Exchanger",
            zone_id="Z1"
        ),
        Machine(
            machine_id="FURN-301",
            name="Atmospheric Fired Heater",
            manufacturer="Zeeco",
            machine_type="Fired Heater",
            zone_id="Z3"
        ),
        Machine(
            machine_id="COL-401",
            name="Atmospheric Distillation Column",
            manufacturer="Sulzer",
            machine_type="Fractionation Tower",
            zone_id="Z4"
        ),
        Machine(
            machine_id="COMP-501",
            name="Overhead Gas Compressor",
            manufacturer="Ariel",
            machine_type="Reciprocating Compressor",
            zone_id="Z5"
        )
    ]

    for m in machines:
        db.insert("machines", m)

    print("CDU Plant Blueprint initialized successfully!")

if __name__ == "__main__":
    init_cdu_plant()
