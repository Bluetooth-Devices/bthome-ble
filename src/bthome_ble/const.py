"""Constants for BTHome measurements."""
import dataclasses
from typing import Union

from sensor_state_data import BinarySensorDeviceClass, SensorLibrary, description

# Sensors with device classes that are available in Home Assistant
HOME_ASSISTANT_SENSOR_DEVICE_CLASSES = [
    "apparent_power",
    "aqi",
    "battery",
    "carbon_monoxide",
    "carbon_dioxide",
    "current",
    "date",
    "duration",
    "energy",
    "frequency",
    "gas",
    "humidity",
    "illuminance",
    "moisture",
    "monetary",
    "nitrogen_dioxide",
    "nitrogen_monoxide",
    "nitrous_oxide",
    "ozone",
    "pm1",
    "pm10",
    "pm25",
    "power_factor",
    "power",
    "pressure",
    "reactive_power",
    "signal_strength",
    "sulphur_dioxide",
    "temperature",
    "timestamp",
    "volatile_organic_compounds",
    "voltage",
]

# Additional BTHome sensors with device classes that
# are not available in Home Assistant
BTHOME_ADDITIONAL_SENSOR_DEVICE_CLASSES = [
    "mass",
    "dew_point",
    "count",
]

# Binary sensors with device classes that are available in Home Assistant
HOME_ASSISTANT_BINARY_SENSOR_DEVICE_CLASSES = [
    "battery",
    "battery_charging",
    "carbon_monoxide",
    "cold",
    "connectivity",
    "door",
    "garage_door",
    "gas",
    "heat",
    "light",
    "lock",
    "moisture",
    "motion",
    "moving",
    "occupancy",
    "opening",
    "plug",
    "power",
    "presence",
    "problem",
    "running",
    "safety",
    "smoke",
    "sound",
    "tamper",
    "update",
    "vibration",
    "window",
]

# Additional BTHome binary sensors with device classes that
# are not available in Home Assistant
BTHOME_ADDITIONAL_BINARY_SENSOR_DEVICE_CLASSES = [
    "generic",
]


@dataclasses.dataclass
class MeasTypes:
    meas_format: Union[
        description.BaseSensorDescription, description.BaseBinarySensorDescription
    ]
    factor: float = 1


MEAS_TYPES: dict[int, MeasTypes] = {
    0x01: MeasTypes(
        meas_format=SensorLibrary.BATTERY__PERCENTAGE,
        factor=1,
    ),
    0x02: MeasTypes(
        meas_format=SensorLibrary.TEMPERATURE__CELSIUS,
        factor=0.01,
    ),
    0x03: MeasTypes(
        meas_format=SensorLibrary.HUMIDITY__PERCENTAGE,
        factor=0.01,
    ),
    0x04: MeasTypes(
        meas_format=SensorLibrary.PRESSURE__MBAR,
        factor=0.01,
    ),
    0x05: MeasTypes(
        meas_format=SensorLibrary.LIGHT__LIGHT_LUX,
        factor=0.01,
    ),
    0x06: MeasTypes(
        meas_format=SensorLibrary.MASS__MASS_KILOGRAMS,
        factor=0.01,
    ),
    0x07: MeasTypes(
        meas_format=SensorLibrary.MASS__MASS_POUNDS,
        factor=0.01,
    ),
    0x08: MeasTypes(
        meas_format=SensorLibrary.DEW_POINT__TEMP_CELSIUS,
        factor=0.01,
    ),
    0x09: MeasTypes(
        meas_format=SensorLibrary.COUNT__NONE,
        factor=1,
    ),
    0x0A: MeasTypes(
        meas_format=SensorLibrary.ENERGY__ENERGY_KILO_WATT_HOUR,
        factor=0.001,
    ),
    0x0B: MeasTypes(
        meas_format=SensorLibrary.POWER__POWER_WATT,
        factor=0.01,
    ),
    0x0C: MeasTypes(
        meas_format=SensorLibrary.VOLTAGE__ELECTRIC_POTENTIAL_VOLT,
        factor=0.001,
    ),
    0x0D: MeasTypes(
        meas_format=SensorLibrary.PM25__CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        factor=1,
    ),
    0x0E: MeasTypes(
        meas_format=SensorLibrary.PM10__CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        factor=1,
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
        factor=1,
    ),
    0x13: MeasTypes(
        meas_format=(
            SensorLibrary.VOLATILE_ORGANIC_COMPOUNDS__CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
        ),
        factor=1,
    ),
    0x14: MeasTypes(
        meas_format=SensorLibrary.MOISTURE__PERCENTAGE,
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
            device_class=BinarySensorDeviceClass.UPDATE,
        )
    ),
    0x2D: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.VIBRATION,
        )
    ),
    0x2E: MeasTypes(
        meas_format=description.BaseBinarySensorDescription(
            device_class=BinarySensorDeviceClass.WINDOW,
        )
    ),
}
