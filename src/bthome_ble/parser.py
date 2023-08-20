"""Parser for BLE advertisements in BTHome format.

This file is shamelessly copied from the following repository:
https://github.com/Ernst79/bleparser/blob/ac8757ad64f1fc17674dcd22111e547cdf2f205b/package/bleparser/ha_ble.py

BTHome was originally developed as HA BLE for ble_monitor and has been renamed
to BTHome for the Home Assistant Bluetooth integration.

MIT License applies.
"""
from __future__ import annotations

import logging
import struct
import sys
from datetime import datetime
from enum import Enum
from typing import Any

import pytz
from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data.description import (
    BaseBinarySensorDescription,
    BaseSensorDescription,
)

from .const import MEAS_TYPES
from .event import BUTTON_EVENTS, DIMMER_EVENTS, EventDeviceKeys

_LOGGER = logging.getLogger(__name__)


class EncryptionScheme(Enum):
    # No encryption is needed to use this device
    NONE = "none"

    # 16 byte encryption key expected
    BTHOME_BINDKEY = "bthome_bindkey"


def to_mac(addr: bytes) -> str:
    """Return formatted MAC address."""
    return ":".join(f"{i:02X}" for i in addr)


def parse_uint(data_obj: bytes, factor: float = 1.0) -> float:
    """Convert bytes (as unsigned integer) and factor to float."""
    decimal_places = -int(f"{factor:e}".split("e")[-1])
    return round(
        int.from_bytes(data_obj, "little", signed=False) * factor, decimal_places
    )


def parse_int(data_obj: bytes, factor: float = 1.0) -> float:
    """Convert bytes (as signed integer) and factor to float."""
    decimal_places = -int(f"{factor:e}".split("e")[-1])
    return round(
        int.from_bytes(data_obj, "little", signed=True) * factor, decimal_places
    )


def parse_float(data_obj: bytes, factor: float = 1.0) -> float | None:
    """Convert bytes (as float) and factor to float."""
    decimal_places = -int(f"{factor:e}".split("e")[-1])
    if len(data_obj) == 2:
        [val] = struct.unpack("e", data_obj)
    elif len(data_obj) == 4:
        [val] = struct.unpack("f", data_obj)
    elif len(data_obj) == 8:
        [val] = struct.unpack("d", data_obj)
    else:
        _LOGGER.error("only 2, 4 or 8 byte long floats are supported in BTHome BLE")
        return None
    return round(val * factor, decimal_places)


def parse_string(data_obj: bytes) -> str | None:
    """Convert bytes to string."""
    try:
        return data_obj.decode("UTF-8")
    except UnicodeDecodeError:
        _LOGGER.error(
            "BTHome data contains bytes that can't be decoded to a string (use UTF-8 encoding)"
        )
        return None


def parse_timestamp(data_obj: bytes) -> datetime:
    """Convert bytes to a datetime object."""
    value = datetime.fromtimestamp(
        int.from_bytes(data_obj, "little", signed=False), tz=pytz.utc
    )
    _LOGGER.error("time %s", value)
    return value


def parse_event_type(event_device: str, data_obj: int) -> str | None:
    """Convert bytes to event type."""
    if event_device == "dimmer":
        event_type = DIMMER_EVENTS.get(data_obj)
    elif event_device == "button":
        event_type = BUTTON_EVENTS.get(data_obj)
    else:
        event_type = None
    return event_type


def parse_event_properties(
    event_device: str, data_obj: bytes
) -> dict[str, str | int | float | None] | None:
    """Convert bytes to event properties."""
    if event_device == "dimmer":
        # number of steps for rotating a dimmer
        return {"steps": int.from_bytes(data_obj, "little", signed=True)}
    else:
        return None


