"""Face detection and tracking logic."""

from __future__ import annotations

import cv2
import numpy as np

from utils.constants import TRACK_DEADZONE, TRACK_SPEED


class FaceTracker:
    """Detects faces and calculates pan/tilt adjustments."""

    def __init__(self):
        # Use OpenCV's built-in Haar cascade
        self.cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.enabled = False
        self.last_face = None  # (x, y, w, h)
        self.smoothed_offset = (0.0, 0.0)

    def detect(self, frame: np.ndarray) -> tuple[int, int, int, int] | None:
        """Detect largest face in frame. Returns (x, y, w, h) or None."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
        )
        if len(faces) == 0:
            return None
        # Return largest face
        largest = max(faces, key=lambda f: f[2] * f[3])
        self.last_face = tuple(largest)
        return self.last_face

    def calculate_offset(
        self, frame: np.ndarray, face: tuple[int, int, int, int]
    ) -> tuple[float, float]:
        """Calculate normalized offset from center (-1 to 1)."""
        frame_h, frame_w = frame.shape[:2]
        x, y, w, h = face

        # Face center
        face_cx = x + w // 2
        face_cy = y + h // 2

        # Frame center
        center_x = frame_w // 2
        center_y = frame_h // 2

        # Offset in pixels
        offset_x = face_cx - center_x
        offset_y = face_cy - center_y

        # Apply deadzone
        if abs(offset_x) < TRACK_DEADZONE:
            offset_x = 0
        if abs(offset_y) < TRACK_DEADZONE:
            offset_y = 0

        # Normalize to -1..1
        norm_x = offset_x / (frame_w / 2) if offset_x != 0 else 0
        norm_y = offset_y / (frame_h / 2) if offset_y != 0 else 0

        # Smooth
        self.smoothed_offset = (
            self.smoothed_offset[0] * (1 - TRACK_SPEED) + norm_x * TRACK_SPEED,
            self.smoothed_offset[1] * (1 - TRACK_SPEED) + norm_y * TRACK_SPEED,
        )

        return self.smoothed_offset

    def get_pan_tilt_delta(
        self, frame: np.ndarray, pan_range: int = 36000, tilt_range: int = 36000
    ) -> tuple[int, int] | None:
        """Get pan/tilt adjustment values. Returns (pan_delta, tilt_delta) or None."""
        face = self.detect(frame)
        if face is None:
            return None

        offset_x, offset_y = self.calculate_offset(frame, face)

        # Convert normalized offset to pan/tilt delta
        # Negative pan = move left (face on right), etc.
        pan_delta = int(-offset_x * pan_range)
        tilt_delta = int(-offset_y * tilt_range)

        return (pan_delta, tilt_delta)

    def draw_overlay(self, frame: np.ndarray) -> np.ndarray:
        """Draw face rectangle on frame."""
        if self.last_face is not None:
            x, y, w, h = self.last_face
            color = (0, 255, 0) if self.enabled else (128, 128, 128)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        return frame

    def reset(self):
        """Reset tracking state."""
        self.last_face = None
        self.smoothed_offset = (0.0, 0.0)
