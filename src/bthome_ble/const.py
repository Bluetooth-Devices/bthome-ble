"""Constants for BTHome measurements."""
import dataclasses
from typing import Union

from sensor_state_data import (
    BaseDeviceClass,
    BinarySensorDeviceClass,
    SensorLibrary,
    Units,
    description,
)

from .event import EventDeviceKeys


@dataclasses.dataclass
class MeasTypes:
    meas_format: Union[
        EventDeviceKeys,
        description.BaseBinarySensorDescription,
        description.BaseSensorDescription,
    ]
    data_length: int = 1
    data_format: str = "unsigned_integer"
    factor: float = 1


class ExtendedSensorDeviceClass(BaseDeviceClass):
    """Device class for additional sensors (compared to sensor-state-data)."""

    # Raw hex data
    RAW = "raw"

    # Text
    TEXT = "text"

    # Volume storage
    VOLUME_STORAGE = "volume_storage"


class ExtendedSensorLibrary(SensorLibrary):
    """Sensor Library for additional sensors (compared to sensor-state-data)."""

    RAW__NONE = description.BaseSensorDescription(
        device_class=ExtendedSensorDeviceClass.RAW,
        native_unit_of_measurement=None,
    )

    TEXT__NONE = description.BaseSensorDescription(
        device_class=ExtendedSensorDeviceClass.TEXT,
        native_unit_of_measurement=None,
    )

    VOLUME_STORAGE__VOLUME_LITERS = description.BaseSensorDescription(
        device_class=ExtendedSensorDeviceClass.VOLUME_STORAGE,
        native_unit_of_measurement=Units.VOLUME_LITERS,
    )


