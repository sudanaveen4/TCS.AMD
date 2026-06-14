# NORMALIZING HEAT TREATMENT FURNACE — MODEL: ELECTROTHERM EHIF-900
## Machine ID: HTR-401A (Production Line A) / HTR-401B (Production Line B)
## COMPREHENSIVE USER & MAINTENANCE MANUAL

---

### Document Control

| Field | Value |
|-------|-------|
| **Document No.** | TBSP-MAN-HTR401-001 |
| **Revision** | 3.5 |
| **Manufacturer** | Electrotherm (India) Ltd., Ahmedabad |
| **Model** | EHIF-900 Electric Induction Heating Furnace |
| **Serial No.** | HTR-401A: ETH-2018-EHIF-3421 / HTR-401B: ETH-2024-EHIF-5678 |
| **Year of Manufacture** | HTR-401A: 2018 / HTR-401B: 2023 |

---

## 1. GENERAL DESCRIPTION

### 1.1 Machine Overview
The Electrotherm EHIF-900 is an inline electric induction heating furnace designed for normalizing welded steel pipes. The furnace heats pipes to 880-920°C using medium-frequency induction coils, followed by controlled air cooling on a roller-type cooling bed. After cooling, pipes pass through a 6-roll hydraulic straightener to correct any bow or twist introduced during heat treatment.

### 1.2 Major Components
1. **Induction Heating Section** — 6 medium-frequency (1-10 kHz) induction coils, 150 kW each (total: 900 kW)
2. **Temperature Measurement** — 3 × non-contact infrared pyrometers (Raytek Marathon series)
3. **Air Cooling Bed** — Roller-type cooling bed (30m length), variable speed fans (4 × 15 kW)
4. **Pipe Straightener** — 6-roll hydraulic straightener (Bronx model, 100 ton capacity)
5. **Entry/Exit Roller Tables** — Motorized roller conveyors with speed synchronization
6. **Cooling Water System** — Dedicated closed-loop cooling for induction coils (150 L/min)
7. **Control System** — Siemens S7-1500 PLC + SCADA (WinCC) with pyrometer feedback loop
8. **Fume Extraction** — Overhead hood with induced-draft fan and bag filter

### 1.3 Technical Specifications

| Parameter | Specification |
|-----------|--------------|
| **Heating Capacity** | 900 kW (6 × 150 kW coils) |
| **Frequency** | 1 – 10 kHz (IGBT inverter, auto-tuning) |
| **Pipe Diameter Range** | 15mm – 150mm OD |
| **Wall Thickness Range** | 1.2mm – 5.4mm |
| **Target Temperature** | 880 – 920°C (normalizing) |
| **Heating Speed** | 10 – 60 m/min |
| **Temperature Uniformity** | ±15°C across cross-section |
| **Cooling Bed Length** | 30 meters |
| **Cooling Method** | Forced air + natural convection |
| **Straightener Capacity** | 100 tons (6-roll, hydraulic) |
| **Straightening Accuracy** | ≤ 1.5mm/meter |
| **Electrical Supply** | 11 kV (step-down to 415V via dedicated transformer) |
| **Cooling Water** | 150 L/min, 25-35°C inlet, DI water |
| **Weight** | 28,000 kg (furnace) + 18,000 kg (cooling bed) + 12,000 kg (straightener) |
| **Dimensions** | Furnace: 12m × 2m × 3m | Cooling bed: 30m × 4m × 2m | Straightener: 6m × 3m × 2.5m |

---

## 2. OPERATING PARAMETERS

| Parameter | Normal Range | Warning | Critical / Trip |
|-----------|-------------|---------|----------------|
| Pipe Temperature (exit furnace) | 880-920°C | <850°C or >950°C | <800°C or >980°C |
| Coil Power (per coil) | 60-150 kW | >155 kW | >160 kW (overpower) |
| Total Power Consumption | 400-900 kW | >920 kW | >950 kW |
| Inverter Temperature | 30-55°C | >60°C | >70°C (thermal trip) |
| Cooling Water Flow (coils) | 130-150 L/min | <120 L/min | <100 L/min (trip) |
| Cooling Water Temp (outlet) | 35-55°C | >60°C | >70°C (trip) |
| Cooling Bed Pipe Temp (exit) | 50-80°C | >100°C | >120°C (not cooled enough) |
| Straightener Hydraulic Pressure | 80-160 bar | <70 bar | <50 bar |
| Vibration (Straightener Rolls) | 0.5-3.0 mm/s | >4.0 mm/s | >6.0 mm/s |
| Fume Extraction Airflow | 8000-10000 CFM | <7000 CFM | <5000 CFM |
| Ambient Temperature (furnace zone) | 25-45°C | >50°C | >55°C |

---

## 3. MAINTENANCE PROCEDURES

