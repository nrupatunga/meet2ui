"""Main application window."""

from __future__ import annotations

import time

import dearpygui.dearpygui as dpg

from config.presets import get_preset, list_preset_names, save_preset
from core.camera import Camera
from core.tracker import FaceTracker
from core.v4l2 import V4L2Control
from ui.controls import create_button, create_slider, create_toggle, update_slider
from ui.preview import Preview
from ui.theme import setup_theme
from utils.constants import (
    CONTROL_GROUPS,
    CONTROLS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


class App:
    """Main application class."""

    def __init__(self):
        self.v4l2 = V4L2Control()
        self.camera = Camera()
        self.tracker = FaceTracker()
        self.preview = Preview()
        self.running = False
        self.current_values: dict[str, int] = {}

    def setup(self):
        """Initialize DearPyGui and create window."""
        dpg.create_context()
        setup_theme()

        # Main window
        with dpg.window(tag="main", label="Meet2UI", no_resize=False, no_close=True):
            # Preview
            self.preview.create()
            dpg.add_spacer(height=4)

            # Tracking toggle + FPS
            with dpg.group(horizontal=True):
                dpg.add_checkbox(
                    label="Track",
                    tag="track_toggle",
                    callback=self._on_track_toggle,
                )
                dpg.add_spacer(width=8)
                dpg.add_text("FPS: --", tag="fps_text")

            dpg.add_spacer(height=4)

            # Tab bar for control groups
            with dpg.tab_bar():
                # PTZ tab
                with dpg.tab(label="PTZ"):
                    for ctrl in CONTROL_GROUPS["PTZ"]:
                        create_slider(ctrl, self._on_slider_change, width=500)

                # Image tab
                with dpg.tab(label="Image"):
                    for ctrl in CONTROL_GROUPS["Image"]:
                        create_slider(ctrl, self._on_slider_change, width=500)

                # Focus tab
                with dpg.tab(label="Focus"):
                    create_toggle("focus_automatic_continuous", self._on_toggle_change)

            dpg.add_spacer(height=4)

            # Presets row
            with dpg.group(horizontal=True):
                dpg.add_combo(
                    items=list_preset_names(),
                    default_value="Default",
                    width=120,
                    tag="preset_combo",
                    callback=self._on_preset_select,
                )
                create_button("Save", self._on_save_preset, width=50)
                create_button("Reset", self._on_reset, width=50)

        # Configure viewport
        dpg.create_viewport(
            title="Meet2UI",
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            min_width=640,
            min_height=480,
            resizable=False,
        )
        dpg.setup_dearpygui()
        dpg.set_primary_window("main", True)

    def _on_slider_change(self, control: str, value: int):
        """Handle slider value change."""
        self.v4l2.set(control, value)
        self.current_values[control] = value

    def _on_toggle_change(self, control: str, enabled: bool):
        """Handle toggle change."""
        self.v4l2.set(control, 1 if enabled else 0)
        self.current_values[control] = 1 if enabled else 0

    def _on_track_toggle(self, sender, value):
        """Handle tracking toggle."""
        self.tracker.enabled = value
        if not value:
            self.tracker.reset()

    def _on_preset_select(self, sender, preset_name):
        """Load selected preset."""
        values = get_preset(preset_name)
        if values:
            self._apply_values(values)

    def _on_save_preset(self):
        """Save current values as preset."""
        # Simple: overwrite current selection
        name = dpg.get_value("preset_combo")
        save_preset(name, self.current_values.copy())

    def _on_reset(self):
        """Reset to defaults."""
        defaults = {name: ctrl[2] for name, ctrl in CONTROLS.items()}
        self._apply_values(defaults)

    def _apply_values(self, values: dict[str, int]):
        """Apply a set of control values."""
        for control, value in values.items():
            self.v4l2.set(control, value)
            self.current_values[control] = value
            update_slider(control, value)

    def _update_loop(self):
        """Called each frame to update preview."""
        frame = self.camera.read()

        if frame is not None and self.tracker.enabled:
            delta = self.tracker.get_pan_tilt_delta(frame)
            if delta:
                pan_delta, tilt_delta = delta
                # Get current values and adjust
                cur_pan = self.current_values.get("pan_absolute", 0)
                cur_tilt = self.current_values.get("tilt_absolute", 0)
                new_pan = max(-648000, min(648000, cur_pan + pan_delta))
                new_tilt = max(-648000, min(648000, cur_tilt + tilt_delta))

                if abs(pan_delta) > 100 or abs(tilt_delta) > 100:
                    self.v4l2.set("pan_absolute", new_pan)
                    self.v4l2.set("tilt_absolute", new_tilt)
                    self.current_values["pan_absolute"] = new_pan
                    self.current_values["tilt_absolute"] = new_tilt
                    update_slider("pan_absolute", new_pan)
                    update_slider("tilt_absolute", new_tilt)

            frame = self.tracker.draw_overlay(frame)

        self.preview.update(frame)

    def run(self):
        """Start the application."""
        # Open camera
        self.camera.open()

        # Load initial values from camera
        for control in CONTROLS:
            val = self.v4l2.get(control)
            if val is not None:
                self.current_values[control] = val
                update_slider(control, val)

        dpg.show_viewport()
        self.running = True

        frame_count = 0
        last_fps_time = time.time()

        while dpg.is_dearpygui_running():
            self._update_loop()
            dpg.render_dearpygui_frame()

            # FPS counter
            frame_count += 1
            now = time.time()
            if now - last_fps_time >= 1.0:
                fps = frame_count / (now - last_fps_time)
                dpg.set_value("fps_text", f"FPS: {fps:.0f}")
                frame_count = 0
                last_fps_time = now

        self.shutdown()

    def shutdown(self):
        """Clean up resources."""
        self.running = False
        self.camera.close()
        dpg.destroy_context()
