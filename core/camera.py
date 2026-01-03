"""Camera device detection and frame capture."""

from __future__ import annotations

import subprocess
from pathlib import Path

import cv2
import numpy as np


def list_devices() -> list[tuple[str, str]]:
    """List available video devices. Returns [(path, name), ...]."""
    devices = []
    try:
        result = subprocess.run(
            ["v4l2-ctl", "--list-devices"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            current_name = ""
            for line in lines:
                if not line.startswith("\t"):
                    current_name = line.rstrip(":")
                elif "/dev/video" in line:
                    dev_path = line.strip()
                    devices.append((dev_path, current_name))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Fallback: scan /dev/video*
        for i in range(10):
            path = f"/dev/video{i}"
            if Path(path).exists():
                devices.append((path, f"Camera {i}"))
    return devices


class Camera:
    """OpenCV video capture wrapper."""

    def __init__(self, device: str = "/dev/video0"):
        self.device = device
        self.cap = None
        self.width = 640
        self.height = 360

    def open(self) -> bool:
        """Open the camera device."""
        self.close()
        # Extract device index from path
        if self.device.startswith("/dev/video"):
            try:
                idx = int(self.device.replace("/dev/video", ""))
            except ValueError:
                idx = 0
        else:
            idx = 0

        self.cap = cv2.VideoCapture(idx)
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            return True
        return False

    def close(self):
        """Release the camera."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def read(self) -> np.ndarray | None:
        """Read a frame. Returns BGR numpy array or None."""
        if self.cap is None or not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        return frame if ret else None

    def set_device(self, device: str):
        """Change device and reopen."""
        self.device = device
        if self.cap is not None:
            self.open()

    @property
    def is_open(self) -> bool:
        return self.cap is not None and self.cap.isOpened()
