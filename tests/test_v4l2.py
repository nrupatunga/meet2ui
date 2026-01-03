"""Tests for core/v4l2.py"""

import subprocess
from unittest.mock import MagicMock, patch

from core.v4l2 import V4L2Control


class TestV4L2Control:
    """Tests for V4L2Control class."""

    def test_init_default_device(self):
        """Test default device initialization."""
        ctrl = V4L2Control()
        assert ctrl.device == "/dev/video0"

    def test_init_custom_device(self):
        """Test custom device initialization."""
        ctrl = V4L2Control("/dev/video2")
        assert ctrl.device == "/dev/video2"

    def test_set_device(self):
        """Test changing device."""
        ctrl = V4L2Control()
        ctrl.set_device("/dev/video1")
        assert ctrl.device == "/dev/video1"

    @patch("subprocess.run")
    def test_get_success(self, mock_run):
        """Test successful get control."""
        mock_run.return_value = MagicMock(returncode=0, stdout="brightness: 75")
        ctrl = V4L2Control()
        result = ctrl.get("brightness")

        assert result == 75
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "v4l2-ctl" in args
        assert "--get-ctrl" in args
        assert "brightness" in args

    @patch("subprocess.run")
    def test_get_negative_value(self, mock_run):
        """Test get control with negative value."""
        mock_run.return_value = MagicMock(returncode=0, stdout="pan_absolute: -36000")
        ctrl = V4L2Control()
        result = ctrl.get("pan_absolute")

        assert result == -36000

    @patch("subprocess.run")
    def test_get_failure(self, mock_run):
        """Test failed get control."""
        mock_run.return_value = MagicMock(returncode=1, stdout="")
        ctrl = V4L2Control()
        result = ctrl.get("invalid_control")

        assert result is None

    @patch("subprocess.run")
    def test_get_timeout(self, mock_run):
        """Test get control timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("v4l2-ctl", 2)
        ctrl = V4L2Control()
        result = ctrl.get("brightness")

        assert result is None

    @patch("subprocess.run")
    def test_get_command_not_found(self, mock_run):
        """Test v4l2-ctl not installed."""
        mock_run.side_effect = FileNotFoundError()
        ctrl = V4L2Control()
        result = ctrl.get("brightness")

        assert result is None

    @patch("subprocess.run")
    def test_set_success(self, mock_run):
        """Test successful set control."""
        mock_run.return_value = MagicMock(returncode=0)
        ctrl = V4L2Control()
        result = ctrl.set("brightness", 80)

        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "--set-ctrl" in args
        assert "brightness=80" in args

    @patch("subprocess.run")
    def test_set_failure(self, mock_run):
        """Test failed set control."""
        mock_run.return_value = MagicMock(returncode=1)
        ctrl = V4L2Control()
        result = ctrl.set("brightness", 80)

        assert result is False

    @patch("subprocess.run")
    def test_set_timeout(self, mock_run):
        """Test set control timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("v4l2-ctl", 2)
        ctrl = V4L2Control()
        result = ctrl.set("brightness", 80)

        assert result is False

    @patch("subprocess.run")
    def test_list_controls(self, mock_run):
        """Test listing available controls."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="""
                     brightness 0x00980900 (int)    : min=0 max=100 step=1 default=50 value=50
                     contrast 0x00980901 (int)    : min=0 max=100 step=1 default=60 value=60
            """,
        )
        ctrl = V4L2Control()
        controls = ctrl.list_controls()

        assert "brightness" in controls
        assert controls["brightness"] == (0, 100, 50)
        assert "contrast" in controls
        assert controls["contrast"] == (0, 100, 60)

    @patch("subprocess.run")
    def test_list_controls_empty(self, mock_run):
        """Test listing controls when none available."""
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        ctrl = V4L2Control()
        controls = ctrl.list_controls()

        assert controls == {}
