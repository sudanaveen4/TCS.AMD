# PUMP TROUBLESHOOTING AND DIAGNOSTIC GUIDE
**Document ID**: PUMP-TSG-001
**Revision**: 1.0
**Asset Class**: Centrifugal Pump
**Purpose**: Systematic Diagnosis, Root Cause Identification and Corrective Action Guidance

## 1. Purpose
This troubleshooting guide provides a structured methodology for diagnosing abnormal pump behavior using:
- Telemetry Data
- AI Predictions
- Operational Observations
- Reliability Principles

This document is intended for Control Room Operators, Maintenance Engineers, Reliability Engineers, and the Industrial AI Copilot.

## 2. Diagnostic Philosophy
Effective troubleshooting requires:
1. Identify abnormal telemetry.
2. Identify affected subsystem.
3. Determine probable failure mode.
4. Verify diagnosis using supporting telemetry.
5. Determine urgency.
6. Recommend corrective action.

## 3. High Vibration Troubleshooting

**Symptom**: `vibration > 4 mm/s`

**Step 1: Check Bearing Temperature**
If `bearing_temp` is increasing -> Proceed to Bearing Failure Investigation.

**Step 2: Check Suction Pressure**
If `suction_pressure` is decreasing -> Proceed to Cavitation Investigation.

**Step 3: Check Motor Current**
If `motor_current` is increasing -> Mechanical resistance likely. Possible causes:
- Bearing degradation
- Misalignment
- Rotor imbalance

**Step 4: Review Historical Trend**
Evaluate previous 7 and 30 days.

### AI Diagnostic Logic (Bearing Failure)
If: `Vibration ↑` + `Bearing Temperature ↑` + `Motor Current ↑`
**Diagnosis**: Bearing Failure
**Confidence**: 90%+

![Pump Bearing Wear Diagram](./images/pump_bearing_wear_diagram.png)

## 4. High Bearing Temperature Troubleshooting

**Symptom**: `bearing_temp > 75°C`

**Step 1: Check Lubrication Level**
If `lubrication_level ↓` -> Lubrication deficiency.

**Step 2: Check Vibration**
If `vibration ↑` -> Bearing wear.

**Step 3: Check Motor Current**
If `motor_current ↑` -> Mechanical drag.

### Diagnosis Matrix
| Temperature | Vibration | Current | Likely Cause |
|-------------|-----------|---------|--------------|
| High        | Normal    | Normal  | Lubrication Issue |
| High        | High      | Normal  | Bearing Wear |
| High        | High      | High    | Advanced Bearing Failure |
| High        | Normal    | High    | Mechanical Resistance |

## 5. Reduced Flow Rate Troubleshooting

**Symptom**: `flow_rate < 250 m³/hr`

**Step 1: Check Suction Pressure**
If `suction_pressure ↓` -> Cavitation.

**Step 2: Check Seal Leakage**
If `seal_leakage_rate ↑` -> Seal Failure.

**Step 3: Check Discharge Pressure**
If `discharge_pressure ↓` -> Seal Leakage or Internal Wear.

## 6. Seal Leakage Troubleshooting

**Symptom**: `seal_leakage_rate > 0.1 L/hr`

**Step 1: Determine Leakage Trend**
Is it stable, gradually increasing, or rapidly increasing?

**Step 2: Check Vibration**
If `vibration ↑` -> Misalignment or Bearing degradation causing seal damage.

**Step 3: Check Discharge Pressure**
If `pressure ↓` -> Seal deterioration.

### AI Diagnostic Logic (Seal Failure)
If: `Leakage ↑` + `Pressure ↓` + `Flow ↓`
**Diagnosis**: Seal Failure
**Confidence**: 95%

![Pump Seal Leakage Diagram](./images/pump_seal_leakage_diagram.png)

## 7. Cavitation Investigation

**Symptom**: Operator reports crackling noise, gravel sound, flow instability.
**Telemetry**: Low Suction Pressure, Increased Vibration, Reduced Flow.

**Step 1: Verify Suction Pressure**
If `< 2 bar` -> High cavitation risk.

**Step 2 & 3: Inspect Strainers and Valves**
Check for blockage, fouling, or partial closure.

### AI Diagnostic Logic (Cavitation)
If: `Low Suction Pressure` + `High Vibration` + `Flow Reduction`
**Diagnosis**: Cavitation
**Confidence**: 95%

![Pump Cavitation Flow Diagram](./images/pump_cavitation_flow_diagram.png)

## 8. AI Copilot Escalation Logic

- **Low Risk**: Failure Probability < 50% -> Monitor
- **Medium Risk**: Failure Probability 50% - 80% -> Maintenance Notification
- **High Risk**: Failure Probability 80% - 90% -> Schedule Maintenance
- **Critical Risk**: Failure Probability 90% - 95%, RUL < 30 Days -> Reliability Engineer Review
- **Emergency**: Failure Probability > 95%, RUL < 10 Days -> Immediate Maintenance Planning
