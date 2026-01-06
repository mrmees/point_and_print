# Klipper Setup Guide for Camera Servo

This guide walks you through setting up a servo-controlled camera mount with Klipper.

## Hardware Requirements

- **Servo motor**: 90° or 180° servo (e.g., SG90, MG90S, or similar)
- **Camera mount**: Attached to the servo
- **Control board**: Your printer's control board with an available PWM-capable pin
- **Wiring**: 3 wires (power, ground, signal)

## Step 1: Wire the Servo

Typical servo wire colors:
- **Red/Orange**: Power (5V)
- **Brown/Black**: Ground (GND)
- **Yellow/White/Orange**: Signal (PWM control)

### Finding Power and Ground

**Option A: Use printer's 5V output**
- Check your board's pinout diagram for 5V and GND pins
- Most boards have 5V pins on endstop or fan connectors

**Option B: External power**
- Use a separate 5V power supply
- **Important**: Connect grounds together (printer GND to external GND)

### Finding a Signal Pin

You need a PWM-capable GPIO pin:

**Raspberry Pi pins** (if running Klipper on RPi):
- GPIO17, GPIO27, GPIO22, GPIO23, GPIO24, GPIO25, etc.
- Example: Connect signal wire to GPIO17

**BTT SKR boards**:
- Common servo pins: PB6, PE5, PA1, PA2, PC6
- Check your board's schematic

**Creality boards**:
- Look for unused fan or probe pins (often labeled "SERVO")

**Warning**: Don't use pins already assigned to heaters, steppers, or endstops!

## Step 2: Configure printer.cfg

### Basic Servo Configuration

Add this to your `printer.cfg`:

```ini
[servo camera_servo]
pin: PB6  # Change to your actual pin
maximum_servo_angle: 180
minimum_pulse_width: 0.0005
maximum_pulse_width: 0.0025
initial_angle: 90
```

### Pin Examples

**For Raspberry Pi GPIO17**:
```ini
pin: gpio17
```

**For SKR board PB6**:
```ini
pin: PB6
```

**For inverted pin** (if servo moves backwards):
```ini
pin: !PB6
```

### Parameter Explanations

- **pin**: The GPIO pin connected to servo signal wire
- **maximum_servo_angle**: 90 or 180 depending on your servo
- **minimum_pulse_width**: Minimum PWM pulse width (typically 0.0005 to 0.001)
- **maximum_pulse_width**: Maximum PWM pulse width (typically 0.0024 to 0.0025)
- **initial_angle**: Starting angle when Klipper starts (use midpoint)

### Advanced: Pulse Width Tuning

If your servo doesn't reach full range or buzzes:

1. Start with default values
2. Test with: `SET_SERVO SERVO=camera_servo ANGLE=0`
3. Test with: `SET_SERVO SERVO=camera_servo ANGLE=180` (or 90)
4. Adjust `minimum_pulse_width` and `maximum_pulse_width` if needed

**Common adjustments**:
- Servo doesn't reach 0°: Decrease `minimum_pulse_width` to 0.0004
- Servo doesn't reach 180°: Increase `maximum_pulse_width` to 0.0026
- Servo buzzes/jitters: Your pulse width is at the mechanical limit

## Step 3: Restart Klipper

After editing `printer.cfg`:

1. Save the file
2. Click **Restart** in your Klipper interface (Mainsail/Fluidd)
3. Check for errors in the console

## Step 4: Test the Servo

### Manual Testing

In your Klipper console, send these commands:

```gcode
# Test midpoint (should point at bed center if physically aligned)
SET_SERVO SERVO=camera_servo ANGLE=90

# Test left rotation
SET_SERVO SERVO=camera_servo ANGLE=45

# Test right rotation
SET_SERVO SERVO=camera_servo ANGLE=135

# For 90° servo, test full range:
SET_SERVO SERVO=camera_servo ANGLE=0
SET_SERVO SERVO=camera_servo ANGLE=45
SET_SERVO SERVO=camera_servo ANGLE=90
```

### Physical Alignment

**Important**: Physically align your servo so that at midpoint, the camera points at bed center:

1. Send: `SET_SERVO SERVO=camera_servo ANGLE=90` (or 45 for 90° servo)
2. Manually adjust the camera/mount so it points at bed center
3. Tighten the servo horn/mount in this position
4. Test other angles to verify smooth rotation

## Step 5: Configure the Script

Edit `gcode_camera_inserter.py`:

```python
CAMERA_X = 0.0      # Your camera's X position
CAMERA_Y = 0.0      # Your camera's Y position
BED_WIDTH = 350.0   # Your bed width
BED_DEPTH = 350.0   # Your bed depth
SERVO_RANGE = 180   # 90 or 180 to match your servo
SERVO_NAME = "camera_servo"  # Must match [servo camera_servo] in printer.cfg
```

