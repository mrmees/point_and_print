#!/usr/bin/env python3
"""
Point and Print - Camera Position Script for Klipper

This script parses a gcode file to:
1. Extract object names and center coordinates from the EXECUTABLE_BLOCK_START section
2. Calculate the angle between the camera position and each object's center point
3. Convert the angle to servo position based on servo range and center alignment
4. Insert Klipper SET_SERVO commands before each EXCLUDE_OBJECT_START line
5. Save the modified gcode back to the original file
"""

import re
import sys
import math
from pathlib import Path


# ============================================================================
# CAMERA CONFIGURATION
# ============================================================================
# Define the camera location relative to the bed's 0,0 coordinate
# Adjust these values to match your printer's camera mount position
CAMERA_X = 0.0  # X coordinate of camera mount (in mm)
CAMERA_Y = 0.0  # Y coordinate of camera mount (in mm)

# Define your print bed dimensions (in mm)
BED_WIDTH = 350.0   # X dimension of your print bed
BED_DEPTH = 350.0   # Y dimension of your print bed

# Servo configuration
# Set to either 90 or 180 depending on your servo's movement capability
SERVO_RANGE = 180  # Options: 90 or 180 degrees

# Klipper servo name (must match the name in your printer.cfg)
# Example: If your printer.cfg has [servo camera_servo], set this to "camera_servo"
SERVO_NAME = "camera_servo"

# Servo angle that points camera at bed center
# This is the angle you manually set where the camera points at the bed center
# After physical alignment, test with: SET_SERVO SERVO=camera_servo ANGLE=X
# and adjust this value to match the angle where camera points at bed center
# Common values: 90 for centered 180° servo, 45 for centered 90° servo
# But can be any value within your SERVO_RANGE if servo is mounted off-center
SERVO_CENTER_ANGLE = 90.0  # The angle that points camera at bed center

# Invert servo angles (for upside-down mounted servos)
# When True, angles are mirrored over the centerline
# Example: For 180° servo: 60° becomes 120°, 90° stays 90°, 120° becomes 60°
INVERT_SERVO = False  # Set to True if servo is mounted upside down

# The servo center angle is your reference point - all object angles are calculated
# relative to this center position
# ============================================================================


def calculate_angle(camera_pos, object_center, bed_center):
    """
    Calculate the servo angle needed to point the camera at an object.
    
    The calculation uses SERVO_CENTER_ANGLE as the reference point where
    the camera points at bed center. All object angles are calculated
    relative to this reference position.
    
    Args:
        camera_pos: Tuple (x, y) of camera position
        object_center: Tuple (x, y) of object center coordinates
        bed_center: Tuple (x, y) of bed center coordinates
    
    Returns:
        float: Servo angle in degrees (0-90 or 0-180 depending on SERVO_RANGE)
    """
    # Calculate the angle from camera to bed center (reference angle)
    dx_ref = bed_center[0] - camera_pos[0]
    dy_ref = bed_center[1] - camera_pos[1]
    angle_to_center_rad = math.atan2(dy_ref, dx_ref)
    angle_to_center_deg = math.degrees(angle_to_center_rad)
    
    # Calculate the angle from camera to object (target angle)
    dx_obj = object_center[0] - camera_pos[0]
    dy_obj = object_center[1] - camera_pos[1]
    angle_to_object_rad = math.atan2(dy_obj, dx_obj)
    angle_to_object_deg = math.degrees(angle_to_object_rad)
    
    # Calculate the angular difference (how much to rotate from center position)
    angle_difference = angle_to_object_deg - angle_to_center_deg
    
    # Normalize the difference to -180 to +180 range
    while angle_difference > 180:
        angle_difference -= 360
    while angle_difference < -180:
        angle_difference += 360
    
    # Calculate servo position using the configured center angle as reference
    servo_angle = SERVO_CENTER_ANGLE + angle_difference
    
    # Clamp to valid servo range
    servo_angle = max(0, min(SERVO_RANGE, servo_angle))
    
    # Invert angle if servo is mounted upside down
    # This mirrors the angle over the centerline
    if INVERT_SERVO:
        servo_angle = SERVO_RANGE - servo_angle
    
    return servo_angle


def parse_executable_block(gcode_lines):
    """
    Parse the EXECUTABLE_BLOCK_START section to extract object data.
    
    Returns:
        dict: Dictionary mapping object names to their center coordinates
              Format: {object_name: (center_x, center_y)}
    """
    objects = {}
    in_block = False
    
    for line in gcode_lines:
        line = line.strip()
        
        # Check for start of executable block (starts with comment)
        if 'EXECUTABLE_BLOCK_START' in line:
            in_block = True
            continue
        
        # Check for end of executable block or if we hit other gcode
        # The block ends when we see non-EXCLUDE_OBJECT_DEFINE lines
        if in_block:
            # Parse EXCLUDE_OBJECT_DEFINE lines
            # Format: EXCLUDE_OBJECT_DEFINE NAME=object_name CENTER=x,y POLYGON=...
            if line.startswith('EXCLUDE_OBJECT_DEFINE'):
                # Extract object name
                name_match = re.search(r'NAME=([^\s]+)', line)
                # Extract center coordinates
                center_match = re.search(r'CENTER=([0-9.]+),([0-9.]+)', line)
                
                if name_match and center_match:
                    object_name = name_match.group(1)
                    center_x = float(center_match.group(1))
                    center_y = float(center_match.group(2))
                    objects[object_name] = (center_x, center_y)
            elif line and not line.startswith(';'):
                # End of executable block when we hit non-comment, non-EXCLUDE_OBJECT_DEFINE
                break
    
    return objects


