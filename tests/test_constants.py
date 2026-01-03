"""Tests for utils/constants.py"""

from utils.constants import (
    CONTROL_GROUPS,
    CONTROLS,
    LABELS,
    PREVIEW_HEIGHT,
    PREVIEW_WIDTH,
    TRACK_DEADZONE,
    TRACK_SPEED,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


class TestControls:
    """Tests for CONTROLS constant."""

    def test_has_ptz_controls(self):
        """Test PTZ controls are defined."""
        assert "zoom_absolute" in CONTROLS
        assert "pan_absolute" in CONTROLS
        assert "tilt_absolute" in CONTROLS

    def test_has_image_controls(self):
        """Test image controls are defined."""
        assert "brightness" in CONTROLS
        assert "contrast" in CONTROLS
        assert "saturation" in CONTROLS
        assert "sharpness" in CONTROLS

    def test_has_focus_control(self):
        """Test focus control is defined."""
        assert "focus_automatic_continuous" in CONTROLS

    def test_control_format(self):
        """Test each control has (min, max, default, step) tuple."""
        for name, value in CONTROLS.items():
            assert isinstance(value, tuple), f"{name} is not a tuple"
            assert len(value) == 4, f"{name} doesn't have 4 elements"
            min_val, max_val, default, step = value
            assert min_val <= default <= max_val, f"{name} default out of range"
            assert step > 0, f"{name} step should be positive"


class TestLabels:
    """Tests for LABELS constant."""

    def test_all_controls_have_labels(self):
        """Test every control has a label."""
        for control in CONTROLS:
            assert control in LABELS, f"{control} missing label"

    def test_labels_are_strings(self):
        """Test all labels are strings."""
        for _control, label in LABELS.items():
            assert isinstance(label, str)
            assert len(label) > 0


class TestControlGroups:
    """Tests for CONTROL_GROUPS constant."""

    def test_has_expected_groups(self):
        """Test expected groups exist."""
        assert "PTZ" in CONTROL_GROUPS
        assert "Image" in CONTROL_GROUPS
        assert "Focus" in CONTROL_GROUPS

    def test_all_controls_in_groups(self):
        """Test all controls are in some group."""
        grouped_controls = set()
        for group_controls in CONTROL_GROUPS.values():
            grouped_controls.update(group_controls)

        for control in CONTROLS:
            assert control in grouped_controls, f"{control} not in any group"


class TestWindowDimensions:
    """Tests for window dimension constants."""

    def test_window_dimensions_positive(self):
        """Test window dimensions are positive."""
        assert WINDOW_WIDTH > 0
        assert WINDOW_HEIGHT > 0

    def test_preview_dimensions_positive(self):
        """Test preview dimensions are positive."""
        assert PREVIEW_WIDTH > 0
        assert PREVIEW_HEIGHT > 0

    def test_preview_fits_in_window(self):
        """Test preview is smaller than window."""
        assert PREVIEW_WIDTH < WINDOW_WIDTH
        assert PREVIEW_HEIGHT < WINDOW_HEIGHT

    def test_window_size(self):
        """Test window is 640x480."""
        assert WINDOW_WIDTH == 640
        assert WINDOW_HEIGHT == 480


class TestTrackingConstants:
    """Tests for tracking constants."""

    def test_deadzone_positive(self):
        """Test deadzone is positive."""
        assert TRACK_DEADZONE > 0

    def test_speed_in_range(self):
        """Test speed is between 0 and 1."""
        assert 0 < TRACK_SPEED <= 1
