# HIGH-FREQUENCY WELDING STATION — MODEL: THERMATOOL HAZ-400
## Machine ID: WLD-301A (Production Line A) / WLD-301B (Production Line B)
## COMPREHENSIVE USER & MAINTENANCE MANUAL

---

### Document Control

| Field | Value |
|-------|-------|
| **Document No.** | TBSP-MAN-WLD301-001 |
| **Revision** | 4.2 |
| **Manufacturer** | Thermatool Corp. (Inductotherm Group, USA) |
| **Model** | HAZ-400 High-Frequency Induction Welder |
| **Serial No.** | WLD-301A: THM-2018-HAZ-05621 / WLD-301B: THM-2024-HAZ-09187 |
| **Year of Manufacture** | WLD-301A: 2018 / WLD-301B: 2023 |

---

## 1. GENERAL DESCRIPTION

### 1.1 Machine Overview
The Thermatool HAZ-400 is a solid-state high-frequency (HF) induction welding system designed for ERW tube and pipe manufacturing. The system heats the strip edges using high-frequency electromagnetic induction (200-400 kHz) to forging temperature, and squeeze rollers press the edges together to form a solid-state forge weld. The system includes inline weld quality monitoring through an eddy current testing (ECT) unit and automatic weld bead scarfing.

### 1.2 Major Components
1. **HF Power Supply** — IGBT-based solid-state inverter (400 kW, 200-400 kHz)
2. **Induction Coil** — Water-cooled copper induction coil (custom per tube diameter)
3. **Impeder** — Ferrite core impeder rod (placed inside the tube to concentrate flux)
4. **Squeeze Roller Stand** — Hydraulic squeeze rollers (forging pressure: 50-120 kN)
5. **External Scarfing Tool** — Carbide-tipped weld bead removal tool (OD scarfing)
6. **Internal Scarfing Tool** — Mandrel-mounted ID scarfing blade (optional, for larger tubes)
7. **Eddy Current Tester (ECT)** — Rohmann Elotest PL-500 inline weld inspection system
8. **Cooling Water System** — Closed-loop deionized water cooling (conductivity: <20 µS/cm)
9. **Control System** — Siemens S7-1500 PLC + Thermatool WeldView™ monitoring system

### 1.3 Technical Specifications

| Parameter | Specification |
|-----------|--------------|
| **RF Power Output** | 400 kW (continuously adjustable 10-100%) |
| **Frequency Range** | 200 – 400 kHz (auto-tuning) |
| **Tube OD Range** | 15mm – 150mm |
| **Wall Thickness Range** | 1.2mm – 5.4mm |
| **Welding Speed** | 10 – 80 m/min |
| **Squeeze Force** | 50 – 120 kN (hydraulic) |
| **Cooling Water Flow** | 120 L/min (coil + inverter combined) |
| **Cooling Water Temperature** | 25 – 35°C (inlet) |
| **Cooling Water Conductivity** | < 20 µS/cm (deionized) |
| **Electrical Supply** | 415V, 3-phase, 50 Hz |
| **Power Factor** | 0.95 (with active PFC) |
| **Efficiency** | 85-90% (RF to weld) |
| **Weight (Inverter Cabinet)** | 3,200 kg |
| **Weight (Welding Head)** | 2,800 kg |

---

## 2. OPERATING PARAMETERS

| Parameter | Normal Range | Warning | Critical / Trip |
|-----------|-------------|---------|----------------|
| RF Power Output | 80-320 kW | >350 kW | >380 kW (power limit) |
| Weld Temperature | 1250-1350°C | >1400°C | >1450°C (overweld) |
| Squeeze Pressure | 60-100 kN | >110 kN | >120 kN |
| Inverter Temperature | 30-55°C | >60°C | >70°C (thermal trip) |
| Cooling Water Temp (inlet) | 25-35°C | >38°C | >42°C (high temp alarm) |
| Cooling Water Flow | 100-120 L/min | <90 L/min | <70 L/min (flow trip) |
| Water Conductivity | 2-20 µS/cm | >30 µS/cm | >50 µS/cm (quality alarm) |
| ECT Weld Quality Signal | 0-50 mV | 50-80 mV (minor defect) | >80 mV (reject/alarm) |
| Impeder Ferrite Temperature | 80-200°C | >250°C | >300°C (impeder damage) |
| Vibration (Squeeze Stand) | 0.5-3.0 mm/s | >4.0 mm/s | >6.0 mm/s |
| Scarfing Tool Wear | 0-2mm | 2-3mm | >3mm (replace) |

---

## 3. MAINTENANCE PROCEDURES

