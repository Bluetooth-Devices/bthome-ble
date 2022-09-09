"""Tests for the parser of BLE advertisements in BTHome format."""
import logging
from unittest.mock import patch

import pytest
from bluetooth_sensor_state_data import BluetoothServiceInfo, DeviceClass, SensorUpdate
from sensor_state_data import (
    BinarySensorDescription,
    BinarySensorDeviceClass,
    BinarySensorValue,
    DeviceKey,
    SensorDescription,
    SensorDeviceInfo,
    SensorValue,
    Units,
)

from bthome_ble.parser import BTHomeBluetoothDeviceData, EncryptionScheme

KEY_BATTERY = DeviceKey(key="battery", device_id=None)
KEY_BINARY_GENERIC = DeviceKey(key="generic", device_id=None)
KEY_BINARY_OPENING = DeviceKey(key="opening", device_id=None)
KEY_BINARY_POWER = DeviceKey(key="power", device_id=None)
KEY_CO2 = DeviceKey(key="carbon_dioxide", device_id=None)
KEY_COUNT = DeviceKey(key="count", device_id=None)
KEY_DEW_POINT = DeviceKey(key="dew_point", device_id=None)
KEY_ENERGY = DeviceKey(key="energy", device_id=None)
KEY_HUMIDITY = DeviceKey(key="humidity", device_id=None)
KEY_ILLUMINANCE = DeviceKey(key="illuminance", device_id=None)
KEY_MASS = DeviceKey(key="mass", device_id=None)
KEY_MOISTURE = DeviceKey(key="moisture", device_id=None)
KEY_PM25 = DeviceKey(key="pm25", device_id=None)
KEY_PM10 = DeviceKey(key="pm10", device_id=None)
KEY_POWER = DeviceKey(key="power", device_id=None)
KEY_PRESSURE = DeviceKey(key="pressure", device_id=None)
KEY_SIGNAL_STRENGTH = DeviceKey(key="signal_strength", device_id=None)
KEY_TEMPERATURE = DeviceKey(key="temperature", device_id=None)
KEY_VOC = DeviceKey(key="volatile_organic_compounds", device_id=None)
KEY_VOLTAGE = DeviceKey(key="voltage", device_id=None)


@pytest.fixture(autouse=True)
def logging_config(caplog):
    caplog.set_level(logging.DEBUG)


@pytest.fixture(autouse=True)
def mock_platform():
    with patch("sys.platform") as p:
        p.return_value = "linux"
        yield p


def bytes_to_service_info(
    payload: bytes, local_name: str, address: str = "00:00:00:00:00:00"
) -> BluetoothServiceInfo:
    """Convert bytes to service info"""
    return BluetoothServiceInfo(
        name=local_name,
        address=address,
        rssi=-60,
        manufacturer_data={},
        service_data={"0000181c-0000-1000-8000-00805f9b34fb": payload},
        service_uuids=["0000181c-0000-1000-8000-00805f9b34fb"],
        source="",
    )


def bytes_to_encrypted_service_info(
    payload: bytes, local_name: str, address: str = "00:00:00:00:00:00"
) -> BluetoothServiceInfo:
    """Convert bytes to service info"""
    return BluetoothServiceInfo(
        name=local_name,
        address=address,
        rssi=-60,
        manufacturer_data={},
        service_data={"0000181e-0000-1000-8000-00805f9b34fb": payload},
        service_uuids=["0000181e-0000-1000-8000-00805f9b34fb"],
        source="",
    )


def test_can_create():
    BTHomeBluetoothDeviceData()


def test_encryption_key_needed():
    """Test that we can detect that an encryption key is needed."""
    data_string = b'\xfb\xa45\xe4\xd3\xc3\x12\xfb\x00\x11"3W\xd9\n\x99'
    advertisement = bytes_to_encrypted_service_info(
        payload=data_string,
        local_name="ATC_8D18B2",
        address="A4:C1:38:8D:18:B2",
    )

    device = BTHomeBluetoothDeviceData()

    assert device.supported(advertisement)
    assert device.encryption_scheme == EncryptionScheme.BTHOME_BINDKEY
    assert not device.bindkey_verified


