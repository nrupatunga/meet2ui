"""UI theme and styling for compact window."""

from __future__ import annotations

from pathlib import Path

import dearpygui.dearpygui as dpg


def setup_theme():
    """Create and apply compact dark theme."""
    with dpg.theme() as global_theme, dpg.theme_component(dpg.mvAll):
        # Compact spacing
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 8, 8)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 2)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 4, 4)
        dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 4, 2)

        # Rounded corners
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
        dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 4)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)

        # Colors - dark theme
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 35))
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (35, 35, 40))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (45, 45, 50))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (60, 60, 70))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (70, 70, 85))
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (100, 150, 200))
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (120, 170, 220))
        dpg.add_theme_color(dpg.mvThemeCol_Button, (55, 55, 65))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (70, 70, 85))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (85, 85, 100))
        dpg.add_theme_color(dpg.mvThemeCol_Tab, (40, 40, 48))
        dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (60, 60, 75))
        dpg.add_theme_color(dpg.mvThemeCol_TabActive, (70, 100, 140))
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (100, 180, 100))
        dpg.add_theme_color(dpg.mvThemeCol_Border, (60, 60, 70))

    dpg.bind_theme(global_theme)


def setup_font():
    """Setup TypeStarOCR font with fallback."""
    font_paths = [
        Path.home() / ".local/share/fonts/Typestar OCR Regular.otf",
        Path.home() / ".fonts/Typestar OCR Regular.otf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    ]

    font_path = None
    for path in font_paths:
        if path.exists():
            font_path = str(path)
            break

    if font_path:
        with dpg.font_registry():
            default_font = dpg.add_font(font_path, 14)
        dpg.bind_font(default_font)