def insert_camera_commands(gcode_lines, objects):
    """
    Insert Klipper SET_SERVO commands after EXCLUDE_OBJECT_START and the next movement command.
    Only inserts commands when switching to a different object.
    
    Args:
        gcode_lines: List of gcode lines
        objects: Dictionary mapping object names to center coordinates
    
    Returns:
        list: Modified list of gcode lines with camera commands inserted
    """
    modified_lines = []
    camera_pos = (CAMERA_X, CAMERA_Y)
    bed_center = (BED_WIDTH / 2.0, BED_DEPTH / 2.0)
    
    pending_servo_command = None  # Store the servo command to insert later
    waiting_for_movement = False   # Flag to track when we're waiting for a movement line
    last_object_name = None        # Track the last object we inserted a command for
    
    # Regex to match movement commands (G0, G1, G2, G3 with X, Y, or Z)
    movement_pattern = re.compile(r'^G[0-3]\s+.*[XYZ]', re.IGNORECASE)
    
    for line in gcode_lines:
        # Add the current line first
        modified_lines.append(line)
        
        # Check if this line starts an object exclusion
        if line.strip().startswith('EXCLUDE_OBJECT_START NAME='):
            # Extract the object name
            match = re.search(r'EXCLUDE_OBJECT_START NAME=([^\s]+)', line)
            if match:
                object_name = match.group(1)
                
                # Only insert a servo command if this is a different object than the last one
                if object_name != last_object_name:
                    # Look up the coordinates for this object
                    if object_name in objects:
                        object_center = objects[object_name]
                        
                        # Calculate the servo angle for the camera to point at the object
                        angle = calculate_angle(camera_pos, object_center, bed_center)
                        
                        # Store the servo command to insert after the next movement
                        pending_servo_command = f"SET_SERVO SERVO={SERVO_NAME} ANGLE={angle:.2f}\n"
                        waiting_for_movement = True
                        last_object_name = object_name  # Update the last object
                    else:
                        print(f"Warning: Object '{object_name}' not found in EXECUTABLE_BLOCK_START section")
                # else: skip inserting a command since we're already pointing at this object
        
        # If we're waiting for a movement command and this line is a movement command
        elif waiting_for_movement and movement_pattern.match(line.strip()):
            # Insert the pending servo command after this movement line
            if pending_servo_command:
                modified_lines.append(pending_servo_command)
                pending_servo_command = None
                waiting_for_movement = False
    
    return modified_lines


def process_gcode_file(filepath):
    """
    Process a gcode file to insert camera positioning commands.
    
    Args:
        filepath: Path to the gcode file to process
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    
    print(f"Processing file: {filepath}")
    
    # Read the gcode file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            gcode_lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    print(f"Read {len(gcode_lines)} lines")
    print(f"Camera position: ({CAMERA_X}, {CAMERA_Y})")
    print(f"Bed size: {BED_WIDTH}x{BED_DEPTH} mm, center: ({BED_WIDTH/2}, {BED_DEPTH/2})")
    print(f"Servo range: {SERVO_RANGE}° (center angle {SERVO_CENTER_ANGLE}° points to bed center)")
    
    # Parse the executable block to get object data
    objects = parse_executable_block(gcode_lines)
    print(f"Found {len(objects)} objects:")
    camera_pos = (CAMERA_X, CAMERA_Y)
    bed_center = (BED_WIDTH / 2.0, BED_DEPTH / 2.0)
    for name, (x, y) in objects.items():
        angle = calculate_angle(camera_pos, (x, y), bed_center)
        print(f"  {name}: center=({x}, {y}), servo angle={angle:.2f}°")
    
    if not objects:
        print("Warning: No objects found in EXECUTABLE_BLOCK_START section")
        print("Please verify the gcode file format")
        sys.exit(1)
    
    # Insert camera commands
    modified_lines = insert_camera_commands(gcode_lines, objects)
    
    # Count how many camera commands were inserted
    camera_count = sum(1 for line in modified_lines if 'SET_SERVO' in line and SERVO_NAME in line)
    print(f"Inserted {camera_count} SET_SERVO commands")
    
    # Save the modified gcode back to the original file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(modified_lines)
        print(f"Successfully saved modified gcode to: {filepath}")
    except Exception as e:
        print(f"Error writing file: {e}")
        sys.exit(1)


def main():
    """Main entry point for the script."""
    # Configuration
    run_in_slicer = True  # Set to False for manual testing
    
    if run_in_slicer:
        if len(sys.argv) != 2:
            print("Usage: python point_and_print.py <gcode_file>")
            print("\nThis script will:")
            print("  1. Parse object names and center points from EXECUTABLE_BLOCK_START")
            print("  2. Insert SET_SERVO commands before each EXCLUDE_OBJECT_START")
            print("  3. Save the modified gcode to the original file")
            sys.exit(1)
        
        path_input = sys.argv[1]  # the path of the gcode given by the slicer
        path_output = path_input  # same input and output
        print('Program', sys.argv[0], 'initiated')  # prints out path to program
    else:
        # For manual testing - insert your file path here
        path_input = r"C:\path\to\your\file.gcode"
        path_output = path_input  # or specify a different output path
    
    process_gcode_file(path_input)


if __name__ == "__main__":
    main()
