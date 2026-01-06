# Point and Print - Camera Position Script for Klipper

## Overview
This Python script (`point_and_print.py`) automatically inserts Klipper `SET_SERVO` commands into your 3D printer gcode files. It reads object definitions from the `EXECUTABLE_BLOCK_START` section, calculates the angle between your camera position and each object's center point, and inserts servo positioning commands before each `EXCLUDE_OBJECT_START` line.

The script is designed to be used as a post-processing script in your slicer software, where it will automatically process each gcode file after slicing.

## Camera Configuration

**IMPORTANT:** Before using this script, you must configure your camera's position and servo!

At the top of the script, you'll find the camera configuration section:

```python
# ============================================================================
# CAMERA CONFIGURATION
# ============================================================================
# Define the camera location relative to the bed's 0,0 coordinate
CAMERA_X = 0.0  # X coordinate of camera mount (in mm)
CAMERA_Y = 0.0  # Y coordinate of camera mount (in mm)

# Define your print bed dimensions (in mm)
BED_WIDTH = 350.0   # X dimension of your print bed
BED_DEPTH = 350.0   # Y dimension of your print bed

# Servo configuration
# Set to either 90 or 180 depending on your servo's movement capability
SERVO_RANGE = 180  # Options: 90 or 180 degrees

# Klipper servo name (must match the name in your printer.cfg)
SERVO_NAME = "camera_servo"

# Servo angle that points camera at bed center
SERVO_CENTER_ANGLE = 90.0  # Manually calibrated center angle

# Invert servo angles (for upside-down mounted servos)
INVERT_SERVO = False  # Set to True if servo is mounted upside down
# ============================================================================
```

### Configuration Steps:

1. **Set Camera Position** (`CAMERA_X`, `CAMERA_Y`)
   - Measure your camera's position relative to your print bed's origin (0,0)
   - Can be negative if camera is mounted off the bed

2. **Set Bed Dimensions** (`BED_WIDTH`, `BED_DEPTH`)
   - Enter your print bed's X and Y dimensions in millimeters
   - This is used to calculate the bed center point

3. **Set Servo Range** (`SERVO_RANGE`)
   - Set to `90` for a 90° servo (0-90° range)
   - Set to `180` for a 180° servo (0-180° range)

4. **Set Servo Name** (`SERVO_NAME`)
   - Must match the servo name defined in your Klipper `printer.cfg`
   - Example: If your config has `[servo camera_servo]`, use `"camera_servo"`

5. **Calibrate Servo Center Angle** (`SERVO_CENTER_ANGLE`)
   - This is the servo angle where the camera points at bed center
   - **How to calibrate:**
     1. Use Klipper console: `SET_SERVO SERVO=camera_servo ANGLE=X`
     2. Try different angles (start with 90° or 45°)
     3. Find the angle where camera points directly at bed center
     4. Set `SERVO_CENTER_ANGLE` to this value
   - Common values: 90 for 180° servo, 45 for 90° servo
   - Can be any value if servo is mounted off-center

6. **Set Servo Inversion** (`INVERT_SERVO`)
   - Set to `False` for normal servo mounting (default)
   - Set to `True` if servo is mounted upside down
   - When inverted, angles are mirrored over the centerline
   - Example: 60° becomes 120°, 90° stays 90°, 120° becomes 60°

## Usage

### Running from Slicer (Recommended)
The script is configured to run automatically as a post-processing script in your slicer:

1. In your slicer, go to the post-processing scripts settings
2. Add this script as a post-processing script
3. The slicer will pass the gcode file path automatically
4. The script will modify the file in place

**Example slicer configuration:**
```
python /path/to/point_and_print.py
```

The slicer will automatically append the gcode file path as an argument.

### Running Manually (For Testing)
```bash
python point_and_print.py <path_to_gcode_file>
```

**Example:**
```bash
python point_and_print.py /path/to/your/print.gcode
```

### Running in Development Mode
If you want to test the script without command-line arguments, modify the script:
1. Open `point_and_print.py`
2. Change `run_in_slicer = True` to `run_in_slicer = False`
3. Set `path_input` to your test file path
4. Run the script without arguments: `python point_and_print.py`

## What the Script Does

