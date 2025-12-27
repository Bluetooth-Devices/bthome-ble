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
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from habluetooth import BluetoothServiceInfoBleak
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


class UuidType(Enum):
    V1_NON_ENCRYPTED = "0000181c-0000-1000-8000-00805f9b34fb"
    V1_ENCRYPTED = "0000181e-0000-1000-8000-00805f9b34fb"
    V2 = "0000fcd2-0000-1000-8000-00805f9b34fb"


class BTHomeVersion(Enum):
    INVALID = 0
    V1 = 1
    V2 = 2


def get_encryption_scheme(uuid_type: UuidType, service_data: bytes) -> EncryptionScheme:
    match uuid_type:
        case UuidType.V1_NON_ENCRYPTED:
            return EncryptionScheme.NONE
        case UuidType.V1_ENCRYPTED:
            return EncryptionScheme.BTHOME_BINDKEY
        case UuidType.V2:
            adv_info = service_data[0]
            encryption = adv_info & (1 << 0)  # bit 0
            if encryption == 1:
                return EncryptionScheme.BTHOME_BINDKEY
            return EncryptionScheme.NONE


def get_bthome_version(
    uuid_type: UuidType, service_info: BluetoothServiceInfoBleak, service_data: bytes
) -> BTHomeVersion:
    match uuid_type:
        case UuidType.V1_NON_ENCRYPTED | UuidType.V1_ENCRYPTED:
            return BTHomeVersion.V1
        case UuidType.V2:
            adv_info = service_data[0]
            sw_version = (adv_info >> 5) & 7  # 3 bits (5-7)
            if sw_version != 2:
                identifier = short_address(service_info.address)
                _LOGGER.error(
                    "%s: Sensor is set to use BTHome version %s, which is not existing. "
                    "Please modify the version in the first byte of the service data",
                    identifier,
                    sw_version,
                )
                return BTHomeVersion.INVALID
            return BTHomeVersion.V2


def get_name(service_info: BluetoothServiceInfoBleak) -> str:
    name = service_info.name

    if name == service_info.address:
        name = "BTHome sensor"

    # Remove identifier from ATC sensors name.
    atc_identifier = service_info.address.replace("-", "").replace(":", "")[-6:].upper()
    if name[-6:] == atc_identifier:
        name = name[:-6].rstrip(" _")
    return name


def is_mac_included(service_data: bytes) -> bool:
    adv_info = service_data[0]
    # If True, the first 6 bytes contain the mac address
    return bool(adv_info & (1 << 1))  # bit 1


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
        [val] = struct.unpack("<e", data_obj)
    elif len(data_obj) == 4:
        [val] = struct.unpack("<f", data_obj)
    elif len(data_obj) == 8:
        [val] = struct.unpack("<d", data_obj)
    else:
        _LOGGER.error("only 2, 4 or 8 byte long floats are supported in BTHome BLE")
        return None
    return round(val * factor, decimal_places)


def parse_raw(data_obj: bytes) -> str | None:
    """Convert bytes to raw hex string."""
    return data_obj.hex()


def parse_string(data_obj: bytes) -> str | None:
    """Convert bytes to string."""
    try:
        return data_obj.decode("UTF-8")
    except UnicodeDecodeError:
        _LOGGER.error(
            "BTHome data contains bytes that can't be decoded to a string (use UTF-8 encoding)"
        )
        return None


