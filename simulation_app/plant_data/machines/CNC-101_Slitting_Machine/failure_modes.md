# CNC-101 SLITTING MACHINE — FAILURE MODES & CORRECTIVE ACTIONS
## Document No: TBSP-FMEA-CNC101-001 | Rev: 3.0

---

## Failure Mode & Effects Analysis (FMEA)

### Machine: Bronx CTL-1500 CNC Slitting Line
### Machine IDs: CNC-101A, CNC-101B

---

## 1. CRITICAL FAILURE MODES

### FM-001: Slitting Arbor Bearing Failure
| Field | Details |
|-------|---------|
| **Component** | Main slitting arbor bearing (FAG 6210-2RS) |
| **Failure Mode** | Progressive bearing degradation → seizure |
| **Detection Method** | Vibration monitoring (threshold: >4.0 mm/s RMS), temperature rise (>80°C), audible noise increase |
| **Root Cause (Common)** | Inadequate lubrication, contamination from metal fines, overloading, age-related fatigue |
| **Effect on Production** | Complete line stoppage. Cannot slit coils. |
| **Severity** | 9/10 |
| **Occurrence Frequency** | Once per 8-12 months (per arbor) |
| **Mean Time to Repair (MTTR)** | 4-6 hours |
| **Corrective Action** | 1. STOP machine immediately. 2. Apply LOTO. 3. Remove blade assembly. 4. Extract old bearings using puller. 5. Clean arbor shaft. 6. Press-fit new bearings (FAG 6210-2RS, 4 nos.). 7. Reassemble blades with spacers. 8. Verify alignment. 9. Run test strip at low speed. |
| **Preventive Action** | Weekly grease lubrication (SKF LGMT 2, 3g/point). Monthly vibration spectrum analysis. Replace bearings at 5000 operating hours regardless of condition. |
| **Required Parts** | FAG 6210-2RS bearings × 4, SKF LGMT 2 grease, arbor locknut |
| **Required Tools** | Bearing puller, hydraulic press, torque wrench (180 Nm), vibration meter |
| **Estimated Cost** | ₹15,000 (parts) + ₹8,000 (labor) |

---

### FM-002: Hydraulic Pump Failure
| Field | Details |
|-------|---------|
| **Component** | Bosch Rexroth A10VSO-45 variable displacement pump |
| **Failure Mode** | Internal wear → loss of pressure/flow |
| **Detection Method** | Hydraulic pressure gauge drops below 100 bar during operation, increased pump noise, slow cylinder movements |
| **Root Cause (Common)** | Oil contamination, cavitation, seal wear, operating with low oil level |
| **Effect on Production** | Decoiler mandrel won't grip coil, strip tension control lost, line cannot operate |
| **Severity** | 8/10 |
| **Occurrence Frequency** | Once per 3-5 years |
| **MTTR** | 8-16 hours (depends on spare availability) |
| **Corrective Action** | 1. STOP machine and apply LOTO. 2. Drain hydraulic oil. 3. Disconnect pump from motor coupling. 4. Remove pump mounting bolts. 5. Install new/rebuilt pump. 6. Fill system with fresh Mobil DTE 25 oil. 7. Bleed air from system. 8. Start pump at no-load. 9. Check pressure at 160 bar. 10. Test all hydraulic functions. |
| **Preventive Action** | Quarterly oil analysis. Change hydraulic filter every 2000 hours. Maintain oil level. Annual pump inspection. |
| **Required Parts** | Rexroth A10VSO-45 pump or rebuild kit, 380L Mobil DTE 25 oil, filters |
| **Estimated Cost** | ₹2,50,000 (new pump) or ₹85,000 (rebuild kit) |

---

### FM-003: Decoiler Motor Drive Fault
| Field | Details |
|-------|---------|
| **Component** | ABB ACS880 VFD (37 kW) |
| **Failure Mode** | IGBT module failure, DC bus capacitor degradation, control board fault |
| **Detection Method** | Drive fault alarm on HMI (error codes: F0001-overcurrent, F0002-overvoltage, F0005-overtemperature), motor stops |
| **Root Cause (Common)** | Power supply transients, cooling fan failure, ambient temperature >45°C, dust accumulation |
| **Effect on Production** | Decoiler cannot rotate → line stopped |
| **Severity** | 9/10 |
| **Occurrence Frequency** | Once per 5-7 years |
| **MTTR** | 2-4 hours (if spare drive available), 2-8 weeks (if ordering new) |
| **Corrective Action** | 1. Note fault code from drive display. 2. Power down drive and wait 10 minutes (DC bus discharge). 3. Check DC bus voltage = 0V. 4. If cooling fan failed → replace fan. 5. If IGBT fault → replace drive module. 6. Reset drive, re-download parameters from backup. 7. Test run motor. |
| **Preventive Action** | Clean drive cooling fins monthly. Replace cooling fan every 3 years. Keep backup of drive parameters on USB. Store 1 spare drive module. |
| **Required Parts** | ABB ACS880-55kW drive or IGBT module, cooling fan assembly |
| **Estimated Cost** | ₹3,80,000 (new drive) or ₹1,20,000 (IGBT module) |

