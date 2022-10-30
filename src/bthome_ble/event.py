"""Event constants for BTHome measurements."""
from __future__ import annotations

from sensor_state_data.enum import StrEnum


class EventDeviceKeys(StrEnum):
    """Keys for devices that send events."""

    # Rocker switch
    SWITCH = "switch"

    # Dimmer
    DIMMER = "dimmer"

    # Button
    BUTTON = "button"


BUTTON_EVENTS: dict[int, str | None] = {
    0x00: None,
    0x01: "press",
    0x02: "double_press",
    0x03: "triple_press",
    0x04: "long_press",
    0x05: "long_double_press",
    0x06: "long_triple_press",
}

DIMMER_EVENTS: dict[int, str | None] = {
    0x00: None,
    0x01: "rotate_left",
    0x02: "rotate_right",
}
