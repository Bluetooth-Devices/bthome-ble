"""Constants for BTHome measurements."""
import dataclasses
from typing import Union

from sensor_state_data import (
    BinarySensorDeviceClass,
    BaseDeviceClass,
    SensorLibrary,
    description,
)


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


class HomeAssistantSensorDeviceClass(BaseDeviceClass):
    """Device class for sensors supported in Home Assistant."""

    # apparent power (VA)
    APPARENT_POWER = "apparent_power"

    # Air Quality Index
    AQI = "aqi"

    # % of battery that is left
    BATTERY = "battery"

    # ppm (parts per million) Carbon Monoxide gas concentration
    CO = "carbon_monoxide"

    # ppm (parts per million) Carbon Dioxide gas concentration
    CO2 = "carbon_dioxide"

    # current (A)
    CURRENT = "current"

    # date (ISO8601)
    DATE = "date"

    # fixed duration (TIME_DAYS, TIME_HOURS, TIME_MINUTES, TIME_SECONDS)
    DURATION = "duration"

    # energy (Wh, kWh, MWh)
    ENERGY = "energy"

    # frequency (Hz, kHz, MHz, GHz)
    FREQUENCY = "frequency"

    # gas (m³ or ft³)
    GAS = "gas"

    # Relative humidity (%)
    HUMIDITY = "humidity"

    # current light level (lx/lm)
    ILLUMINANCE = "illuminance"

    # moisture (%)
    MOISTURE = "moisture"

    # Amount of money (currency)
    MONETARY = "monetary"

    # Amount of NO2 (µg/m³)
    NITROGEN_DIOXIDE = "nitrogen_dioxide"

    # Amount of NO (µg/m³)
    NITROGEN_MONOXIDE = "nitrogen_monoxide"

    # Amount of N2O  (µg/m³)
    NITROUS_OXIDE = "nitrous_oxide"

    # Amount of O3 (µg/m³)
    OZONE = "ozone"

    # Particulate matter <= 0.1 μm (µg/m³)
    PM1 = "pm1"

    # Particulate matter <= 10 μm (µg/m³)
    PM10 = "pm10"

    # Particulate matter <= 2.5 μm (µg/m³)
    PM25 = "pm25"

    # power factor (%)
    POWER_FACTOR = "power_factor"

    # power (W/kW)
    POWER = "power"

    # pressure (hPa/mbar)
    PRESSURE = "pressure"

    # reactive power (var)
    REACTIVE_POWER = "reactive_power"

    # signal strength (dB/dBm)
    SIGNAL_STRENGTH = "signal_strength"

    # Amount of SO2 (µg/m³)
    SULPHUR_DIOXIDE = "sulphur_dioxide"

    # temperature (C/F)
    TEMPERATURE = "temperature"

    # timestamp (ISO8601)
    TIMESTAMP = "timestamp"

    # Amount of VOC (µg/m³)
    VOLATILE_ORGANIC_COMPOUNDS = "volatile_organic_compounds"

    # voltage (V)
    VOLTAGE = "voltage"


class BTHomeAdditionalSensorDeviceClass(BaseDeviceClass):
    """Device class for sensors supported in BTHome but not available in Home Assistant."""

    # Mass
    MASS = "mass"

    # Dew Point
    DEW_POINT = "dew_point"

    # Count
    COUNT = "count"


class HomeAssistantBinarySensorDeviceClass(BaseDeviceClass):
    """Device class for binary sensors supported in Home Assistant."""

    # On means low, Off means normal
    BATTERY = "battery"

    # On means charging, Off means not charging
    BATTERY_CHARGING = "battery_charging"

    # On means carbon monoxide detected, Off means no carbon monoxide (clear)
    CO = "carbon_monoxide"

    # On means cold, Off means normal
    COLD = "cold"

    # On means connected, Off means disconnected
    CONNECTIVITY = "connectivity"

    # On means open, Off means closed
    DOOR = "door"

    # On means open, Off means closed
    GARAGE_DOOR = "garage_door"

    # On means gas detected, Off means no gas (clear)
    GAS = "gas"

    # On means hot, Off means normal
    HEAT = "heat"

    # On means light detected, Off means no light
    LIGHT = "light"

    # On means open (unlocked), Off means closed (locked)
    LOCK = "lock"

    # On means wet, Off means dry
    MOISTURE = "moisture"

    # On means motion detected, Off means no motion (clear)
    MOTION = "motion"

    # On means moving, Off means not moving (stopped)
    MOVING = "moving"

    # On means occupied, Off means not occupied (clear)
    OCCUPANCY = "occupancy"

    # On means open, Off means closed
    OPENING = "opening"

    # On means plugged in, Off means unplugged
    PLUG = "plug"

    # On means power detected, Off means no power
    POWER = "power"

    # On means home, Off means away
    PRESENCE = "presence"

    # On means problem detected, Off means no problem (OK)
    PROBLEM = "problem"

    # On means running, Off means not running
    RUNNING = "running"

    # On means unsafe, Off means safe
    SAFETY = "safety"

    # On means smoke detected, Off means no smoke (clear)
    SMOKE = "smoke"

    # On means sound detected, Off means no sound (clear)
    SOUND = "sound"

    # On means tampering detected, Off means no tampering (clear)
    TAMPER = "tamper"

    # On means update available, Off means up-to-date
    UPDATE = "update"

    # On means vibration detected, Off means no vibration
    VIBRATION = "vibration"

    # On means open, Off means closed
    WINDOW = "window"


class BTHomeAdditionalBinarySensorDeviceClass(BaseDeviceClass):
    """Device class for binary sensors supported in BTHome but not available in Home Assistant."""

    # On means On, Off means Off
    GENERIC = "generic"