---

### FM-004: Strip Breakage During Slitting
| Field | Details |
|-------|---------|
| **Component** | Strip material being processed |
| **Failure Mode** | Strip snaps at slitting point or at winder tension |
| **Detection Method** | Tension sensor drops to zero suddenly, line speed drops, audible snap |
| **Root Cause (Common)** | Material defect (lamination, inclusion), edge crack in coil, excessive tension setting, wrong blade clearance |
| **Effect on Production** | Line stop, 15-30 min to re-thread |
| **Severity** | 5/10 |
| **Occurrence Frequency** | 2-3 times per month |
| **MTTR** | 15-30 minutes |
| **Corrective Action** | 1. STOP line. 2. Remove broken strip from blades and rollers carefully (use gloves). 3. Inspect blade area for damage. 4. Trim damaged strip end. 5. Re-thread strip through machine. 6. Reduce tension by 10-15% for this coil. 7. Resume at reduced speed. |
| **Preventive Action** | Inspect incoming coils for edge damage. Set correct blade clearance (8-10% of thickness). Calibrate tension sensor monthly. |
| **Required Parts** | None (material issue) |
| **Estimated Cost** | ₹5,000 (scrap material + labor time) |

---

### FM-005: Blade Chipping / Breakage
| Field | Details |
|-------|---------|
| **Component** | HSS M2 grade slitting blades (Ø250mm) |
| **Failure Mode** | Edge chipping, cracking, or catastrophic blade fracture |
| **Detection Method** | Poor slit edge quality (burr formation), vibration spike, strip width variation, visual inspection |
| **Root Cause (Common)** | Impact from hard inclusion in steel, blade fatigue, improper blade clearance, blade not properly seated |
| **Effect on Production** | Poor quality output, potential strip damage, line must stop for blade change |
| **Severity** | 7/10 |
| **Occurrence Frequency** | 1-2 times per quarter |
| **MTTR** | 1-2 hours (blade change) |
| **Corrective Action** | 1. STOP line immediately. 2. LOTO. 3. Remove blade assembly from arbor. 4. Identify damaged blade(s). 5. Replace with new blade (matching dimensions). 6. Verify spacer stack height. 7. Re-install assembly, torque arbor nut (180 Nm). 8. Run test strip, check edge quality. |
| **Preventive Action** | Inspect blades every shift. Replace after max 500 tons processed. Maintain correct clearance. Store blades in protective cases. |
| **Required Parts** | Slitting blade BRX-SB-250-M2, spacer rings as needed |
| **Estimated Cost** | ₹12,000 per blade |

---

## 2. MODERATE FAILURE MODES

### FM-006: Edge Trimmer Blade Wear
| **Severity** | 5/10 | **MTTR** | 30 min |
|---|---|---|---|
| **Detection** | Ragged edge trim, burr on strip edge | **Frequency** | Every 2-3 weeks |
| **Corrective Action** | Replace or re-sharpen trimmer blades. Adjust trimmer gap. |
| **Preventive Action** | Inspect weekly. Keep 2 sets of sharpened blades ready. |

### FM-007: Accumulator Photocell Sensor Failure
| **Severity** | 4/10 | **MTTR** | 20 min |
|---|---|---|---|
| **Detection** | Accumulator level not reading correctly, line speed hunting | **Frequency** | Every 3-6 months |
| **Corrective Action** | Clean sensor lens. Check wiring. Replace sensor if defective. |
| **Preventive Action** | Clean sensors daily. Keep 2 spare sensors in stock. |

### FM-008: Scrap Winder Clutch Slippage
| **Severity** | 4/10 | **MTTR** | 1 hour |
|---|---|---|---|
| **Detection** | Edge scrap not winding properly, scrap tangling | **Frequency** | Every 4-6 months |
| **Corrective Action** | Replace clutch pads. Adjust spring tension. |
| **Preventive Action** | Inspect clutch pads monthly. Replace when thickness <3mm. |

### FM-009: PLC Communication Error
| **Severity** | 7/10 | **MTTR** | 30-120 min |
|---|---|---|---|
| **Detection** | HMI shows "PLC COMM LOST", indicators frozen | **Frequency** | Once per 1-2 years |
| **Corrective Action** | Check PROFINET cables. Restart PLC. Replace communication module if faulty. |
| **Preventive Action** | Use shielded cables. Check connections quarterly. Keep spare CPU module. |

### FM-010: Pneumatic Cylinder Leak
| **Severity** | 3/10 | **MTTR** | 45 min |
|---|---|---|---|
| **Detection** | Slow blade guard movement, hissing sound, pressure drop at FRL | **Frequency** | Every 6-12 months |
| **Corrective Action** | Replace cylinder seals. Check tube fittings. |
| **Preventive Action** | Monthly leak check with soapy water. Keep seal kits in stock. |

