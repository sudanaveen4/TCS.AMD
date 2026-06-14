# STANDARD OPERATING PROCEDURE (SOP)
**Document Title**: Atmospheric Distillation Column Startup & Normal Operations
**Document ID**: CDU-SOP-01
**Unit**: Crude Distillation Unit (CDU)
**Revision**: 3.2
**Date**: 2026-04-15

## 1. Overview
The Atmospheric Distillation Column separates heated crude oil into distinct fractions (naphtha, kerosene, diesel, and atmospheric residue) based on boiling points. This SOP outlines the safe startup and steady-state monitoring of the column.

![Distillation Column Diagram](./images/distillation_column_diagram.png)

## 2. Pre-Startup Prerequisites
1. **Safety Permitting**: Ensure all Confined Space Entry (CSE) and Hot Work permits are closed out.
2. **Valve Alignment**: Complete a full line-walk. Ensure all block valves on the overhead condensers and side-strippers are in the OPEN position.
3. **Nitrogen Purge**: Confirm the tower has been purged with nitrogen to < 2% oxygen.

## 3. Startup Sequence
1. **Establish Cold Circulation**: Start the main crude charge pumps. Circulate cold crude oil through the Heat Exchanger Network (HEN) and the bypass loop of the Fired Heater.
2. **Introduce Heat**: Gradually introduce fuel gas to the Fired Heater (refer to `SOP_Fired_Heater_Operations.md`). Increase temperature at a maximum rate of 25°C/hr.
3. **Establish Reflux**: Once the overhead vapor reaches the condenser and accumulates in the reflux drum, start the reflux pumps.
   * *Critical Parameter*: Maintain reflux ratio to control the top temperature at 110°C ± 5°C.
4. **Side-Draws**: As internal liquid traffic builds, slowly open the control valves to the side-strippers.

## 4. Normal Operating Parameters
| Parameter | Setpoint | Alarm High (AH) | Alarm Low (AL) |
|-----------|----------|-----------------|----------------|
| Tower Top Temp | 110°C | 120°C | 95°C |
| Flash Zone Temp | 350°C | 365°C | 330°C |
| Overhead Pressure | 1.2 barg | 1.5 barg | 0.8 barg |
| Bottoms Level | 50% | 80% | 20% |

## 5. Troubleshooting
* **Loss of Reflux**: If reflux pumps fail (see AI prediction models), the top temperature will spike. Product will go off-spec immediately. Action: Reduce Fired Heater duty by 20% and manually start the standby pump.
* **Flooding**: Indicated by a high differential pressure across the column (> 0.5 barg). Action: Reduce the feed rate and check for excessive steam injection in the side-strippers.
