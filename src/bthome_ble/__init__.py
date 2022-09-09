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

from .parser import BTHomeBluetoothDeviceData
from .const import (
    BTHOME_ADDITIONAL_BINARY_SENSOR_DEVICE_CLASSES,
    BTHOME_ADDITIONAL_SENSOR_DEVICE_CLASSES,
    HOME_ASSISTANT_BINARY_SENSOR_DEVICE_CLASSES,
    HOME_ASSISTANT_SENSOR_DEVICE_CLASSES,
)

BTHOME_SENSORS = (
    HOME_ASSISTANT_SENSOR_DEVICE_CLASSES + BTHOME_ADDITIONAL_SENSOR_DEVICE_CLASSES
)
BTHOME_BINARY_SENSORS = (
    HOME_ASSISTANT_BINARY_SENSOR_DEVICE_CLASSES
    + BTHOME_ADDITIONAL_BINARY_SENSOR_DEVICE_CLASSES
)

__version__ = "1.1.0"

__all__ = [
    "BTHOME_ADDITIONAL_BINARY_SENSOR_DEVICE_CLASSES",
    "BTHOME_ADDITIONAL_SENSOR_DEVICE_CLASSES",
    "BTHOME_BINARY_SENSORS",
    "BTHOME_SENSORS",
    "HOME_ASSISTANT_BINARY_SENSOR_DEVICE_CLASSES",
    "HOME_ASSISTANT_SENSOR_DEVICE_CLASSES",
    "BTHomeBluetoothDeviceData",
    "DeviceClass",
    "DeviceKey",
    "SensorDescription",
    "SensorDeviceInfo",
    "SensorUpdate",
    "SensorValue",
    "Units",
]