## Step 6: Test with GCode

Slice a test print and run the post-processing script. Check the generated gcode contains:

```gcode
SET_SERVO SERVO=camera_servo ANGLE=90.00
EXCLUDE_OBJECT_START NAME=object_name
```

## Troubleshooting

### Servo doesn't move
- Check wiring (especially signal pin)
- Verify pin assignment in printer.cfg
- Check Klipper console for errors
- Try a different PWM-capable pin

### Servo moves in wrong direction
- Angles are correct but camera points wrong way
- The servo horn might be installed 180° off
- **OR** the servo is mounted upside down
- **Solution 1**: Remove and reattach servo horn in correct orientation
- **Solution 2**: Set `INVERT_SERVO = True` in the script (mirrors all angles)

### Understanding INVERT_SERVO

If your servo is physically mounted upside down, the rotation direction will be reversed. Instead of remounting the hardware, you can set `INVERT_SERVO = True` in the script.

**How it works:**
- Mirrors angles over the centerline
- For 180° servo: `inverted_angle = 180 - normal_angle`
- For 90° servo: `inverted_angle = 90 - normal_angle`
- Center angle (90° or 45°) stays the same

**Example with 180° servo:**
- Normal 60° → Inverted 120°
- Normal 90° → Inverted 90° (unchanged)
- Normal 120° → Inverted 60°

**When to use:**
- Servo is physically mounted upside down and cannot be remounted
- Camera pans in the opposite direction from expected
- Angles are numerically correct but pointing wrong way

### Servo jitters/buzzes
- Pulse width at mechanical limit
- Adjust `minimum_pulse_width` or `maximum_pulse_width`
- Some servos are just noisy (especially cheap ones)

### Servo doesn't hold position
- Weak servo - may need more torque
- Power supply insufficient (use external 5V supply)
- Loose camera mount (add mechanical resistance)

### Wrong angles in gcode
- Verify `SERVO_NAME` in script matches printer.cfg
- Check camera position (`CAMERA_X`, `CAMERA_Y`) is correct
- Verify bed dimensions (`BED_WIDTH`, `BED_DEPTH`)
- Ensure `SERVO_RANGE` matches servo type (90 or 180)

### Servo moves but camera doesn't point at objects
- Camera not physically aligned at midpoint
- Re-align: Set servo to midpoint, adjust camera to point at bed center
- Check that initial_angle in printer.cfg matches servo midpoint

## Example Complete Configuration

### printer.cfg
```ini
[servo camera_servo]
pin: gpio17  # Raspberry Pi GPIO17
maximum_servo_angle: 180
minimum_pulse_width: 0.0005
maximum_pulse_width: 0.0025
initial_angle: 90
```

### gcode_camera_inserter.py
```python
CAMERA_X = -40.0
CAMERA_Y = 350.0
BED_WIDTH = 350.0
BED_DEPTH = 350.0
SERVO_RANGE = 180
SERVO_NAME = "camera_servo"
INVERT_SERVO = False  # Set to True if mounted upside down
```

### Test Commands
```gcode
# Center
SET_SERVO SERVO=camera_servo ANGLE=90

# Pan left
SET_SERVO SERVO=camera_servo ANGLE=60

# Pan right  
SET_SERVO SERVO=camera_servo ANGLE=120

# Full left
SET_SERVO SERVO=camera_servo ANGLE=0

# Full right
SET_SERVO SERVO=camera_servo ANGLE=180
```

## Advanced: Macros

You can create Klipper macros for common camera positions:

```ini
[gcode_macro CAMERA_CENTER]
gcode:
    SET_SERVO SERVO=camera_servo ANGLE=90

[gcode_macro CAMERA_LEFT]
gcode:
    SET_SERVO SERVO=camera_servo ANGLE=45

[gcode_macro CAMERA_RIGHT]
gcode:
    SET_SERVO SERVO=camera_servo ANGLE=135

[gcode_macro CAMERA_HOME]
gcode:
    SET_SERVO SERVO=camera_servo ANGLE=90
    G4 P500  # Wait 500ms for servo to move
```

Then use in gcode:
```gcode
CAMERA_CENTER
CAMERA_LEFT
CAMERA_RIGHT
```

## Power Consumption Notes

- Small servos (SG90): ~100-200mA when moving, ~10-20mA holding
- Medium servos (MG90S): ~200-400mA when moving, ~20-40mA holding
- Most printer boards can supply this current
- For multiple servos or larger ones, use external 5V supply

## Safety Considerations

- **Don't block the servo**: Ensure camera mount can rotate freely
- **Cable management**: Secure wires so they don't interfere with print
- **Mounting**: Servo should be firmly attached to printer frame
- **Testing**: Always test servo range before starting a print
