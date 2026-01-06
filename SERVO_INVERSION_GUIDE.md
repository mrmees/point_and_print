# Servo Inversion Guide

## Understanding INVERT_SERVO

The `INVERT_SERVO` setting mirrors all servo angles over the centerline. This is useful when your servo is physically mounted upside down.

## Visual Representation

### 180° Servo - Normal Orientation (INVERT_SERVO = False)

```
        Camera View Direction
              ↓
    0° ←------|------→ 180°
         90° (center)

Servo Range:
├────────┼────────┤
0°      90°     180°

Example angles:
- Object left of center  : 60°
- Object at bed center   : 90°
- Object right of center : 120°
```

### 180° Servo - Inverted Orientation (INVERT_SERVO = True)

```
        Camera View Direction
              ↓
  180° ←------|------→ 0°
         90° (center)

Servo Range (mirrored):
├────────┼────────┤
180°    90°      0°

Example angles (mirrored):
- Object left of center  : 120° (was 60°)
- Object at bed center   : 90°  (unchanged)
- Object right of center : 60°  (was 120°)
```

## How Angles Are Mirrored

### Formula
```
inverted_angle = SERVO_RANGE - normal_angle
```

### 180° Servo Examples

| Normal Angle | Inverted Angle | Calculation |
|--------------|----------------|-------------|
| 0°           | 180°           | 180 - 0     |
| 30°          | 150°           | 180 - 30    |
| 45°          | 135°           | 180 - 45    |
| 60°          | 120°           | 180 - 60    |
| 90°          | 90°            | 180 - 90    |
| 120°         | 60°            | 180 - 120   |
| 135°         | 45°            | 180 - 135   |
| 150°         | 30°            | 180 - 150   |
| 180°         | 0°             | 180 - 180   |

**Notice**: The centerline (90°) stays at 90° - it's the mirror point.

### 90° Servo Examples

| Normal Angle | Inverted Angle | Calculation |
|--------------|----------------|-------------|
| 0°           | 90°            | 90 - 0      |
| 15°          | 75°            | 90 - 15     |
| 30°          | 60°            | 90 - 30     |
| 45°          | 45°            | 90 - 45     |
| 60°          | 30°            | 90 - 60     |
| 75°          | 15°            | 90 - 75     |
| 90°          | 0°             | 90 - 90     |

**Notice**: The centerline (45°) stays at 45° - it's the mirror point.

## Real-World Scenario

### Problem: Upside-Down Servo

You mount your servo upside down like this:

```
Normal Mount:          Upside-Down Mount:
   ┌─────┐                ┌─────┐
   │ ▓▓▓ │ Servo          │     │
   └─────┘                └─────┘
      │                      │
    ┌───┐ Camera          ┌───┐
    │ o │                 │ o │
    └───┘                 └───┘
      │                      │
   ┌─────┐                └─────┘
   │ ▓▓▓ │                │ ▓▓▓ │ Servo
   └─────┘                └─────┘
```

### What Happens:

**Without INVERT_SERVO (False):**
- Script calculates: "rotate 60° to point at object"
- Servo rotates 60° in the WRONG direction (upside down)
- Camera points away from the object ❌

**With INVERT_SERVO (True):**
- Script calculates: "rotate 60° to point at object"
- Script inverts: 180° - 60° = 120°
- Servo receives 120° command
- Due to upside-down mounting, this results in correct 60° rotation ✓
- Camera points at the object correctly ✓

## When to Use INVERT_SERVO

### Use INVERT_SERVO = True when:
- ✓ Servo is physically mounted upside down
- ✓ Cannot or don't want to remount the servo
- ✓ Camera pans opposite direction from expected
- ✓ Angles are numerically correct but pointing is backwards

### Don't use INVERT_SERVO when:
- ✗ Servo horn is just rotated (remove and reattach horn instead)
- ✗ Camera position is wrong (fix CAMERA_X, CAMERA_Y instead)
- ✗ Bed dimensions are wrong (fix BED_WIDTH, BED_DEPTH instead)
- ✗ Servo is mounted normally but movements seem random (check physical alignment)

## Testing the Inversion

### Step 1: Test Normal Configuration
```python
INVERT_SERVO = False
```

Run the script and test:
```gcode
SET_SERVO SERVO=camera_servo ANGLE=60
```

Does the camera rotate left or right?

### Step 2: If Wrong Direction, Enable Inversion
```python
INVERT_SERVO = True
```

Run the script again and test:
```gcode
SET_SERVO SERVO=camera_servo ANGLE=60
```

Now the camera should rotate in the correct direction.

### Step 3: Verify Center Position
```gcode
SET_SERVO SERVO=camera_servo ANGLE=90
```

Regardless of INVERT_SERVO setting, 90° should always point at bed center (or 45° for 90° servo).

## Debugging

### Camera points completely wrong
- INVERT_SERVO is probably not the issue
- Check physical alignment first
- Verify CAMERA_X, CAMERA_Y, BED_WIDTH, BED_DEPTH

### Camera pans but in opposite direction
- This is exactly what INVERT_SERVO fixes
- Set INVERT_SERVO = True

### Camera pans correctly sometimes, wrong other times
- Physical alignment issue (servo midpoint not aimed at bed center)
- Re-align servo at midpoint position

### Center position (90°) doesn't point at bed center
- Physical alignment issue
- INVERT_SERVO won't fix this
- Manually adjust servo so 90° points at bed center

## Mathematical Proof

The inversion maintains the relationship between angles and objects, just flipped:

```
Normal servo:
- Object at (85, 85)   → 60° (left of center)
- Object at (175, 175) → 90° (center)
- Object at (265, 265) → 120° (right of center)

Inverted servo (same objects):
- Object at (85, 85)   → 120° (still left of center, but servo is upside down)
- Object at (175, 175) → 90° (still center)
- Object at (265, 265) → 60° (still right of center, but servo is upside down)
```

The angles flip, but the physical pointing direction stays correct because the servo itself is flipped!

## Summary

| Setting | When to Use | Effect |
|---------|-------------|--------|
| `INVERT_SERVO = False` | Normal servo mounting | No angle modification |
| `INVERT_SERVO = True` | Upside-down servo mounting | All angles mirrored: `angle = SERVO_RANGE - angle` |

The center angle (90° or 45°) always stays the same because it's the mirror point.
