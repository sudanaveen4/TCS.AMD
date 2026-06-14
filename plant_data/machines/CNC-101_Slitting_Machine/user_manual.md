# CNC SLITTING & CUTTING MACHINE — MODEL: BRONX CTL-1500
## Machine ID: CNC-101A (Production Line A) / CNC-101B (Production Line B)
## COMPREHENSIVE USER & MAINTENANCE MANUAL

---

### Document Control

| Field | Value |
|-------|-------|
| **Document No.** | TBSP-MAN-CNC101-001 |
| **Revision** | 5.0 |
| **Date** | January 2026 |
| **Manufacturer** | Bronx International (UK) |
| **Model** | CTL-1500 CNC Slitting Line |
| **Serial No.** | CNC-101A: BRX-2018-04521 / CNC-101B: BRX-2024-08934 |
| **Year of Manufacture** | CNC-101A: 2018 / CNC-101B: 2024 |
| **Installation Date** | CNC-101A: 15-Jun-2018 / CNC-101B: 10-Mar-2024 |
| **Warranty Status** | CNC-101A: Expired / CNC-101B: Valid until Mar 2027 |

---

## 1. GENERAL DESCRIPTION

### 1.1 Machine Overview
The Bronx CTL-1500 is a fully automated CNC coil slitting and cut-to-length line designed for processing hot-rolled (HR) and cold-rolled (CR) steel coils into precision-width flat strips. The machine is the first stage in the pipe manufacturing process, converting master coils into strips ready for tube forming.

### 1.2 Major Components
1. **Decoiler** — Hydraulically expanding mandrel (capacity: 25 MT, coil OD: 1200-2000mm)
2. **Straightener/Leveller** — 9-roll precision leveller for strip flatness correction
3. **Edge Trimmer** — Dual rotary blade edge trimming unit
4. **CNC Slitting Head** — Multi-blade rotary slitting arbor (up to 12 blades)
5. **Scrap Winder** — Edge scrap collection reels (2 nos.)
6. **Strip Accumulator** — Looping pit (capacity: 30m strip length) for continuous downstream feeding
7. **Flying Shear** — Pneumatic cut-off for length-based cutting (optional mode)
8. **Control Panel** — Siemens S7-1500 PLC with HMI touchscreen

### 1.3 Technical Specifications

| Parameter | Specification |
|-----------|--------------|
| **Coil Width (input)** | 200mm – 1500mm |
| **Strip Width (output)** | 30mm – 500mm (±0.1mm tolerance) |
| **Strip Thickness** | 1.2mm – 6.0mm |
| **Line Speed** | 0 – 120 m/min (variable) |
| **Maximum Coil Weight** | 25,000 kg |
| **Slitting Blade Diameter** | 250mm (HSS M2 grade) |
| **Motor — Decoiler** | 37 kW AC Servo (ABB ACS880) |
| **Motor — Slitting Drive** | 55 kW AC Servo (ABB ACS880) |
| **Motor — Leveller** | 22 kW AC Motor (Siemens) |
| **Hydraulic System** | Bosch Rexroth, 160 bar, 45 LPM |
| **Pneumatic Supply** | 6-7 bar, dry air, 200 NL/min |
| **Electrical Supply** | 415V, 3-phase, 50 Hz |
| **Control System** | Siemens S7-1500 PLC + KTP1200 HMI |
| **Weight (total)** | 38,000 kg |
| **Dimensions (L×W×H)** | 18m × 4m × 3.5m |

---

## 2. OPERATING PROCEDURES

### 2.1 Pre-Start Checklist

