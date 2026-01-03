"""Camera control constants and defaults."""

# Control definitions: (min, max, default, step)
CONTROLS = {
    # PTZ
    "zoom_absolute": (0, 100, 50, 1),
    "pan_absolute": (-648000, 648000, 0, 3600),
    "tilt_absolute": (-648000, 648000, 0, 3600),
    # Image
    "brightness": (0, 100, 50, 1),
    "contrast": (0, 100, 60, 1),
    "saturation": (0, 100, 50, 1),
    "sharpness": (0, 100, 50, 1),
    # Focus
    "focus_automatic_continuous": (0, 1, 1, 1),
}

# Display labels for controls
LABELS = {
    "zoom_absolute": "Zoom",
    "pan_absolute": "Pan",
    "tilt_absolute": "Tilt",
    "brightness": "Brightness",
    "contrast": "Contrast",
    "saturation": "Saturation",
    "sharpness": "Sharpness",
    "focus_automatic_continuous": "Autofocus",
}

# Control groups for tabbed UI
CONTROL_GROUPS = {
    "PTZ": ["zoom_absolute", "pan_absolute", "tilt_absolute"],
    "Image": ["brightness", "contrast", "saturation", "sharpness"],
    "Focus": ["focus_automatic_continuous"],
}

# Window dimensions
WINDOW_WIDTH = 350
WINDOW_HEIGHT = 320
PREVIEW_WIDTH = 320
PREVIEW_HEIGHT = 180

# Face tracking
TRACK_DEADZONE = 30  # pixels from center before tracking kicks in
TRACK_SPEED = 0.3  # smoothing factor (0-1)
