"""Main application window."""

from __future__ import annotations

import time

import dearpygui.dearpygui as dpg

from config.presets import get_preset, list_preset_names, save_preset
from core.camera import Camera, list_devices
from core.tracker import FaceTracker
from core.v4l2 import V4L2Control
from ui.controls import create_button, create_slider, create_toggle, update_slider
from ui.preview import Preview
from ui.theme import setup_font, setup_theme
from utils.constants import (
    CONTROL_GROUPS,
    CONTROLS,
    CONTROLS_HEIGHT,
    CONTROLS_WIDTH,
    PREVIEW_PADDING,
    PREVIEW_WIDTH,
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
        setup_font()

        # Main window
        with dpg.window(tag="main", label="Meet2UI", no_resize=False, no_close=True):
            # Horizontal layout: preview left, controls right
            with dpg.group(horizontal=True):
                # === LEFT PANEL: Preview (centered vertically) ===
                with dpg.child_window(
                    width=PREVIEW_WIDTH + 16,
                    height=CONTROLS_HEIGHT,
                    border=True,
                    no_scrollbar=True,
                ):
                    dpg.add_spacer(height=PREVIEW_PADDING)
                    self.preview.create()
                    dpg.add_spacer(height=PREVIEW_PADDING)

                dpg.add_spacer(width=8)

                # === RIGHT PANEL: Controls in child window ===
                with dpg.child_window(
                    width=CONTROLS_WIDTH,
                    height=CONTROLS_HEIGHT,
                    border=True,
                    no_scrollbar=True,
                ):
                    # Camera selector
                    devices = list_devices()
                    device_names = [d[1] for d in devices] if devices else ["No camera"]
                    dpg.add_text("Camera")
                    dpg.add_combo(
                        items=device_names,
                        default_value=device_names[0] if device_names else "",
                        width=-1,
                        tag="camera_combo",
                        callback=self._on_camera_select,
                    )
                    dpg.add_spacer(height=4)

                    # PTZ Controls section
                    dpg.add_text("PTZ Controls")
                    dpg.add_separator()
                    for ctrl in CONTROL_GROUPS["PTZ"]:
                        create_slider(ctrl, self._on_slider_change, width=120)
                    dpg.add_spacer(height=4)

                    # Image section
                    dpg.add_text("Image")
                    dpg.add_separator()
                    for ctrl in CONTROL_GROUPS["Image"]:
                        create_slider(ctrl, self._on_slider_change, width=120)
                    dpg.add_spacer(height=4)

                    # Focus section
                    dpg.add_separator()
                    create_toggle("focus_automatic_continuous", self._on_toggle_change)
                    dpg.add_spacer(height=4)

                    # Track toggle
                    dpg.add_checkbox(
                        label="Face Track",
                        tag="track_toggle",
                        callback=self._on_track_toggle,
                    )
                    dpg.add_spacer(height=4)

                    # Presets section
                    dpg.add_separator()
                    dpg.add_text("Presets")
                    dpg.add_combo(
                        items=list_preset_names(),
                        default_value="Default",
                        width=-1,
                        tag="preset_combo",
                        callback=self._on_preset_select,
                    )
                    with dpg.group(horizontal=True):
                        create_button("Save", self._on_save_preset, width=60)
                        create_button("Reset", self._on_reset, width=60)
                    dpg.add_spacer(height=4)

                    # FPS display at bottom of controls
                    dpg.add_text("FPS: --", tag="fps_text")

        # Configure viewport
        dpg.create_viewport(
            title="Meet2UI",
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            min_width=WINDOW_WIDTH,
            min_height=WINDOW_HEIGHT,
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

    def _on_camera_select(self, sender, camera_name):
        """Handle camera selection change."""
        devices = list_devices()
        for path, name in devices:
            if name == camera_name:
                self.camera.set_device(path)
                self.v4l2.set_device(path)
                break

    def _on_preset_select(self, sender, preset_name):
        """Load selected preset."""
        values = get_preset(preset_name)
        if values:
            self._apply_values(values)

    def _on_save_preset(self):
        """Save current values as preset."""
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