| # | Check Item | Method | Accept Criteria |
|---|-----------|--------|----------------|
| 1 | Hydraulic oil level | Sight glass on HPU | Between MIN and MAX marks |
| 2 | Hydraulic oil temperature | Temperature gauge | 25°C – 55°C |
| 3 | Pneumatic supply pressure | Pressure gauge at FRL | 6.0 – 7.0 bar |
| 4 | Slitting blades condition | Visual inspection | No chips, cracks, or wear >0.5mm |
| 5 | Blade spacer rings | Micrometer check | Correct width per job card |
| 6 | Edge trimmer blades | Visual inspection | Sharp edges, no burrs |
| 7 | Safety guards in place | Physical check | All interlocks engaged (green LED) |
| 8 | Emergency stops | Function test (all 4 E-stops) | Immediate line stop |
| 9 | Lubrication system | Check grease reservoir level | Above minimum mark |
| 10 | Strip accumulator pit | Visual check | No debris, sensors clean |

### 2.2 Startup Sequence

1. Turn ON main isolator (MCC panel)
2. Turn ON control power (key switch on main panel)
3. Wait for PLC boot (approx. 45 seconds — HMI shows "SYSTEM READY")
4. Select mode: AUTO / MANUAL / JOG
5. Enter job parameters on HMI:
   - Coil ID / Material grade
   - Input coil width
   - Number of strips
   - Strip width(s)
   - Line speed setpoint
6. Start hydraulic power pack (HPP button)
7. Wait for hydraulic pressure to reach 120 bar (green indicator)
8. Load coil onto decoiler mandrel using crane
9. Thread strip through leveller → slitting head → scrap winders → accumulator
10. Press LINE START (green illuminated button)

### 2.3 Normal Operating Parameters

| Parameter | Normal Range | Warning | Critical / Trip |
|-----------|-------------|---------|----------------|
| Line Speed | 40-100 m/min | >110 m/min | >120 m/min (auto-stop) |
| Decoiler Motor Current | 25-80 A | >100 A | >120 A (overload trip) |
| Slitting Drive Current | 40-120 A | >140 A | >160 A (overload trip) |
| Hydraulic Pressure | 100-160 bar | <90 bar | <70 bar (low pressure trip) |
| Hydraulic Oil Temp | 30-55°C | >60°C | >70°C (high temp trip) |
| Vibration (Slitting Head) | 0.5-3.0 mm/s RMS | >4.0 mm/s | >6.0 mm/s (bearing alarm) |
| Vibration (Decoiler) | 0.3-2.5 mm/s RMS | >3.5 mm/s | >5.0 mm/s (imbalance alarm) |
| Strip Tension | 5-25 kN | >30 kN | >35 kN (tension trip) |
| Blade Temperature | 30-80°C | >90°C | >110°C (overheat alarm) |
| Noise Level | 75-85 dB(A) | >90 dB(A) | >95 dB(A) (investigate) |

### 2.4 Shutdown Sequence

1. Complete current coil processing
2. Press LINE STOP (controlled deceleration)
3. Retract decoiler mandrel
4. Remove scrap coils from winders
5. Clean slitting head area (remove metal fines)
6. Stop hydraulic power pack
7. Switch to MANUAL mode
8. Turn OFF control power
9. Turn OFF main isolator (if end of production shift)

---

## 3. MAINTENANCE PROCEDURES

### 3.1 Preventive Maintenance Schedule

#### Daily Maintenance (Every Shift — 15 minutes)
- [ ] Clean metal fines from slitting head and blade guard area
- [ ] Check hydraulic oil level and top up if needed (use Mobil DTE 25)
- [ ] Inspect slitting blades for wear (use wear gauge)
- [ ] Verify all safety interlocks are functional
- [ ] Grease decoiler mandrel expansion mechanism (2 pumps NLGI-2 grease)
- [ ] Check strip accumulator photocell sensors — clean with dry cloth
- [ ] Record vibration readings from decoiler and slitting head (vibration meter)
- [ ] Log all parameters in shift logbook

