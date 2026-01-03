#!/usr/bin/env python3
"""Apply saved camera settings using v4l2-ctl.

Run this script before using the camera in other apps (Meet, Hangouts, Zoom, etc.)
to apply your saved Meet2UI settings.

Usage:
    python apply_settings.py              # Apply Default preset
    python apply_settings.py "MyPreset"   # Apply specific preset
    ./apply_settings.py                   # If executable
"""

from __future__ import annotations

import sys

from config.presets import get_preset, list_preset_names
from core.v4l2 import V4L2Control


def apply_settings(preset_name: str = "Default", device: str = "/dev/video0"):
    """Apply saved preset settings to camera."""
    v4l2 = V4L2Control(device)

    preset = get_preset(preset_name)
    if not preset:
        print(f"Preset '{preset_name}' not found.")
        print(f"Available presets: {', '.join(list_preset_names())}")
        return False

    print(f"Applying preset '{preset_name}' to {device}...")

    for control, value in preset.items():
        success = v4l2.set(control, value)
        status = "OK" if success else "FAILED"
        print(f"  {control}: {value} [{status}]")

    print("Done.")
    return True


def main():
    preset_name = sys.argv[1] if len(sys.argv) > 1 else "Default"
    device = sys.argv[2] if len(sys.argv) > 2 else "/dev/video0"

    if preset_name in ("--help", "-h"):
        print(__doc__)
        print(f"Available presets: {', '.join(list_preset_names())}")
        return

    apply_settings(preset_name, device)


if __name__ == "__main__":
    main()