1. **Parses the EXECUTABLE_BLOCK_START section** (around line 190)
   - Extracts object names and their center coordinates
   - Example: `NAME=object1 CENTER=150.5,200.3`

2. **Calculates bed center** from configured bed dimensions

3. **Calculates servo angles for each object**
   - Determines the angle from camera to bed center (reference position)
   - Calculates angle from camera to each object
   - Computes the angular difference
   - Converts to servo position (0-90° or 0-180° depending on servo range)
   - Assumes servo midpoint points camera at bed center

4. **Finds all EXCLUDE_OBJECT_START lines**
   - Identifies which object is being started
   - Example: `EXCLUDE_OBJECT_START NAME=object1`

5. **Inserts Klipper SET_SERVO commands with calculated servo angles**
   - Adds a servo positioning command before each object start
   - Uses the configured servo name from `SERVO_NAME`
   - Example: `SET_SERVO SERVO=camera_servo ANGLE=74.50`

6. **Saves the modified file**
   - Overwrites the original gcode file with the modified version
   - Creates a backup is recommended before running

## Expected GCode Format

The script expects your gcode to have:

### EXECUTABLE_BLOCK_START Section
```gcode
; EXECUTABLE_BLOCK_START
EXCLUDE_OBJECT_DEFINE NAME=part1 CENTER=100.5,150.2 POLYGON=...
EXCLUDE_OBJECT_DEFINE NAME=part2 CENTER=200.3,180.7 POLYGON=...
```

### EXCLUDE_OBJECT_START Lines
```gcode
EXCLUDE_OBJECT_START NAME=part1
; ... printing commands for part1 ...
EXCLUDE_OBJECT_END NAME=part1
```

### After Processing
```gcode
SET_SERVO SERVO=camera_servo ANGLE=90.00
EXCLUDE_OBJECT_START NAME=part1
; ... printing commands for part1 ...
EXCLUDE_OBJECT_END NAME=part1

SET_SERVO SERVO=camera_servo ANGLE=74.54
EXCLUDE_OBJECT_START NAME=part2
; ... printing commands for part2 ...
EXCLUDE_OBJECT_END NAME=part2
```

## Klipper Printer Configuration

Before using this script, you must configure the servo in your Klipper `printer.cfg` file.

### Add Servo Configuration to printer.cfg

Add this section to your `printer.cfg`:

```ini
[servo camera_servo]
pin: PB6  # Change to your actual servo control pin
maximum_servo_angle: 180  # Or 90 if using a 90° servo
minimum_pulse_width: 0.0005
maximum_pulse_width: 0.0025
initial_angle: 90  # Start at midpoint (45 for 90° servo)
```

**Configuration notes:**
- **pin**: Set to the GPIO pin connected to your servo signal wire
- **maximum_servo_angle**: Must match your `SERVO_RANGE` setting in the script (90 or 180)
- **initial_angle**: Set to servo midpoint (90° for 180° servo, 45° for 90° servo)
- **name**: The `[servo camera_servo]` name must match `SERVO_NAME` in the script

### Common Pin Assignments

Check your printer's documentation for available GPIO pins:
- **Raspberry Pi**: `gpio17`, `gpio27`, etc.
- **SKR boards**: `PB6`, `PE5`, etc.
- **Octopus boards**: `PB6`, `PB7`, etc.

### Testing Your Servo

After adding the configuration, restart Klipper and test the servo manually:

```gcode
SET_SERVO SERVO=camera_servo ANGLE=90
SET_SERVO SERVO=camera_servo ANGLE=45
SET_SERVO SERVO=camera_servo ANGLE=135
```

The camera should rotate to point at different parts of the bed.

## Servo Angle Calculation

The script calculates servo positions using `SERVO_CENTER_ANGLE` as the reference point where the camera points at bed center.

### How It Works:
1. Calculate angle from camera to bed center (reference)
2. Calculate angle from camera to object (target)
3. Find angular difference: `target - reference`
4. Add to servo center angle: `servo_angle = SERVO_CENTER_ANGLE + difference`
5. Clamp to valid servo range (0-90 or 0-180)

### Why Manual Calibration?

