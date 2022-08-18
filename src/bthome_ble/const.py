"""Constants for BThome measurements."""
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
        meas_format=SensorLibrary.VOLATILE_ORGANIC_COMPOUNDS__CONCENTRATION_PARTS_PER_MILLION,
        factor=1,
    ),
}
