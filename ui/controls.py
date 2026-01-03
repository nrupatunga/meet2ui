"""Reusable UI control builders."""

from typing import Callable

import dearpygui.dearpygui as dpg

from utils.constants import CONTROLS, LABELS


def create_slider(
    control_name: str,
    callback: Callable[[str, int], None],
    width: int = 200,
) -> int:
    """Create a labeled slider for a camera control.

    Args:
        control_name: Key from CONTROLS dict
        callback: Function(control_name, value) called on change
        width: Slider width in pixels

    Returns:
        DPG slider widget ID
    """
    min_val, max_val, default, _ = CONTROLS[control_name]
    label = LABELS.get(control_name, control_name)

    def on_change(sender, value):
        callback(control_name, int(value))

    with dpg.group(horizontal=True):
        dpg.add_text(f"{label:11}")
        slider_id = dpg.add_slider_int(
            default_value=default,
            min_value=min_val,
            max_value=max_val,
            width=width,
            callback=on_change,
            tag=f"slider_{control_name}",
        )
    return slider_id


def create_toggle(
    control_name: str,
    callback: Callable[[str, bool], None],
) -> int:
    """Create a labeled toggle/checkbox.

    Args:
        control_name: Key from CONTROLS dict
        callback: Function(control_name, enabled) called on change

    Returns:
        DPG checkbox widget ID
    """
    _, _, default, _ = CONTROLS[control_name]
    label = LABELS.get(control_name, control_name)

    def on_change(sender, value):
        callback(control_name, value)

    checkbox_id = dpg.add_checkbox(
        label=label,
        default_value=bool(default),
        callback=on_change,
        tag=f"toggle_{control_name}",
    )
    return checkbox_id


def create_button(
    label: str,
    callback: Callable[[], None],
    width: int = -1,
) -> int:
    """Create a simple button.

    Args:
        label: Button text
        callback: Function called on click
        width: Button width (-1 for auto)

    Returns:
        DPG button widget ID
    """

    def on_click(sender, data):
        callback()

    return dpg.add_button(label=label, callback=on_click, width=width)


def update_slider(control_name: str, value: int):
    """Update a slider's value without triggering callback."""
    tag = f"slider_{control_name}"
    if dpg.does_item_exist(tag):
        dpg.set_value(tag, value)


def update_toggle(control_name: str, value: bool):
    """Update a toggle's value without triggering callback."""
    tag = f"toggle_{control_name}"
    if dpg.does_item_exist(tag):
        dpg.set_value(tag, value)
