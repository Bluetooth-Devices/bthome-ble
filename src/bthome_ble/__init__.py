"""Parser for BLE advertisements in BTHome format."""
from __future__ import annotations

from sensor_state_data import (
    DeviceClass,
    DeviceKey,
    SensorDescription,
    SensorDeviceInfo,
    SensorUpdate,
    SensorValue,
    Units,
)

from .parser import BTHomeBluetoothDeviceData, BTHOME_BINARY_SENSOR_DEVICE_CLASS

__version__ = "1.1.0"

__all__ = [
    "BTHOME_BINARY_SENSOR_DEVICE_CLASS",
    "BTHomeBluetoothDeviceData",
    "DeviceClass",
    "DeviceKey",
    "SensorDescription",
    "SensorDeviceInfo",
    "SensorUpdate",
    "SensorValue",
    "Units",
]