def test_encryption_no_key_needed():
    """Test that we can detect that no encryption key is needed."""
    data_string = b"\x02\x00\x0c\x04\x04\x13\x8a\x01"
    advertisement = bytes_to_service_info(
        payload=data_string,
        local_name="ATC_8D18B2",
        address="A4:C1:38:8D:18:B2",
    )

    device = BTHomeBluetoothDeviceData()

    assert device.supported(advertisement)
    assert device.encryption_scheme == EncryptionScheme.NONE
    assert not device.bindkey_verified


def test_bindkey_wrong():
    """Test BTHome parser with wrong encryption key."""
    bindkey = "814aac74c4f17b6c1581e1ab87816b99"
    data_string = b'\xfb\xa45\xe4\xd3\xc3\x12\xfb\x00\x11"3W\xd9\n\x99'
    advertisement = bytes_to_encrypted_service_info(
        data_string,
        local_name="ATC_8D18B2",
        address="A4:C1:38:8D:18:B2",
    )

    device = BTHomeBluetoothDeviceData(bindkey=bytes.fromhex(bindkey))
    assert device.supported(advertisement)
    assert not device.bindkey_verified
    assert device.update(advertisement) == SensorUpdate(
        title="ATC 18B2",
        devices={
            None: SensorDeviceInfo(
                name="ATC 18B2",
                manufacturer="Xiaomi",
                model="BTHome sensor",
                sw_version="BTHome BLE (encrypted)",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_SIGNAL_STRENGTH: SensorValue(
                name="Signal Strength", device_key=KEY_SIGNAL_STRENGTH, native_value=-60
            ),
        },
    )


def test_bindkey_correct():
    """Test BTHome parser with correct encryption key."""
    bindkey = "231d39c1d7cc1ab1aee224cd096db932"
    data_string = b'\xfb\xa45\xe4\xd3\xc3\x12\xfb\x00\x11"3W\xd9\n\x99'
    advertisement = bytes_to_encrypted_service_info(
        data_string,
        local_name="TEST DEVICE",
        address="54:48:E6:8F:80:A5",
    )

    device = BTHomeBluetoothDeviceData(bindkey=bytes.fromhex(bindkey))
    assert device.supported(advertisement)
    assert device.bindkey_verified
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 80A5",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 80A5",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE (encrypted)",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_TEMPERATURE: SensorDescription(
                device_key=KEY_TEMPERATURE,
                device_class=DeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            KEY_HUMIDITY: SensorDescription(
                device_key=KEY_HUMIDITY,
                device_class=DeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_TEMPERATURE: SensorValue(
                device_key=KEY_TEMPERATURE, name="Temperature", native_value=25.06
            ),
            KEY_HUMIDITY: SensorValue(
                device_key=KEY_HUMIDITY, name="Humidity", native_value=50.55
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bindkey_verified_can_be_unset():
    """Test BTHome parser with wrong encryption key."""
    bindkey = "814aac74c4f17b6c1581e1ab87816b99"
    data_string = b'\xfb\xa45\xe4\xd3\xc3\x12\xfb\x00\x11"3W\xd9\n\x99'
    advertisement = bytes_to_encrypted_service_info(
        data_string,
        local_name="ATC_8D18B2",
        address="A4:C1:38:8D:18:B2",
    )

    device = BTHomeBluetoothDeviceData(bindkey=bytes.fromhex(bindkey))
    device.bindkey_verified = True

    assert device.supported(advertisement)
    assert not device.bindkey_verified


def test_bthome_temperature_humidity(caplog):
    """Test BTHome parser for temperature humidity reading without encryption."""
    data_string = b"#\x02\xca\t\x03\x03\xbf\x13"
    advertisement = bytes_to_service_info(
        data_string, local_name="ATC_8D18B2", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="ATC 18B2",
        devices={
            None: SensorDeviceInfo(
                name="ATC 18B2",
                manufacturer="Xiaomi",
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_TEMPERATURE: SensorDescription(
                device_key=KEY_TEMPERATURE,
                device_class=DeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            KEY_HUMIDITY: SensorDescription(
                device_key=KEY_HUMIDITY,
                device_class=DeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_TEMPERATURE: SensorValue(
                device_key=KEY_TEMPERATURE, name="Temperature", native_value=25.06
            ),
            KEY_HUMIDITY: SensorValue(
                device_key=KEY_HUMIDITY, name="Humidity", native_value=50.55
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_temperature_humidity_battery(caplog):
    """Test BTHome parser for temperature humidity battery reading."""
    data_string = b"\x02\x00\xa8#\x02]\t\x03\x03\xb7\x18\x02\x01]"
    advertisement = bytes_to_service_info(
        data_string, local_name="ATC_8D18B2", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="ATC 18B2",
        devices={
            None: SensorDeviceInfo(
                name="ATC 18B2",
                manufacturer="Xiaomi",
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_TEMPERATURE: SensorDescription(
                device_key=KEY_TEMPERATURE,
                device_class=DeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            KEY_HUMIDITY: SensorDescription(
                device_key=KEY_HUMIDITY,
                device_class=DeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_BATTERY: SensorDescription(
                device_key=KEY_BATTERY,
                device_class=DeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_TEMPERATURE: SensorValue(
                device_key=KEY_TEMPERATURE, name="Temperature", native_value=23.97
            ),
            KEY_HUMIDITY: SensorValue(
                device_key=KEY_HUMIDITY, name="Humidity", native_value=63.27
            ),
            KEY_BATTERY: SensorValue(
                device_key=KEY_BATTERY, name="Battery", native_value=93
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_pressure(caplog):
    """Test BTHome parser for pressure reading without encryption."""
    data_string = b"\x02\x00\x0c\x04\x04\x13\x8a\x01"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_PRESSURE: SensorDescription(
                device_key=KEY_PRESSURE,
                device_class=DeviceClass.PRESSURE,
                native_unit_of_measurement=Units.PRESSURE_MBAR,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_PRESSURE: SensorValue(
                device_key=KEY_PRESSURE, name="Pressure", native_value=1008.83
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_illuminance(caplog):
    """Test BTHome parser for illuminance reading without encryption."""
    data_string = b"\x04\x05\x13\x8a\x14"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_ILLUMINANCE: SensorDescription(
                device_key=KEY_ILLUMINANCE,
                device_class=DeviceClass.ILLUMINANCE,
                native_unit_of_measurement=Units.LIGHT_LUX,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_ILLUMINANCE: SensorValue(
                device_key=KEY_ILLUMINANCE, name="Illuminance", native_value=13460.67
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_mass_kilograms(caplog):
    """Test BTHome parser for mass reading in kilograms without encryption."""
    data_string = b"\x03\x06\x5E\x1F"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_MASS: SensorDescription(
                device_key=KEY_MASS,
                device_class=None,
                native_unit_of_measurement=Units.MASS_KILOGRAMS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_MASS: SensorValue(device_key=KEY_MASS, name="Mass", native_value=80.3),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_mass_pounds(caplog):
    """Test BTHome parser for mass reading in pounds without encryption."""
    data_string = b"\x03\x07\x3E\x1d"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_MASS: SensorDescription(
                device_key=KEY_MASS,
                device_class=None,
                native_unit_of_measurement=Units.MASS_POUNDS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_MASS: SensorValue(device_key=KEY_MASS, name="Mass", native_value=74.86),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_dew_point(caplog):
    """Test BTHome parser for dew point reading without encryption."""
    data_string = b"\x23\x08\xCA\x06"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_DEW_POINT: SensorDescription(
                device_key=KEY_DEW_POINT,
                device_class=None,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_DEW_POINT: SensorValue(
                device_key=KEY_DEW_POINT, name="Dew Point", native_value=17.38
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_count(caplog):
    """Test BTHome parser for counter reading without encryption."""
    data_string = b"\x02\x09\x60"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_COUNT: SensorDescription(
                device_key=KEY_COUNT,
                device_class=None,
                native_unit_of_measurement=None,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_COUNT: SensorValue(device_key=KEY_COUNT, name="Count", native_value=96),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_energy(caplog):
    """Test BTHome parser for energy reading without encryption."""
    data_string = b"\x04\n\x13\x8a\x14"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_ENERGY: SensorDescription(
                device_key=KEY_ENERGY,
                device_class=DeviceClass.ENERGY,
                native_unit_of_measurement=Units.ENERGY_KILO_WATT_HOUR,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_ENERGY: SensorValue(
                device_key=KEY_ENERGY, name="Energy", native_value=1346.067
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_power(caplog):
    """Test BTHome parser for power reading without encryption."""
    data_string = b"\x04\x0b\x02\x1b\x00"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_POWER: SensorDescription(
                device_key=KEY_POWER,
                device_class=DeviceClass.POWER,
                native_unit_of_measurement=Units.POWER_WATT,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_POWER: SensorValue(
                device_key=KEY_POWER, name="Power", native_value=69.14
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_voltage(caplog):
    """Test BThome parser for voltage reading without encryption."""
    data_string = b"\x03\x0c\x02\x0c"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_VOLTAGE: SensorDescription(
                device_key=KEY_VOLTAGE,
                device_class=DeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_VOLTAGE: SensorValue(
                device_key=KEY_VOLTAGE, name="Voltage", native_value=3.074
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_binary_sensor(caplog):
    """Test BTHome parser for binary sensor without device class, without encryption."""
    data_string = b"\x02\x0F\x01"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()

    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
        binary_entity_descriptions={
            KEY_BINARY_GENERIC: BinarySensorDescription(
                device_key=KEY_BINARY_GENERIC,
                device_class=None,
            ),
        },
        binary_entity_values={
            KEY_BINARY_GENERIC: BinarySensorValue(
                device_key=KEY_BINARY_GENERIC, name="Generic", native_value=True
            ),
        },
    )


def test_bthome_binary_sensor_power(caplog):
    """Test BTHome parser for binary sensor power without encryption."""
    data_string = b"\x02\x10\x01"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()

    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
        binary_entity_descriptions={
            KEY_BINARY_POWER: BinarySensorDescription(
                device_key=KEY_BINARY_POWER,
                device_class=BinarySensorDeviceClass.POWER,
            ),
        },
        binary_entity_values={
            KEY_BINARY_POWER: BinarySensorValue(
                device_key=KEY_BINARY_POWER, name="Power", native_value=True
            ),
        },
    )


def test_bthome_binary_sensor_opening(caplog):
    """Test BTHome parser for binary sensor opening without encryption."""
    data_string = b"\x02\x11\x00"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()

    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
        binary_entity_descriptions={
            KEY_BINARY_OPENING: BinarySensorDescription(
                device_key=KEY_BINARY_OPENING,
                device_class=BinarySensorDeviceClass.OPENING,
            ),
        },
        binary_entity_values={
            KEY_BINARY_OPENING: BinarySensorValue(
                device_key=KEY_BINARY_OPENING, name="Opening", native_value=False
            ),
        },
    )


def test_bthome_pm(caplog):
    """Test BTHome parser for PM2.5 and PM10 reading without encryption."""
    data_string = b"\x03\r\x12\x0c\x03\x0e\x02\x1c"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_PM25: SensorDescription(
                device_key=KEY_PM25,
                device_class=DeviceClass.PM25,
                native_unit_of_measurement=(
                    Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
                ),
            ),
            KEY_PM10: SensorDescription(
                device_key=KEY_PM10,
                device_class=DeviceClass.PM10,
                native_unit_of_measurement=(
                    Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
                ),
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_PM25: SensorValue(device_key=KEY_PM25, name="Pm25", native_value=3090),
            KEY_PM10: SensorValue(device_key=KEY_PM10, name="Pm10", native_value=7170),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_co2(caplog):
    """Test BTHome parser for CO2 reading without encryption."""
    data_string = b"\x03\x12\xe2\x04"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_CO2: SensorDescription(
                device_key=KEY_CO2,
                device_class=DeviceClass.CO2,
                native_unit_of_measurement=Units.CONCENTRATION_PARTS_PER_MILLION,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_CO2: SensorValue(
                device_key=KEY_CO2, name="Carbon Dioxide", native_value=1250
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_voc(caplog):
    """Test BTHome parser for VOC reading without encryption."""
    data_string = b"\x03\x133\x01"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 18B2",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_VOC: SensorDescription(
                device_key=KEY_VOC,
                device_class=DeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                native_unit_of_measurement=Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_VOC: SensorValue(
                device_key=KEY_VOC, name="Volatile Organic Compounds", native_value=307
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_moisture(caplog):
    """Test BTHome parser for moisture reading from b-parasite sensor."""
    data_string = b"\x03\x14\x02\x0c"
    advertisement = bytes_to_service_info(
        data_string, local_name="prst", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="b-parasite 18B2",
        devices={
            None: SensorDeviceInfo(
                name="b-parasite 18B2",
                manufacturer="b-parasite",
                model="BTHome sensor",
                sw_version="BTHome BLE",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_MOISTURE: SensorDescription(
                device_key=KEY_MOISTURE,
                device_class=DeviceClass.MOISTURE,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=DeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_MOISTURE: SensorValue(
                device_key=KEY_MOISTURE, name="Moisture", native_value=30.74
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )
