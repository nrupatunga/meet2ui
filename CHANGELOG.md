# Changelog

All notable changes to Meet2UI will be documented in this file.

## [Unreleased]

### Changed
- Refactored to side-by-side layout (preview left, controls right)
- Window size: 748x350
- Preview: 480x270 (16:9 aspect ratio)
- Controls panel: 220px wide with sections for PTZ, Image, Focus
- Added camera device selector dropdown

## [0.1.0] - 2024-01-03

### Added
- Initial release
- Core modules:
  - `core/v4l2.py` - v4l2-ctl wrapper for camera controls
  - `core/camera.py` - OpenCV video capture and device detection
  - `core/tracker.py` - Face detection with Haar cascades and pan/tilt tracking
- UI modules:
  - `ui/app.py` - Main DearPyGui application window
  - `ui/preview.py` - Live video preview widget
  - `ui/controls.py` - Reusable slider/toggle/button builders
  - `ui/theme.py` - Dark theme styling
- Config:
  - `config/presets.py` - JSON preset save/load
- Camera controls:
  - PTZ: Zoom, Pan, Tilt
  - Image: Brightness, Contrast, Saturation, Sharpness
  - Focus: Autofocus toggle
- Face tracking mode with auto pan/tilt
- Preset system (save/load/reset)
- 72 unit tests with pytest
- Pre-commit hooks with ruff (linting + formatting)
