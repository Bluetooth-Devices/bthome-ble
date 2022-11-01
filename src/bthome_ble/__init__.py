"""Parser for BLE advertisements in BTHome format."""
from __future__ import annotations

from sensor_state_data import (
    BinarySensorDeviceClass,
    DeviceClass,
    DeviceKey,
    SensorDescription,
    SensorDeviceClass,
    SensorDeviceInfo,
    SensorUpdate,
    SensorValue,
    Units,
)

from .parser import BTHomeBluetoothDeviceData

__version__ = "2.0.0"

__all__ = [
    "BinarySensorDeviceClass",
    "BTHomeBluetoothDeviceData",
    "DeviceClass",
    "DeviceKey",
    "SensorDescription",
    "SensorDeviceClass",
    "SensorDeviceInfo",
    "SensorUpdate",
    "SensorValue",
    "Units",
]
