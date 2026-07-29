"""Tests for the parser of BLE advertisements in BTHome V1 format."""

import binascii

from bthome_ble.bthome_v1_encryption import decrypt_aes_ccm, encrypt_payload


def test_encryption_example():
    """Test BTHome V1 encryption example."""
    data = bytes.fromhex("2302CA090303BF13")  # BTHome data (not encrypted)
    count_id = bytes.fromhex("00112233")  # count id (change every message)
    mac = binascii.unhexlify("5448E68F80A5")  # MAC
    uuid16 = b"\x1e\x18"
    bindkey = binascii.unhexlify("231d39c1d7cc1ab1aee224cd096db932")

    payload = encrypt_payload(
        data=data, mac=mac, uuid16=uuid16, count_id=count_id, key=bindkey
    )
    assert decrypt_aes_ccm(key=bindkey, mac=mac, data=payload) == {
        "humidity": 50.55,
        "temperature": 25.06,
    }


def test_decrypt_aes_ccm_invalid_packet_returns_none() -> None:
    """Malformed advertisements should not raise from decrypt_aes_ccm."""
    bindkey = binascii.unhexlify("231d39c1d7cc1ab1aee224cd096db932")
    mac = binascii.unhexlify("5448E68F80A5")
    assert decrypt_aes_ccm(key=bindkey, mac=mac, data=b"tooshort") is None
