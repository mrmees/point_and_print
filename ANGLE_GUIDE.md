# Camera Servo Configuration Guide

## Understanding the Servo-Based Angle System

The script calculates servo angles needed to point your camera at different objects on the print bed. This guide explains how the servo positioning works and how to configure your setup.

## Key Concept: Center-Aligned Servo

The script assumes your servo is positioned so that **at its midpoint, the camera points at the center of your print bed**:

- **90° servo**: When at 45° (midpoint), camera points at bed center
- **180° servo**: When at 90° (midpoint), camera points at bed center

From this reference position, the script calculates how much to rotate the servo to point at each object.

## Example Scenarios

### Scenario 1: 180° Servo, Camera at Front-Left (0, 0), 350x350mm Bed

```
Configuration:
- Camera: (0, 0)
- Bed Center: (175, 175)
- Servo Range: 180°
- Servo Midpoint: 90° (points at bed center)

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

### Scenario 2: 90° Servo, Same Setup

```
Configuration:
- Camera: (0, 0)
- Bed Center: (175, 175)
- Servo Range: 90°
- Servo Midpoint: 45° (points at bed center)

Results (same objects as above):
- Object at (175, 175) [bed center] → servo angle = 45.00°
- Object at (85, 85) [closer to camera] → servo angle = 45.00°
- Object at (250, 85) [right side] → servo angle = 29.54°
- Object at (85, 250) [top side] → servo angle = 63.69°

Note: Angles are exactly half of the 180° servo values
```

### Scenario 3: Camera Off-Bed at (-40, 350)

```
Configuration:
- Camera: (-40, 350)
- Bed Center: (175, 175)
- Servo Range: 180°
- Servo Midpoint: 90° (points at bed center)

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

Results:
- Objects below and to the right of camera
- All servo angles between 64-75° (all to the right of center)
- Camera needs to rotate right (angles < 90°) to see objects
```

## Configuring Your Setup

### Step 1: Measure Your Setup

You need to know:
1. **Camera position** (X, Y) relative to bed origin (0, 0)
2. **Bed dimensions** (width × depth in mm)
3. **Servo range** (90° or 180°)

### Step 2: Physical Servo Alignment

**IMPORTANT**: Physically position your servo so that at its midpoint, the camera points at the bed center.

For a **180° servo**:
1. Set servo to 90° using a servo tester or your printer
2. Manually aim the camera at the bed center (bed_width/2, bed_depth/2)
3. Secure the servo in this position

For a **90° servo**:
1. Set servo to 45° using a servo tester or your printer
2. Manually aim the camera at the bed center
3. Secure the servo in this position

### Step 3: Update the Script

Edit `gcode_camera_inserter.py` and find the configuration section:

```python
# ============================================================================
# CAMERA CONFIGURATION
# ============================================================================
CAMERA_X = 0.0      # Your camera's X coordinate
CAMERA_Y = 0.0      # Your camera's Y coordinate

BED_WIDTH = 350.0   # Your bed's X dimension
BED_DEPTH = 350.0   # Your bed's Y dimension

SERVO_RANGE = 180   # Your servo's range (90 or 180)
# ============================================================================
```

**Example for camera at front-left of a 300×300mm bed with 180° servo:**
```python
CAMERA_X = 0.0
CAMERA_Y = 0.0
BED_WIDTH = 300.0
BED_DEPTH = 300.0
SERVO_RANGE = 180
```

**Example for camera mounted off-bed at back-right with 90° servo:**
```python
CAMERA_X = 310.0
CAMERA_Y = 310.0
BED_WIDTH = 300.0
BED_DEPTH = 300.0
SERVO_RANGE = 90
```

### Step 4: Test

Run the script on a test gcode file and verify:
1. Console shows reasonable servo angles
2. All angles are within your servo's range (0-90 or 0-180)
3. Bed center angle equals servo midpoint (45° or 90°)

## Understanding Your Results

When the script runs, it displays calculated servo angles:
```
Bed size: 350.0x350.0 mm, center: (175.0, 175.0)
Servo range: 180° (midpoint at 90.0° points to bed center)
Found 3 objects:
  Object1: center=(84.9995, 84.9989), servo angle=90.00°
  Object2: center=(150.001, 84.9989), servo angle=74.54°
  Object3: center=(84.9987, 171.874), servo angle=108.69°
```

**Interpreting the results:**

For **180° servo** (midpoint at 90°):
- **90°**: Camera points at bed center (or very close to it)
- **< 90°** (e.g., 74°): Camera rotates right/clockwise from center
- **> 90°** (e.g., 108°): Camera rotates left/counter-clockwise from center
- **Range check**: All angles should be 0-180°

For **90° servo** (midpoint at 45°):
- **45°**: Camera points at bed center
- **< 45°** (e.g., 29°): Camera rotates right from center
- **> 45°** (e.g., 64°): Camera rotates left from center
- **Range check**: All angles should be 0-90°

**Warning signs:**
- Angles hitting 0° or max (90°/180°): Object may be outside servo's viewing range
- All angles very similar: Objects clustered together (normal for multi-part prints)
- Unexpected angles: Check camera position and bed dimensions in config

## Troubleshooting

**Servo hitting limits (0° or 90°/180°):**
- Some objects may be outside the servo's viewing range
- Consider relocating camera mount for better coverage
- Or adjust bed dimensions if configured incorrectly

**Angles seem backwards:**
- Check that bed dimensions match your actual bed size
- Verify camera position coordinates are correct
- Test: Place a print at bed center - servo should be at midpoint (45° or 90°)

**All angles close to midpoint:**
- Objects are clustered near bed center (might be expected)
- Verify objects are actually spread out on the bed in your slicer

**Angles don't match physical setup:**
- Double-check CAMERA_X and CAMERA_Y values
- Verify BED_WIDTH and BED_DEPTH match your printer
- Ensure servo is physically aligned (midpoint → bed center)
- Test with a known object position

**Servo jittering or oscillating:**
- May need to tune servo update rate in your printer firmware
- Some servos need deadband/threshold settings
- Consider adding small delays between camera movements in firmware

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

4. **Convert to servo position**:
   ```
   servo_angle = (SERVO_RANGE / 2) + difference
   ```
   (clamped to 0 to SERVO_RANGE)

This approach ensures that:
- Servo midpoint always corresponds to bed center view
- Angular differences are correctly calculated
- Servo stays within its physical range
