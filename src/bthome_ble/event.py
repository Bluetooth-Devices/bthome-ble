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


class EventTypes(StrEnum):
    """Device trigger event types."""

    # Turn on
    TURN_ON = "turn_on"

    # Turn off
    TURN_OFF = "turn_off"

    # Toggle
    TOGGLE = "toggle"

    # Button press
    PRESS = "press"

    # Single press
    SINGLE_PRESS = "single_press"

    # Double press
    DOUBLE_PRESS = "double_press"

    # Triple press
    TRIPLE_PRESS = "triple_press"

    # long single press
    LONG_PRESS = "long_single_press"

    # long single press
    LONG_SINGLE_PRESS = "long_single_press"

    # long double press
    LONG_DOUBLE_PRESS = "long_double_press"

    # Long triple press
    LONG_TRIPLE_PRESS = "long_triple_press"

    # Rotate left
    ROTATE_LEFT = "rotate_left"

    # Rotate right
    ROTATE_RIGHT = "rotate_right"


EVENT_TYPES: dict[int, EventTypes] = {
    0x01: EventTypes.TURN_ON,
    0x02: EventTypes.TURN_OFF,
    0x03: EventTypes.TOGGLE,
    0x04: EventTypes.PRESS,
    0x05: EventTypes.SINGLE_PRESS,
    0x06: EventTypes.DOUBLE_PRESS,
    0x07: EventTypes.TRIPLE_PRESS,
    0x08: EventTypes.LONG_PRESS,
    0x09: EventTypes.LONG_SINGLE_PRESS,
    0x0A: EventTypes.LONG_DOUBLE_PRESS,
    0x0B: EventTypes.LONG_TRIPLE_PRESS,
    0x0C: EventTypes.ROTATE_LEFT,
    0x0D: EventTypes.ROTATE_RIGHT,
}
