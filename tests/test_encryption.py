"""Tests for the parser of BLE advertisements in BTHome format."""
import binascii

from bthome_ble.bthome_encryption import decrypt_aes_ccm, encrypt_payload


def test_encryption_example():
    """Test BTHome encryption example."""
    data = bytes(bytearray.fromhex("2302CA090303BF13"))  # BTHome data (not encrypted)
    count_id = bytes(bytearray.fromhex("00112233"))  # count id (change every message)
    mac = binascii.unhexlify("5448E68F80A5")  # MAC
    uuid16 = b"\x1E\x18"
    bindkey = binascii.unhexlify("231d39c1d7cc1ab1aee224cd096db932")

    payload = encrypt_payload(
        data=data, mac=mac, uuid16=uuid16, count_id=count_id, key=bindkey
    )
    assert decrypt_aes_ccm(key=bindkey, mac=mac, data=payload) == {
        "humidity": 50.55,
        "temperature": 25.06,
    }