### 3.1 Daily (Every Shift)
- [ ] Check cooling water flow and temperature on all 6 coils
- [ ] Inspect induction coil surfaces for discoloration (overheating sign)
- [ ] Verify pyrometer readings against manual thermocouple check (±10°C)
- [ ] Inspect cooling bed roller bearings for noise
- [ ] Check fume extraction fan operation and filter condition
- [ ] Clean pyrometer lens with soft cloth
- [ ] Record all temperatures and power readings in shift logbook
- [ ] Check straightener hydraulic oil level

### 3.2 Weekly
- [ ] Test cooling water conductivity (<50 µS/cm)
- [ ] Inspect cooling bed fan bearings for vibration
- [ ] Check straightener roll surface condition
- [ ] Inspect electrical connections at coil terminals (visual, thermal camera)
- [ ] Clean inverter cabinet air filters
- [ ] Check fume extraction duct for blockages

### 3.3 Monthly
- [ ] Calibrate pyrometers against reference blackbody source
- [ ] Vibration analysis on straightener bearings and cooling bed motors
- [ ] Hydraulic oil analysis for straightener
- [ ] Inspect refractory lining in coil support brackets
- [ ] Test all emergency stops and water flow interlocks
- [ ] Megger test coil insulation (minimum 10 MΩ at 1000V)

### 3.4 Quarterly
- [ ] Replace cooling water (full system drain and refill with DI water)
- [ ] Inspect and re-torque all coil bus-bar connections
- [ ] Replace fume extraction bag filters
- [ ] Inspect straightener hydraulic cylinder seals
- [ ] Replace cooling bed roller bearings (high-wear positions)
- [ ] Calibrate temperature controller and SCADA trends

### 3.5 Annual
- [ ] Complete furnace overhaul (coil inspection, insulation check, bus-bar replacement if needed)
- [ ] Replace all cooling bed roller bearings
- [ ] Straightener hydraulic system overhaul
- [ ] Inverter full inspection (capacitors, IGBT modules, gate drivers)
- [ ] Cooling tower maintenance and chemical treatment
- [ ] Re-calibrate all instrumentation

---

## 4. FAILURE MODES

| FM Code | Failure Mode | Severity | Frequency | MTTR |
|---------|-------------|----------|-----------|------|
| FM-301 | Induction coil insulation breakdown | 9/10 | 1/2-3 years | 8-16 hrs |
| FM-302 | Inverter IGBT failure | 9/10 | 1/4-6 years | 4-8 hrs |
| FM-303 | Pyrometer calibration drift | 5/10 | Every 2-3 months | 1 hr |
| FM-304 | Cooling water flow loss | 9/10 | 1/3-5 years | 1-4 hrs |
| FM-305 | Cooling bed roller bearing failure | 5/10 | Every 2-4 months (rotating basis) | 1.5 hrs |
| FM-306 | Straightener hydraulic leak | 6/10 | 1/year | 3 hrs |
| FM-307 | Fume extraction fan failure | 5/10 | 1/2-3 years | 2-4 hrs |
| FM-308 | Coil bus-bar overheating | 7/10 | 1/2-3 years | 4 hrs |
| FM-309 | Uneven heating (temperature gradient) | 6/10 | Monthly | 30 min |
| FM-310 | Cooling bed conveyor chain stretch | 4/10 | 1/year | 3 hrs |
| FM-311 | Straightener roll surface wear | 5/10 | Every 6-12 months | 6 hrs |
| FM-312 | Power supply transformer fault | 10/10 | 1/10+ years | 2-7 days |

---

## 5. FAILURE HISTORY (Last 24 Months)

| Date | Machine | FM Code | Description | Downtime | Root Cause | Action Taken |
|------|---------|---------|-------------|----------|------------|--------------|
| 2024-08-12 | HTR-401A | FM-305 | Cooling bed roller #8 bearing seized | 1.5 hrs | Water splash causing corrosion | Bearing replaced, splash guard installed |
| 2024-10-25 | HTR-401A | FM-303 | Pyrometer reading 40°C low | 1 hr | Lens contamination (scale dust) | Lens cleaned, calibrated against reference |
| 2024-12-08 | HTR-401A | FM-301 | Coil #3 ground fault trip | 14 hrs | Insulation breakdown (water ingress at joint) | Coil replaced, joint sealing improved |
| 2025-01-22 | HTR-401A | FM-309 | Uneven heating on PL-A | 0.5 hrs | Coil #2 power reduced (auto-tune drift) | Re-tuned inverter, power balanced |
| 2025-03-15 | HTR-401A | FM-305 | Cooling bed rollers #14, #15 noisy | 2 hrs | Normal bearing wear | Bearings replaced |
| 2025-05-08 | HTR-401A | FM-308 | Bus-bar connection overheated (detected by thermal camera) | 4 hrs | Loose bolt (thermal cycling) | Re-torqued all bus-bar connections |
| 2025-06-30 | HTR-401A | FM-306 | Straightener hydraulic oil leak | 3.5 hrs | Cylinder rod seal worn | Seal kit replaced |
| 2025-09-12 | HTR-401A | FM-307 | Fume extraction fan tripped | 3 hrs | Motor winding burnout | Motor replaced |
| 2025-11-20 | HTR-401A | FM-302 | Inverter fault on coil #5 | 6 hrs | IGBT module shorted (power surge) | IGBT replaced, added line reactor |
| 2026-01-08 | HTR-401B | FM-305 | Cooling bed roller #5 bearing noisy | 1.5 hrs | Contamination | Bearing replaced |
| 2026-03-14 | HTR-401A | FM-303 | Pyrometer #2 failed completely | 1 hr | Internal sensor degradation (age) | Pyrometer unit replaced |
| 2026-05-20 | HTR-401A | FM-311 | Straightener roll surface worn | 8 hrs | 2 years continuous use | Rolls re-chromed and re-installed |

