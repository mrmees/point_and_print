# Servo Center Angle Calibration Guide

This guide walks you through calibrating the `SERVO_CENTER_ANGLE` setting, which tells the script what servo angle points your camera at the bed center.

## Why Calibration is Needed

Unlike the old assumption that servos are always centered at their midpoint (45° or 90°), this manual calibration approach gives you flexibility:

- ✓ Works with any servo mounting position
- ✓ Accounts for mechanical play or servo horn positioning
- ✓ Allows fine-tuning for perfect alignment
- ✓ No assumptions about "standard" mounting

## Quick Calibration (5 Minutes)

### Step 1: Access Klipper Console

Open your Klipper interface (Mainsail, Fluidd, or Octoprint).

### Step 2: Test Different Angles

Send these commands one at a time and observe where the camera points:

```gcode
# For 180° servo - try these angles:
SET_SERVO SERVO=camera_servo ANGLE=90
SET_SERVO SERVO=camera_servo ANGLE=80
SET_SERVO SERVO=camera_servo ANGLE=100
SET_SERVO SERVO=camera_servo ANGLE=85
SET_SERVO SERVO=camera_servo ANGLE=95

# For 90° servo - try these angles:
SET_SERVO SERVO=camera_servo ANGLE=45
SET_SERVO SERVO=camera_servo ANGLE=40
SET_SERVO SERVO=camera_servo ANGLE=50
SET_SERVO SERVO=camera_servo ANGLE=43
SET_SERVO SERVO=camera_servo ANGLE=47
```

### Step 3: Identify Center Angle

Watch where the camera points for each angle. Find the angle where the camera points **directly at the center of your print bed**.

**Tip**: Place a small piece of tape or a coin at the exact center of your bed as a visual target.

### Step 4: Update the Script

Edit `point_and_print.py` and set:

```python
SERVO_CENTER_ANGLE = X.X  # Replace X.X with your calibrated angle
```

**Examples:**
```python
SERVO_CENTER_ANGLE = 90.0  # Common for centered 180° servo
SERVO_CENTER_ANGLE = 45.0  # Common for centered 90° servo
SERVO_CENTER_ANGLE = 85.5  # Example of off-center mount
SERVO_CENTER_ANGLE = 73.0  # Another off-center example
```

### Step 5: Verify

Run the script on a test gcode file and check that the console shows your calibrated angle:
```
Servo range: 180° (center angle 85.5° points to bed center)
```

## Detailed Calibration Method

For more precise calibration:

### 1. Mark Your Bed Center

Calculate bed center coordinates:
```
center_x = BED_WIDTH / 2
center_y = BED_DEPTH / 2
```

For a 350x350mm bed: `center = (175, 175)`

