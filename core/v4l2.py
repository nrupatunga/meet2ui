"""v4l2-ctl wrapper for camera control."""

from __future__ import annotations

import re
import subprocess


class V4L2Control:
    """Wrapper for v4l2-ctl commands."""

    def __init__(self, device: str = "/dev/video0"):
        self.device = device

    def get(self, control: str) -> int | None:
        """Get current value of a control."""
        try:
            result = subprocess.run(
                ["v4l2-ctl", "-d", self.device, "--get-ctrl", control],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                match = re.search(r":\s*(-?\d+)", result.stdout)
                if match:
                    return int(match.group(1))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def set(self, control: str, value: int) -> bool:
        """Set a control value."""
        try:
            result = subprocess.run(
                ["v4l2-ctl", "-d", self.device, "--set-ctrl", f"{control}={value}"],
                capture_output=True,
                timeout=2,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def list_controls(self) -> dict[str, tuple[int, int, int]]:
        """List available controls with (min, max, default)."""
        controls = {}
        try:
            result = subprocess.run(
                ["v4l2-ctl", "-d", self.device, "--list-ctrls"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    match = re.match(
                        r"\s*(\w+)\s.*min=(-?\d+)\s+max=(-?\d+).*default=(-?\d+)",
                        line,
                    )
                    if match:
                        name = match.group(1)
                        controls[name] = (
                            int(match.group(2)),
                            int(match.group(3)),
                            int(match.group(4)),
                        )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return controls

    def set_device(self, device: str):
        """Change the target device."""
        self.device = device