#### Weekly Maintenance (Saturday Day Shift — 2 hours)
- [ ] Replace hydraulic filter if differential pressure indicator shows RED
- [ ] Check and adjust blade clearance (target: 8-10% of strip thickness)
- [ ] Inspect edge trimmer blades — sharpen or replace if worn
- [ ] Check belt tension on leveller drive (deflection: 10-15mm at mid-span)
- [ ] Lubricate all linear guides (Mobilux EP-2 grease, 3 pumps per point)
- [ ] Inspect pneumatic cylinders for leaks (apply soapy water)
- [ ] Clean HMI screen and check all indicator lamps
- [ ] Verify hydraulic oil temperature alarm setpoints on PLC

#### Monthly Maintenance (1st Saturday — 4 hours)
- [ ] Complete hydraulic oil analysis (send sample to lab — check viscosity, particle count, water content)
- [ ] Inspect and clean hydraulic tank breather filter
- [ ] Check decoiler motor alignment (laser alignment tool)
- [ ] Inspect slitting arbor bearings (vibration spectrum analysis)
- [ ] Calibrate strip tension sensor (use calibrated load cell)
- [ ] Inspect electrical connections in MCC panel (torque check all terminals)
- [ ] Test all emergency stop circuits (function test with witness)
- [ ] Update PLC backup on USB drive

#### Quarterly Maintenance (Planned Shutdown — 8 hours)
- [ ] Replace hydraulic oil (Mobil DTE 25 — 380 liters) if oil analysis indicates
- [ ] Replace slitting arbor bearings (FAG 6210-2RS — 4 nos. per arbor)
- [ ] Overhaul decoiler hydraulic cylinder seals
- [ ] Inspect and replace scrap winder clutch pads
- [ ] Calibrate all pressure gauges and temperature sensors
- [ ] Inspect electrical cables and conduits for damage
- [ ] Megger test all motors (minimum insulation resistance: 5 MΩ)
- [ ] Complete vibration baseline survey

#### Annual Maintenance (Annual Shutdown — 3 days)
- [ ] Complete machine overhaul per manufacturer's checklist
- [ ] Replace all hydraulic hoses (regardless of condition)
- [ ] Re-align complete slitting line (laser alignment)
- [ ] Replace all slitting blades (full set — 24 blades)
- [ ] Overhaul leveller rolls (re-chrome if worn)
- [ ] Calibrate PLC analog inputs/outputs
- [ ] Update machine documentation and nameplate data
- [ ] Repaint machine guards and safety markings

### 3.2 Lubrication Chart

| Location | Lubricant | Grade | Quantity | Frequency | Method |
|----------|-----------|-------|----------|-----------|--------|
| Decoiler mandrel bearings | Grease | Mobilux EP-2 (NLGI-2) | 5g per point | Daily | Grease gun |
| Slitting arbor bearings | Grease | SKF LGMT 2 | 3g per point | Weekly | Grease gun |
| Leveller roll bearings | Grease | Mobilux EP-2 | 5g per point | Weekly | Grease gun |
| Linear guides (all) | Grease | Mobilux EP-2 | 3 pumps/guide | Weekly | Central lube pump |
| Hydraulic system | Oil | Mobil DTE 25 (ISO VG 46) | 380 liters | Quarterly / as needed | Fill via breather filter |
| Gearbox (leveller) | Oil | Mobilgear 600 XP 220 | 8 liters | 6 months | Drain & fill |
| Pneumatic FRL | Oil | Mobil Almo 525 | 200ml | As needed | Lubricator refill |

### 3.3 Spare Parts List (Critical)