def parse_timestamp(data_obj: bytes) -> datetime | None:
    """Convert bytes to a datetime object."""
    try:
        value = datetime.fromtimestamp(
            int.from_bytes(data_obj, "little", signed=False), tz=timezone.utc
        )
    except ValueError:
        _LOGGER.error(
            "BTHome data contains bytes that can't be decoded to a datetime object"
        )
        return None
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

        # The encryption counter can be used to verify that the counter of encrypted
        # advertisements is increasing, to have some replay protection. We always
        # start at zero allow the first message after a restart.
        self.encryption_counter = 0.0

        # The packet_id is used to filter duplicate messages in BTHome V2.
        self.packet_id: float | None = None

        # If True then we have used the provided encryption key to decrypt at least
        # one payload.
        # If False then we have either not seen an encrypted payload, the key is wrong
        # or encryption is not in use
        self.bindkey_verified = False

        # If True then the decryption has failed or has not been verified yet.
        # If False then the decryption has succeeded.
        self.decryption_failed = True

        # If this is True, then we have not seen an advertisement with a payload
        # Until we see a payload, we can't tell if this device is encrypted or not
        self.pending = True

        # The last service_info we saw that had a payload
        # We keep this to help in reauth flows where we want to reprocess and old
        # value with a new bindkey.
        self.last_service_info: BluetoothServiceInfoBleak | None = None

        # If this is True, the device is not sending advertisements in a regular interval
        self.sleepy_device = False

        # Holds the software version of the device.
        self.bthome_version: BTHomeVersion = BTHomeVersion.INVALID

        # If this is True, the last update was blocked due to encryption downgrade
        # (received unencrypted data when bindkey is configured)
        self.downgrade_detected = False

    def set_bindkey(self, bindkey: bytes | None) -> None:
        """Set the bindkey."""
        self.bindkey = bindkey
        if bindkey:
            self.cipher: AESCCM | None = AESCCM(bindkey, tag_length=4)
        else:
            self.cipher = None

    def supported(self, data: BluetoothServiceInfoBleak) -> bool:
        if not super().supported(data):
            return False
        return True

    def _start_update(self, service_info: BluetoothServiceInfoBleak) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing BTHome BLE advertisement data: %s", service_info)
        for uuid, service_data in service_info.service_data.items():
            if self._parse_bthome(uuid, service_info, service_data):
                self.last_service_info = service_info
        return None

    def _set_encryption_scheme(self, uuid: UuidType, service_data: bytes) -> None:
        self.encryption_scheme = get_encryption_scheme(uuid, service_data)

    def _set_downgrade_detected(self, service_info: BluetoothServiceInfoBleak) -> None:
        if self.bindkey and self.encryption_scheme == EncryptionScheme.NONE:
            identifier = short_address(service_info.address)
            _LOGGER.warning(
                "Received plaintext adv from %s while bindkey is known, ignoring!",
                identifier,
            )
            self.downgrade_detected = True
            return

        # Clear flag when processing valid data (encrypted or unencrypted without bindkey)
        self.downgrade_detected = False

    def _set_sleepy_devices(self, service_data: bytes) -> None:
        match self.bthome_version:
            case BTHomeVersion.V1:
                self.sleepy_devices = False
            case BTHomeVersion.V2:
                adv_info = service_data[0]
                # If True, the device is only updating when trigger
                self.sleepy_device = bool(adv_info & (1 << 2))  # bit 2
            case _:
                raise ValueError

    def _set_bthome_version(
        self,
        uuid_type: UuidType,
        service_info: BluetoothServiceInfoBleak,
        service_data: bytes,
    ) -> None:
        self.bthome_version = get_bthome_version(uuid_type, service_info, service_data)
        # This is a little misleading for the user, since we show the bthome version
        # instead of the firmware version.
        match self.encryption_scheme:
            case EncryptionScheme.NONE:
                self.set_device_sw_version(f"BTHome BLE v{self.bthome_version.value}")
            case EncryptionScheme.BTHOME_BINDKEY:
                self.set_device_sw_version(
                    f"BTHome BLE v{self.bthome_version.value} (encrypted)"
                )

    def _set_manufacture_name_type_and_title(
        self, service_info: BluetoothServiceInfoBleak
    ) -> None:
        # Try to get manufacturer based on the name
        identifier = short_address(service_info.address)
        name = get_name(service_info)
        if name.startswith(("ATC", "LYWSD03MMC")):
            manufacturer = "Xiaomi"
            device_type = "Temperature/Humidity sensor"
        elif name.startswith("prst"):
            manufacturer = "b-parasite"
            name = "b-parasite"
            device_type = "Plant sensor"
        elif name == "SBBT-002C":
            manufacturer = "Shelly"
            name = "Shelly BLU Button1"
            device_type = "BLU Button1"
        elif name == "SBBT-102C":
            manufacturer = "Shelly"
            name = "Shelly BLU Button1 ZB"
            device_type = "BLU Button1 ZB"
        elif name == "SBDW-002C":
            manufacturer = "Shelly"
            name = "Shelly BLU Door/Window"
            device_type = "BLU Door/Window"
        elif name == "SBMO-003Z":
            manufacturer = "Shelly"
            name = "Shelly BLU Motion"
            device_type = "BLU Motion"
        elif name == "SBHT-003C":
            manufacturer = "Shelly"
            name = "Shelly BLU H&T"
            device_type = "BLU H&T"
        elif name == "SBHT-203C":
            manufacturer = "Shelly"
            name = "Shelly BLU H&T ZB"
            device_type = "BLU H&T ZB"
        elif name == "SBHT-103C":
            manufacturer = "Shelly"
            name = "Shelly BLU H&T Display ZB"
            device_type = "BLU H&T Display ZB"
        elif name == "SBBT-004CEU":
            manufacturer = "Shelly"
            name = "Shelly BLU Wall Switch 4"
            device_type = "BLU Wall Switch 4"
        elif name == "SBBT-004CUS":
            manufacturer = "Shelly"
            name = "Shelly BLU RC Button 4"
            device_type = "BLU RC Button 4"
        elif name == "SBTR-001AEU":
            manufacturer = "Shelly"
            name = "Shelly BLU TRV"
            device_type = "BLU TRV"
        else:
            manufacturer = None
            device_type = "BTHome sensor"
        if manufacturer:
            self.set_device_manufacturer(manufacturer)
        # Get device information from local name and identifier
        self.set_device_name(f"{name} {identifier}")
        self.set_title(f"{name} {identifier}")
        self.set_device_type(device_type)

    def _get_mac_readable(
        self, service_info: BluetoothServiceInfoBleak, service_data: bytes
    ) -> str:
        match self.bthome_version:
            case BTHomeVersion.V1:
                return service_info.address
            case BTHomeVersion.V2:
                if is_mac_included(service_data):
                    bthome_mac_reversed = service_data[1:7]
                    return to_mac(bthome_mac_reversed[::-1])
                return service_info.address
            case _:
                raise ValueError

    def _get_payload(self, service_data: bytes) -> bytes:
        match self.bthome_version:
            case BTHomeVersion.V1:
                return service_data
            case BTHomeVersion.V2:
                if is_mac_included(service_data):
                    return service_data[7:]
                return service_data[1:]
            case _:
                raise ValueError

    def _get_adv_info(self, service_data: bytes) -> int:
        match self.bthome_version:
            case BTHomeVersion.V1:
                return 65
            case BTHomeVersion.V2:
                return service_data[0]
            case _:
                raise ValueError

    def _get_decrypted_payload(
        self,
        service_info: BluetoothServiceInfoBleak,
        service_data: bytes,
    ) -> bytes | None:
        payload = self._get_payload(service_data)
        match self.encryption_scheme:
            case EncryptionScheme.NONE:
                return payload
            case EncryptionScheme.BTHOME_BINDKEY:
                mac_readable = self._get_mac_readable(service_info, service_data)
                source_mac = bytes.fromhex(mac_readable.replace(":", ""))
                adv_info = self._get_adv_info(service_data)
                try:
                    return self._decrypt_bthome(
                        service_info, payload, source_mac, adv_info
                    )
                except (ValueError, TypeError):
                    return None

    def _parse_bthome(
        self,
        uuid: str,
        service_info: BluetoothServiceInfoBleak,
        service_data: bytes,
    ) -> bool:
        """Parser for BTHome sensors"""
        try:
            uuid_type = UuidType(uuid)
        except ValueError:
            return False

        self._set_encryption_scheme(uuid_type, service_data)
        self._set_downgrade_detected(service_info)
        if self.downgrade_detected:
            return False
        self._set_bthome_version(uuid_type, service_info, service_data)
        if self.bthome_version == BTHomeVersion.INVALID:
            return False
        self._set_sleepy_devices(service_data)
        self._set_manufacture_name_type_and_title(service_info)

        payload = self._get_decrypted_payload(service_info, service_data)
        if payload is None:
            return True
        return self._parse_payload(payload, service_info.time)

    def _skip_old_or_duplicated_advertisement(
        self, new_packet_id: float, adv_time: float
    ) -> bool:
        """
        Detect duplicated or older packets

        Devices may send duplicated advertisements or advertisements order can change
        when passing through a proxy. If more than 4 seconds pass since the last
        advertisement assume it is a new packet even if it has the same packet id.
        Packet id rollover at 255 to 0, validate that the difference between last packet id
        and new packet id is less than 64. This assumes device is not sending more than 16
        advertisements per second.
        """
        last_packet_id = self.packet_id

        # no history, first packet, don't discard packet
        if last_packet_id is None or self.last_service_info is None:
            _LOGGER.debug(
                "%s: First packet, not filtering packet_id %i",
                self.title,
                new_packet_id,
            )
            return False

        # more than 4 seconds since last packet, don't discard packet
        if adv_time - self.last_service_info.time > 4:
            _LOGGER.debug(
                "%s: Not filtering packet_id, more than 4 seconds since last packet. "
                "New time: %i, Old time: %i",
                self.title,
                adv_time,
                self.last_service_info.time,
            )
            return False

        # distance between new packet and old packet is less then 64
        if (new_packet_id > last_packet_id and new_packet_id - last_packet_id < 64) or (
            new_packet_id < last_packet_id and new_packet_id + 256 - last_packet_id < 64
        ):
            return False

        # discard packet (new_packet_id=last_packet_id or older packet)
        _LOGGER.debug(
            "%s: New packet_id %i indicates an older packet (previous packet_id %i). "
            "BLE advertisement will be skipped",
            self.title,
            new_packet_id,
            last_packet_id,
        )
        return True

    def _parse_payload(self, payload: bytes, adv_time: float) -> bool:
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

            match self.bthome_version:
                case BTHomeVersion.V1:
                    obj_meas_type = payload[obj_start + 1]
                    obj_control_byte = payload[obj_start]
                    obj_data_length = (obj_control_byte >> 0) & 31  # 5 bits (0-4)
                    obj_data_format = (obj_control_byte >> 5) & 7  # 3 bits (5-7)
                    obj_data_start = obj_start + 2
                    next_obj_start = obj_start + obj_data_length + 1
                case BTHomeVersion.V2:
                    obj_meas_type = payload[obj_start]
                    if prev_obj_meas_type > obj_meas_type:
                        _LOGGER.warning(
                            "%s: BTHome device is not sending object ids in numerical order "
                            "(from low to high object id). This can cause issues with your BTHome "
                            "receiver, payload: %s",
                            self.title,
                            payload.hex(),
                        )
                    if obj_meas_type not in MEAS_TYPES:
                        _LOGGER.debug(
                            "%s: Invalid Object ID found in payload: %s",
                            self.title,
                            payload.hex(),
                        )
                        break
                    prev_obj_meas_type = obj_meas_type
                    obj_data_format = MEAS_TYPES[obj_meas_type].data_format

                    if obj_data_format in ["raw", "string"]:
                        obj_data_length = payload[obj_start + 1]
                        obj_data_start = obj_start + 2
                    else:
                        obj_data_length = MEAS_TYPES[obj_meas_type].data_length
                        obj_data_start = obj_start + 1
                    next_obj_start = obj_data_start + obj_data_length
                case _:
                    raise ValueError

            if obj_data_length == 0:
                _LOGGER.debug(
                    "%s: Invalid payload data length found with length 0, payload: %s",
                    self.title,
                    payload.hex(),
                )
                continue

            if payload_length < next_obj_start:
                _LOGGER.debug(
                    "%s: Invalid payload data length, payload: %s",
                    self.title,
                    payload.hex(),
                )
                break

            # Filter BLE advertisements with packet_id that has already been parsed.
            if obj_meas_type == 0:
                new_packet_id = parse_uint(payload[obj_data_start:next_obj_start])
                if self._skip_old_or_duplicated_advertisement(new_packet_id, adv_time):
                    break
                self.packet_id = new_packet_id

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
                    "%s: UNKNOWN measurement type %s in BTHome BLE payload! Adv: %s",
                    self.title,
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
            elif meas["data format"] == 4 or meas["data format"] == "raw":
                value = parse_raw(meas["measurement data"])
            elif meas["data format"] == 5 or meas["data format"] == "timestamp":
                value = parse_timestamp(meas["measurement data"])
            else:
                _LOGGER.error(
                    "%s: UNKNOWN dataobject in BTHome BLE payload! Adv: %s",
                    self.title,
                    payload.hex(),
                )
                continue

            if value is not None:
                if (
                    isinstance(meas_format, BaseSensorDescription)
                    and meas_format.device_class
                ):
                    self.update_sensor(
                        key=f"{str(meas_format.device_class)}{postfix}",
                        native_unit_of_measurement=meas_format.native_unit_of_measurement,
                        native_value=value,
                        device_class=meas_format.device_class,
                    )
                elif (
                    isinstance(meas_format, BaseBinarySensorDescription)
                    and meas_format.device_class
                ):
                    self.update_binary_sensor(
                        key=f"{str(meas_format.device_class)}{postfix}",
                        device_class=meas_format.device_class,
                        native_value=bool(value),
                    )
                elif isinstance(meas_format, EventDeviceKeys):
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
                    "%s: UNKNOWN dataobject in BTHome BLE payload! Adv: %s",
                    self.title,
                    payload.hex(),
                )

        if not result:
            return False

        return True

    def _check_minumum_length(self, service_data: bytes) -> None:
        match self.bthome_version:
            case BTHomeVersion.V1:
                min_length = 12
            case BTHomeVersion.V2:
                min_length = 10
            case _:
                raise ValueError

        if len(service_data) < min_length:
            _LOGGER.debug(
                "%s: Invalid data length (for decryption), adv: %s",
                self.title,
                service_data.hex(),
            )
            raise ValueError

    def _get_nonce(self, bthome_mac: bytes, adv_info: int, counter: bytes) -> bytes:
        match self.bthome_version:
            case BTHomeVersion.V1:
                uuid = b"\x1e\x18"
            case BTHomeVersion.V2:
                uuid = b"\xd2\xfc" + bytes([adv_info])
            case _:
                raise ValueError
        # nonce: mac [6], uuid16 [2 (v1) or 3 (v2)], counter [4]
        return b"".join([bthome_mac, uuid, counter])

    def _decrypt_bthome(
        self,
        service_info: BluetoothServiceInfoBleak,
        service_data: bytes,
        bthome_mac: bytes,
        adv_info: int = 65,
    ) -> bytes:
        """Decrypt encrypted BTHome BLE advertisements"""
        if not self.bindkey:
            self.bindkey_verified = False
            _LOGGER.debug("%s: Encryption key not set and adv is encrypted", self.title)
            raise ValueError

        if not self.bindkey or len(self.bindkey) != 16:
            self.bindkey_verified = False
            _LOGGER.error(
                "%s: Encryption key should be 16 bytes (32 characters) long", self.title
            )
            raise ValueError

        # check for minimum length of encrypted advertisement
        self._check_minumum_length(service_data)

        # prepare the data for decryption
        encrypted_payload = service_data[:-8]
        last_encryption_counter = self.encryption_counter
        counter = service_data[-8:-4]
        new_encryption_counter = parse_uint(counter)
        mic = service_data[-4:]

        # nonce: mac [6], uuid16 [2 (v1) or 3 (v2)], counter [4]
        nonce = self._get_nonce(bthome_mac, adv_info, counter)

        match self.bthome_version:
            case BTHomeVersion.V1:
                associated_data: bytes | None = b"\x11"
            case BTHomeVersion.V2:
                associated_data = None
            case _:
                raise ValueError

        assert self.cipher is not None  # nosec

        # filter advertisements that are exactly the same as the previous advertisement
        if (
            self.last_service_info
            and service_info.service_data == self.last_service_info.service_data
            and self.bindkey_verified is True
        ):
            _LOGGER.debug(
                "%s: The service data is the same as the previous service data. Skipping "
                "this BLE advertisement.",
                self.title,
            )
            raise ValueError

        # Filter advertisements with a decreasing encryption counter.
        # Allow cases where the counter has restarted from 0
        # (after reaching the highest number or due to a battery change).
        # In all other cases, assume the data has been compromised and skip the advertisement.
        if (
            new_encryption_counter < last_encryption_counter
            and self.bindkey_verified is True
            and new_encryption_counter >= 100
        ):
            _LOGGER.warning(
                "%s: The new encryption counter (%i) is lower than the previous value (%i). "
                "The data might be compromised. BLE advertisement will be skipped.",
                self.title,
                new_encryption_counter,
                last_encryption_counter,
            )
            raise ValueError

        # decrypt the data
        try:
            decrypted_payload = self.cipher.decrypt(
                nonce, encrypted_payload + mic, associated_data
            )
        except InvalidTag as error:
            if self.decryption_failed is True:
                # we only ask for reautentification after the decryption has failed twice.
                self.bindkey_verified = False
            else:
                self.decryption_failed = True
            _LOGGER.warning("%s: Decryption failed: %s", self.title, error)
            _LOGGER.debug("%s: mic: %s", self.title, mic.hex())
            _LOGGER.debug("%s: nonce: %s", self.title, nonce.hex())
            _LOGGER.debug(
                "%s: encrypted_payload: %s", self.title, encrypted_payload.hex()
            )
            raise ValueError
        if decrypted_payload is None:
            self.bindkey_verified = False
            _LOGGER.error(
                "%s: Decryption failed for %s, decrypted payload is None",
                self.title,
                to_mac(bthome_mac),
            )
            raise ValueError
        self.decryption_failed = False
        self.bindkey_verified = True
        self.encryption_counter = new_encryption_counter

        return decrypted_payload