class BTHomeBluetoothDeviceData(BluetoothData):
    """Data for BTHome Bluetooth devices."""

    def __init__(self, bindkey: bytes | None = None) -> None:
        super().__init__()
        self.set_bindkey(bindkey)

        # Data that we know how to parse but don't yet map to the SensorData model.
        self.unhandled: dict[str, Any] = {}

        # Encryption to expect, based on flags in the UUID.
        self.encryption_scheme = EncryptionScheme.NONE

        # If True, then we know the actual MAC of the device.
        # On macOS, we don't unless the device includes it in the advertisement
        # (CoreBluetooth uses UUID's generated by CoreBluetooth instead of the MAC)
        self.mac_known = sys.platform != "darwin"

        # If True then we have used the provided encryption key to decrypt at least
        # one payload.
        # If False then we have either not seen an encrypted payload, the key is wrong
        # or encryption is not in use
        self.bindkey_verified = False

        # If this is True, then we have not seen an advertisement with a payload
        # Until we see a payload, we can't tell if this device is encrypted or not
        self.pending = True

        # The last service_info we saw that had a payload
        # We keep this to help in reauth flows where we want to reprocess and old
        # value with a new bindkey.
        self.last_service_info: BluetoothServiceInfo | None = None

        # If this is True, the device is not sending advertisements in a regular interval
        self.sleepy_device = False

    def set_bindkey(self, bindkey: bytes | None) -> None:
        """Set the bindkey."""
        self.bindkey = bindkey
        if bindkey:
            self.cipher: AESCCM | None = AESCCM(bindkey, tag_length=4)
        else:
            self.cipher = None

    def supported(self, data: BluetoothServiceInfo) -> bool:
        if not super().supported(data):
            return False

        # Where a device uses encryption we need to know its actual MAC address.
        # As the encryption uses it as part of the nonce.
        # On macOS, we instead only know its CoreBluetooth UUID.
        # It seems its impossible to automatically get that in the general case.
        # So devices do duplicate the MAC in the advertisement, we use that
        # when we can on macOS.
        # We may want to ask the user for the MAC address during config flow
        # For now, just hide these devices for macOS users.
        if self.encryption_scheme != EncryptionScheme.NONE:
            if not self.mac_known:
                return False

        return True

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing BTHome BLE advertisement data: %s", service_info)
        for uuid, data in service_info.service_data.items():
            if uuid in [
                "0000181c-0000-1000-8000-00805f9b34fb",
                "0000181e-0000-1000-8000-00805f9b34fb",
            ]:
                if self._parse_bthome_v1(service_info, service_info.name, data):
                    self.last_service_info = service_info
            elif uuid == "0000fcd2-0000-1000-8000-00805f9b34fb":
                if self._parse_bthome_v2(service_info, service_info.name, data):
                    self.last_service_info = service_info
        return None

    def _parse_bthome_v1(
        self, service_info: BluetoothServiceInfo, name: str, data: bytes
    ) -> bool:
        """Parser for BTHome sensors version V1"""
        identifier = short_address(service_info.address)
        sw_version = 1

        # Remove identifier from ATC sensors.
        atc_identifier = (
            service_info.address.replace("-", "").replace(":", "")[-6:].upper()
        )
        if name[-6:] == atc_identifier:
            name = name[:-6].rstrip(" _")

        # Try to get manufacturer
        if name.startswith(("ATC", "LYWSD03MMC")):
            manufacturer = "Xiaomi"
        elif name.startswith("prst"):
            manufacturer = "b-parasite"
            name = "b-parasite"
        else:
            manufacturer = None

        if manufacturer:
            self.set_device_manufacturer(manufacturer)

        self.set_device_name(f"{name} {identifier}")
        self.set_title(f"{name} {identifier}")
        self.set_device_type("BTHome sensor")

        uuid16 = list(service_info.service_data.keys())
        if "0000181c-0000-1000-8000-00805f9b34fb" in uuid16:
            # Non-encrypted BTHome BLE format
            self.encryption_scheme = EncryptionScheme.NONE
            self.set_device_sw_version("BTHome BLE v1")
            payload = data
            packet_id = None  # noqa: F841
        elif "0000181e-0000-1000-8000-00805f9b34fb" in uuid16:
            # Encrypted BTHome BLE format
            self.encryption_scheme = EncryptionScheme.BTHOME_BINDKEY
            self.set_device_sw_version("BTHome BLE v1 (encrypted)")

            mac_readable = service_info.address
            if len(mac_readable) != 17 and mac_readable[2] != ":":
                # On macOS, we get a UUID, which is useless for BTHome sensors
                self.mac_known = False
                return False
            else:
                self.mac_known = True
            source_mac = bytes.fromhex(mac_readable.replace(":", ""))

            try:
                payload = self._decrypt_bthome(data, source_mac, sw_version)
            except (ValueError, TypeError):
                return True

            packet_id = parse_uint(data[-8:-4])  # noqa: F841
        else:
            return False

        return self._parse_payload(payload, sw_version)

    def _parse_bthome_v2(
        self, service_info: BluetoothServiceInfo, name: str, data: bytes
    ) -> bool:
        """Parser for BTHome sensors version V2"""
        identifier = short_address(service_info.address)
        if name == service_info.address:
            name = "BTHome sensor"

        # Remove identifier from ATC sensors name.
        atc_identifier = (
            service_info.address.replace("-", "").replace(":", "")[-6:].upper()
        )
        if name[-6:] == atc_identifier:
            name = name[:-6].rstrip(" _")

        adv_info = data[0]

        # Determine if encryption is used
        encryption = adv_info & (1 << 0)  # bit 0
        if encryption == 1:
            self.encryption_scheme = EncryptionScheme.BTHOME_BINDKEY
        else:
            self.encryption_scheme = EncryptionScheme.NONE

        # If True, the first 6 bytes contain the mac address
        mac_included = adv_info & (1 << 1)  # bit 1
        if mac_included:
            bthome_mac_reversed = data[1:7]
            mac_readable = to_mac(bthome_mac_reversed[::-1])
            payload = data[7:]
        else:
            mac_readable = service_info.address
            payload = data[1:]

        # If True, the device is only updating when triggered
        self.sleepy_device = bool(adv_info & (1 << 2))  # bit 2

        # Check BTHome version
        sw_version = (adv_info >> 5) & 7  # 3 bits (5-7)
        if sw_version == 2:
            if self.encryption_scheme == EncryptionScheme.BTHOME_BINDKEY:
                self.set_device_sw_version(f"BTHome BLE v{sw_version} (encrypted)")
            else:
                self.set_device_sw_version(f"BTHome BLE v{sw_version}")
        else:
            _LOGGER.error(
                "Sensor is set to use BTHome version %s, which is not existing. "
                "Please modify the version in the first byte of the service data",
                sw_version,
            )
            return False

        # Try to get manufacturer based on the name
        if name.startswith(("ATC", "LYWSD03MMC")):
            manufacturer = "Xiaomi"
            device_type = "Temperature/Humidity sensor"
        elif name.startswith("prst"):
            manufacturer = "b-parasite"
            name = "b-parasite"
            device_type = "Plant sensor"
        elif name.startswith("SBBT"):
            manufacturer = "Shelly"
            name = "Shelly BLU Button1"
            device_type = "BLU Button1"
        elif name.startswith("SBDW"):
            manufacturer = "Shelly"
            name = "Shelly BLU Door/Window"
            device_type = "BLU Door/Window"
        else:
            manufacturer = None
            device_type = "BTHome sensor"

        if manufacturer:
            self.set_device_manufacturer(manufacturer)

        # Get device information from local name and identifier
        self.set_device_name(f"{name} {identifier}")
        self.set_title(f"{name} {identifier}")
        self.set_device_type(device_type)

        if self.encryption_scheme == EncryptionScheme.BTHOME_BINDKEY:
            if len(mac_readable) != 17 and mac_readable[2] != ":":
                # On macOS, we get a UUID, which is useless for BTHome sensors
                # Unless the MAC address is specified in the payload
                self.mac_known = False
                return False
            else:
                self.mac_known = True
            bthome_mac = bytes.fromhex(mac_readable.replace(":", ""))
            # Decode encrypted payload
            try:
                payload = self._decrypt_bthome(
                    payload, bthome_mac, sw_version, adv_info
                )
            except (ValueError, TypeError):
                return True

        return self._parse_payload(payload, sw_version)

    def _parse_payload(self, payload: bytes, sw_version: int) -> bool:
        payload_length = len(payload)
        next_obj_start = 0
        prev_obj_meas_type = 0
        result = False
        measurements: list[dict[str, Any]] = []
        postfix_dict: dict[str, int] = {}
        obj_data_format: str | int

        # Create a list with all individual objects
        while payload_length >= next_obj_start + 1:
            obj_start = next_obj_start

            if sw_version == 1:
                # BTHome V1
                obj_meas_type = payload[obj_start + 1]
                obj_control_byte = payload[obj_start]
                obj_data_length = (obj_control_byte >> 0) & 31  # 5 bits (0-4)
                obj_data_format = (obj_control_byte >> 5) & 7  # 3 bits (5-7)
                obj_data_start = obj_start + 2
                next_obj_start = obj_start + obj_data_length + 1
            else:
                # BTHome V2
                obj_meas_type = payload[obj_start]
                if prev_obj_meas_type > obj_meas_type:
                    _LOGGER.warning(
                        "BTHome device is not sending object ids in numerical order (from low to "
                        "high object id). This can cause issues with your BTHome receiver, "
                        "payload: %s",
                        payload.hex(),
                    )
                if obj_meas_type not in MEAS_TYPES:
                    _LOGGER.debug(
                        "Invalid Object ID found in payload: %s",
                        payload.hex(),
                    )
                    break
                prev_obj_meas_type = obj_meas_type
                obj_data_format = MEAS_TYPES[obj_meas_type].data_format

                if obj_data_format == "string":
                    obj_data_length = payload[obj_start + 1]
                    obj_data_start = obj_start + 2
                else:
                    obj_data_length = MEAS_TYPES[obj_meas_type].data_length
                    obj_data_start = obj_start + 1
                next_obj_start = obj_data_start + obj_data_length

            if obj_data_length == 0:
                _LOGGER.debug(
                    "Invalid payload data length found with length 0, payload: %s",
                    payload.hex(),
                )
                continue

            if payload_length < next_obj_start:
                _LOGGER.debug("Invalid payload data length, payload: %s", payload.hex())
                break
            measurements.append(
                {
                    "data format": obj_data_format,
                    "data length": obj_data_length,
                    "measurement type": obj_meas_type,
                    "measurement data": payload[obj_data_start:next_obj_start],
                    "device id": None,
                }
            )

        # Get a list of measurement types that are included more than once.
        seen_meas_formats = set()
        dup_meas_formats = set()
        for meas in measurements:
            if meas["measurement type"] in MEAS_TYPES:
                meas_format = MEAS_TYPES[meas["measurement type"]].meas_format
                if meas_format in seen_meas_formats:
                    dup_meas_formats.add(meas_format)
                else:
                    seen_meas_formats.add(meas_format)

        # Parse each object into readable information
        for meas in measurements:
            if meas["measurement type"] not in MEAS_TYPES:
                _LOGGER.debug(
                    "UNKNOWN measurement type %s in BTHome BLE payload! Adv: %s",
                    meas["measurement type"],
                    payload.hex(),
                )
                continue

            meas_type = MEAS_TYPES[meas["measurement type"]]
            meas_format = meas_type.meas_format
            meas_factor = meas_type.factor

            if meas_type.meas_format in dup_meas_formats:
                # Add a postfix for advertisements with multiple measurements of the same type
                postfix_counter = postfix_dict.get(meas_format, 0) + 1
                postfix_dict[meas_format] = postfix_counter
                postfix = f"_{postfix_counter}"
            else:
                postfix = ""

            value: None | str | int | float | datetime
            if meas["data format"] == 0 or meas["data format"] == "unsigned_integer":
                value = parse_uint(meas["measurement data"], meas_factor)
            elif meas["data format"] == 1 or meas["data format"] == "signed_integer":
                value = parse_int(meas["measurement data"], meas_factor)
            elif meas["data format"] == 2 or meas["data format"] == "float":
                value = parse_float(meas["measurement data"], meas_factor)
            elif meas["data format"] == 3 or meas["data format"] == "string":
                value = parse_string(meas["measurement data"])
            elif meas["data format"] == 5 or meas["data format"] == "timestamp":
                value = parse_timestamp(meas["measurement data"])
            else:
                _LOGGER.error(
                    "UNKNOWN dataobject in BTHome BLE payload! Adv: %s",
                    payload.hex(),
                )
                continue

            if value is not None:
                if (
                    type(meas_format) == BaseSensorDescription
                    and meas_format.device_class
                ):
                    self.update_sensor(
                        key=f"{str(meas_format.device_class)}{postfix}",
                        native_unit_of_measurement=meas_format.native_unit_of_measurement,
                        native_value=value,
                        device_class=meas_format.device_class,
                    )
                elif (
                    type(meas_format) == BaseBinarySensorDescription
                    and meas_format.device_class
                ):
                    self.update_binary_sensor(
                        key=f"{str(meas_format.device_class)}{postfix}",
                        device_class=meas_format.device_class,
                        native_value=bool(value),
                    )
                elif type(meas_format) == EventDeviceKeys:
                    event_type = parse_event_type(
                        event_device=meas_format,
                        data_obj=meas["measurement data"][0],
                    )
                    event_properties = parse_event_properties(
                        event_device=meas_format,
                        data_obj=meas["measurement data"][1:],
                    )
                    if event_type:
                        self.fire_event(
                            key=f"{str(meas_format)}{postfix}",
                            event_type=event_type,
                            event_properties=event_properties,
                        )
                result = True
            else:
                _LOGGER.debug(
                    "UNKNOWN dataobject in BTHome BLE payload! Adv: %s",
                    payload.hex(),
                )

        if not result:
            return False

        return True

    def _decrypt_bthome(
        self, data: bytes, bthome_mac: bytes, sw_version: int, adv_info: int = 65
    ) -> bytes:
        """Decrypt encrypted BTHome BLE advertisements"""
        if not self.bindkey:
            self.bindkey_verified = False
            _LOGGER.debug("Encryption key not set and adv is encrypted")
            raise ValueError

        if not self.bindkey or len(self.bindkey) != 16:
            self.bindkey_verified = False
            _LOGGER.error("Encryption key should be 16 bytes (32 characters) long")
            raise ValueError

        # check for minimum length of encrypted advertisement
        if len(data) < (12 if sw_version == 1 else 11):
            _LOGGER.debug("Invalid data length (for decryption), adv: %s", data.hex())
            raise ValueError

        # prepare the data for decryption
        if sw_version == 1:
            uuid = b"\x1e\x18"
        else:
            uuid = b"\xd2\xfc" + bytes([adv_info])
        encrypted_payload = data[:-8]
        count_id = data[-8:-4]
        mic = data[-4:]

        # nonce: mac [6], uuid16 [2 (v1) or 3 (v2)], count_id [4]
        nonce = b"".join([bthome_mac, uuid, count_id])

        associated_data = None
        if sw_version == 1:
            associated_data = b"\x11"

        assert self.cipher is not None  # nosec
        # decrypt the data
        try:
            decrypted_payload = self.cipher.decrypt(
                nonce, encrypted_payload + mic, associated_data
            )
        except InvalidTag as error:
            self.bindkey_verified = False
            _LOGGER.warning("Decryption failed: %s", error)
            _LOGGER.debug("mic: %s", mic.hex())
            _LOGGER.debug("nonce: %s", nonce.hex())
            _LOGGER.debug("encrypted_payload: %s", encrypted_payload.hex())
            raise ValueError
        if decrypted_payload is None:
            self.bindkey_verified = False
            _LOGGER.error(
                "Decryption failed for %s, decrypted payload is None",
                to_mac(bthome_mac),
            )
            raise ValueError
        self.bindkey_verified = True

        return decrypted_payload
