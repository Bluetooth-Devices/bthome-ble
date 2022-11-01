"""Constants for BTHome measurements."""
import dataclasses
from typing import Union

from sensor_state_data import BinarySensorDeviceClass, SensorLibrary, description

from .event import EventDeviceKeys


@dataclasses.dataclass
class MeasTypes:
    meas_format: Union[
        EventDeviceKeys,
        description.BaseBinarySensorDescription,
        description.BaseSensorDescription,
    ]
    data_length: int = 1
    data_format: str = "uint"
    factor: float = 1


MEAS_TYPES: dict[int, MeasTypes] = {
    0x01: MeasTypes(meas_format=SensorLibrary.BATTERY__PERCENTAGE),
    0x02: MeasTypes(
        meas_format=SensorLibrary.TEMPERATURE__CELSIUS,
        data_length=2,
        data_format="int",
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
        data_format="int",
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
}