Place a visible marker (tape, sticker, or use the crosshair in your slicer's preview).

### 2. Binary Search Method

This method quickly finds the exact angle:

**Start with rough estimate:**
```gcode
# For 180° servo
SET_SERVO SERVO=camera_servo ANGLE=90

# For 90° servo
SET_SERVO SERVO=camera_servo ANGLE=45
```

**Is camera left or right of center?**

If **LEFT** of center (pointing too far left):
- Try a **lower** angle
- Example: `SET_SERVO SERVO=camera_servo ANGLE=85`

If **RIGHT** of center (pointing too far right):
- Try a **higher** angle
- Example: `SET_SERVO SERVO=camera_servo ANGLE=95`

**Narrow down:**
Keep adjusting by smaller increments until camera points exactly at center:
```gcode
SET_SERVO SERVO=camera_servo ANGLE=87
SET_SERVO SERVO=camera_servo ANGLE=88
SET_SERVO SERVO=camera_servo ANGLE=87.5
```

### 3. Record Your Value

Once you find the perfect angle, write it down and update the script.

## Understanding the Center Angle

### What This Angle Represents

`SERVO_CENTER_ANGLE` is your **reference point**. All object angles are calculated relative to this angle:

- Object at bed center → servo angle = `SERVO_CENTER_ANGLE`
- Object right of center → servo angle = `SERVO_CENTER_ANGLE - X°`
- Object left of center → servo angle = `SERVO_CENTER_ANGLE + X°`

### Common Values

**180° Servo:**
| Mounting | Typical Center Angle |
|----------|---------------------|
| Perfectly centered | 90° |
| Slightly off-center | 85° - 95° |
| Significantly off | 70° - 110° |

**90° Servo:**
| Mounting | Typical Center Angle |
|----------|---------------------|
| Perfectly centered | 45° |
| Slightly off-center | 40° - 50° |
| Significantly off | 30° - 60° |

### Off-Center Mounting Example

Imagine your servo is mounted so that when at 75°, the camera points at bed center:

```python
SERVO_CENTER_ANGLE = 75.0
```

**Results:**
- Object at bed center → 75°
- Object 10° right of center → 65° (75 - 10)
- Object 10° left of center → 85° (75 + 10)

The physical mounting doesn't matter - the script adapts to whatever angle points at center.

## Verification Tests

After calibration, verify your setting works correctly:

### Test 1: Center Object
Print a small object placed exactly at bed center in your slicer. The generated gcode should have:
```gcode
SET_SERVO SERVO=camera_servo ANGLE=XX.XX  # Should equal SERVO_CENTER_ANGLE
```

### Test 2: Console Output
Run the script and check the console shows objects relative to your center angle:
```
Servo range: 180° (center angle 75.0° points to bed center)
Found 3 objects:
  Object1: center=(175.0, 175.0), servo angle=75.00°  ← Exactly center!
  Object2: center=(250.0, 175.0), servo angle=60.23°  ← Right of center
  Object3: center=(100.0, 175.0), servo angle=89.45°  ← Left of center
```

### Test 3: Physical Test Print
Start a test print and verify the camera actually points at each object when commanded.

## Troubleshooting Calibration

**Camera never points exactly at center**
- Servo may have mechanical play
- Try angles in 0.5° increments: 89.5, 90.0, 90.5
- Small offset (±2°) is usually acceptable

**Angles seem way off (like 130° for center)**
- This is fine! Use whatever angle works
- The script adapts to any center angle
- Verify servo range setting is correct (90 or 180)

**Camera points at center sometimes, not others**
- Servo may be loose or have inconsistent movement
- Check servo mounting screws
- Verify power supply is adequate
- Some cheap servos have poor repeatability

**Can't find any angle that points at center**
- Servo range may be too limited
- Camera may be mounted too far from bed
- Try repositioning camera mount
- Verify servo is actually moving (try extreme angles like 0° and 180°)

**Angle changes after restarting Klipper**
- Check `initial_angle` in printer.cfg
- Set to your `SERVO_CENTER_ANGLE` value
- Example: `initial_angle: 85.5`

## Advanced: Multiple Center Positions

Some users may want the camera to track objects in different ways:

### Typical Use Case (Recommended)
```python
SERVO_CENTER_ANGLE = 90.0  # Points at bed center
```
Camera pans to each object from the bed center reference point.

### Alternative: Off-Center Tracking
```python
SERVO_CENTER_ANGLE = 60.0  # Points at right side of bed
```
If your prints are usually on the right side, you can set center angle to favor that area, giving more servo range for right-side objects.

## Re-Calibration

You should re-calibrate if:
- You move or remount the servo
- You change camera mounts
- Servo behavior changes over time
- You want to fine-tune alignment

Re-calibration takes only 2-3 minutes using the Quick Method above.

## Summary

1. **Test angles** using `SET_SERVO` commands
2. **Find the angle** where camera points at bed center
3. **Set** `SERVO_CENTER_ANGLE` to that angle
4. **Verify** with test prints

That's it! The script handles all the math to calculate object angles relative to your calibrated center angle.
