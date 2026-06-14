# Coperion Twin-Screw Extruder TE-90 Service Guide
**Manufacturer**: Coperion
**Machine Type**: Co-Rotating Twin-Screw Extruder (ZSK Series equivalent)
**Location**: Zone Z2 (Forming & Extrusion)

## 1. System Overview
The TE-90 twin-screw extruder is the heart of the High-Moisture Extrusion (HME) process. It applies intense thermomechanical energy (heat and shear) to denature plant proteins and melt them into a continuous viscoelastic mass.

![Coperion Extruder Diagram](./images/coperion_extruder_diagram.png)

## 2. Operating Parameters
- **Normal RPM**: 1400 - 1480 RPM
- **Normal Throughput**: 400 - 480 kg/h
- **Melt Temperature**: 135°C - 155°C (Critical)
- **Motor Current**: 10.0 A - 15.0 A
- **Normal Vibration Limit**: < 3.5 mm/s

## 3. Maintenance & Troubleshooting

### 3.1 Overheating / Cooling Jacket Failure
The barrel uses water cooling jackets to maintain exact temperature profiles.
- **Symptoms**: Temperature rises sharply above 160°C.
- **Risk**: Protein burning, blocked die, product degradation.
- **Action**: Check cooling water flow. If flow is normal, suspect a failed thermocouple or scaling in the cooling jacket.

### 3.2 Main Drive Bearing Failure
The intense axial load on the twin screws requires robust thrust bearings.
- **Symptoms**: Vibration spikes > 12.0 mm/s, often accompanied by a drive unit temperature > 80°C.
- **Action**: Emergency Stop. A bearing failure under full load will destroy the gearbox. Requires complete gearbox inspection and bearing replacement (Coperion Part #BRG-90-A).

### 3.3 Die Pressure Spikes
- **Symptoms**: Current spikes > 20A, pressure rises rapidly.
- **Action**: Indicates a blockage in the cooling die (Z3). Reduce RPM immediately to prevent barrel burst.

## 4. Operational Safety
- **Burn Hazard**: Barrel temperatures exceed 150°C. High-temperature gloves mandatory.
- **Pressure Hazard**: Never open the die plate while the barrel is pressurized.
