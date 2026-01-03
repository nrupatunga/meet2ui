"""Tests for config/presets.py"""

import json
from pathlib import Path

from config.presets import (
    delete_preset,
    get_defaults,
    get_preset,
    get_presets_path,
    list_preset_names,
    load_presets,
    save_preset,
    save_presets,
)
from utils.constants import CONTROLS


class TestGetDefaults:
    """Tests for get_defaults function."""

    def test_returns_dict(self):
        """Test that defaults returns a dict."""
        defaults = get_defaults()
        assert isinstance(defaults, dict)

    def test_contains_all_controls(self):
        """Test that all controls have defaults."""
        defaults = get_defaults()
        for control in CONTROLS:
            assert control in defaults

    def test_values_match_constants(self):
        """Test default values match CONTROLS."""
        defaults = get_defaults()
        for control, (_, _, default, _) in CONTROLS.items():
            assert defaults[control] == default


class TestPresetsPath:
    """Tests for get_presets_path function."""

    def test_returns_path(self, temp_presets_dir):
        """Test that path is returned."""
        path = get_presets_path()
        assert isinstance(path, Path)
        assert path.name == "presets.json"

    def test_creates_parent_dirs(self, temp_presets_dir):
        """Test that parent directories are created."""
        path = get_presets_path()
        assert path.parent.exists()


class TestLoadPresets:
    """Tests for load_presets function."""

    def test_returns_default_when_no_file(self, temp_presets_dir):
        """Test loading when file doesn't exist."""
        presets = load_presets()

        assert "Default" in presets
        assert presets["Default"] == get_defaults()

    def test_loads_existing_presets(self, temp_presets_dir):
        """Test loading existing presets file."""
        presets_path = get_presets_path()
        test_presets = {
            "Default": {"brightness": 50},
            "Custom": {"brightness": 80},
        }
        with open(presets_path, "w") as f:
            json.dump(test_presets, f)

        loaded = load_presets()

        assert loaded == test_presets

    def test_handles_invalid_json(self, temp_presets_dir):
        """Test handling of corrupted JSON file."""
        presets_path = get_presets_path()
        with open(presets_path, "w") as f:
            f.write("invalid json {{{")

        presets = load_presets()

        # Should return default
        assert "Default" in presets


class TestSavePresets:
    """Tests for save_presets function."""

    def test_saves_to_file(self, temp_presets_dir):
        """Test saving presets to file."""
        test_presets = {"Test": {"brightness": 75}}
        save_presets(test_presets)

        presets_path = get_presets_path()
        with open(presets_path) as f:
            loaded = json.load(f)

        assert loaded == test_presets


class TestSavePreset:
    """Tests for save_preset function."""

    def test_saves_new_preset(self, temp_presets_dir):
        """Test saving a new preset."""
        save_preset("MyPreset", {"brightness": 90})

        presets = load_presets()
        assert "MyPreset" in presets
        assert presets["MyPreset"]["brightness"] == 90

    def test_overwrites_existing(self, temp_presets_dir):
        """Test overwriting existing preset."""
        save_preset("Test", {"brightness": 50})
        save_preset("Test", {"brightness": 100})

        presets = load_presets()
        assert presets["Test"]["brightness"] == 100


class TestDeletePreset:
    """Tests for delete_preset function."""

    def test_deletes_preset(self, temp_presets_dir):
        """Test deleting a preset."""
        save_preset("ToDelete", {"brightness": 50})
        assert "ToDelete" in load_presets()

        delete_preset("ToDelete")

        assert "ToDelete" not in load_presets()

    def test_cannot_delete_default(self, temp_presets_dir):
        """Test that Default preset cannot be deleted."""
        delete_preset("Default")

        presets = load_presets()
        assert "Default" in presets

    def test_deleting_nonexistent_is_safe(self, temp_presets_dir):
        """Test deleting non-existent preset doesn't error."""
        delete_preset("NonExistent")  # Should not raise


class TestGetPreset:
    """Tests for get_preset function."""

    def test_gets_existing_preset(self, temp_presets_dir):
        """Test getting an existing preset."""
        save_preset("Existing", {"brightness": 70})

        result = get_preset("Existing")

        assert result == {"brightness": 70}

    def test_returns_none_for_nonexistent(self, temp_presets_dir):
        """Test getting non-existent preset returns None."""
        result = get_preset("NonExistent")

        assert result is None


class TestListPresetNames:
    """Tests for list_preset_names function."""

    def test_lists_all_names(self, temp_presets_dir):
        """Test listing preset names."""
        save_preset("Alpha", {"brightness": 50})
        save_preset("Beta", {"brightness": 60})

        names = list_preset_names()

        assert "Default" in names
        assert "Alpha" in names
        assert "Beta" in names

    def test_returns_list(self, temp_presets_dir):
        """Test return type is list."""
        names = list_preset_names()
        assert isinstance(names, list)
