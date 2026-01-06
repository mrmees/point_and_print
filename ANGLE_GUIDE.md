# Camera Servo Configuration Guide

## Understanding the Servo-Based Angle System

The script calculates servo angles needed to point your camera at different objects on the print bed. This guide explains how the servo positioning works and how to configure your setup.

## Key Concepts

### 1. Manual Center Calibration
Instead of assuming your servo is centered at a specific angle (like 90° or 45°), you manually calibrate and tell the script which angle points at bed center. This provides:
- ✓ Flexibility for any mounting position
- ✓ Compensation for mechanical play
- ✓ Works with off-center servo mounts
- ✓ No assumptions about "standard" configurations

### 2. Configurable Center Angle
The `SERVO_CENTER_ANGLE` is your reference point. All object angles are calculated relative to this angle:
- Object at bed center → servo angle = `SERVO_CENTER_ANGLE`
- Objects elsewhere → calculated offset from center angle

### 3. Servo Inversion for Upside-Down Mounting
If your servo is mounted upside down, set `INVERT_SERVO = True` to mirror all angles over the centerline without remounting hardware.

## Example Scenarios

### Scenario 1: Standard 180° Servo, Camera at Front-Left (0, 0)

```
Configuration:
- Camera: (0, 0)
- Bed: 350x350mm, center at (175, 175)
- Servo Range: 180°
- Calibrated Center Angle: 90° (camera points at bed center when servo is at 90°)

           Y
           ↑
           |  Bed Center (175, 175)
       175 +     ● [servo at 90°]
           |    /
           |   /
           |  /
           | /
Camera ●---+--------→ X
  (0,0)    0   175

Results:
- Object at (175, 175) [bed center] → servo angle = 90.00°
- Object at (85, 85) [closer to camera] → servo angle = 90.00° (nearly center)
- Object at (250, 85) [right side] → servo angle = 74.54°
- Object at (85, 250) [top side] → servo angle = 108.69°
```

### Scenario 2: Off-Center Mounted Servo

```
Configuration:
- Camera: (0, 0)
- Bed: 350x350mm, center at (175, 175)
- Servo Range: 180°
- Calibrated Center Angle: 75° (off-center mount or mechanical offset)

Results (same objects as above):
- Object at (175, 175) [bed center] → servo angle = 75.00°
- Object at (85, 85) [closer to camera] → servo angle = 75.00°
- Object at (250, 85) [right side] → servo angle = 59.54°
- Object at (85, 250) [top side] → servo angle = 93.69°

Note: All angles shift by 15° (90-75=15) but relative relationships stay the same.
This is why manual calibration is important - the script adapts to YOUR mount!
```

### Scenario 3: 90° Servo, Centered

```
Configuration:
- Camera: (0, 0)
- Bed: 350x350mm, center at (175, 175)
- Servo Range: 90°
- Calibrated Center Angle: 45°

Results:
- Object at (175, 175) [bed center] → servo angle = 45.00°
- Object at (85, 85) [closer to camera] → servo angle = 45.00°
- Object at (250, 85) [right side] → servo angle = 29.54°
- Object at (85, 250) [top side] → servo angle = 63.69°

Note: Angles are exactly half of the 180° servo values because the servo range is half.
```

### Scenario 4: Camera Off-Bed, Inverted Servo

```
Configuration:
- Camera: (-40, 350) [off bed, top-left]
- Bed: 350x350mm, center at (175, 175)
- Servo Range: 180°
- Calibrated Center Angle: 87° (slightly off due to mounting)
- INVERT_SERVO: True (mounted upside down)

           Y
       350 +  Camera ●
           |       \
           |        \
       175 +         ● Bed Center
           |        /
           |       / Objects
           |      ● ● ●
         0 +----------→ X
         -40   0  175

Results (with inversion):
- Objects below and to the right of camera
- Angles automatically inverted to compensate for upside-down mounting
- Camera correctly points at each object despite unusual mounting
```

## Configuring Your Setup

### Step 1: Measure Your Setup

You need to know:
1. **Camera position** (X, Y) relative to bed origin (0, 0)
2. **Bed dimensions** (width × depth in mm)
3. **Servo range** (90° or 180°)
4. **Servo orientation** (normal or upside down)

### Step 2: Physical Servo Installation

Mount your servo securely to the printer frame with the camera attached. The servo doesn't need to be "centered" at any particular angle - you'll calibrate this in the next step.

### Step 3: Calibrate Center Angle