### 3.1 Daily (Every Shift)
- [ ] Check cooling water flow and temperature on display
- [ ] Inspect induction coil for cracks, discoloration, or water leaks
- [ ] Check impeder condition (ferrite integrity, holder position)
- [ ] Inspect scarfing tool wear (measure with gauge)
- [ ] Verify ECT calibration tube check (run reference tube with known defects)
- [ ] Clean weld area of spatter and scale
- [ ] Check squeeze roller surface condition
- [ ] Record RF power, weld temperature, and ECT readings in logbook

### 3.2 Weekly
- [ ] Test cooling water conductivity (must be <20 µS/cm)
- [ ] Inspect coil water hose connections for leaks
- [ ] Check squeeze roller bearing play (should be <0.1mm radial)
- [ ] Clean inverter cabinet air filters
- [ ] Inspect weld zone camera lens (clean with alcohol wipe)
- [ ] Replace impeder ferrite rod if cracked or discolored

### 3.3 Monthly
- [ ] Complete cooling water system flush and DI water top-up
- [ ] Vibration analysis on squeeze stand bearings
- [ ] Inspect inverter IGBT modules (visual check through viewing window)
- [ ] Calibrate ECT system with certified reference tubes
- [ ] Inspect and clean DC bus capacitor bank (check for swelling)
- [ ] Test all interlocks and emergency stops

### 3.4 Quarterly
- [ ] Replace induction coil if efficiency drops >5% (copper erosion)
- [ ] Replace squeeze roller bearings (SKF 23120 CC/W33)
- [ ] Replace DI water resin cartridges
- [ ] Full inverter inspection (IGBT gate driver check, capacitor ESR test)
- [ ] Calibrate all temperature and pressure sensors
- [ ] Megger test incoming power cables

### 3.5 Critical Spare Parts

| Part No. | Description | Min Stock | Lead Time |
|----------|-------------|-----------|-----------|
| THM-COIL-SET | Induction coil set (per tube size, 5 sizes) | 2 sets per size | 6-8 weeks |
| THM-IMP-FER-25 | Impeder ferrite rod Ø25mm | 20 nos. | 2 weeks |
| THM-IGBT-MOD | IGBT power module (Infineon) | 2 nos. | 8 weeks |
| THM-SCARF-TIP | Carbide scarfing tool tip | 10 nos. | 2 weeks |
| SKF-23120-CC | Squeeze roller bearing | 4 nos. | 1 week |
| THM-DC-CAP | DC bus capacitor bank | 1 set | 8 weeks |
| ROH-ECT-PROBE | ECT inspection probe coil | 2 nos. per size | 4 weeks |
| THM-DI-RESIN | DI water resin cartridge | 4 nos. | 1 week |

---

## 4. FAILURE MODES

| FM Code | Failure Mode | Severity | Frequency | MTTR |
|---------|-------------|----------|-----------|------|
| FM-201 | IGBT module failure | 9/10 | 1/3-5 years | 4-8 hrs |
| FM-202 | Induction coil leak/crack | 7/10 | Every 4-8 months | 2-3 hrs |
| FM-203 | Impeder ferrite breakage | 5/10 | Every 2-4 weeks | 30 min |
| FM-204 | Squeeze roller bearing failure | 7/10 | 1/year | 4-6 hrs |
| FM-205 | Cooling water flow loss | 8/10 | 1/2-3 years | 1-4 hrs |
| FM-206 | ECT calibration drift | 4/10 | Monthly | 1 hr |
| FM-207 | Scarfing tool breakage | 5/10 | Every 2-3 months | 30 min |
| FM-208 | DC bus capacitor degradation | 8/10 | 1/5-7 years | 8-16 hrs |
| FM-209 | Weld cold joint (underweld) | 6/10 | Weekly (process) | 10 min (re-adjust power) |
| FM-210 | Weld burn-through (overweld) | 6/10 | Every 2 weeks | 10 min (re-adjust power) |
| FM-211 | Water conductivity high | 5/10 | Every 3-6 months | 2 hrs (resin change) |
| FM-212 | Coil-to-tube arc (flashover) | 7/10 | 1/year | 1-2 hrs |

---

## 5. FAILURE HISTORY (Last 24 Months)

