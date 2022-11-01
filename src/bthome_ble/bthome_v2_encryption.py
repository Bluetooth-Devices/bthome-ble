"""Example showing encoding and decoding of BTHome v2 advertisement"""
from __future__ import annotations

import binascii

from Cryptodome.Cipher import AES


def parse_value(data: bytes) -> dict[str, float]:
    """Parse decrypted payload to readable BTHome data"""
    vlength = len(data)
    if vlength >= 3:
        temp = round(int.from_bytes(data[1:3], "little", signed=False) * 0.01, 2)
        humi = round(int.from_bytes(data[4:6], "little", signed=False) * 0.01, 2)
        print("Temperature:", temp, "Humidity:", humi)
        return {"temperature": temp, "humidity": humi}
    print("MsgLength:", vlength, "HexValue:", data.hex())
    return {}


def decrypt_payload(
    payload: bytes, mic: bytes, key: bytes, nonce: bytes
) -> dict[str, float] | None:
    """Decrypt payload."""
    print("Nonce:", nonce.hex())
    print("CryptData:", payload.hex())
    print("Mic:", mic.hex())
    cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
    cipher.update(b"\x11")
    print()
    print("Starting Decryption data")
    try:
        data = cipher.decrypt_and_verify(payload, mic)
    except ValueError as error:
        print()
        print("Decryption failed:", error)
        return None
    print("Decryption succeeded, decrypted data:", data.hex())
    print()
    return parse_value(data=data)


def decrypt_aes_ccm(key: bytes, mac: bytes, data: bytes) -> dict[str, float] | None:
    """Decrypt AES CCM."""
    print("MAC:", mac.hex())
    print("Bindkey:", key.hex())
    adslength = len(data)
    if adslength > 15 and data[0] == 0xD2 and data[1] == 0xFC:
        pkt = data[: data[0] + 1]
        uuid = pkt[0:2]
        sw_version = pkt[2:3]
        encrypted_data = pkt[3:-8]
        count_id = pkt[-8:-4]
        mic = pkt[-4:]
        # nonce: mac [6], uuid16 [2], count_id [4] # 6+3+4 = 13 bytes
        nonce = b"".join([mac, uuid, sw_version, count_id])
        return decrypt_payload(encrypted_data, mic, key, nonce)
    else:
        print("Error: format packet!")
    return None


def encrypt_payload(
    data: bytes,
    mac: bytes,
    uuid16: bytes,
    sw_version: bytes,
    count_id: bytes,
    key: bytes,
) -> bytes:
    """Encrypt payload."""
    nonce = b"".join([mac, uuid16, sw_version, count_id])  # 6+2+1+4 = 13 bytes
    cipher = AES.new(key, AES.MODE_CCM, nonce=nonce, mac_len=4)
    cipher.update(b"\x11")
    ciphertext, mic = cipher.encrypt_and_digest(data)
    print("MAC:", mac.hex())
    print("Binkey:", key.hex())
    print("Data:", data.hex())
    print("Nonce:", nonce.hex())
    print("CryptData:", ciphertext.hex(), "Mic:", mic.hex())
    return b"".join([uuid16, sw_version, ciphertext, count_id, mic])


# =============================
# main()
# =============================
def main() -> None:
    """Example to encrypt and decrypt BTHome payload."""
    print()
    print("====== Test encode -----------------------------------------")
    data = bytes(bytearray.fromhex("02CA0903BF13"))  # BTHome data (not encrypted)
    parse_value(data)  # Print temperature and humidity

    print()
    print("Preparing data for encryption")
    count_id = bytes(bytearray.fromhex("00112233"))  # count id (change every message)
    mac = binascii.unhexlify("5448E68F80A5")  # MAC
    uuid16 = b"\xD2\xFC"
    sw_version = b"\x42"
    bindkey = binascii.unhexlify("231d39c1d7cc1ab1aee224cd096db932")

    payload = encrypt_payload(
        data=data,
        mac=mac,
        uuid16=uuid16,
        sw_version=sw_version,
        count_id=count_id,
        key=bindkey,
    )
    print()
    print("Encrypted data:", payload.hex())
    print()
    print("====== Test decode -----------------------------------------")
    decrypt_aes_ccm(key=bindkey, mac=mac, data=payload)


if __name__ == "__main__":
    main()
