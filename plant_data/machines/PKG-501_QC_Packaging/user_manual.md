# QC INSPECTION & AUTOMATIC PACKAGING SYSTEM — MODEL: FIVES OTO-500
## Machine ID: PKG-501A (Production Line A) / PKG-501B (Production Line B)
## COMPREHENSIVE USER & MAINTENANCE MANUAL

---

### Document Control

| Field | Value |
|-------|-------|
| **Document No.** | TBSP-MAN-PKG501-001 |
| **Revision** | 3.0 |
| **Manufacturer** | Fives OTO S.p.A. (Italy) — Packaging System / Magnetic Analysis Corp (MAC, USA) — Hydrostatic Tester |
| **Model** | OTO-500 Auto Bundling Line + MAC HydroStar 70 |
| **Serial No.** | PKG-501A: OTO-2018-0500-1234 / PKG-501B: OTO-2024-0500-5678 |

---

## 1. GENERAL DESCRIPTION

### 1.1 System Overview
The Stage 5 QC & Packaging system is an integrated line performing final quality inspection and automatic packaging of finished steel pipes. The system comprises:

1. **Hydrostatic Pressure Tester (MAC HydroStar 70)** — Tests pipe integrity at pressures up to 70 bar (per IS 1239 / ASTM A53 requirements)
2. **Dimensional Inspection Station** — Laser-based OD measurement, wall thickness (ultrasonic), length measurement, and ovality check
3. **Visual Inspection Conveyor** — Slow-speed conveyor with overhead lighting for manual surface inspection
4. **Automatic Cut-Off Saw** — Flying cut-off saw for cutting pipes to specified lengths
5. **Marking/Stenciling Unit** — Inkjet printer for BIS marking, heat number, size, grade
6. **Automatic Bundling Machine** — Hexagonal bundling, strapping (2 or 4 straps per bundle)
7. **Weighing Station** — Platform scale with digital display and printer
8. **Pipe End Facing/Threading** — Optional (for threaded pipe orders)

### 1.2 Technical Specifications

| Parameter | Specification |
|-----------|--------------|
| **Hydrostatic Test Pressure** | 0 – 70 bar (adjustable) |
| **Test Hold Time** | 5 – 15 seconds (adjustable) |
| **Laser OD Measurement** | ±0.01mm accuracy (Keyence LS-9000 series) |
| **UT Wall Thickness** | ±0.02mm accuracy (Olympus 38DL Plus) |
| **Length Measurement** | ±1mm accuracy (encoder-based) |
| **Bundling Capacity** | Up to 61 pipes per bundle (hex pattern) |
| **Strapping** | Steel strapping, 19mm × 0.5mm, 4 straps/bundle |
| **Weighing** | 0 – 5000 kg, ±0.5 kg accuracy |
| **Throughput** | 25-40 pipes/minute (depending on length) |
| **Electrical Supply** | 415V, 3-phase, 50 Hz |
| **Pneumatic Supply** | 6-7 bar |
| **Hydraulic Supply** | 250 bar (dedicated HPU for hydro test) |

---

## 2. OPERATING PARAMETERS

| Parameter | Normal Range | Warning | Critical / Trip |
|-----------|-------------|---------|----------------|
| Hydro Test Pressure | Per spec (e.g., 50 bar for IS 1239 Medium) | Pressure drop >2 bar in hold | Pipe burst / seal leak |
| Test Pump Motor Current | 15-40 A | >45 A | >50 A (trip) |
| Pipe OD Deviation | ±0.5% of nominal | >±0.8% | >±1.0% (reject) |
| Wall Thickness Deviation | ±5% of nominal | >±8% | >±10% (reject) |
| Ovality | <1.5% | >2.0% | >3.0% (reject) |
| Bundling Strap Tension | 800-1200 N | <700 N | <500 N (loose strap) |
| Conveyor Speed | 10-30 m/min | N/A | Motor overload trip |
| Vibration (Test Pump) | 1.0-4.0 mm/s | >5.0 mm/s | >7.0 mm/s |
| Hydraulic Oil Temp | 30-55°C | >60°C | >70°C |
| Pneumatic Pressure | 6.0-7.0 bar | <5.5 bar | <5.0 bar |
| Cut-off Saw Blade Temp | 30-80°C | >90°C | >100°C |

