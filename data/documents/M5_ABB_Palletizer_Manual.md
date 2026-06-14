# ABB Robotic Palletizer Pro Guide
**Manufacturer**: ABB Robotics
**Machine Type**: 4-Axis Articulated Palletizing Robot
**Location**: Zone Z5 (Packaging & Dispatch)

## 1. System Overview
The Palletizer Pro takes the boxed, finished plant-based meat products and stacks them onto shipping pallets using a customized vacuum gripper. 

![ABB Palletizer Diagram](./images/abb_palletizer_diagram.png)

## 2. Operating Parameters
- **Normal Operations**: 400 - 460 kg/h packing rate.
- **Servo Temperature**: 40°C - 55°C
- **Current**: 5.0 A - 15.0 A
- **Payload Capacity**: 50 kg

## 3. Maintenance & Troubleshooting

### 3.1 Servo Overheating
- **Symptoms**: Base or wrist servo temperatures exceed 65°C.
- **Action**: This indicates a failing servo brake, poor ventilation, or operating above payload limits. Halt the robot, allow cooling, and perform a thermal diagnostic on Servo Axis 2 and 3.

### 3.2 Vacuum Gripper Failure
- **Symptoms**: Dropped boxes. Air pressure alarms.
- **Action**: Inspect the suction cups for tears. Verify the pneumatic air supply line is maintaining > 6.0 Bar pressure.

## 4. Safety & Zone Z5 Restrictions
- **Restricted Zone**: The robot operates within a fenced safety cell.
- **Light Curtain**: Entry into Zone Z5 will trip the safety light curtain, instantly causing an Emergency Stop (Category 0). 
- **Restart Procedure**: Must be manually acknowledged from the HMI panel outside the cell before motion can resume.