**This is the most important step!**

1. Use Klipper console to test angles:
   ```gcode
   SET_SERVO SERVO=camera_servo ANGLE=90  # For 180° servo
   SET_SERVO SERVO=camera_servo ANGLE=45  # For 90° servo
   ```

2. Observe where the camera points

3. Adjust angle up or down until camera points exactly at bed center:
   ```gcode
   SET_SERVO SERVO=camera_servo ANGLE=85
   SET_SERVO SERVO=camera_servo ANGLE=87
   SET_SERVO SERVO=camera_servo ANGLE=88  # Perfect!
   ```

4. Record this angle - this is your `SERVO_CENTER_ANGLE`

**Tip:** Place a marker at bed center (175, 175 for a 350mm bed) as a visual target.

### Step 4: Update the Script

Edit `point_and_print.py` and configure these values:

```python
# Camera Configuration
CAMERA_X = 0.0      # Your camera's X position (can be negative)
CAMERA_Y = 0.0      # Your camera's Y position (can be negative)

# Bed Dimensions
BED_WIDTH = 350.0   # Your bed's X dimension
BED_DEPTH = 350.0   # Your bed's Y dimension

# Servo Configuration
SERVO_RANGE = 180           # 90 or 180
SERVO_NAME = "camera_servo" # Must match printer.cfg
SERVO_CENTER_ANGLE = 88.0   # From calibration step!
INVERT_SERVO = False        # True if upside down
```

**Example configurations:**

**Standard centered 180° servo:**
```python
SERVO_CENTER_ANGLE = 90.0
```

**Off-center mount:**
```python
SERVO_CENTER_ANGLE = 75.0  # Whatever angle points at center
```

**90° servo:**
```python
SERVO_RANGE = 90
SERVO_CENTER_ANGLE = 45.0  # Or whatever you calibrated
```

**Upside-down mount:**
```python
SERVO_CENTER_ANGLE = 90.0  # Center angle stays the same
INVERT_SERVO = True         # This handles the inversion
```

### Step 5: Test

Run the script on a test gcode file and verify:
1. Console shows your calibrated center angle
2. All angles are within your servo's range (0-90 or 0-180)
3. Bed center object angle equals your `SERVO_CENTER_ANGLE`

## Understanding Your Results

When the script runs, it displays calculated servo angles:
```
Bed size: 350.0x350.0 mm, center: (175.0, 175.0)
Servo range: 180° (center angle 90.0° points to bed center)
Found 3 objects:
  Object1: center=(84.9995, 84.9989), servo angle=90.00°
  Object2: center=(150.001, 84.9989), servo angle=74.54°
  Object3: center=(84.9987, 171.874), servo angle=108.69°
```

### Interpreting the Results

**The center angle is your reference:**
- Object at bed center = `SERVO_CENTER_ANGLE`
- Objects to the right < `SERVO_CENTER_ANGLE`
- Objects to the left > `SERVO_CENTER_ANGLE`

**Example with SERVO_CENTER_ANGLE = 90:**
- **90.00°**: Object at (or very near) bed center
- **74.54°**: Object to the right (90 - 15.46 = 74.54)
- **108.69°**: Object to the left (90 + 18.69 = 108.69)

**Example with SERVO_CENTER_ANGLE = 75:** (off-center mount)
- **75.00°**: Object at bed center
- **59.54°**: Object to the right (75 - 15.46 = 59.54)
- **93.69°**: Object to the left (75 + 18.69 = 93.69)

Notice the relative differences stay the same (15.46° right, 18.69° left), but all angles shift by the center angle offset!

### Understanding Angle Ranges

**For 180° servo:**
- Valid range: 0° to 180°
- Typical center angles: 70° to 110° (depending on mount)
- Objects can be ±90° from center (theoretically)

**For 90° servo:**
- Valid range: 0° to 90°
- Typical center angles: 35° to 55° (depending on mount)
- Objects can be ±45° from center (theoretically)

**Warning signs:**
- Angles hitting 0° or max (90°/180°): Object may be at edge of servo's viewing range
- All angles very similar: Objects clustered together (normal for multi-part prints)
- Center angle seems way off: That's OK! Use whatever works for your mount

### How SERVO_CENTER_ANGLE Works

Think of `SERVO_CENTER_ANGLE` as shifting the entire angle range:

