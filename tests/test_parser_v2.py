"""Tests for the parser of BLE advertisements in BTHome V2 format."""
import logging
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from bluetooth_sensor_state_data import SensorUpdate
from home_assistant_bluetooth import BluetoothServiceInfoBleak
from sensor_state_data import (
    BinarySensorDescription,
    BinarySensorDeviceClass,
    BinarySensorValue,
    DeviceKey,
    Event,
    SensorDescription,
    SensorDeviceClass,
    SensorDeviceInfo,
    SensorValue,
    Units,
)

from bthome_ble.const import ExtendedSensorDeviceClass
from bthome_ble.parser import BTHomeBluetoothDeviceData, EncryptionScheme

ADVERTISEMENT_TIME = 1709331995.5181565

KEY_ACCELERATION = DeviceKey(key="acceleration", device_id=None)
KEY_BATTERY = DeviceKey(key="battery", device_id=None)
KEY_BINARY_GENERIC = DeviceKey(key="generic", device_id=None)
KEY_BINARY_OPENING = DeviceKey(key="opening", device_id=None)
KEY_BINARY_POWER = DeviceKey(key="power", device_id=None)
KEY_BINARY_WINDOW = DeviceKey(key="window", device_id=None)
KEY_BUTTON = DeviceKey(key="button", device_id=None)
KEY_CO2 = DeviceKey(key="carbon_dioxide", device_id=None)
KEY_DIMMER = DeviceKey(key="dimmer", device_id=None)
KEY_DISTANCE = DeviceKey(key="distance", device_id=None)
KEY_COUNT = DeviceKey(key="count", device_id=None)
KEY_CURRENT = DeviceKey(key="current", device_id=None)
KEY_DEW_POINT = DeviceKey(key="dew_point", device_id=None)
KEY_DURATION = DeviceKey(key="duration", device_id=None)
KEY_ENERGY = DeviceKey(key="energy", device_id=None)
KEY_GAS = DeviceKey(key="gas", device_id=None)
KEY_GYROSCOPE = DeviceKey(key="gyroscope", device_id=None)
KEY_HUMIDITY = DeviceKey(key="humidity", device_id=None)
KEY_ILLUMINANCE = DeviceKey(key="illuminance", device_id=None)
KEY_MASS = DeviceKey(key="mass", device_id=None)
KEY_MOISTURE = DeviceKey(key="moisture", device_id=None)
KEY_PACKET_ID = DeviceKey(key="packet_id", device_id=None)
KEY_PM25 = DeviceKey(key="pm25", device_id=None)
KEY_PM10 = DeviceKey(key="pm10", device_id=None)
KEY_POWER = DeviceKey(key="power", device_id=None)
KEY_PRESSURE = DeviceKey(key="pressure", device_id=None)
KEY_RAW = DeviceKey(key="raw", device_id=None)
KEY_ROTATION = DeviceKey(key="rotation", device_id=None)
KEY_SIGNAL_STRENGTH = DeviceKey(key="signal_strength", device_id=None)
KEY_SPEED = DeviceKey(key="speed", device_id=None)
KEY_TEMPERATURE = DeviceKey(key="temperature", device_id=None)
KEY_TEXT = DeviceKey(key="text", device_id=None)
KEY_TIMESTAMP = DeviceKey(key="timestamp", device_id=None)
KEY_UV_INDEX = DeviceKey(key="uv_index", device_id=None)
KEY_VOC = DeviceKey(key="volatile_organic_compounds", device_id=None)
KEY_VOLTAGE = DeviceKey(key="voltage", device_id=None)
KEY_VOLUME = DeviceKey(key="volume", device_id=None)
KEY_VOLUME_FLOW_RATE = DeviceKey(key="volume_flow_rate", device_id=None)
KEY_VOLUME_STORAGE = DeviceKey(key="volume_storage", device_id=None)
KEY_WATER = DeviceKey(key="water", device_id=None)


@pytest.fixture(autouse=True)
def logging_config(caplog):
    caplog.set_level(logging.DEBUG)


@pytest.fixture(autouse=True)
def mock_platform():
    with patch("sys.platform") as p:
        p.return_value = "linux"
        yield p


def bytes_to_service_info(
    payload: bytes,
    local_name: str,
    address: str = "00:00:00:00:00:00",
    time: float = ADVERTISEMENT_TIME,
) -> BluetoothServiceInfoBleak:
    """Convert bytes to service info"""
    return BluetoothServiceInfoBleak(
        name=local_name,
        address=address,
        rssi=-60,
        manufacturer_data={},
        service_data={"0000fcd2-0000-1000-8000-00805f9b34fb": payload},
        service_uuids=[],
        source="",
        device=None,
        advertisement=None,
        connectable=False,
        time=time,
    )


def test_can_create():
    BTHomeBluetoothDeviceData()


