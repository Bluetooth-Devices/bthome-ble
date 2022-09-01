"""Constants for BTHome measurements."""
import dataclasses

from sensor_state_data import SensorLibrary, description


@dataclasses.dataclass
class MeasTypes:
    meas_format: description.BaseSensorDescription
    factor: float


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
}

HA_SUPPORTED_DEVICE_CLASSES = [
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
