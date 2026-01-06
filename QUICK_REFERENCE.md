# Point and Print - Quick Reference

## Script Name
`point_and_print.py`

## Purpose
Automatically point your camera at each object during multi-object 3D prints by inserting Klipper servo commands into gcode.

## Quick Start (5 Steps)

### 1. Hardware Setup
- Mount servo with camera
- Connect servo signal wire to printer control board
- Wire power and ground

### 2. Klipper Configuration (printer.cfg)
```ini
[servo camera_servo]
pin: PB6  # Change to your pin
maximum_servo_angle: 180
minimum_pulse_width: 0.0005
maximum_pulse_width: 0.0025
initial_angle: 90
```

### 3. Calibrate Servo Center Angle
```gcode
SET_SERVO SERVO=camera_servo ANGLE=90
SET_SERVO SERVO=camera_servo ANGLE=85
SET_SERVO SERVO=camera_servo ANGLE=87  # Camera points at bed center!
```
Record the angle where camera points at bed center.

### 4. Configure Script
Edit `point_and_print.py`:
```python
CAMERA_X = 0.0              # Camera position X
CAMERA_Y = 0.0              # Camera position Y
BED_WIDTH = 350.0           # Bed width
BED_DEPTH = 350.0           # Bed depth
SERVO_RANGE = 180           # 90 or 180
SERVO_NAME = "camera_servo" # Must match printer.cfg
SERVO_CENTER_ANGLE = 87.0   # From calibration
INVERT_SERVO = False        # True if upside down
```

### 5. Add to Slicer
PrusaSlicer/SuperSlicer: Print Settings → Output Options → Post-processing scripts:
```
python /full/path/to/point_and_print.py
```

## Configuration Variables

| Variable | Purpose | Common Values |
|----------|---------|---------------|
| `CAMERA_X` | Camera X position (mm) | 0, -40, 350 |
| `CAMERA_Y` | Camera Y position (mm) | 0, 350, -40 |
| `BED_WIDTH` | Bed X dimension (mm) | 220, 300, 350 |
| `BED_DEPTH` | Bed Y dimension (mm) | 220, 300, 350 |
| `SERVO_RANGE` | Servo movement range | 90, 180 |
| `SERVO_NAME` | Name in printer.cfg | "camera_servo" |
| `SERVO_CENTER_ANGLE` | Angle pointing at bed center | 45, 90, or custom |
| `INVERT_SERVO` | Upside-down mounting | True, False |

## Testing

### Manual Test
```bash
python point_and_print.py test_file.gcode
```

### Verify Output
Open gcode, search for `SET_SERVO`:
```gcode
SET_SERVO SERVO=camera_servo ANGLE=90.00
EXCLUDE_OBJECT_START NAME=object_name
```

### Test Print
Start print and verify servo moves camera to point at each object.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Servo doesn't move | Check wiring, verify pin in printer.cfg |
| Points wrong direction | Calibrate `SERVO_CENTER_ANGLE` |
| Moves opposite way | Set `INVERT_SERVO = True` |
| Servo name error | Match `SERVO_NAME` to printer.cfg |
| Angles out of range | Check `SERVO_RANGE` (90 or 180) |

## Common Pin Assignments

**Raspberry Pi:**
- `gpio17`, `gpio27`, `gpio22`

**SKR Boards:**
- `PB6`, `PE5`, `PA1`

**Check your board's pinout diagram!**

## Example Configurations

### Front-Left Camera, 180° Servo
```python
CAMERA_X = 0.0
CAMERA_Y = 0.0
BED_WIDTH = 350.0
BED_DEPTH = 350.0
SERVO_RANGE = 180
SERVO_CENTER_ANGLE = 90.0
```

### Back-Right Camera, 90° Servo
```python
CAMERA_X = 350.0
CAMERA_Y = 350.0
BED_WIDTH = 350.0
BED_DEPTH = 350.0
SERVO_RANGE = 90
SERVO_CENTER_ANGLE = 45.0
```

### Off-Bed Camera, Upside-Down
```python
CAMERA_X = -40.0
CAMERA_Y = 350.0
BED_WIDTH = 350.0
BED_DEPTH = 350.0
SERVO_RANGE = 180
SERVO_CENTER_ANGLE = 87.5
INVERT_SERVO = True
```

## Files Included

- `point_and_print.py` - Main script
- `README.md` - Full documentation
- `KLIPPER_SETUP.md` - Klipper configuration guide
- `SERVO_CALIBRATION_GUIDE.md` - Calibration walkthrough
- `SLICER_SETUP.md` - Slicer integration guide
- `ANGLE_GUIDE.md` - Understanding angle calculations
- `SERVO_INVERSION_GUIDE.md` - Upside-down servo guide

## Support

For detailed instructions, see the full documentation files.

## Quick Command Reference

```gcode
# Test servo movement
SET_SERVO SERVO=camera_servo ANGLE=0
SET_SERVO SERVO=camera_servo ANGLE=90
SET_SERVO SERVO=camera_servo ANGLE=180

# Calibrate center
SET_SERVO SERVO=camera_servo ANGLE=85
SET_SERVO SERVO=camera_servo ANGLE=87
SET_SERVO SERVO=camera_servo ANGLE=90
SET_SERVO SERVO=camera_servo ANGLE=92
SET_SERVO SERVO=camera_servo ANGLE=95
```

## License

Free to use and modify.