---

## 3. MAINTENANCE PROCEDURES

### 3.1 Daily (Every Shift)
- [ ] Check hydro test pump oil level and seals for leaks
- [ ] Inspect test end seals (O-rings) — replace if worn
- [ ] Calibrate laser OD gauge with reference standard
- [ ] Verify UT wall thickness with calibration block
- [ ] Check strapping coil supply — replace if running low
- [ ] Inspect cut-off saw blade condition
- [ ] Clean ink jet printer head (if streaky markings)
- [ ] Check weighing scale zero reading

### 3.2 Weekly
- [ ] Calibrate weighing scale with certified test weights
- [ ] Inspect hydraulic hoses for bulging or leaks
- [ ] Check pneumatic cylinder operation (bundling arms)
- [ ] Clean and inspect all conveyor rollers
- [ ] Verify marking content against BIS requirements
- [ ] Inspect safety guards on cut-off saw

### 3.3 Monthly
- [ ] Hydro test pump oil analysis
- [ ] Replace test end seal O-ring sets (preventive)
- [ ] Calibrate pressure gauge against certified reference
- [ ] Vibration analysis on test pump motor
- [ ] Inspect bundling machine gear train
- [ ] Full UT instrument calibration with V1/V2 blocks

### 3.4 Quarterly
- [ ] Replace hydro test pump oil
- [ ] Replace cut-off saw blade
- [ ] Inspect and replace bundling strapping head if worn
- [ ] Overhaul hydraulic HPU (filter, oil, check pump)
- [ ] Replace inkjet printer cartridge

---

## 4. FAILURE MODES

| FM Code | Failure Mode | Severity | Frequency | MTTR |
|---------|-------------|----------|-----------|------|
| FM-401 | Hydro test pump failure | 8/10 | 1/2-3 years | 4-8 hrs |
| FM-402 | Test end seal leakage | 4/10 | Every 1-2 weeks | 15 min |
| FM-403 | Laser OD gauge calibration drift | 4/10 | Monthly | 30 min |
| FM-404 | UT probe failure | 5/10 | Every 6-12 months | 1 hr |
| FM-405 | Cut-off saw blade wear/breakage | 5/10 | Every 2-3 months | 1 hr |
| FM-406 | Bundling machine jam | 5/10 | Every 1-2 weeks | 30 min |
| FM-407 | Strapping head failure | 6/10 | Every 6-12 months | 2 hrs |
| FM-408 | Conveyor roller bearing failure | 4/10 | Every 3-6 months | 1 hr |
| FM-409 | Inkjet printer head clogged | 3/10 | Monthly | 30 min |
| FM-410 | Weighing scale calibration drift | 3/10 | Every 3-6 months | 30 min |
| FM-411 | Hydraulic HPU overheating | 5/10 | 1/year | 2 hrs |
| FM-412 | Pipe threading die wear | 5/10 | Every 500-1000 pipes | 1 hr |

---

## 5. FAILURE HISTORY (Last 24 Months)

| Date | Machine | FM Code | Description | Downtime | Root Cause | Action Taken |
|------|---------|---------|-------------|----------|------------|--------------|
| 2024-07-20 | PKG-501A | FM-406 | Bundling arm jammed | 0.5 hrs | Pipe misalignment in collector | Cleared jam, adjusted guide rails |
| 2024-09-05 | PKG-501A | FM-405 | Saw blade chipped | 1 hr | Hit end plug left in pipe | Blade replaced, SOP updated |
| 2024-11-18 | PKG-501A | FM-401 | Hydro test pump pressure fluctuation | 5 hrs | Pump check valve worn | Pump overhauled, check valve replaced |
| 2025-01-10 | PKG-501A | FM-404 | UT probe no signal | 1 hr | Crystal element cracked | Probe replaced |
| 2025-03-22 | PKG-501A | FM-407 | Strapping head won't crimp | 2 hrs | Crimper jaw worn | Strapping head replaced |
| 2025-05-15 | PKG-501A | FM-408 | Conveyor roller #12 seized | 1 hr | Water damage to bearing | Bearing replaced, splash guard added |
| 2025-07-28 | PKG-501A | FM-406 | Bundling jam (3 times in shift) | 1.5 hrs | Pipes different lengths mixed | Sorted pipes, QC checkpoint added |
| 2025-09-14 | PKG-501A | FM-411 | HPU overheating | 2 hrs | Cooler fan failed | Fan motor replaced |
| 2025-11-30 | PKG-501A | FM-409 | Marking illegible | 0.5 hrs | Printer head clogged | Head cleaned, new cartridge |
| 2026-01-20 | PKG-501B | FM-402 | Test seal leak (high pressure pipe) | 0.25 hrs | O-ring sized for smaller pipe | Correct O-ring installed |
| 2026-03-08 | PKG-501A | FM-401 | Pump motor vibration high (5.8 mm/s) | 6 hrs | Motor bearing degraded | Motor bearings replaced |
| 2026-05-12 | PKG-501A | FM-405 | Saw blade worn (cut quality poor) | 1 hr | Normal wear (3 months service) | Blade replaced (scheduled) |

