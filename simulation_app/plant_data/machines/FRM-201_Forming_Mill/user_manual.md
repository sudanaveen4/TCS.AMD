# TUBE FORMING MILL — MODEL: YODER M-25
## Machine ID: FRM-201A (Production Line A) / FRM-201B (Production Line B)
## COMPREHENSIVE USER & MAINTENANCE MANUAL

---

### Document Control

| Field | Value |
|-------|-------|
| **Document No.** | TBSP-MAN-FRM201-001 |
| **Revision** | 4.0 |
| **Manufacturer** | Yoder Manufacturing (Formtek Group, USA) |
| **Model** | M-25 ERW Tube Forming Mill |
| **Serial No.** | FRM-201A: YDR-2018-M25-0783 / FRM-201B: YDR-2024-M25-1245 |
| **Year of Manufacture** | FRM-201A: 2018 / FRM-201B: 2023 |
| **Installation Date** | FRM-201A: 20-Jul-2018 / FRM-201B: 15-Mar-2024 |

---

## 1. GENERAL DESCRIPTION

### 1.1 Machine Overview
The Yoder M-25 is a multi-stand ERW (Electric Resistance Welded) tube forming mill designed to progressively form flat steel strips into round or square/rectangular tubes. The mill consists of multiple forming stands, each containing a pair of rolls that incrementally shape the strip into the desired tube profile.

### 1.2 Major Components
1. **Entry Guide Assembly** — Strip edge alignment and centering
2. **Breakdown Stands (Stands 1-4)** — Initial roll forming from flat to U-shape
3. **Fin Pass Stands (Stands 5-7)** — Final forming to achieve precise diameter and edge alignment
4. **Seam Guide Assembly** — Aligns strip edges for welding
5. **Drive System** — 110 kW main drive motor with universal joint shaft drives to each stand
6. **Roll Quick-Change System** — Hydraulic roll change cassettes (changeover time: 45 min)
7. **Strip Edge Conditioning** — Edge trimming wheels for weld preparation
8. **Control System** — Siemens S7-1200 PLC + KTP900 HMI

### 1.3 Technical Specifications

| Parameter | Specification |
|-----------|--------------|
| **Tube OD Range** | 15mm – 150mm |
| **Wall Thickness Range** | 1.2mm – 5.4mm |
| **Forming Speed** | 10 – 80 m/min |
| **Number of Stands** | 7 (4 breakdown + 3 fin pass) |
| **Roll Material** | D2 tool steel, hardened to 58-62 HRC |
| **Main Drive Motor** | 110 kW AC Motor (Siemens 1LA8) |
| **Gearbox** | Flender ZAPEX ZE-series, ratio 1:3.5 |
| **Drive Shafts** | Universal joints (Spicer-type) — 14 nos. |
| **Stand Adjustment** | Hydraulic (top roll) + Manual screw (side rolls) |
| **Electrical Supply** | 415V, 3-phase, 50 Hz |
| **Coolant System** | Soluble oil flood cooling (500 L/min recirculation) |
| **Weight** | 52,000 kg |
| **Dimensions (L×W×H)** | 14m × 3.5m × 2.8m |

---

## 2. OPERATING PROCEDURES

### 2.1 Normal Operating Parameters

| Parameter | Normal Range | Warning | Critical / Trip |
|-----------|-------------|---------|----------------|
| Forming Speed | 20-70 m/min | >75 m/min | >80 m/min (auto-stop) |
| Main Drive Motor Current | 80-200 A | >230 A | >260 A (overload trip) |
| Main Motor Temperature | 40-75°C | >85°C | >95°C (thermal trip) |
| Gearbox Oil Temperature | 35-65°C | >70°C | >80°C (alarm) |
| Vibration (Main Drive) | 1.0-4.0 mm/s RMS | >5.5 mm/s | >7.5 mm/s (bearing alarm) |
| Vibration (Stands) | 0.5-3.0 mm/s RMS | >4.5 mm/s | >6.5 mm/s |
| Coolant Flow Rate | 400-500 L/min | <350 L/min | <250 L/min (alarm) |
| Coolant Temperature | 20-40°C | >45°C | >55°C |
| Hydraulic Pressure (Stand Adj.) | 80-140 bar | <70 bar | <50 bar |
| Roll Gap Accuracy | ±0.05mm | >±0.1mm | >±0.2mm (quality reject) |

### 2.2 Roll Change Procedure (Changeover)