Different servo mounting positions may result in different center angles:
- **Centered mount at 90°**: `SERVO_CENTER_ANGLE = 90`
- **Off-center mount**: `SERVO_CENTER_ANGLE = 75` or any other value
- **90° servo centered**: `SERVO_CENTER_ANGLE = 45`
- **90° servo off-center**: `SERVO_CENTER_ANGLE = 50` or any other value

By manually calibrating, you get precise control regardless of how your servo is physically mounted.

### Example Calculation:

**Configuration:**
- Camera at (0, 0)
- Bed center at (175, 175)
- `SERVO_CENTER_ANGLE = 90`

**Results:**
- Object at (175, 175) [bed center] → servo angle = 90° (no offset from center)
- Object at (85, 85) [lower-left] → servo angle = 90° (nearly at center in this example)
- Object at (250, 85) [right side] → servo angle = 74.54° (15.46° right of center)
- Object at (85, 250) [top side] → servo angle = 108.69° (18.69° left of center)

## Requirements
- Python 3.6 or higher
- No external dependencies required (uses only standard library)

## Configuration

Inside the script, you can modify the `run_in_slicer` flag:

- **`run_in_slicer = True`** (Default): Script expects a file path as a command-line argument (for use in slicer post-processing)
- **`run_in_slicer = False`**: Script uses the hardcoded `path_input` variable (for manual testing/development)

This mirrors the behavior of other popular gcode post-processing scripts.

## Notes

- **Always backup your gcode files before processing**
- **Configure the camera position** (CAMERA_X, CAMERA_Y) at the top of the script before first use
- The script will overwrite the original file
- If object names in EXECUTABLE_BLOCK_START don't match those in EXCLUDE_OBJECT_START, a warning will be displayed
- The script preserves all original gcode content, only adding camera commands

## Verification

After slicing a file, check that the script ran successfully:

1. Open the generated gcode file in a text editor
2. Search for `SET_SERVO`
3. You should see lines like:
   ```gcode
   SET_SERVO SERVO=camera_servo ANGLE=90.00
   EXCLUDE_OBJECT_START NAME=object_name
   ```

**Console Output Example:**
```
Program point_and_print.py initiated
Processing file: print.gcode
Read 9316 lines
Camera position: (0.0, 0.0)
Bed size: 350.0x350.0 mm, center: (175.0, 175.0)
Servo range: 180° (center angle 90.0° points to bed center)
Found 3 objects:
  GoPro_Shaft.stl_id_0_copy_0: center=(84.9995, 84.9989), servo angle=90.00°
  GoPro_Shaft.stl_id_1_copy_0: center=(150.001, 84.9989), servo angle=74.54°
  Threaded_Ball.stl_id_2_copy_0: center=(84.9987, 171.874), servo angle=108.69°
Inserted 19 SET_SERVO commands
Successfully saved modified gcode to: print.gcode
```

## Customization

If your gcode format differs from the expected format, you may need to adjust the regular expressions in the `parse_executable_block()` function to match your specific format.

## Troubleshooting

**"No objects found in EXECUTABLE_BLOCK_START section"**
- Check that your gcode file has an EXECUTABLE_BLOCK_START section
- Verify the format of object definitions matches the expected pattern
- The script may need adjustment for your specific slicer's output format

**"Object 'xyz' not found in EXECUTABLE_BLOCK_START section"**
- Object names in EXECUTABLE_BLOCK_START and EXCLUDE_OBJECT_START don't match
- Check for typos or formatting differences in object names

**Servo moves opposite direction from expected**
- Your servo may be mounted upside down
- Set `INVERT_SERVO = True` in the script configuration
- This will mirror all angles over the centerline (60° ↔ 120°, 90° stays 90°)

**Servo doesn't point at objects correctly**
- Verify physical alignment: calibrate `SERVO_CENTER_ANGLE` properly
- Use `SET_SERVO` commands to find angle where camera points at bed center
- Check `CAMERA_X`, `CAMERA_Y`, `BED_WIDTH`, `BED_DEPTH` settings
- Ensure `SERVO_RANGE` matches your servo (90 or 180)
- See SERVO_CALIBRATION_GUIDE.md for detailed calibration steps

**Servo name error in Klipper**
- `SERVO_NAME` in script must exactly match servo name in `printer.cfg`
- Example: `[servo my_cam]` requires `SERVO_NAME = "my_cam"`
