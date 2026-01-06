# Slicer Setup Guide

This guide shows how to add the point_and_print.py script as a post-processing script in popular slicers.

## ⚠️ CRITICAL REQUIREMENT

**You MUST enable "Exclude objects" in your slicer settings!**

The script requires the `EXCLUDE_OBJECT_DEFINE` and `EXCLUDE_OBJECT_START` commands that are only generated when "Exclude objects" is enabled.

- ❌ **"Label objects" alone is NOT sufficient** - this only adds comments
- ✅ **"Exclude objects" must be enabled** - this generates the required commands

**Without "Exclude objects" enabled, the script will fail with an error during printing.**

---

## PrusaSlicer / SuperSlicer / OrcaSlicer

### Step 1: Enable Exclude Objects
1. Open your slicer
2. Go to **Print Settings** → **Output options**
3. Find and **enable** the checkbox: **"Exclude objects"**
4. Click **OK** or **Save**

### Step 2: Add Post-Processing Script

### Step 2: Add Post-Processing Script
1. In the same **Print Settings** → **Output options** section
2. Find the **Post-processing scripts** field
3. Add the following line:
   ```
   python /full/path/to/point_and_print.py
   ```
   Replace `/full/path/to/` with the actual path where you saved the script

5. Click **OK** or **Save**

**Example:**
- Windows: `python C:\Users\YourName\Documents\point_and_print.py`
- Linux/Mac: `python /home/yourname/scripts/point_and_print.py`

### Alternative: Using Python3 explicitly
If you have both Python 2 and Python 3 installed, use:
```
python3 /full/path/to/point_and_print.py
```

## Cura

1. Open Cura
2. Go to **Extensions** → **Post Processing** → **Modify G-Code**
3. Click **Add a script**
4. Look for or create a custom script option
5. In older versions of Cura, you may need to use a plugin like "Post Processing Plugin"

**Note:** Cura's post-processing works differently. You may need to:
- Use the built-in "Search and Replace" functionality for simple modifications
- Or install a plugin that allows running external Python scripts
- Or manually run the script after slicing

## Simplify3D

1. Open Simplify3D
2. Click **Edit Process Settings**
3. Go to the **Scripts** tab
4. In the **Post Processing** section, add:
   ```
   python /full/path/to/point_and_print.py [output_filepath]
   ```

**Note:** Use `[output_filepath]` as a placeholder - Simplify3D will replace it with the actual file path.

## IdeaMaker

1. Open IdeaMaker
2. Go to **Settings** → **G-Code**
3. Find the **Post-processing script** section
4. Add:
   ```
   python /full/path/to/point_and_print.py
   ```

## Bambu Studio

1. Open Bambu Studio
2. Go to **Printer Settings**
3. Look for **Machine G-code** or **Post-processing scripts**
4. Add the Python command with the full path to the script

## General Troubleshooting

### "python is not recognized"
- Make sure Python is installed and added to your system PATH
- Try using the full path to python:
  - Windows: `C:\Python39\python.exe /path/to/script.py`
  - Linux/Mac: `/usr/bin/python3 /path/to/script.py`

### Script not executing
- Check that the script has the correct permissions (especially on Linux/Mac):
  ```bash
  chmod +x /path/to/point_and_print.py
  ```
- Verify the Python path is correct
- Check slicer logs for error messages

### Testing the script
Before adding it to your slicer, test it manually:
```bash
python point_and_print.py /path/to/test_file.gcode
```

If this works, the slicer integration should work too.

## Verification

After slicing a file, check that both requirements are met:

### 1. Verify "Exclude objects" is working
Open the generated gcode file and search for:
- `EXCLUDE_OBJECT_DEFINE` - Should appear near the beginning
- `EXCLUDE_OBJECT_START` - Should appear throughout the file

If these commands are **missing**, "Exclude objects" is not enabled in your slicer!

### 2. Verify the script ran successfully
Search for `SET_SERVO` in the gcode:
```gcode
SET_SERVO SERVO=camera_servo ANGLE=90.00
EXCLUDE_OBJECT_START NAME=object_name
```

If you see these commands, everything is working correctly!

## Troubleshooting "Exclude Objects"

### Error: "No objects found in EXECUTABLE_BLOCK_START section"

**Cause:** "Exclude objects" is not enabled in your slicer.

**Solution:**
1. Go back to **Print Settings** → **Output options**
2. Enable the **"Exclude objects"** checkbox
3. Re-slice your model
4. Verify `EXCLUDE_OBJECT_DEFINE` appears in the gcode

### "Label objects" vs "Exclude objects"

Many slicers have BOTH options:
- **Label objects** - Adds comments like `; printing object name`
- **Exclude objects** - Adds actual commands like `EXCLUDE_OBJECT_START`

**You need "Exclude objects" enabled!** Label objects alone won't work.

### Common Mistakes

❌ Only enabled "Label objects"  
❌ Enabled neither option  
❌ Enabled "Exclude objects" but it's not generating commands (try different slicer version)

✅ "Exclude objects" is enabled and `EXCLUDE_OBJECT_START` appears in gcode