| Part No. | Description | Quantity (Min Stock) | Lead Time | Supplier |
|----------|-------------|---------------------|-----------|----------|
| BRX-SB-250-M2 | Slitting blade Ø250mm HSS M2 | 24 nos. | 4 weeks | Bronx UK / TCT India |
| FAG-6210-2RS | Arbor bearing 6210-2RS | 8 nos. | 1 week | FAG India |
| BRX-HYD-SEAL-KIT | Decoiler cylinder seal kit | 2 sets | 6 weeks | Bronx UK |
| ABB-ACS880-55KW | Drive module (slitting) | 1 no. | 8 weeks | ABB India |
| SIM-S7-1500-CPU | PLC CPU module (spare) | 1 no. | 4 weeks | Siemens India |
| BRX-CLUTCH-PAD | Scrap winder clutch pad set | 4 sets | 3 weeks | Bronx UK |
| MOBIL-DTE25-200L | Hydraulic oil drum 200L | 2 drums | 3 days | ExxonMobil distributor |
| BRX-TENSION-LOAD | Tension sensor load cell | 1 no. | 6 weeks | Bronx UK |

---

## 4. TROUBLESHOOTING GUIDE

### 4.1 Common Faults and Remedies

| Fault Code | Description | Possible Cause | Remedy | Severity |
|-----------|-------------|----------------|--------|----------|
| F-001 | Decoiler overload trip | Coil stuck on mandrel / bearing seizure | Check mandrel expansion, inspect bearings | HIGH |
| F-002 | Slitting drive overcurrent | Blade dullness / misalignment / strip jam | Replace blades, check alignment | HIGH |
| F-003 | Low hydraulic pressure | Oil leak / pump wear / filter clogged | Check for leaks, replace filter, inspect pump | MEDIUM |
| F-004 | High hydraulic oil temperature | Cooler fan failure / oil degradation | Check cooler fan, replace oil if viscosity low | MEDIUM |
| F-005 | High vibration — slitting head | Bearing wear / blade imbalance / loose bolts | Replace bearings, balance blade assembly | HIGH |
| F-006 | High vibration — decoiler | Coil eccentricity / bearing wear | Re-center coil, check bearings | MEDIUM |
| F-007 | Strip tension fault | Tension sensor failure / strip breakage | Calibrate sensor, check strip quality | HIGH |
| F-008 | Strip width out of tolerance | Blade spacer error / blade wear | Verify spacers, replace worn blades | MEDIUM |
| F-009 | Emergency stop activated | Safety hazard detected | Investigate cause, reset after clearance | CRITICAL |
| F-010 | PLC communication loss | Network cable fault / module failure | Check cables, replace module if needed | HIGH |
| F-011 | Accumulator pit full alarm | Downstream machine stopped | Check forming mill status, clear accumulator | MEDIUM |
| F-012 | Pneumatic pressure low | Compressor issue / air leak | Check main compressor, find and fix leaks | LOW |
| F-013 | Edge trim scrap winder full | Scrap not removed | Remove full scrap coil, install empty reel | LOW |
| F-014 | Blade temperature high | Insufficient cooling / excessive speed | Reduce speed, check coolant flow | MEDIUM |
| F-015 | Decoiler mandrel won't expand | Hydraulic cylinder seal leak | Replace cylinder seals | HIGH |

### 4.2 Diagnostic Decision Tree

```
MACHINE WON'T START
├── Check main isolator → OFF? → Turn ON
├── Check E-stop buttons → Pressed? → Investigate, release, reset
├── Check HMI → Error displayed? → Note error code, refer to 4.1
├── Check hydraulic pressure → Low? → See F-003
├── Check safety interlocks → Open? → Close guards, verify sensors
└── PLC fault → Call electrical maintenance

HIGH VIBRATION ALARM
├── Which component? → Slitting Head → See F-005
│                    → Decoiler → See F-006
├── Recent blade change? → YES → Check blade balance and spacers
├── New coil loaded? → YES → Check coil centering and weight
├── Vibration level? → >6.0 mm/s → STOP IMMEDIATELY
│                    → 4.0-6.0 → Reduce speed, schedule maintenance
│                    → <4.0 → Monitor, log readings
└── Bearing temperature rising? → YES → Lubrication issue, check grease

STRIP WIDTH OUT OF TOLERANCE
├── Check blade spacers → Wrong sizes? → Correct per job card
├── Check blade condition → Worn? → Replace blade set
├── Check blade tightness → Loose? → Re-torque arbor nut (180 Nm)
├── Check strip material → Different grade? → Verify material certificate
└── Recent blade change? → YES → Verify setup against job card
```