---

## 3. FAILURE HISTORY LOG (Last 24 Months)

| Date | Machine | Fault Code | Description | Downtime | Root Cause | Action Taken |
|------|---------|-----------|-------------|----------|------------|--------------|
| 2024-07-15 | CNC-101A | FM-001 | Arbor bearing seized | 5.5 hrs | Lubrication missed for 3 weeks | Bearings replaced, PM schedule enforced |
| 2024-09-22 | CNC-101A | FM-005 | Blade #3 chipped | 1.5 hrs | Hard inclusion in coil material | Blade replaced, supplier notified |
| 2024-11-10 | CNC-101A | FM-004 | Strip broke at winder | 0.5 hrs | Edge crack in coil | Coil rejected, better incoming inspection |
| 2024-12-03 | CNC-101A | FM-003 | VFD cooling fan failed | 3 hrs | Fan motor burnout (age) | Fan replaced, spare ordered |
| 2025-02-18 | CNC-101A | FM-006 | Edge trimmer dull | 0.5 hrs | Normal wear | Blades re-sharpened |
| 2025-04-05 | CNC-101A | FM-001 | Arbor vibration high (4.8 mm/s) | 4 hrs | Bearing outer race damage | Bearings replaced proactively |
| 2025-06-21 | CNC-101A | FM-008 | Scrap winder slipping | 1 hr | Clutch pad worn thin | Clutch pads replaced |
| 2025-08-14 | CNC-101A | FM-002 | Hydraulic pressure low (85 bar) | 12 hrs | Pump internal wear | Pump rebuilt with new swashplate |
| 2025-10-30 | CNC-101A | FM-004 | Strip broke twice in shift | 1 hr | Bad quality coil batch | Coils quarantined, vendor audit done |
| 2025-12-15 | CNC-101A | FM-009 | PLC comm lost | 0.75 hrs | Loose PROFINET connector | Connector re-crimped |
| 2026-01-20 | CNC-101B | FM-005 | 2 blades chipped | 2 hrs | Incorrect blade clearance set by new operator | Blades replaced, operator retrained |
| 2026-03-08 | CNC-101A | FM-001 | Vibration trending up (3.8 mm/s) | 4 hrs | Bearing wear (scheduled replacement) | Bearings replaced at scheduled PM |
| 2026-05-14 | CNC-101B | FM-010 | Pneumatic leak on guard cylinder | 0.75 hrs | Worn O-ring | Seals replaced |
| 2026-06-02 | CNC-101A | FM-004 | Strip snapped | 0.25 hrs | Material edge crack | Re-threaded, continued with reduced tension |

---

## 4. TELEMETRY THRESHOLDS CONFIGURATION

```json
{
  "machine_id": "CNC-101",
  "thresholds": {
    "vibration_slitting_head": {
      "unit": "mm/s RMS",
      "normal_min": 0.5,
      "normal_max": 3.0,
      "warning": 4.0,
      "critical": 6.0,
      "trip": 8.0
    },
    "vibration_decoiler": {
      "unit": "mm/s RMS",
      "normal_min": 0.3,
      "normal_max": 2.5,
      "warning": 3.5,
      "critical": 5.0,
      "trip": 7.0
    },
    "hydraulic_pressure": {
      "unit": "bar",
      "normal_min": 100,
      "normal_max": 160,
      "warning_low": 90,
      "critical_low": 70,
      "warning_high": 165,
      "critical_high": 175
    },
    "hydraulic_oil_temperature": {
      "unit": "°C",
      "normal_min": 25,
      "normal_max": 55,
      "warning": 60,
      "critical": 70,
      "trip": 75
    },
    "decoiler_motor_current": {
      "unit": "A",
      "normal_min": 25,
      "normal_max": 80,
      "warning": 100,
      "critical": 120,
      "trip": 130
    },
    "slitting_motor_current": {
      "unit": "A",
      "normal_min": 40,
      "normal_max": 120,
      "warning": 140,
      "critical": 160,
      "trip": 170
    },
    "blade_temperature": {
      "unit": "°C",
      "normal_min": 30,
      "normal_max": 80,
      "warning": 90,
      "critical": 110,
      "trip": 120
    },
    "line_speed": {
      "unit": "m/min",
      "normal_min": 20,
      "normal_max": 100,
      "warning": 110,
      "critical": 120,
      "trip": 125
    },
    "strip_tension": {
      "unit": "kN",
      "normal_min": 5,
      "normal_max": 25,
      "warning": 30,
      "critical": 35,
      "trip": 38
    },
    "noise_level": {
      "unit": "dB(A)",
      "normal_min": 65,
      "normal_max": 85,
      "warning": 90,
      "critical": 95
    }
  }
}
```

---

*Document Prepared by: Reliability Engineering Team, TCS Bharat Steel Pipes*
*Approved by: Mr. Arun Mehta (Maintenance Manager)*
*Date: June 2026*
