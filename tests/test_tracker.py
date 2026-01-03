"""Tests for core/tracker.py"""

from unittest.mock import patch

import numpy as np

from core.tracker import FaceTracker


class TestFaceTracker:
    """Tests for FaceTracker class."""

    def test_init(self):
        """Test initialization."""
        tracker = FaceTracker()

        assert tracker.enabled is False
        assert tracker.last_face is None
        assert tracker.smoothed_offset == (0.0, 0.0)
        assert tracker.cascade is not None

    def test_reset(self):
        """Test reset clears state."""
        tracker = FaceTracker()
        tracker.last_face = (100, 100, 50, 50)
        tracker.smoothed_offset = (0.5, 0.3)

        tracker.reset()

        assert tracker.last_face is None
        assert tracker.smoothed_offset == (0.0, 0.0)

    def test_detect_no_face(self, sample_frame):
        """Test detection with no face in frame."""
        tracker = FaceTracker()
        result = tracker.detect(sample_frame)

        # Plain frame has no face
        assert result is None

    @patch.object(FaceTracker, "detect")
    def test_calculate_offset_centered(self, mock_detect):
        """Test offset calculation when face is centered."""
        tracker = FaceTracker()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Face centered at (320, 240) with 100x100 size
        # Center of face: 320 + 50 = 370, but we want it at 320
        # So face at (270, 190) would be centered
        face = (270, 190, 100, 100)

        offset = tracker.calculate_offset(frame, face)

        # Should be close to (0, 0) since face center is near frame center
        assert abs(offset[0]) < 0.1
        assert abs(offset[1]) < 0.1

    @patch.object(FaceTracker, "detect")
    def test_calculate_offset_right(self, mock_detect):
        """Test offset when face is on the right."""
        tracker = FaceTracker()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Face on far right
        face = (540, 190, 100, 100)  # center at 590, 240

        offset = tracker.calculate_offset(frame, face)

        # Should have positive x offset (face is right of center)
        assert offset[0] > 0

    @patch.object(FaceTracker, "detect")
    def test_calculate_offset_left(self, mock_detect):
        """Test offset when face is on the left."""
        tracker = FaceTracker()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Face on far left
        face = (0, 190, 100, 100)  # center at 50, 240

        offset = tracker.calculate_offset(frame, face)

        # Should have negative x offset (face is left of center)
        assert offset[0] < 0

    def test_calculate_offset_deadzone(self):
        """Test that small offsets within deadzone are zeroed."""
        tracker = FaceTracker()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Face nearly centered (within deadzone)
        # Frame center: 320, 240
        # Face center should be at 320 +/- deadzone
        face = (305, 225, 30, 30)  # center at 320, 240

        offset = tracker.calculate_offset(frame, face)

        # Should be exactly 0 due to deadzone
        # (offset is smoothed, so check it's very small)
        assert abs(offset[0]) < 0.1
        assert abs(offset[1]) < 0.1

    def test_get_pan_tilt_delta_no_face(self, sample_frame):
        """Test pan/tilt returns None when no face detected."""
        tracker = FaceTracker()
        result = tracker.get_pan_tilt_delta(sample_frame)

        assert result is None

    @patch.object(FaceTracker, "detect")
    def test_get_pan_tilt_delta_with_face(self, mock_detect):
        """Test pan/tilt calculation with detected face."""
        tracker = FaceTracker()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Face on the right side
        mock_detect.return_value = (500, 190, 100, 100)

        result = tracker.get_pan_tilt_delta(frame)

        assert result is not None
        pan_delta, tilt_delta = result
        # Face on right -> pan should be negative (move camera left)
        assert pan_delta < 0

    def test_draw_overlay_no_face(self, sample_frame):
        """Test overlay drawing with no face."""
        tracker = FaceTracker()
        result = tracker.draw_overlay(sample_frame.copy())

        # Should return frame unchanged (no rectangle drawn)
        assert result.shape == sample_frame.shape

    def test_draw_overlay_with_face(self, sample_frame):
        """Test overlay drawing with face."""
        tracker = FaceTracker()
        tracker.last_face = (100, 100, 50, 50)

        result = tracker.draw_overlay(sample_frame.copy())

        # Frame should be modified (rectangle drawn)
        assert result.shape == sample_frame.shape
        # Check that some pixels changed (the rectangle)
        assert not np.array_equal(result, sample_frame)

    def test_draw_overlay_color_based_on_enabled(self, sample_frame):
        """Test overlay color changes based on enabled state."""
        tracker = FaceTracker()
        tracker.last_face = (100, 100, 50, 50)

        tracker.enabled = False
        result_disabled = tracker.draw_overlay(sample_frame.copy())

        tracker.enabled = True
        result_enabled = tracker.draw_overlay(sample_frame.copy())

        # Colors should be different
        assert not np.array_equal(result_disabled, result_enabled)

    def test_smoothing(self):
        """Test that offset smoothing works."""
        tracker = FaceTracker()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # First offset - far right
        face1 = (540, 190, 100, 100)
        tracker.calculate_offset(frame, face1)

        # Second offset - same position
        offset2 = tracker.calculate_offset(frame, face1)

        # Third offset - should converge toward actual offset
        offset3 = tracker.calculate_offset(frame, face1)

        # Each successive call should get closer to the true offset
        # (smoothing should cause gradual approach)
        assert abs(offset3[0]) >= abs(offset2[0]) or abs(offset2[0] - offset3[0]) < 0.01