---

## 6. SAFETY — ZONE Z5 (HEAT TREATMENT AREA)

### ⚠️ CRITICAL SAFETY WARNINGS
- 🔴 **EXTREME HEAT**: Pipes emerge at 880-920°C. Burns cause Category-III injury. Maintain 3m minimum distance.
- 🔴 **ELECTROMAGNETIC FIELD**: Induction coils produce strong EM fields. No metallic jewelry, watches, or credit cards near furnace.
- 🔴 **HOT SURFACES**: Cooling bed pipes remain hot (>100°C) for several minutes. Do not touch without thermal gloves.
- 🔴 **FUMES**: Scale and oil vapor produced during heating. Ensure fume extraction is running before starting furnace.
- 🔴 **HIGH VOLTAGE**: 11kV supply and 800V DC bus. Only authorized electricians may access panels.

### Mandatory PPE in Zone Z5
- ✅ Aluminized heat-resistant jacket (for furnace side operations)
- ✅ Heat-resistant face shield (shade 3)
- ✅ Thermal leather gloves (EN 407 rated)
- ✅ Safety boots with heat-resistant sole (>200°C)
- ✅ Safety helmet
- ✅ Hearing protection (cooling fans: 90 dB(A))
- ✅ Long cotton/FR clothing (no synthetics — melt risk)

### Emergency Procedures
1. **Cooling Water Loss**: Furnace auto-trips. Verify pipe inside coils is removed within 60 seconds to prevent coil damage.
2. **Coil Ground Fault**: Do NOT touch any metal parts. Wait for automatic isolation. Call electrical supervisor.
3. **Fire in Fume Duct**: Activate fire suppression system (CO2 flooding). Evacuate Zone Z5.

---

## 7. TELEMETRY THRESHOLDS

```json
{
  "machine_id": "HTR-401",
  "thresholds": {
    "pipe_exit_temperature": {
      "unit": "°C",
      "normal_min": 880,
      "normal_max": 920,
      "warning_low": 850,
      "warning_high": 950,
      "critical_low": 800,
      "critical_high": 980
    },
    "coil_power": {
      "unit": "kW",
      "normal_min": 60,
      "normal_max": 150,
      "warning": 155,
      "critical": 160
    },
    "inverter_temperature": {
      "unit": "°C",
      "normal_min": 30,
      "normal_max": 55,
      "warning": 60,
      "critical": 70,
      "trip": 75
    },
    "cooling_water_flow": {
      "unit": "L/min",
      "normal_min": 130,
      "normal_max": 150,
      "warning": 120,
      "critical": 100,
      "trip": 80
    },
    "cooling_water_outlet_temp": {
      "unit": "°C",
      "normal_min": 35,
      "normal_max": 55,
      "warning": 60,
      "critical": 70,
      "trip": 75
    },
    "cooling_bed_exit_temp": {
      "unit": "°C",
      "normal_min": 30,
      "normal_max": 80,
      "warning": 100,
      "critical": 120
    },
    "straightener_hydraulic_pressure": {
      "unit": "bar",
      "normal_min": 80,
      "normal_max": 160,
      "warning_low": 70,
      "critical_low": 50
    },
    "vibration_straightener": {
      "unit": "mm/s RMS",
      "normal_min": 0.5,
      "normal_max": 3.0,
      "warning": 4.0,
      "critical": 6.0,
      "trip": 8.0
    },
    "fume_extraction_airflow": {
      "unit": "CFM",
      "normal_min": 8000,
      "normal_max": 10000,
      "warning": 7000,
      "critical": 5000
    },
    "ambient_temperature": {
      "unit": "°C",
      "normal_min": 25,
      "normal_max": 45,
      "warning": 50,
      "critical": 55
    }
  }
}
```

---

*Manual by: Electrotherm (India) Ltd., Ahmedabad*
*Last Updated: May 2026*