| Date | Machine | FM Code | Description | Downtime | Root Cause | Action Taken |
|------|---------|---------|-------------|----------|------------|--------------|
| 2024-07-28 | WLD-301A | FM-203 | Impeder cracked | 0.5 hrs | Thermal stress | Replaced with new ferrite rod |
| 2024-09-14 | WLD-301A | FM-202 | Induction coil water leak | 2.5 hrs | Copper erosion at bend | Coil replaced, spare ordered |
| 2024-11-03 | WLD-301A | FM-207 | Scarfing tip broke | 0.5 hrs | Weld bead impact | Tip replaced |
| 2024-12-20 | WLD-301A | FM-201 | IGBT module #3 failed | 6 hrs | Power transient during storm | Module replaced, surge protector upgraded |
| 2025-02-10 | WLD-301A | FM-205 | Low water flow alarm | 3 hrs | DI pump impeller degraded | Pump replaced |
| 2025-04-15 | WLD-301A | FM-204 | Squeeze roller vibration high | 5 hrs | Bearing degradation (outer race spalling) | Bearings replaced |
| 2025-06-28 | WLD-301A | FM-212 | Arc flash at coil | 1.5 hrs | Tube misalignment (entry guide shifted) | Coil replaced, entry guide re-set |
| 2025-08-22 | WLD-301A | FM-202 | Coil efficiency dropped 8% | 3 hrs | Internal copper erosion | Coil replaced |
| 2025-10-05 | WLD-301A | FM-211 | Water conductivity 45 µS/cm | 2 hrs | Resin exhausted | Resin cartridge replaced |
| 2025-12-18 | WLD-301A | FM-203 | Impeder cracked twice in week | 1 hr | Wrong impeder size for tube OD | Correct size installed |
| 2026-02-03 | WLD-301B | FM-209 | Cold weld defects (3 tubes) | 0.5 hrs | Power supply auto-tune shifted | Re-calibrated, increased power 5% |
| 2026-04-10 | WLD-301A | FM-204 | Squeeze bearing noise | 4.5 hrs | Lubrication missed | Bearings replaced, PM enforced |
| 2026-05-25 | WLD-301A | FM-202 | Coil micro-crack detected | 2 hrs | Fatigue (4000+ hrs use) | Preventive replacement |

---

## 6. SAFETY — ZONE Z4 (WELDING STATION)

### ⚠️ CRITICAL SAFETY WARNINGS
- 🔴 **HIGH VOLTAGE**: Inverter operates at 800V DC bus. ONLY qualified electrical engineers may open inverter cabinet.
- 🔴 **RF RADIATION**: HF field present during welding. Persons with pacemakers MUST NOT enter Zone Z4 during welding operations.
- 🔴 **EXTREME HEAT**: Weld zone temperature exceeds 1300°C. Maintain 2m minimum distance from weld point.
- 🔴 **UV/IR RADIATION**: Welding produces UV and IR radiation. Welding goggles (shade 3-5) mandatory.
- 🔴 **PINCH POINTS**: Squeeze rollers — NEVER reach into squeeze stand during operation.

### Mandatory PPE
- ✅ Safety helmet
- ✅ Welding goggles (shade 3-5) or auto-darkening visor
- ✅ Heat-resistant leather gloves
- ✅ Fire-retardant clothing (cotton, no synthetics)
- ✅ Safety shoes (heat-resistant sole)
- ✅ Hearing protection
- ✅ Face shield (when inspecting weld area)

---

## 7. TELEMETRY THRESHOLDS

```json
{
  "machine_id": "WLD-301",
  "thresholds": {
    "rf_power_output": {
      "unit": "kW",
      "normal_min": 80,
      "normal_max": 320,
      "warning": 350,
      "critical": 380,
      "trip": 400
    },
    "weld_temperature": {
      "unit": "°C",
      "normal_min": 1250,
      "normal_max": 1350,
      "warning_low": 1200,
      "warning_high": 1400,
      "critical_high": 1450
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
      "normal_min": 100,
      "normal_max": 120,
      "warning": 90,
      "critical": 70,
      "trip": 60
    },
    "cooling_water_temp": {
      "unit": "°C",
      "normal_min": 25,
      "normal_max": 35,
      "warning": 38,
      "critical": 42,
      "trip": 45
    },
    "squeeze_pressure": {
      "unit": "kN",
      "normal_min": 60,
      "normal_max": 100,
      "warning": 110,
      "critical": 120
    },
    "vibration_squeeze_stand": {
      "unit": "mm/s RMS",
      "normal_min": 0.5,
      "normal_max": 3.0,
      "warning": 4.0,
      "critical": 6.0,
      "trip": 8.0
    },
    "ect_weld_signal": {
      "unit": "mV",
      "normal_max": 50,
      "warning": 80,
      "critical": 120,
      "reject": 150
    },
    "water_conductivity": {
      "unit": "µS/cm",
      "normal_max": 20,
      "warning": 30,
      "critical": 50
    }
  }
}
```

---

*Manual by: Thermatool Corp. (Inductotherm Group), USA*
*Localized by: TCS Bharat Steel Pipes Engineering Department*
*Last Updated: May 2026*