def test_encryption_key_needed():
    """Test that we can detect that an encryption key is needed."""
    data_string = (
        b"\x41\xd2\xfc\xef\xe5\x2e\xb2\x12\xd6\x00\x11\x22\x33\xbc\x38\xc9\x66"
    )
    advertisement = bytes_to_service_info(
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
    data_string = b"\x40\x04\x13\x8a\x01"
    advertisement = bytes_to_service_info(
        payload=data_string,
        local_name="ATC_8D18B2",
        address="A4:C1:38:8D:18:B2",
    )

    device = BTHomeBluetoothDeviceData()

    assert device.supported(advertisement)
    assert device.encryption_scheme == EncryptionScheme.NONE
    assert not device.bindkey_verified


def test_sleepy_device():
    """Test that we can detect that a device that doesn't update regularly."""
    data_string = b"\x44\x04\x13\x8a\x01"
    advertisement = bytes_to_service_info(
        payload=data_string,
        local_name="ATC_8D18B2",
        address="A4:C1:38:8D:18:B2",
    )

    device = BTHomeBluetoothDeviceData()

    assert device.supported(advertisement)
    assert device.sleepy_device


def test_no_sleepy_device():
    """Test that we can detect that a device that updates regularly."""
    data_string = b"\x40\x04\x13\x8a\x01"
    advertisement = bytes_to_service_info(
        payload=data_string,
        local_name="ATC_8D18B2",
        address="A4:C1:38:8D:18:B2",
    )

    device = BTHomeBluetoothDeviceData()

    assert device.supported(advertisement)
    assert not device.sleepy_device


def test_mac_as_name():
    """
    A sensor without a name gets its MAC address as name from BluetoothServiceInfo.
    Test that this sensor has BTHome sensor + identifier as its name.
    """
    data_string = b"\x40\x04\x13\x8a\x01"
    advertisement = bytes_to_service_info(
        payload=data_string,
        local_name="A4:C1:38:8D:18:B2",
        address="A4:C1:38:8D:18:B2",
    )

    device = BTHomeBluetoothDeviceData()

    assert device.supported(advertisement)
    assert device.update(advertisement) == SensorUpdate(
        title="BTHome sensor 18B2",
        devices={
            None: SensorDeviceInfo(
                name="BTHome sensor 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_PRESSURE: SensorDescription(
                device_key=KEY_PRESSURE,
                device_class=SensorDeviceClass.PRESSURE,
                native_unit_of_measurement=Units.PRESSURE_MBAR,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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


def test_has_incorrect_version():
    """Test that we can detect a non-existing version v7."""
    data_string = b"\xE1\x02\x00\x0c\x04\x04\x13\x8a\x01"
    advertisement = bytes_to_service_info(
        payload=data_string,
        local_name="A4:C1:38:8D:18:B2",
        address="A4:C1:38:8D:18:B2",
    )

    device = BTHomeBluetoothDeviceData()

    assert not device.supported(advertisement)


def test_bindkey_wrong():
    """Test BTHome parser with wrong encryption key."""
    bindkey = "814aac74c4f17b6c1581e1ab87816b99"
    data_string = (
        b"\x41\xd2\xfc\xef\xe5\x2e\xb2\x12\xd6\x00\x11\x22\x33\xbc\x38\xc9\x66"
    )
    advertisement = bytes_to_service_info(
        data_string,
        local_name="Test Sensor",
        address="A4:C1:38:8D:18:B2",
    )

    device = BTHomeBluetoothDeviceData(bindkey=bytes.fromhex(bindkey))
    assert device.supported(advertisement)
    assert not device.bindkey_verified
    assert device.update(advertisement) == SensorUpdate(
        title="Test Sensor 18B2",
        devices={
            None: SensorDeviceInfo(
                name="Test Sensor 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE v2 (encrypted)",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x41\xa4\x72\x66\xc9\x5f\x73\x00\x11\x22\x33\x78\x23\x72\x14"
    advertisement = bytes_to_service_info(
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
                sw_version="BTHome BLE v2 (encrypted)",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_TEMPERATURE: SensorDescription(
                device_key=KEY_TEMPERATURE,
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            KEY_HUMIDITY: SensorDescription(
                device_key=KEY_HUMIDITY,
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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


def test_bindkey_set_late():
    """Test BTHome parser with correct encryption key set after the device is created."""
    bindkey = "231d39c1d7cc1ab1aee224cd096db932"
    data_string = b"\x41\xa4\x72\x66\xc9\x5f\x73\x00\x11\x22\x33\x78\x23\x72\x14"
    advertisement = bytes_to_service_info(
        data_string,
        local_name="TEST DEVICE",
        address="54:48:E6:8F:80:A5",
    )

    device = BTHomeBluetoothDeviceData()
    device.set_bindkey(bytes.fromhex(bindkey))
    assert device.supported(advertisement)
    assert device.bindkey_verified
    assert device.update(advertisement) == SensorUpdate(
        title="TEST DEVICE 80A5",
        devices={
            None: SensorDeviceInfo(
                name="TEST DEVICE 80A5",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE v2 (encrypted)",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_TEMPERATURE: SensorDescription(
                device_key=KEY_TEMPERATURE,
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            KEY_HUMIDITY: SensorDescription(
                device_key=KEY_HUMIDITY,
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x41\xa4\x72\x66\xc9\x5f\x73\x00\x11\x22\x33\x78\x23\x72\x14"
    advertisement = bytes_to_service_info(
        data_string,
        local_name="ATC_8D18B2",
        address="A4:C1:38:8D:18:B2",
    )

    device = BTHomeBluetoothDeviceData(bindkey=bytes.fromhex(bindkey))
    device.bindkey_verified = True

    assert device.supported(advertisement)
    assert not device.bindkey_verified


def test_same_service_data(caplog):
    """Test BTHome parser with the same service data."""
    bindkey = "231d39c1d7cc1ab1aee224cd096db932"
    data_string = b"\x41\xe4\x45\xf3\xc9\x96\x2b\x33\x22\x11\x00\x6c\x7c\x45\x19"
    advertisement = bytes_to_service_info(
        data_string,
        local_name="TEST DEVICE",
        address="54:48:E6:8F:80:A5",
    )

    device = BTHomeBluetoothDeviceData(bindkey=bytes.fromhex(bindkey))
    assert device.supported(advertisement)
    assert device.bindkey_verified
    assert device.encryption_counter == 1122867

    data_string = b"\x41\xe4\x45\xf3\xc9\x96\x2b\x33\x22\x11\x00\x6c\x7c\x45\x19"
    advertisement = bytes_to_service_info(
        data_string,
        local_name="TEST DEVICE",
        address="54:48:E6:8F:80:A5",
    )
    assert device.supported(advertisement)
    assert device.bindkey_verified
    assert device.encryption_counter == 1122867
    assert (
        "TEST DEVICE 80A5 The service data is the same as the previous service data. "
        "Skipping this BLE advertisement." in caplog.text
    )


def test_increasing_encryption_counter(caplog):
    """Test BTHome parser with increasing encryption counter."""
    bindkey = "231d39c1d7cc1ab1aee224cd096db932"
    data_string = b"\x41\xe4\x45\xf3\xc9\x96\x2b\x33\x22\x11\x00\x6c\x7c\x45\x19"
    advertisement = bytes_to_service_info(
        data_string,
        local_name="TEST DEVICE",
        address="54:48:E6:8F:80:A5",
    )

    device = BTHomeBluetoothDeviceData(bindkey=bytes.fromhex(bindkey))
    assert device.supported(advertisement)
    assert device.bindkey_verified
    assert device.encryption_counter == 1122867

    data_string = b"\x41\x3e\x93\x2c\xc7\x17\x5f\x34\x22\x11\x00\x55\x38\x76\xaf"
    advertisement = bytes_to_service_info(
        data_string,
        local_name="TEST DEVICE",
        address="54:48:E6:8F:80:A5",
    )
    assert device.supported(advertisement)
    assert device.bindkey_verified
    assert device.encryption_counter == 1122868


def test_decreasing_encryption_counter(caplog):
    """Test BTHome parser with decreasing encryption counter."""
    bindkey = "231d39c1d7cc1ab1aee224cd096db932"
    data_string = b"\x41\xe4\x45\xf3\xc9\x96\x2b\x33\x22\x11\x00\x6c\x7c\x45\x19"
    advertisement = bytes_to_service_info(
        data_string,
        local_name="TEST DEVICE",
        address="54:48:E6:8F:80:A5",
    )

    device = BTHomeBluetoothDeviceData(bindkey=bytes.fromhex(bindkey))
    assert device.supported(advertisement)
    assert device.bindkey_verified
    assert device.encryption_counter == 1122867

    data_string = b"\x41\x72\x3d\x30\x35\xfb\x88\x32\x22\x11\x00\x9e\x74\x14\xc0"
    advertisement = bytes_to_service_info(
        data_string,
        local_name="TEST DEVICE",
        address="54:48:E6:8F:80:A5",
    )
    assert device.supported(advertisement)
    assert device.bindkey_verified
    # encryption counter should not be updated as it is lower
    assert device.encryption_counter == 1122867
    assert (
        "TEST DEVICE 80A5 The new encryption counter (1122866) is lower than the previous value "
        "(1122867). The data might be compromised. BLE advertisement will be skipped."
        in caplog.text
    )


def test_reset_encryption_counter(caplog):
    """Test BTHome parser during reset of the encryption counter."""
    bindkey = "231d39c1d7cc1ab1aee224cd096db932"
    data_string = b"\x41\xba\x0d\xb0\x7a\xee\xf6\xff\xff\xff\xff\x21\xfd\x46\x00"
    advertisement = bytes_to_service_info(
        data_string,
        local_name="TEST DEVICE",
        address="54:48:E6:8F:80:A5",
    )

    device = BTHomeBluetoothDeviceData(bindkey=bytes.fromhex(bindkey))
    assert device.supported(advertisement)
    assert device.bindkey_verified
    assert device.encryption_counter == 4294967295

    data_string = b"\x41\xde\x40\xb5\x0e\x67\x66\x00\x00\x00\x00\xd7\xcb\x95\xde"
    advertisement = bytes_to_service_info(
        data_string,
        local_name="TEST DEVICE",
        address="54:48:E6:8F:80:A5",
    )
    assert device.supported(advertisement)
    assert device.bindkey_verified
    assert device.encryption_counter == 0


def test_too_short_encryption_advertisement(caplog):
    """Test BTHome parser with a too short encrypted advertisement."""
    bindkey = "231d39c1d7cc1ab1aee224cd096db932"
    data_string = b"\x41\xba\x0d\xb0\x7a\xee\xf6\x00"
    advertisement = bytes_to_service_info(
        data_string,
        local_name="TEST DEVICE",
        address="54:48:E6:8F:80:A5",
    )

    device = BTHomeBluetoothDeviceData(bindkey=bytes.fromhex(bindkey))
    assert device.supported(advertisement)
    assert "TEST DEVICE 80A5 Invalid data length (for decryption), adv:" in caplog.text


def test_identical_packet_id(caplog):
    """Test BTHome parser for skipping BLE advertisement with identical or older packet id."""
    # 1st advertisement
    data_string = b"\x40\x00\x09"
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
                model="Temperature/Humidity sensor",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_PACKET_ID: SensorDescription(
                device_key=KEY_PACKET_ID,
                device_class=SensorDeviceClass.PACKET_ID,
                native_unit_of_measurement=None,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_PACKET_ID: SensorValue(
                device_key=KEY_PACKET_ID, name="Packet Id", native_value=9
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )
    assert device.packet_id == 9
    assert "ATC 18B2 First packet, not filtering packet_id 9" in caplog.text

    # advertisement with the same packet id
    device.update(advertisement)
    assert device.packet_id == 9
    assert (
        "ATC 18B2 New packet_id 9 indicates an older packet (previous packet_id 9). "
        "BLE advertisement will be skipped" in caplog.text
    )

    # advertisement packet id decreased by one, should be dropped
    data_string_2 = b"\x40\x00\x08"
    advertisement_2 = bytes_to_service_info(
        data_string_2, local_name="ATC_8D18B2", address="A4:C1:38:8D:18:B2"
    )

    assert device.update(advertisement_2)
    assert device.packet_id == 9
    assert (
        "ATC 18B2 New packet_id 8 indicates an older packet (previous packet_id 9). "
        "BLE advertisement will be skipped" in caplog.text
    )

    # advertisement more than 4 seconds from last advertisement
    advertisement_3 = bytes_to_service_info(
        data_string,
        local_name="ATC_8D18B2",
        address="A4:C1:38:8D:18:B2",
        time=ADVERTISEMENT_TIME + 5,
    )

    assert device.update(advertisement_3)
    assert device.packet_id == 9
    assert (
        "ATC 18B2 Not filtering packet_id, more than 4 seconds since last packet."
        in caplog.text
    )


def test_increasing_packet_id(caplog):
    """Test BTHome parser for BLE advertisement with increasing packet id."""
    # start with 189
    data_string = b"\x40\x00\xBD"
    advertisement = bytes_to_service_info(
        data_string, local_name="ATC_8D18B2", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    device.update(advertisement)
    assert device.packet_id == 189

    # increase by 1 to 190
    data_string_2 = b"\x40\x00\xBE"
    advertisement_2 = bytes_to_service_info(
        data_string_2, local_name="ATC_8D18B2", address="A4:C1:38:8D:18:B2"
    )

    assert device.update(advertisement_2) == SensorUpdate(
        title="ATC 18B2",
        devices={
            None: SensorDeviceInfo(
                name="ATC 18B2",
                manufacturer="Xiaomi",
                model="Temperature/Humidity sensor",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_PACKET_ID: SensorDescription(
                device_key=KEY_PACKET_ID,
                device_class=SensorDeviceClass.PACKET_ID,
                native_unit_of_measurement=None,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_PACKET_ID: SensorValue(
                device_key=KEY_PACKET_ID, name="Packet Id", native_value=190
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )
    assert device.packet_id == 190

    # increast by 63 to 253
    data_string_3 = b"\x40\x00\xFD"
    advertisement_3 = bytes_to_service_info(
        data_string_3, local_name="ATC_8D18B2", address="A4:C1:38:8D:18:B2"
    )

    device.update(advertisement_3)
    assert device.packet_id == 253

    # increast by 50, rollover to 47
    data_string_4 = b"\x40\x00\x2F"
    advertisement_4 = bytes_to_service_info(
        data_string_4, local_name="ATC_8D18B2", address="A4:C1:38:8D:18:B2"
    )

    device.update(advertisement_4)
    assert device.packet_id == 47


def test_bthome_wrong_object_id(caplog):
    """Test BTHome parser for a non-existing Object ID xFE."""
    data_string = b"\x40\xFE\xca\x09"
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
                model="Temperature/Humidity sensor",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_battery_wrong_object_id_humidity(caplog):
    """
    Test BTHome parser for battery, wrong object id and humidity reading.
    Should only return the battery reading, as humidity is after wrong object id.
    """
    data_string = b"\x40\x01\x5d\xfe\x5d\x09\x03\xb7\x18"
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
                model="Temperature/Humidity sensor",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_BATTERY: SensorDescription(
                device_key=KEY_BATTERY,
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_BATTERY: SensorValue(
                device_key=KEY_BATTERY, name="Battery", native_value=93
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_with_mac(caplog):
    """Test BTHome parser for pressure reading mac address in payload."""
    data_string = b"\x42\xb2\x18\x8d\x38\xc1\xa4\x04\x13\x8a\x01"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_PRESSURE: SensorDescription(
                device_key=KEY_PRESSURE,
                device_class=SensorDeviceClass.PRESSURE,
                native_unit_of_measurement=Units.PRESSURE_MBAR,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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


def test_bthome_with_mac_encrypted():
    """Test BTHome parser with mac address in payload plus encryption."""
    bindkey = "231d39c1d7cc1ab1aee224cd096db932"
    data = b"\x43\xa5\x80\x8f\xe6\x48\x54\xf1\x96\xc0\x6f\xfb\x49\x00\x11\x22\x33\xf0\x8e\xcb\xde"
    advertisement = bytes_to_service_info(
        data,
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
                sw_version="BTHome BLE v2 (encrypted)",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_TEMPERATURE: SensorDescription(
                device_key=KEY_TEMPERATURE,
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            KEY_HUMIDITY: SensorDescription(
                device_key=KEY_HUMIDITY,
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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


def test_bthome_temperature_humidity(caplog):
    """Test BTHome parser for temperature humidity reading without encryption."""
    data_string = b"\x40\x02\xca\x09\x03\xbf\x13"
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
                model="Temperature/Humidity sensor",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_TEMPERATURE: SensorDescription(
                device_key=KEY_TEMPERATURE,
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            KEY_HUMIDITY: SensorDescription(
                device_key=KEY_HUMIDITY,
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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


def test_bthome_packet_id_temperature_humidity_battery(caplog):
    """Test BTHome parser for packet_id, temperature, humidity and battery reading."""
    data_string = b"\x40\x00\x09\x01\x5d\x02\x5d\x09\x03\xb7\x18"
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
                model="Temperature/Humidity sensor",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_PACKET_ID: SensorDescription(
                device_key=KEY_PACKET_ID,
                device_class=SensorDeviceClass.PACKET_ID,
                native_unit_of_measurement=None,
            ),
            KEY_TEMPERATURE: SensorDescription(
                device_key=KEY_TEMPERATURE,
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            KEY_HUMIDITY: SensorDescription(
                device_key=KEY_HUMIDITY,
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_BATTERY: SensorDescription(
                device_key=KEY_BATTERY,
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_PACKET_ID: SensorValue(
                device_key=KEY_PACKET_ID, name="Packet Id", native_value=9
            ),
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
    data_string = b"\x40\x04\x13\x8a\x01"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_PRESSURE: SensorDescription(
                device_key=KEY_PRESSURE,
                device_class=SensorDeviceClass.PRESSURE,
                native_unit_of_measurement=Units.PRESSURE_MBAR,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x40\x05\x13\x8a\x14"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_ILLUMINANCE: SensorDescription(
                device_key=KEY_ILLUMINANCE,
                device_class=SensorDeviceClass.ILLUMINANCE,
                native_unit_of_measurement=Units.LIGHT_LUX,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x40\x06\x5E\x1F"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_MASS: SensorDescription(
                device_key=KEY_MASS,
                device_class=SensorDeviceClass.MASS,
                native_unit_of_measurement=Units.MASS_KILOGRAMS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x40\x07\x3E\x1d"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_MASS: SensorDescription(
                device_key=KEY_MASS,
                device_class=SensorDeviceClass.MASS,
                native_unit_of_measurement=Units.MASS_POUNDS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x40\x08\xCA\x06"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_DEW_POINT: SensorDescription(
                device_key=KEY_DEW_POINT,
                device_class=SensorDeviceClass.DEW_POINT,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x40\x09\x60"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_COUNT: SensorDescription(
                device_key=KEY_COUNT,
                device_class=SensorDeviceClass.COUNT,
                native_unit_of_measurement=None,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x40\x0a\x13\x8a\x14"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_ENERGY: SensorDescription(
                device_key=KEY_ENERGY,
                device_class=SensorDeviceClass.ENERGY,
                native_unit_of_measurement=Units.ENERGY_KILO_WATT_HOUR,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x40\x0b\x02\x1b\x00"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_POWER: SensorDescription(
                device_key=KEY_POWER,
                device_class=SensorDeviceClass.POWER,
                native_unit_of_measurement=Units.POWER_WATT,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x40\x0c\x02\x0c"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_VOLTAGE: SensorDescription(
                device_key=KEY_VOLTAGE,
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x40\x0F\x01"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
                device_class=BinarySensorDeviceClass.GENERIC,
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
    data_string = b"\x40\x10\x01"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x40\x11\x00"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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


def test_bthome_binary_sensor_window(caplog):
    """Test BTHome parser for binary sensor window without encryption."""
    data_string = b"\x40\x2D\x01"
    advertisement = bytes_to_service_info(
        data_string, local_name="SBDW-002C", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()

    assert device.update(advertisement) == SensorUpdate(
        title="Shelly BLU Door/Window 18B2",
        devices={
            None: SensorDeviceInfo(
                name="Shelly BLU Door/Window 18B2",
                manufacturer="Shelly",
                model="BLU Door/Window",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
        binary_entity_descriptions={
            KEY_BINARY_WINDOW: BinarySensorDescription(
                device_key=KEY_BINARY_WINDOW,
                device_class=BinarySensorDeviceClass.WINDOW,
            ),
        },
        binary_entity_values={
            KEY_BINARY_WINDOW: BinarySensorValue(
                device_key=KEY_BINARY_WINDOW, name="Window", native_value=True
            ),
        },
    )


def test_bthome_pm(caplog):
    """Test BTHome parser for PM2.5 and PM10 reading without encryption."""
    data_string = b"\x40\x0d\x12\x0c\x0e\x02\x1c"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_PM25: SensorDescription(
                device_key=KEY_PM25,
                device_class=SensorDeviceClass.PM25,
                native_unit_of_measurement=(
                    Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
                ),
            ),
            KEY_PM10: SensorDescription(
                device_key=KEY_PM10,
                device_class=SensorDeviceClass.PM10,
                native_unit_of_measurement=(
                    Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
                ),
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x40\x12\xe2\x04"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_CO2: SensorDescription(
                device_key=KEY_CO2,
                device_class=SensorDeviceClass.CO2,
                native_unit_of_measurement=Units.CONCENTRATION_PARTS_PER_MILLION,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x40\x133\x01"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_VOC: SensorDescription(
                device_key=KEY_VOC,
                device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                native_unit_of_measurement=Units.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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
    data_string = b"\x40\x14\x02\x0c"
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
                model="Plant sensor",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_MOISTURE: SensorDescription(
                device_key=KEY_MOISTURE,
                device_class=SensorDeviceClass.MOISTURE,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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


def test_bthome_event_button_long_press(caplog):
    """Test BTHome parser for an event of a long press on a button without encryption."""
    data_string = b"\x40\x3A\x04"
    advertisement = bytes_to_service_info(
        data_string, local_name="SBBT-002C", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()

    assert device.update(advertisement) == SensorUpdate(
        title="Shelly BLU Button1 18B2",
        devices={
            None: SensorDeviceInfo(
                name="Shelly BLU Button1 18B2",
                manufacturer="Shelly",
                model="BLU Button1",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
        events={
            KEY_BUTTON: Event(
                device_key=KEY_BUTTON,
                name="Button",
                event_type="long_press",
                event_properties=None,
            ),
        },
    )


def test_bthome_event_triple_button_device(caplog):
    """
    Test BTHome parser for an event of a triple button device where
    the 2nd button is pressed and the 3rd button is triple pressed.
    """
    data_string = b"\x40\x3A\x00\x3A\x01\x3A\x03"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
        events={
            DeviceKey(key="button_2", device_id=None): Event(
                device_key=DeviceKey(key="button_2", device_id=None),
                name="Button 2",
                event_type="press",
                event_properties=None,
            ),
            DeviceKey(key="button_3", device_id=None): Event(
                device_key=DeviceKey(key="button_3", device_id=None),
                name="Button 3",
                event_type="triple_press",
                event_properties=None,
            ),
        },
    )


def test_bthome_event_dimmer_rotate_left_3_steps(caplog):
    """Test BTHome parser for an event rotating a dimmer 3 steps left."""
    data_string = b"\x40\x3C\x01\x03"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
        events={
            KEY_DIMMER: Event(
                device_key=KEY_DIMMER,
                name="Dimmer",
                event_type="rotate_left",
                event_properties={"steps": 3},
            ),
        },
    )


def test_bthome_rotation(caplog):
    """Test BTHome parser for rotation."""
    data_string = b"\x40\x3F\x02\x0c"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_ROTATION: SensorDescription(
                device_key=KEY_ROTATION,
                device_class=SensorDeviceClass.ROTATION,
                native_unit_of_measurement=Units.DEGREE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_ROTATION: SensorValue(
                device_key=KEY_ROTATION, name="Rotation", native_value=307.4
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_invalid_button_event(caplog):
    """Test BTHome parser for an invalid button event."""
    data_string = b"\x40\x3A\xFE"
    advertisement = bytes_to_service_info(
        data_string, local_name="SBBT-002C", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()

    assert device.update(advertisement) == SensorUpdate(
        title="Shelly BLU Button1 18B2",
        devices={
            None: SensorDeviceInfo(
                name="Shelly BLU Button1 18B2",
                manufacturer="Shelly",
                model="BLU Button1",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
        events={},
    )


def test_encrypted_shelly_blu_button_event(caplog):
    """Test BTHome parser for an encrypted shelly blu button event."""
    bindkey = "90bffd73cb6b26ef58a7a8eba9232036"
    data_string = b"\x45\x0a\xeb\x84\x46\x7f\x85\xba\x01\x00\x00\x31\x88\x78\x8c"

    advertisement = bytes_to_service_info(
        data_string,
        local_name="SBBT-002C",
        address="B4:35:22:F5:3D:A4",
    )

    device = BTHomeBluetoothDeviceData(bindkey=bytes.fromhex(bindkey))
    assert device.supported(advertisement)
    assert device.bindkey_verified


def test_bthome_distance_millimeters(caplog):
    """Test BTHome parser for distance in millimeters."""
    data_string = b"\x40\x40\x0C\x00"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_DISTANCE: SensorDescription(
                device_key=KEY_DISTANCE,
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=Units.LENGTH_MILLIMETERS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_DISTANCE: SensorValue(
                device_key=KEY_DISTANCE, name="Distance", native_value=12
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_distance_meters(caplog):
    """Test BTHome parser for distance in meters."""
    data_string = b"\x40\x41\x4E\x00"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_DISTANCE: SensorDescription(
                device_key=KEY_DISTANCE,
                device_class=SensorDeviceClass.DISTANCE,
                native_unit_of_measurement=Units.LENGTH_METERS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_DISTANCE: SensorValue(
                device_key=KEY_DISTANCE, name="Distance", native_value=7.8
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_duration(caplog):
    """Test BTHome parser for duration in seconds."""
    data_string = b"\x40\x42\x4E\x34\x00"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_DURATION: SensorDescription(
                device_key=KEY_DURATION,
                device_class=SensorDeviceClass.DURATION,
                native_unit_of_measurement=Units.TIME_SECONDS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_DURATION: SensorValue(
                device_key=KEY_DURATION, name="Duration", native_value=13.39
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_current(caplog):
    """Test BTHome parser for current in VA."""
    data_string = b"\x40\x43\x4E\x34"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_CURRENT: SensorDescription(
                device_key=KEY_CURRENT,
                device_class=SensorDeviceClass.CURRENT,
                native_unit_of_measurement=Units.ELECTRIC_CURRENT_AMPERE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_CURRENT: SensorValue(
                device_key=KEY_CURRENT, name="Current", native_value=13.39
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_speed(caplog):
    """Test BTHome parser for speed in m/s."""
    data_string = b"\x40\x44\x4E\x34"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SPEED: SensorDescription(
                device_key=KEY_SPEED,
                device_class=SensorDeviceClass.SPEED,
                native_unit_of_measurement=Units.SPEED_METERS_PER_SECOND,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_SPEED: SensorValue(
                device_key=KEY_SPEED, name="Speed", native_value=133.9
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_temperature_2(caplog):
    """Test BTHome parser for temperature with one digit."""
    data_string = b"\x40\x45\x11\x01"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_TEMPERATURE: SensorDescription(
                device_key=KEY_TEMPERATURE,
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_TEMPERATURE: SensorValue(
                device_key=KEY_TEMPERATURE, name="Temperature", native_value=27.3
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_uv_index(caplog):
    """Test BTHome parser for UV index."""
    data_string = b"\x40\x46\x32"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_UV_INDEX: SensorDescription(
                device_key=KEY_UV_INDEX,
                device_class=SensorDeviceClass.UV_INDEX,
                native_unit_of_measurement=None,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_UV_INDEX: SensorValue(
                device_key=KEY_UV_INDEX, name="Uv Index", native_value=5.0
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_volume_liters(caplog):
    """Test BTHome parser for Volume in Liters."""
    data_string = b"\x40\x47\x87\x56"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_VOLUME: SensorDescription(
                device_key=KEY_VOLUME,
                device_class=SensorDeviceClass.VOLUME,
                native_unit_of_measurement=Units.VOLUME_LITERS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_VOLUME: SensorValue(
                device_key=KEY_VOLUME, name="Volume", native_value=2215.1
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_volume_milliliters(caplog):
    """Test BTHome parser for Volume in milliliters."""
    data_string = b"\x40\x48\xDC\x87"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_VOLUME: SensorDescription(
                device_key=KEY_VOLUME,
                device_class=SensorDeviceClass.VOLUME,
                native_unit_of_measurement=Units.VOLUME_MILLILITERS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_VOLUME: SensorValue(
                device_key=KEY_VOLUME, name="Volume", native_value=34780
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_volume_flow_rate(caplog):
    """Test BTHome parser for Volume flow rate in m3 per hour."""
    data_string = b"\x40\x49\xDC\x87"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_VOLUME_FLOW_RATE: SensorDescription(
                device_key=KEY_VOLUME_FLOW_RATE,
                device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
                native_unit_of_measurement=Units.VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_VOLUME_FLOW_RATE: SensorValue(
                device_key=KEY_VOLUME_FLOW_RATE,
                name="Volume Flow Rate",
                native_value=34.780,
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_voltage_2(caplog):
    """Test BThome parser for voltage reading without encryption."""
    data_string = b"\x40\x4a\x02\x0c"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_VOLTAGE: SensorDescription(
                device_key=KEY_VOLTAGE,
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_VOLTAGE: SensorValue(
                device_key=KEY_VOLTAGE, name="Voltage", native_value=307.4
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_gas(caplog):
    """Test BTHome parser for gas reading without encryption."""
    data_string = b"\x40\x4b\x13\x8a\x14"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_GAS: SensorDescription(
                device_key=KEY_GAS,
                device_class=SensorDeviceClass.GAS,
                native_unit_of_measurement=Units.VOLUME_CUBIC_METERS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_GAS: SensorValue(device_key=KEY_GAS, name="Gas", native_value=1346.067),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_gas_2(caplog):
    """Test BTHome parser for gas reading without encryption."""
    data_string = b"\x40\x4c\x41\x01\x8a\x01"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_GAS: SensorDescription(
                device_key=KEY_GAS,
                device_class=SensorDeviceClass.GAS,
                native_unit_of_measurement=Units.VOLUME_CUBIC_METERS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_GAS: SensorValue(
                device_key=KEY_GAS, name="Gas", native_value=25821.505
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_energy_2(caplog):
    """Test BTHome parser for energy reading without encryption."""
    data_string = b"\x40\x4d\x12\x13\x8a\x14"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_ENERGY: SensorDescription(
                device_key=KEY_ENERGY,
                device_class=SensorDeviceClass.ENERGY,
                native_unit_of_measurement=Units.ENERGY_KILO_WATT_HOUR,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_ENERGY: SensorValue(
                device_key=KEY_ENERGY, name="Energy", native_value=344593.17
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_volume_liters_2(caplog):
    """Test BTHome parser for Volume in Liters."""
    data_string = b"\x40\x4e\x87\x56\x2a\x01"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_VOLUME: SensorDescription(
                device_key=KEY_VOLUME,
                device_class=SensorDeviceClass.VOLUME,
                native_unit_of_measurement=Units.VOLUME_LITERS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_VOLUME: SensorValue(
                device_key=KEY_VOLUME, name="Volume", native_value=19551.879
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_volume_water(caplog):
    """Test BTHome parser for water in Liters."""
    data_string = b"\x40\x4f\x87\x56\x2a\x01"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_WATER: SensorDescription(
                device_key=KEY_WATER,
                device_class=SensorDeviceClass.WATER,
                native_unit_of_measurement=Units.VOLUME_LITERS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_WATER: SensorValue(
                device_key=KEY_WATER, name="Water", native_value=19551.879
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_timestamp(caplog):
    """Test BTHome parser for Unix timestamp (seconds from 1-1-1970)."""
    data_string = b"\x44\x50\x5D\x39\x61\x64"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_TIMESTAMP: SensorDescription(
                device_key=KEY_TIMESTAMP,
                device_class=SensorDeviceClass.TIMESTAMP,
                native_unit_of_measurement=None,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_TIMESTAMP: SensorValue(
                device_key=KEY_TIMESTAMP,
                name="Timestamp",
                native_value=datetime(2023, 5, 14, 19, 41, 17, tzinfo=timezone.utc),
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_acceleration(caplog):
    """Test BTHome parser for acceleration in m/s°."""
    data_string = b"\x44\x51\x87\x56"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_ACCELERATION: SensorDescription(
                device_key=KEY_ACCELERATION,
                device_class=SensorDeviceClass.ACCELERATION,
                native_unit_of_measurement=Units.ACCELERATION_METERS_PER_SQUARE_SECOND,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_ACCELERATION: SensorValue(
                device_key=KEY_ACCELERATION, name="Acceleration", native_value=22.151
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_gyroscope(caplog):
    """Test BTHome parser for gyroscope in °/s."""
    data_string = b"\x44\x52\x87\x56"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_GYROSCOPE: SensorDescription(
                device_key=KEY_GYROSCOPE,
                device_class=SensorDeviceClass.GYROSCOPE,
                native_unit_of_measurement=Units.GYROSCOPE_DEGREES_PER_SECOND,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_GYROSCOPE: SensorValue(
                device_key=KEY_GYROSCOPE, name="Gyroscope", native_value=22.151
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_text(caplog):
    """Test BTHome parser for text."""
    data_string = b"\x44\x53\x0C\x48\x65\x6C\x6C\x6F\x20\x57\x6F\x72\x6C\x64\x21"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_TEXT: SensorDescription(
                device_key=KEY_TEXT,
                device_class=ExtendedSensorDeviceClass.TEXT,
                native_unit_of_measurement=None,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_TEXT: SensorValue(
                device_key=KEY_TEXT, name="Text", native_value="Hello World!"
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_raw(caplog):
    """Test BTHome parser for raw hex data."""
    data_string = b"\x44\x54\x0C\x48\x65\x6C\x6C\x6F\x20\x57\x6F\x72\x6C\x64\x21"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_RAW: SensorDescription(
                device_key=KEY_RAW,
                device_class=ExtendedSensorDeviceClass.RAW,
                native_unit_of_measurement=None,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_RAW: SensorValue(
                device_key=KEY_RAW, name="Raw", native_value="48656c6c6f20576f726c6421"
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_text_invalid(caplog):
    """Test BTHome parser for text sensor with invalid format."""
    data_string = b"\x44\x53\x01\x87"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_volume_storage(caplog):
    """Test BTHome parser for volume storage in Liters."""
    data_string = b"\x40\x55\x87\x56\x2a\x01"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_VOLUME_STORAGE: SensorDescription(
                device_key=KEY_VOLUME_STORAGE,
                device_class=ExtendedSensorDeviceClass.VOLUME_STORAGE,
                native_unit_of_measurement=Units.VOLUME_LITERS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_VOLUME_STORAGE: SensorValue(
                device_key=KEY_VOLUME_STORAGE,
                name="Volume Storage",
                native_value=19551.879,
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_double_temperature(caplog):
    """Test BTHome parser for double temperature reading without encryption."""
    data_string = b"\x40\x02\xca\x09\x02\xcf\x09"
    advertisement = bytes_to_service_info(
        data_string, local_name="A4:C1:38:8D:18:B2", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="BTHome sensor 18B2",
        devices={
            None: SensorDeviceInfo(
                name="BTHome sensor 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="temperature_1", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature_1", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="temperature_2", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature_2", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            DeviceKey(key="temperature_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature_1", device_id=None),
                name="Temperature 1",
                native_value=25.06,
            ),
            DeviceKey(key="temperature_2", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature_2", device_id=None),
                name="Temperature 2",
                native_value=25.11,
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_triple_temperature_double_humidity_battery(caplog):
    """
    Test BTHome parser for triple temperature, double humidity and
    single battery reading without encryption.
    """
    data_string = (
        b"\x40\x02\xca\x09\x02\xcf\x09\x02\xcf\x08\x03\xb7\x18\x03\xb7\x17\x01\x5d"
    )
    advertisement = bytes_to_service_info(
        data_string, local_name="A4:C1:38:8D:18:B2", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="BTHome sensor 18B2",
        devices={
            None: SensorDeviceInfo(
                name="BTHome sensor 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="temperature_1", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature_1", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="temperature_2", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature_2", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="temperature_3", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature_3", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="humidity_1", device_id=None): SensorDescription(
                device_key=DeviceKey(key="humidity_1", device_id=None),
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="humidity_2", device_id=None): SensorDescription(
                device_key=DeviceKey(key="humidity_2", device_id=None),
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_BATTERY: SensorDescription(
                device_key=KEY_BATTERY,
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            DeviceKey(key="temperature_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature_1", device_id=None),
                name="Temperature 1",
                native_value=25.06,
            ),
            DeviceKey(key="temperature_2", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature_2", device_id=None),
                name="Temperature 2",
                native_value=25.11,
            ),
            DeviceKey(key="temperature_3", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature_3", device_id=None),
                name="Temperature 3",
                native_value=22.55,
            ),
            DeviceKey(key="humidity_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="humidity_1", device_id=None),
                name="Humidity 1",
                native_value=63.27,
            ),
            DeviceKey(key="humidity_2", device_id=None): SensorValue(
                device_key=DeviceKey(key="humidity_2", device_id=None),
                name="Humidity 2",
                native_value=60.71,
            ),
            KEY_BATTERY: SensorValue(KEY_BATTERY, name="Battery", native_value=93),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_multiple_uuids(caplog):
    """Test BTHome parser for a device that broadcasts multiple uuids."""
    advertisement = BluetoothServiceInfoBleak(
        name="ATC_8D18B2",
        address="A4:C1:38:8D:18:B2",
        rssi=-60,
        manufacturer_data={},
        service_data={
            "0000181a-0000-1000-8000-00805f9b34fb": b"\xc4$\x818\xc1\xa4V\x08\x83\x18\xbf",
            "0000fe95-0000-1000-8000-00805f9b34fb": b"0X[\x05\x01\xc4$\x818\xc1\xa4(\x01\x00",
            "0000fcd2-0000-1000-8000-00805f9b34fb": b"\x40\x01\x5d\x02\x5d\x09\x03\xb7\x18",
        },
        service_uuids=[
            "0000181a-0000-1000-8000-00805f9b34fb",
            "0000fe95-0000-1000-8000-00805f9b34fb",
            "0000fcd2-0000-1000-8000-00805f9b34fb",
        ],
        source="",
        device=None,
        advertisement=None,
        connectable=False,
        time=ADVERTISEMENT_TIME,
    )

    device = BTHomeBluetoothDeviceData()

    assert device.update(advertisement) == SensorUpdate(
        title="ATC 18B2",
        devices={
            None: SensorDeviceInfo(
                name="ATC 18B2",
                manufacturer="Xiaomi",
                model="Temperature/Humidity sensor",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_TEMPERATURE: SensorDescription(
                device_key=KEY_TEMPERATURE,
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            KEY_HUMIDITY: SensorDescription(
                device_key=KEY_HUMIDITY,
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_BATTERY: SensorDescription(
                device_key=KEY_BATTERY,
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
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


def test_bthome_double_voltage_different_object_id(caplog):
    """
    Test BTHome parser for double voltage with different object id.
    """
    data_string = b"@\x00\x01\x0b\x00\x00\x00J\r\t\x013\x0c\xe9\x0c"
    advertisement = bytes_to_service_info(
        data_string, local_name="A4:C1:38:8D:18:B2", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    assert device.update(advertisement) == SensorUpdate(
        title="BTHome sensor 18B2",
        devices={
            None: SensorDeviceInfo(
                name="BTHome sensor 18B2",
                manufacturer=None,
                model="BTHome sensor",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_PACKET_ID: SensorDescription(
                device_key=KEY_PACKET_ID,
                device_class=SensorDeviceClass.PACKET_ID,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="power", device_id=None): SensorDescription(
                device_key=DeviceKey(key="power", device_id=None),
                device_class=SensorDeviceClass.POWER,
                native_unit_of_measurement=Units.POWER_WATT,
            ),
            DeviceKey(key="voltage_1", device_id=None): SensorDescription(
                device_key=DeviceKey(key="voltage_1", device_id=None),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            KEY_BATTERY: SensorDescription(
                device_key=KEY_BATTERY,
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="voltage_2", device_id=None): SensorDescription(
                device_key=DeviceKey(key="voltage_2", device_id=None),
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_PACKET_ID: SensorValue(
                device_key=KEY_PACKET_ID, name="Packet Id", native_value=1
            ),
            DeviceKey(key="power", device_id=None): SensorValue(
                device_key=DeviceKey(key="power", device_id=None),
                name="Power",
                native_value=0.0,
            ),
            DeviceKey(key="voltage_1", device_id=None): SensorValue(
                device_key=DeviceKey(key="voltage_1", device_id=None),
                name="Voltage 1",
                native_value=231.7,
            ),
            KEY_BATTERY: SensorValue(KEY_BATTERY, name="Battery", native_value=51),
            DeviceKey(key="voltage_2", device_id=None): SensorValue(
                device_key=DeviceKey(key="voltage_2", device_id=None),
                name="Voltage 2",
                native_value=3.305,
            ),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
    )


def test_bthome_shelly_button(caplog):
    """
    Test BTHome parser with a shelly button.
    """
    data_string = b"@\x00R\x01d:\x01"
    advertisement = bytes_to_service_info(
        data_string, local_name="A4:C1:38:8D:18:B2", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    update = device.update(advertisement)
    assert device.supported(advertisement) is True
    assert update == SensorUpdate(
        title="BTHome sensor 18B2",
        devices={
            None: SensorDeviceInfo(
                name="BTHome sensor 18B2",
                model="BTHome sensor",
                manufacturer=None,
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="packet_id", device_id=None): SensorDescription(
                device_key=DeviceKey(key="packet_id", device_id=None),
                device_class=SensorDeviceClass.PACKET_ID,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            DeviceKey(key="packet_id", device_id=None): SensorValue(
                device_key=DeviceKey(key="packet_id", device_id=None),
                name="Packet " "Id",
                native_value=82,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal " "Strength",
                native_value=-60,
            ),
        },
        binary_entity_descriptions={},
        binary_entity_values={},
        events={
            DeviceKey(key="button", device_id=None): Event(
                device_key=DeviceKey(key="button", device_id=None),
                name="Button",
                event_type="press",
                event_properties=None,
            )
        },
    )


def test_bthome_shelly_button_no_press(caplog):
    """Test BTHome parser for button event followed by empty event."""
    data_string = b"\x44\x00\x21\x01\x5E\x3A\x01"
    advertisement = bytes_to_service_info(
        data_string, local_name="SBBT-002C", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()

    assert device.update(advertisement) == SensorUpdate(
        title="Shelly BLU Button1 18B2",
        devices={
            None: SensorDeviceInfo(
                name="Shelly BLU Button1 18B2",
                manufacturer="Shelly",
                model="BLU Button1",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_PACKET_ID: SensorDescription(
                device_key=KEY_PACKET_ID,
                device_class=SensorDeviceClass.PACKET_ID,
                native_unit_of_measurement=None,
            ),
            KEY_BATTERY: SensorDescription(
                device_key=KEY_BATTERY,
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_PACKET_ID: SensorValue(
                device_key=KEY_PACKET_ID, name="Packet Id", native_value=33
            ),
            KEY_BATTERY: SensorValue(KEY_BATTERY, name="Battery", native_value=94),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
        events={
            DeviceKey(key="button", device_id=None): Event(
                device_key=DeviceKey(key="button", device_id=None),
                name="Button",
                event_type="press",
                event_properties=None,
            )
        },
    )

    data_string = b"\x44\x00\x23\x01\x5E\x3A\x00"
    advertisement = bytes_to_service_info(
        data_string, local_name="SBBT-002C", address="A4:C1:38:8D:18:B2"
    )

    assert device.update(advertisement) == SensorUpdate(
        title="Shelly BLU Button1 18B2",
        devices={
            None: SensorDeviceInfo(
                name="Shelly BLU Button1 18B2",
                manufacturer="Shelly",
                model="BLU Button1",
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_PACKET_ID: SensorDescription(
                device_key=KEY_PACKET_ID,
                device_class=SensorDeviceClass.PACKET_ID,
                native_unit_of_measurement=None,
            ),
            KEY_BATTERY: SensorDescription(
                device_key=KEY_BATTERY,
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_PACKET_ID: SensorValue(
                device_key=KEY_PACKET_ID, name="Packet Id", native_value=35
            ),
            KEY_BATTERY: SensorValue(KEY_BATTERY, name="Battery", native_value=94),
            KEY_SIGNAL_STRENGTH: SensorValue(
                device_key=KEY_SIGNAL_STRENGTH, name="Signal Strength", native_value=-60
            ),
        },
        events={},
    )


def test_bthome_test(caplog):
    """Test BTHome parser for acceleration in m/s°."""
    data_string = b"@\x00\xa7\x0cx\x0b\x10\x00"
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
                sw_version="BTHome BLE v2",
                hw_version=None,
            )
        },
        entity_descriptions={
            KEY_PACKET_ID: SensorDescription(
                device_key=KEY_PACKET_ID,
                device_class=SensorDeviceClass.PACKET_ID,
                native_unit_of_measurement=None,
            ),
            KEY_VOLTAGE: SensorDescription(
                device_key=KEY_VOLTAGE,
                device_class=SensorDeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
            ),
            KEY_SIGNAL_STRENGTH: SensorDescription(
                device_key=KEY_SIGNAL_STRENGTH,
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            KEY_PACKET_ID: SensorValue(
                device_key=KEY_PACKET_ID, name="Packet Id", native_value=167
            ),
            KEY_VOLTAGE: SensorValue(
                device_key=KEY_VOLTAGE, name="Voltage", native_value=2.936
            ),
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
                device_key=KEY_BINARY_POWER, name="Power", native_value=False
            ),
        },
    )


def test_incorrect_bthome_version(caplog):
    """Test BTHome parser with incorrect BTHome version."""
    data_string = b"\x00"
    advertisement = bytes_to_service_info(
        data_string, local_name="TEST DEVICE", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()

    device.update(advertisement)
    assert device.supported(advertisement) is False
    assert (
        "18B2 Sensor is set to use BTHome version 0, which is not existing. "
        "Please modify the version in the first byte of the service data" in caplog.text
    )


def test_bthome_not_sending_object_ids_in_numerical_order(caplog):
    """Test BTHome parser for not sending object ids in numerical order."""
    data_string = b"\x40\x03\xbf\x13\x02\xca\x09"
    advertisement = bytes_to_service_info(
        data_string, local_name="ATC_8D18B2", address="A4:C1:38:8D:18:B2"
    )

    device = BTHomeBluetoothDeviceData()
    device.update(advertisement)
    assert (
        "ATC 18B2 BTHome device is not sending object ids in numerical order "
        "(from low to high object id). This can cause issues with your BTHome receiver, "
        "payload: 03bf1302ca09" in caplog.text
    )