1. Complete current production batch
2. STOP mill and apply LOTO
3. Drain coolant from forming area
4. Disconnect universal joint shafts (4 pin clips per stand)
5. Activate hydraulic roll change cylinders
6. Slide out roll cassettes using cassette change trolley
7. Position new roll cassettes (verify roll markings match job card)
8. Slide in and lock cassettes
9. Reconnect universal joint shafts
10. Adjust roll gaps per setup sheet:
    - Top roll gap: Use hydraulic adjustment + dial indicator
    - Side rolls: Manual screw adjustment + dial indicator
11. Thread test strip at 10 m/min
12. Check formed tube profile (roundness, diameter, edge alignment)
13. Adjust if needed → approve by QC → resume production

**Target changeover time: 45 minutes (SMED methodology)**

---

## 3. MAINTENANCE PROCEDURES

### 3.1 Preventive Maintenance Schedule

#### Daily (Every Shift)
- [ ] Check coolant level and concentration (refractometer: 3-5%)
- [ ] Inspect rolls for surface damage (scoring, pitting)
- [ ] Verify roll gap settings against job card
- [ ] Check universal joint shaft play (should be <0.5mm)
- [ ] Lubricate seam guide assembly (NLGI-2 grease, 2 pumps)
- [ ] Clean coolant filters (remove metal sludge)
- [ ] Record motor current and vibration readings

#### Weekly
- [ ] Inspect gearbox oil level (sight glass)
- [ ] Check drive shaft coupling bolts (torque: 120 Nm)
- [ ] Inspect roll surface with magnifying glass for micro-cracks
- [ ] Clean and inspect entry guide rollers
- [ ] Verify hydraulic stand adjustment is responsive
- [ ] Check coolant pH (target: 8.5-9.2)

#### Monthly
- [ ] Gearbox oil analysis (viscosity, particle count)
- [ ] Vibration spectrum analysis on main drive bearings
- [ ] Inspect universal joint spider bearings (replace if worn)
- [ ] Calibrate roll gap dial indicators
- [ ] Inspect and clean electrical panel, check VFD heat sinks
- [ ] Test emergency stops

#### Quarterly
- [ ] Replace gearbox oil (Mobilgear 600 XP 320, 45 liters)
- [ ] Replace coolant (full drain, clean tank, refill)
- [ ] Inspect and re-chrome rolls if wear exceeds 0.1mm
- [ ] Replace universal joint spider bearings (full set)
- [ ] Megger test main motor

#### Annual
- [ ] Complete mill alignment (laser tracker)
- [ ] Main motor bearing replacement
- [ ] Gearbox inspection and bearing check
- [ ] Roll inventory audit and refurbishment
- [ ] Update machine documentation

### 3.2 Spare Parts (Critical)

| Part No. | Description | Min Stock | Lead Time |
|----------|-------------|-----------|-----------|
| YDR-ROLL-SET-25 | Complete roll set per size (7 stands) | 3 sets (popular sizes) | 8-12 weeks |
| YDR-UJ-SPIDER | Universal joint spider bearing | 28 nos. | 2 weeks |
| YDR-SEAL-KIT-HYD | Hydraulic cylinder seal kit | 4 sets | 4 weeks |
| SIM-MOTOR-110KW | Main drive motor 110kW | 1 no. | 6-8 weeks |
| FLD-GEAR-OIL-320 | Mobilgear 600 XP 320 (20L) | 3 pails | 3 days |
| YDR-COOLANT-CONC | Soluble cutting oil concentrate (200L) | 2 drums | 1 week |

---

## 4. TROUBLESHOOTING GUIDE

| Fault | Possible Cause | Remedy |
|-------|---------------|--------|
| Tube diameter too large | Roll gap too wide / wrong roll set | Re-adjust gap per setup sheet |
| Tube diameter too small | Roll gap too tight / thermal expansion | Open gap slightly, check coolant flow |
| Poor edge alignment (mismatch) | Entry guide misaligned / fin pass worn | Re-align guide, inspect fin pass rolls |
| Tube surface scoring | Roll surface damage / foreign particle | Inspect and polish or replace rolls |
| Excessive motor current | Roll gap too tight / bearing seizure / strip too hard | Open gap, check bearings, verify material spec |
| High vibration on drive | Universal joint worn / gearbox bearing / motor bearing | Inspect UJ spiders, vibration analysis |
| Coolant foaming | Wrong concentration / contamination | Test and adjust concentration, change coolant |
| Gearbox noise | Low oil / bearing wear / gear tooth damage | Check oil level, vibration analysis, inspect gears |
| Roll marks on tube | Roll surface defect / coolant contamination | Polish roll surface, filter coolant |
| Uneven forming (twist/bow) | Unequal roll gaps between stands / material camber | Re-set all gaps symmetrically, check material |