---

## 6. QUALITY STANDARDS & TEST REQUIREMENTS

### 6.1 Hydrostatic Test Pressures (IS 1239 Part-I)

| Pipe Class | Test Pressure | Hold Time |
|------------|--------------|-----------|
| Light (Class A) | 25 bar | 7 sec |
| Medium (Class B) | 50 bar | 10 sec |
| Heavy (Class C) | 50 bar | 10 sec |

### 6.2 Dimensional Tolerances (IS 1239 Part-I)

| Parameter | Tolerance |
|-----------|----------|
| Outside Diameter | ±0.5% (≥15mm OD) |
| Wall Thickness | +15% / -12.5% |
| Length | +0 / -6mm for 6m pipes |
| Ovality | ≤1.5% of OD |
| Straightness | ≤1.5mm/m |
| Weight | ±5% per piece |

---

## 7. SAFETY — ZONE Z6 (QC & PACKAGING)

### Mandatory PPE
- ✅ Safety helmet
- ✅ Safety shoes (steel toe)
- ✅ Safety glasses
- ✅ Hearing protection (saw area >85 dB(A))
- ✅ High-visibility vest (forklift movement area)

### Specific Hazards
- ⚠️ **HIGH PRESSURE**: Hydrostatic test at 70 bar. Maintain 3m distance during testing. Pipe burst risk.
- ⚠️ **ROTATING SAW BLADE**: Cut-off saw. Never reach into saw area. Wait for blade to fully stop.
- ⚠️ **HEAVY LOADS**: Pipe bundles up to 2000 kg. Forklift movement zone — stay in pedestrian walkways.
- ⚠️ **PINCH POINTS**: Bundling arms, strapping machine. Keep hands clear during cycle.

---

## 8. TELEMETRY THRESHOLDS

```json
{
  "machine_id": "PKG-501",
  "thresholds": {
    "hydro_test_pressure": {
      "unit": "bar",
      "varies_by_product": true,
      "max_system": 70
    },
    "test_pump_motor_current": {
      "unit": "A",
      "normal_min": 15,
      "normal_max": 40,
      "warning": 45,
      "critical": 50,
      "trip": 55
    },
    "vibration_test_pump": {
      "unit": "mm/s RMS",
      "normal_min": 1.0,
      "normal_max": 4.0,
      "warning": 5.0,
      "critical": 7.0,
      "trip": 9.0
    },
    "hydraulic_oil_temp": {
      "unit": "°C",
      "normal_min": 30,
      "normal_max": 55,
      "warning": 60,
      "critical": 70,
      "trip": 75
    },
    "pneumatic_pressure": {
      "unit": "bar",
      "normal_min": 6.0,
      "normal_max": 7.0,
      "warning": 5.5,
      "critical": 5.0
    },
    "conveyor_speed": {
      "unit": "m/min",
      "normal_min": 10,
      "normal_max": 30
    },
    "strap_tension": {
      "unit": "N",
      "normal_min": 800,
      "normal_max": 1200,
      "warning_low": 700,
      "critical_low": 500
    },
    "saw_blade_temperature": {
      "unit": "°C",
      "normal_min": 30,
      "normal_max": 80,
      "warning": 90,
      "critical": 100
    }
  }
}
```

---

*Manual by: Fives OTO S.p.A., Italy & MAC, USA*
*Localized by: TCS Bharat Steel Pipes QC Department*
*Last Updated: May 2026*