---

## 5. SAFETY INSTRUCTIONS

### 5.1 Mandatory PPE in Machine Zone (Z2)
- ✅ Safety helmet (IS 2925)
- ✅ Safety shoes (IS 15298, steel toe)
- ✅ Cut-resistant gloves (EN 388 Level 5)
- ✅ Safety glasses (IS 5983)
- ✅ Ear plugs/muffs (NRR 25 dB minimum)
- ✅ High-visibility vest

### 5.2 Lockout/Tagout (LOTO) Requirements
Before any maintenance work:
1. Inform shift supervisor and control room
2. Press Emergency Stop on machine
3. Turn OFF main isolator and apply LOTO padlock
4. Bleed hydraulic pressure to zero (open bleed valve)
5. Bleed pneumatic pressure (open drain valve)
6. Verify zero energy state (attempt restart — must not start)
7. Place LOTO tag with technician name, date, time, and reason
8. Only the person who applied LOTO can remove it

### 5.3 Hazard Warnings
- ⚠️ **PINCH POINTS**: Multiple nip points at rollers. Never reach into running rolls.
- ⚠️ **SHARP EDGES**: Slit strip edges are extremely sharp. Always use cut-resistant gloves.
- ⚠️ **ROTATING PARTS**: Slitting arbor, winders, and rolls rotate at high speed. Keep clear.
- ⚠️ **HYDRAULIC PRESSURE**: System operates at 160 bar. Never open connections under pressure.
- ⚠️ **HOT SURFACES**: Blades and strip can reach 80-100°C during operation.
- ⚠️ **NOISE**: Operating noise exceeds 85 dB(A). Hearing protection mandatory.
- ⚠️ **FLYING METAL CHIPS**: Edge trimming produces metal chips. Safety glasses mandatory.

---

## 6. ELECTRICAL SCHEMATICS (Summary)

### 6.1 Power Distribution

```
Incoming Supply (415V, 3-phase, 50Hz)
├── Main Isolator (630A MCCB)
│   ├── Slitting Drive Motor (55 kW) — via ABB ACS880 VFD
│   ├── Decoiler Motor (37 kW) — via ABB ACS880 VFD
│   ├── Leveller Motor (22 kW) — via DOL Starter
│   ├── Scrap Winder Motors (2 × 5.5 kW) — via VFD
│   ├── Hydraulic Pump Motor (22 kW) — via Star-Delta Starter
│   ├── Cooling Fan Motors (2 × 2.2 kW) — via DOL
│   └── Control Power Transformer (415V/230V, 5 kVA)
│       ├── PLC Power Supply (24V DC)
│       ├── HMI Panel
│       ├── Solenoid Valves
│       └── Sensor Power
```

### 6.2 PLC I/O Summary

| Module | Type | Count | Connected To |
|--------|------|-------|-------------|
| DI-01 | Digital Input 32ch | 32 | E-stops, interlocks, limit switches |
| DI-02 | Digital Input 32ch | 32 | Proximity sensors, photocells |
| DO-01 | Digital Output 16ch | 16 | Solenoid valves, indicator lamps |
| DO-02 | Digital Output 16ch | 16 | Motor starters, horns |
| AI-01 | Analog Input 8ch | 8 | Pressure, temperature, tension |
| AI-02 | Analog Input 8ch | 8 | Vibration sensors, current sensors |
| AO-01 | Analog Output 4ch | 4 | VFD speed references |

---

*Manual prepared by: Bronx International Engineering Dept., UK*
*Localized by: TCS Bharat Steel Pipes Technical Team*
*Last Updated: January 2026*
