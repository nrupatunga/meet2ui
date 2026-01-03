"""Video preview widget for DearPyGui."""

from __future__ import annotations

import cv2
import dearpygui.dearpygui as dpg
import numpy as np

from utils.constants import PREVIEW_HEIGHT, PREVIEW_WIDTH


class Preview:
    """Manages live video preview in DearPyGui."""

    def __init__(self, width: int = PREVIEW_WIDTH, height: int = PREVIEW_HEIGHT):
        self.width = width
        self.height = height
        self.texture_id = None
        self.image_id = None
        self._blank = self._create_blank()

    def _create_blank(self) -> np.ndarray:
        """Create blank frame for when camera is off."""
        blank = np.zeros((self.height, self.width, 4), dtype=np.float32)
        blank[:, :, 3] = 1.0  # Alpha channel
        return blank.flatten()

    def _create_loading_frame(self) -> np.ndarray:
        """Create frame with 'Loading...' text."""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:] = (35, 35, 30)  # Dark background matching theme

        text = "Loading..."
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        thickness = 2
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (self.width - text_size[0]) // 2
        text_y = (self.height + text_size[1]) // 2
        cv2.putText(
            frame, text, (text_x, text_y), font, font_scale, (150, 150, 150), thickness
        )

        # Convert to RGBA float32
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        frame = frame.astype(np.float32) / 255.0
        return frame.flatten()

    def show_loading(self):
        """Display loading message in preview."""
        loading_frame = self._create_loading_frame()
        dpg.set_value("preview_texture", loading_frame)

    def create(self) -> int:
        """Create the texture and image widget. Returns image widget ID."""
        # Create texture registry if needed
        with dpg.texture_registry():
            self.texture_id = dpg.add_raw_texture(
                width=self.width,
                height=self.height,
                default_value=self._blank,
                format=dpg.mvFormat_Float_rgba,
                tag="preview_texture",
            )

        self.image_id = dpg.add_image(
            "preview_texture",
            width=self.width,
            height=self.height,
            tag="preview_image",
        )
        return self.image_id

    def update(self, frame: np.ndarray | None):
        """Update preview with new frame (BGR numpy array)."""
        if frame is None:
            dpg.set_value("preview_texture", self._blank)
            return

        # Resize to preview dimensions
        frame = cv2.resize(frame, (self.width, self.height))

        # Convert BGR to RGBA float32
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        frame = frame.astype(np.float32) / 255.0
        frame = frame.flatten()

        dpg.set_value("preview_texture", frame)

    def clear(self):
        """Clear the preview to blank."""
        dpg.set_value("preview_texture", self._blank)
