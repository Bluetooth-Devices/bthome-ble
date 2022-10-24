"""Tests for the parser of BLE advertisements in BTHome V2 format."""
import binascii

from bthome_ble.bthome_v2_encryption import decrypt_aes_ccm, encrypt_payload


def test_encryption_example():
    """Test BTHome V2 encryption example."""
    data = bytes(bytearray.fromhex("02CA0903BF13"))  # BTHome data (not encrypted)
    count_id = bytes(bytearray.fromhex("00112233"))  # count id (change every message)
    mac = binascii.unhexlify("5448E68F80A5")  # MAC
    uuid16 = b"\xd2\xfc"
    sw_version = b"\x42"
    bindkey = binascii.unhexlify("231d39c1d7cc1ab1aee224cd096db932")

    encrypted_payload = encrypt_payload(
        data=data,
        mac=mac,
        uuid16=uuid16,
        sw_version=sw_version,
        count_id=count_id,
        key=bindkey,
    )
    assert (
        encrypted_payload
        == b"\xd2\xfc\x42\x69\x6c\x8c\x91\x85\x6f\x00\x11\x22\x33\x04\x5b\xbc\x2a"
    )
    assert decrypt_aes_ccm(key=bindkey, mac=mac, data=encrypted_payload) == {
        "humidity": 50.55,
        "temperature": 25.06,
    }
