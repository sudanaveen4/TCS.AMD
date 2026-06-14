# MAINTENANCE PROCEDURE
**Document Title**: Reciprocating Compressor Overhaul & Troubleshooting
**Document ID**: MAINT-COMP-05
**Asset Class**: Reciprocating Gas Compressor

## 1. Scope
This document covers the mechanical troubleshooting, diagnostic parameters, and major overhaul procedures for multi-stage reciprocating compressors used for overhead gas recovery.

![Reciprocating Compressor Diagram](./images/reciprocating_compressor_diagram.png)

## 2. AI Digital Twin Diagnostics
Our XGBoost Digital Twin model evaluates compressor health. 
* **Failure Probability > 80%**: Schedule valve inspection.
* **Failure Probability > 95%**: Immediate shutdown required to prevent piston rod failure.

### Diagnostic Matrix
| Symptom | Telemetry Evidence | Root Cause |
|---------|--------------------|------------|
| Low discharge capacity | `suction_press` normal, `discharge_press` low, `vibration` normal | Worn piston rings or leaking suction/discharge valves. |
| High discharge temp | `discharge_temp > 130°C` | Fouled intercoolers or broken valve plates. |
| High Rod Drop | `rod_drop > 0.5mm` | Severe rider band wear. Impending piston-to-cylinder contact. |

## 3. Valve Replacement Procedure
1. **Isolation**: Close suction and discharge block valves. Vent gas to the flare header. Purge with N2.
2. **Removal**: Unbolt the valve covers using hydraulic tensioners. Extract the valve assemblies.
3. **Inspection**: Inspect the valve seats for grooving and the springs for fatigue.
4. **Reassembly**: Install new valve assemblies. Torque to 350 Nm. Do NOT reuse metallic gaskets.

## 4. Preventative Maintenance Schedule
* **1,000 Hours**: Oil analysis and vibration spectrum analysis.
* **8,000 Hours**: Replace suction and discharge valves.
* **24,000 Hours**: Major overhaul (replace piston rings, rider bands, rod packing, and crosshead pin bearings).