```
Standard (SERVO_CENTER_ANGLE = 90):
├─────────┼─────────┤
0°       90°      180°

Off-center (SERVO_CENTER_ANGLE = 75):
├──────┼──────────────┤
0°    75°           180°
      ↑ bed center

Off-center (SERVO_CENTER_ANGLE = 110):
├──────────────┼──────┤
0°           110°   180°
              ↑ bed center
```

The math automatically compensates so objects are tracked correctly regardless of your center angle!

## Troubleshooting

**Servo hitting limits (0° or 90°/180°):**
- Some objects may be outside the servo's viewing range
- Consider relocating camera mount for better coverage
- Or adjust `SERVO_CENTER_ANGLE` if you have room to shift the range
- Check bed dimensions are correct

**Camera doesn't point at bed center when expected:**
- Re-calibrate `SERVO_CENTER_ANGLE`
- Use `SET_SERVO` commands to find the exact angle
- Update the script with the correct value
- See SERVO_CALIBRATION_GUIDE.md for detailed steps

**Angles seem backwards (camera points opposite direction):**
- Check if servo is mounted upside down
- Set `INVERT_SERVO = True` in script
- This mirrors all angles over the centerline
- See SERVO_INVERSION_GUIDE.md for details

**All angles close to center angle:**
- Objects are clustered near bed center (might be expected)
- Verify objects are actually spread out on the bed in your slicer
- This is normal for prints with multiple small parts near center

**Angles don't match physical setup:**
- Double-check `CAMERA_X` and `CAMERA_Y` values
- Verify `BED_WIDTH` and `BED_DEPTH` match your printer
- Re-calibrate `SERVO_CENTER_ANGLE` using `SET_SERVO` commands
- Ensure `SERVO_RANGE` is correct (90 or 180)

**Center angle seems unusual (like 73° or 112°):**
- **This is perfectly fine!** Use whatever angle works
- Manual calibration means any value is valid
- The script adapts to YOUR specific mount
- Don't try to force it to 90° or 45° if that's not where your camera centers

**Servo jittering or oscillating:**
- May need to tune servo update rate in printer firmware
- Some servos need deadband/threshold settings
- Consider adding small delays between movements
- Check power supply is adequate (servos draw current when moving)

**Script shows wrong center angle in output:**
- Check that you saved the script after editing `SERVO_CENTER_ANGLE`
- Verify you're running the correct version of the script
- Console should show: "center angle XX.X° points to bed center"

## How It Works Mathematically

The script uses the following process:

1. **Calculate reference angle** (camera → bed center):
   ```
   angle_ref = atan2(center_y - camera_y, center_x - camera_x)
   ```

2. **Calculate target angle** (camera → object):
   ```
   angle_obj = atan2(object_y - camera_y, object_x - camera_x)
   ```

3. **Find angular difference**:
   ```
   difference = angle_obj - angle_ref
   ```
   (normalized to -180° to +180°)

4. **Convert to servo position using calibrated center**:
   ```
   servo_angle = SERVO_CENTER_ANGLE + difference
   ```
   (clamped to 0 to SERVO_RANGE)

5. **Apply inversion if needed**:
   ```
   if INVERT_SERVO:
       servo_angle = SERVO_RANGE - servo_angle
   ```

This approach ensures that:
- User's calibrated center angle is the reference point
- Angular differences are correctly calculated
- Servo stays within its physical range
- Works with any servo mounting configuration
- Handles upside-down servos automatically

## Configuration Summary

| Setting | What It Is | How to Set | Example Values |
|---------|------------|------------|----------------|
| `CAMERA_X` | Camera X position | Measure from bed origin | 0, -40, 350 |
| `CAMERA_Y` | Camera Y position | Measure from bed origin | 0, 350, -40 |
| `BED_WIDTH` | Bed X dimension | Read from specs | 220, 300, 350 |
| `BED_DEPTH` | Bed Y dimension | Read from specs | 220, 300, 350 |
| `SERVO_RANGE` | Servo movement range | Check servo specs | 90, 180 |
| `SERVO_NAME` | Klipper servo name | Match printer.cfg | "camera_servo" |
| `SERVO_CENTER_ANGLE` | **Angle pointing at bed center** | **Calibrate with SET_SERVO** | **45, 73, 90, 110, etc.** |
| `INVERT_SERVO` | Upside-down mounting | Set True if inverted | False, True |

**Key Point**: `SERVO_CENTER_ANGLE` is the only value that requires calibration. All other values are either measurements or specifications. This one setting makes the entire system work with any servo mounting configuration!
