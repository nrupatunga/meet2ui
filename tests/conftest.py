"""Shared test fixtures."""

import sys
from pathlib import Path

import numpy as np
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_frame():
    """Create a sample BGR frame for testing."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Add some color
    frame[100:200, 100:200] = [255, 0, 0]  # Blue square
    return frame


@pytest.fixture
def frame_with_face(sample_frame):
    """Create a frame with a face-like region (for cascade detection)."""
    # Note: Real face detection needs actual face images
    # This is a placeholder that won't trigger detection
    return sample_frame


@pytest.fixture
def temp_presets_dir(tmp_path, monkeypatch):
    """Create temporary presets directory."""
    config_dir = tmp_path / ".config" / "meet2ui"
    config_dir.mkdir(parents=True)

    # Monkeypatch Path.home to return tmp_path
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    return config_dir