MEAS_TYPES: dict[int, MeasTypes] = {
    0x00: MeasTypes(meas_format=SensorLibrary.PACKET_ID__NONE),
    0x01: MeasTypes(meas_format=SensorLibrary.BATTERY__PERCENTAGE),
    0x02: MeasTypes(
        meas_format=SensorLibrary.TEMPERATURE__CELSIUS,
        data_length=2,
        data_format="signed_integer",
        factor=0.01,
    ),
    0x03: MeasTypes(
        meas_format=SensorLibrary.HUMIDITY__PERCENTAGE,
        data_length=2,
        factor=0.01,
    ),
    0x04: MeasTypes(
        meas_format=SensorLibrary.PRESSURE__MBAR,
        data_length=3,
        factor=0.01,
    ),
    0x05: MeasTypes(
        meas_format=SensorLibrary.LIGHT__LIGHT_LUX,
        data_length=3,
        factor=0.01,
    ),
    0x06: MeasTypes(
        meas_format=SensorLibrary.MASS__MASS_KILOGRAMS,
        data_length=2,
        factor=0.01,
    ),
    0x07: MeasTypes(
        meas_format=SensorLibrary.MASS__MASS_POUNDS,
        data_length=2,
        factor=0.01,
    ),
    0x08: MeasTypes(
        meas_format=SensorLibrary.DEW_POINT__TEMP_CELSIUS,
        data_length=2,
        data_format="signed_integer",
        factor=0.01,
    ),
    0x09: MeasTypes(
        meas_format=SensorLibrary.COUNT__NONE,
        data_length=1,
    ),
    0x0A: MeasTypes(
        meas_format=SensorLibrary.ENERGY__ENERGY_KILO_WATT_HOUR,
        data_length=3,
        factor=0.001,
    ),
    0x0B: MeasTypes(
        meas_format=SensorLibrary.POWER__POWER_WATT,
        data_length=3,
        factor=0.01,
    ),
    0x0C: MeasTypes(
        meas_format=SensorLibrary.VOLTAGE__ELECTRIC_POTENTIAL_VOLT,
        data_length=2,
        factor=0.001,
    ),
    0x0D: MeasTypes(
        meas_format=SensorLibrary.PM25__CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        data_length=2,
    ),
    0x0E: MeasTypes(
        meas_format=SensorLibrary.PM10__CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        data_length=2,
    ),
    0x0F: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.GENERIC,
        ),
    ),
    0x10: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.POWER,
        ),
    ),
    0x11: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.OPENING,
        ),
    ),
    0x12: MeasTypes(
        meas_format=SensorLibrary.CO2__CONCENTRATION_PARTS_PER_MILLION,
        data_length=2,
    ),
    0x13: MeasTypes(
        meas_format=(
            SensorLibrary.VOLATILE_ORGANIC_COMPOUNDS__CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
        ),
        data_length=2,
    ),
    0x14: MeasTypes(
        meas_format=SensorLibrary.MOISTURE__PERCENTAGE,
        data_length=2,
        factor=0.01,
    ),
    0x15: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.BATTERY,
        )
    ),
    0x16: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        )
    ),
    0x17: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.CO,
        )
    ),
    0x18: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.COLD,
        )
    ),
    0x19: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.CONNECTIVITY,
        )
    ),
    0x1A: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.DOOR,
        )
    ),
    0x1B: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.GARAGE_DOOR,
        )
    ),
    0x1C: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.GAS,
        )
    ),
    0x1D: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.HEAT,
        )
    ),
    0x1E: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.LIGHT,
        )
    ),
    0x1F: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.LOCK,
        )
    ),
    0x20: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.MOISTURE,
        )
    ),
    0x21: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.MOTION,
        )
    ),
    0x22: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.MOVING,
        )
    ),
    0x23: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.OCCUPANCY,
        )
    ),
    0x24: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.PLUG,
        )
    ),
    0x25: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.PRESENCE,
        )
    ),
    0x26: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.PROBLEM,
        )
    ),
    0x27: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.RUNNING,
        )
    ),
    0x28: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.SAFETY,
        )
    ),
    0x29: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.SMOKE,
        )
    ),
    0x2A: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.SOUND,
        )
    ),
    0x2B: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.TAMPER,
        )
    ),
    0x2C: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.VIBRATION,
        )
    ),
    0x2D: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.WINDOW,
        )
    ),
    0x2E: MeasTypes(meas_format=SensorLibrary.HUMIDITY__PERCENTAGE),
    0x2F: MeasTypes(meas_format=SensorLibrary.MOISTURE__PERCENTAGE),
    0x3A: MeasTypes(meas_format=EventDeviceKeys.BUTTON),
    0x3C: MeasTypes(
        meas_format=EventDeviceKeys.DIMMER,
        data_length=2,
    ),
    0x3D: MeasTypes(
        meas_format=SensorLibrary.COUNT__NONE,
        data_length=2,
    ),
    0x3E: MeasTypes(
        meas_format=SensorLibrary.COUNT__NONE,
        data_length=4,
    ),
    0x3F: MeasTypes(
        meas_format=SensorLibrary.ROTATION__DEGREE,
        data_length=2,
        data_format="signed_integer",
        factor=0.1,
    ),
    0x40: MeasTypes(
        meas_format=SensorLibrary.DISTANCE__LENGTH_MILLIMETERS,
        data_length=2,
        factor=1,
    ),
    0x41: MeasTypes(
        meas_format=SensorLibrary.DISTANCE__LENGTH_METERS,
        data_length=2,
        factor=0.1,
    ),
    0x42: MeasTypes(
        meas_format=SensorLibrary.DURATION__TIME_SECONDS,
        data_length=3,
        factor=0.001,
    ),
    0x43: MeasTypes(
        meas_format=SensorLibrary.CURRENT__ELECTRIC_CURRENT_AMPERE,
        data_length=2,
        factor=0.001,
    ),
    0x44: MeasTypes(
        meas_format=SensorLibrary.SPEED__SPEED_METERS_PER_SECOND,
        data_length=2,
        factor=0.01,
    ),
    0x45: MeasTypes(
        meas_format=SensorLibrary.TEMPERATURE__CELSIUS,
        data_length=2,
        data_format="signed_integer",
        factor=0.1,
    ),
    0x46: MeasTypes(
        meas_format=SensorLibrary.UV_INDEX__NONE,
        data_length=1,
        factor=0.1,
    ),
    0x47: MeasTypes(
        meas_format=SensorLibrary.VOLUME__VOLUME_LITERS,
        data_length=2,
        factor=0.1,
    ),
    0x48: MeasTypes(
        meas_format=SensorLibrary.VOLUME__VOLUME_MILLILITERS,
        data_length=2,
    ),
    0x49: MeasTypes(
        meas_format=SensorLibrary.VOLUME_FLOW_RATE__VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
        data_length=2,
        factor=0.001,
    ),
    0x4A: MeasTypes(
        meas_format=SensorLibrary.VOLTAGE__ELECTRIC_POTENTIAL_VOLT,
        data_length=2,
        factor=0.1,
    ),
    0x4B: MeasTypes(
        meas_format=SensorLibrary.GAS__VOLUME_CUBIC_METERS,
        data_length=3,
        factor=0.001,
    ),
    0x4C: MeasTypes(
        meas_format=SensorLibrary.GAS__VOLUME_CUBIC_METERS,
        data_length=4,
        factor=0.001,
    ),
    0x4D: MeasTypes(
        meas_format=SensorLibrary.ENERGY__ENERGY_KILO_WATT_HOUR,
        data_length=4,
        factor=0.001,
    ),
    0x4E: MeasTypes(
        meas_format=SensorLibrary.VOLUME__VOLUME_LITERS,
        data_length=4,
        factor=0.001,
    ),
    0x4F: MeasTypes(
        meas_format=SensorLibrary.WATER__VOLUME_LITERS,
        data_length=4,
        factor=0.001,
    ),
    0x50: MeasTypes(
        meas_format=SensorLibrary.TIMESTAMP__NONE,
        data_length=4,
        data_format="timestamp",
    ),
    0x51: MeasTypes(
        meas_format=SensorLibrary.ACCELERATION__ACCELERATION_METERS_PER_SQUARE_SECOND,
        data_length=2,
        factor=0.001,
    ),
    0x52: MeasTypes(
        meas_format=SensorLibrary.GYROSCOPE__GYROSCOPE_DEGREES_PER_SECOND,
        data_length=2,
        factor=0.001,
    ),
    0x53: MeasTypes(
        meas_format=ExtendedSensorLibrary.TEXT__NONE,
        data_format="string",
    ),
    0x54: MeasTypes(
        meas_format=ExtendedSensorLibrary.RAW__NONE,
        data_format="raw",
    ),
    0x55: MeasTypes(
        meas_format=ExtendedSensorLibrary.VOLUME_STORAGE__VOLUME_LITERS,
        data_length=4,
        factor=0.001,
    ),
}