---

## 5. SAFETY REQUIREMENTS

### Zone Z3 — Forming Mill Hall
- ✅ Safety helmet with face shield
- ✅ Safety shoes (steel toe, oil-resistant sole)
- ✅ Close-fitting clothing (no loose sleeves near rotating parts)
- ✅ Hearing protection (noise >88 dB(A))
- ✅ Safety glasses (coolant splash protection)
- ⚠️ **EXTREME PINCH HAZARD**: Forming rolls — Never place hands near running rolls
- ⚠️ **ROTATING SHAFTS**: Universal joints rotate at high speed — Stay behind safety guards
- ⚠️ **HOT SURFACES**: Formed tube exits at 50-80°C
- ⚠️ **SLIPPERY FLOOR**: Coolant makes floor slippery — Walk carefully

---

## 6. FAILURE MODES SUMMARY

| FM Code | Failure Mode | Severity | Frequency | MTTR |
|---------|-------------|----------|-----------|------|
| FM-101 | Main drive motor bearing failure | 9/10 | 1/2-3 years | 8-12 hrs |
| FM-102 | Gearbox bearing failure | 8/10 | 1/5-7 years | 16-24 hrs |
| FM-103 | Universal joint spider wear | 5/10 | Every 3-6 months | 2 hrs/joint |
| FM-104 | Roll surface wear/damage | 6/10 | Every 2-4 months | 4-6 hrs (changeover + re-chrome) |
| FM-105 | Coolant pump failure | 5/10 | 1/2-3 years | 2 hrs |
| FM-106 | Hydraulic stand adjustment failure | 6/10 | 1/year | 3 hrs |
| FM-107 | Entry guide misalignment | 4/10 | Monthly | 30 min |
| FM-108 | VFD fault (main drive) | 8/10 | 1/5 years | 2-4 hrs |
| FM-109 | Gearbox oil seal leak | 4/10 | 1/year | 4 hrs |
| FM-110 | Stand foundation bolt loosening | 5/10 | Every 6 months | 2 hrs |

---

## 7. FAILURE HISTORY (Last 24 Months)

| Date | Machine | FM Code | Description | Downtime | Root Cause | Action Taken |
|------|---------|---------|-------------|----------|------------|--------------|
| 2024-08-05 | FRM-201A | FM-103 | UJ spider bearing #3 worn | 2 hrs | Normal wear | Spider replaced |
| 2024-10-12 | FRM-201A | FM-104 | Scoring on Stand 2 top roll | 6 hrs | Metal chip trapped | Roll re-chromed |
| 2024-12-28 | FRM-201A | FM-107 | Edge mismatch on tube | 0.5 hrs | Entry guide shifted | Guide re-aligned |
| 2025-02-14 | FRM-201A | FM-101 | Main motor vibration high (6.2 mm/s) | 10 hrs | Motor DE bearing degraded | Bearing replaced (SKF 6316-2Z) |
| 2025-04-22 | FRM-201A | FM-103 | UJ spiders #1, #5 worn | 3 hrs | Normal wear | Spiders replaced (2 nos.) |
| 2025-07-09 | FRM-201A | FM-105 | Coolant pump seized | 2.5 hrs | Pump impeller wear | Pump replaced |
| 2025-09-18 | FRM-201A | FM-109 | Gearbox output seal leaking | 4 hrs | Shaft wear at seal lip | Seal replaced, shaft sleeve installed |
| 2025-11-25 | FRM-201A | FM-104 | Roll surface pitting Stand 6 | 5 hrs | Coolant contamination | Roll re-chromed, coolant replaced |
| 2026-01-15 | FRM-201B | FM-107 | Entry guide loose after changeover | 0.5 hrs | Bolts not torqued properly | Re-torqued, checklist updated |
| 2026-03-20 | FRM-201A | FM-106 | Hydraulic stand adj. slow on Stand 3 | 3 hrs | Cylinder seal leak | Seal kit replaced |
| 2026-05-08 | FRM-201A | FM-103 | UJ spiders #2, #6, #7 worn | 4 hrs | Accelerated wear (heavy pipe production) | All 14 spiders replaced (preventive) |

---

*Manual Prepared by: Yoder Manufacturing (Formtek Group), USA*
*Localized by: TCS Bharat Steel Pipes Maintenance Department*
*Last Updated: May 2026*
