"""Event constants for BTHome measurements."""
from sensor_state_data.enum import StrEnum


class EventDeviceKeys(StrEnum):
    """Keys for devices that send events."""

    # Rocker switch
    SWITCH = "switch"

    # Dimmer
    DIMMER = "dimmer"

    # Button
    BUTTON = "button"


EVENT_TYPES: dict[int, str] = {
    0x01: "turn_on",
    0x02: "turn_off",
    0x03: "toggle",
    0x04: "press",
    0x05: "single_press",
    0x06: "double_press",
    0x07: "triple_press",
    0x08: "long_press",
    0x09: "long_single_press",
    0x0A: "long_double_press",
    0x0B: "long_triple_press",
    0x0C: "rotate_left",
    0x0D: "rotate_right",
}
