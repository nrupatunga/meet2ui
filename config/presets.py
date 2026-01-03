"""Preset management for camera settings."""

from __future__ import annotations

import json
from pathlib import Path

from utils.constants import CONTROLS


def get_presets_path() -> Path:
    """Get path to presets file."""
    config_dir = Path.home() / ".config" / "meet2ui"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "presets.json"


def get_defaults() -> dict[str, int]:
    """Get default values for all controls."""
    return {name: ctrl[2] for name, ctrl in CONTROLS.items()}


def load_presets() -> dict[str, dict[str, int]]:
    """Load all presets from disk."""
    path = get_presets_path()
    if not path.exists():
        return {"Default": get_defaults()}

    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {"Default": get_defaults()}


def save_presets(presets: dict[str, dict[str, int]]):
    """Save all presets to disk."""
    path = get_presets_path()
    with open(path, "w") as f:
        json.dump(presets, f, indent=2)


def save_preset(name: str, values: dict[str, int]):
    """Save a single preset."""
    presets = load_presets()
    presets[name] = values
    save_presets(presets)


def delete_preset(name: str):
    """Delete a preset (cannot delete Default)."""
    if name == "Default":
        return
    presets = load_presets()
    presets.pop(name, None)
    save_presets(presets)


def get_preset(name: str) -> dict[str, int] | None:
    """Get a specific preset's values."""
    presets = load_presets()
    return presets.get(name)


def list_preset_names() -> list[str]:
    """Get list of preset names."""
    return list(load_presets().keys())
