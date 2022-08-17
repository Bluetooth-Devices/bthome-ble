# Usage BThome for DIY sensors

## Introduction

The BThome BLE format was originally developed as HA BLE for the custom Home Assistant integration "BLE monitor", and is soon also available for the official Home Assistant Bluetooth integration.
The BThome BLE format allows you to create for your own DIY BLE sensors, which can be read by the Home Assistant Bluetooth integration.
This format tries to provide an energy effective, but still flexible BLE format that can be customized to your own needs.
A proof of concept is the latest [ATC firmware](https://github.com/pvvx/ATC_MiThermometer), which is supporting the BThome BLE format (firmware version 3.7 and up). Note that in firmware 3.7 it is called `HA BLE` format.

To use this package, import it:

```python
import bthome_ble
```

## The BThome BLE format

The `BThome BLE` format can best be explained with an example. A BLE advertisement is a long message with bytes (bytestring).

```
043E1B02010000A5808FE648540F0201060B161C182302C4090303BF13CC
```

This message is split up in three parts, the **header**, the **advertising payload** and an **RSSI value**

- Header: `043E1B02010000A5808FE648540F`
- Adverting payload `0201060B161C182302C4090303BF13`
- RSSI value `CC`

## Header

The first part `043E1B02010000A5808FE648540F` is the header of the message and contains, amongst others

- the length of the message in the 3rd byte (`0x1B` in hex is 27 in decimals, meaning 27 bytes after the third byte = 30 bytes in total)
- the MAC address in reversed order in byte 8-13 (`A5808FE64854`, in reversed order, this corresponds to a MAC address `54:48:E6:8F:80:A5`)
- the length of the advertising payload in byte 14 (`0x0F` = 15)

## Advertising payload

The second part `0201060B161C182302C4090303BF13` contains the advertising payload, and can consist of one or more **Advertising Data (AD) elements**. Each element contains the following:

- 1st byte: length of the element (excluding the length byte itself)
- 2nd byte: AD type – specifies what data is included in the element
- AD data – one or more bytes - the meaning is defined by the AD type

In the `BThome BLE` format, the advertising payload should contain the following two AD elements:

- Flags (`0x01`)
- Service Data - 16-bit UUID (`0x16`)

In the example, we have:

- First AD element: `020106`

  - `0x02` = length (2 bytes)
    `0x01` = Flags
    `0x06` = in bits, this is `00000110`. Bit 1 and bit 2 are 1, meaning:
    Bit 1: “LE General Discoverable Mode”
    Bit 2: “BR/EDR Not Supported”
  - This part always has to be added, and is always the same (`0x020106`)

- Second AD element: `0B161C182302C4090303BF13` (BThome BLE data)

  - `0x0B` = length (11 bytes)
    `0x16` = Service Data - 16-bit UUID
    `0x1C182302C4090303BF13` = BThome BLE data

### BThome BLE data format (non-encrypted)

The BThome BLE data is the part that contains the data. The data can contain multiple measurements. We continue with the example from above.

- BThome BLE data = `0x1C182302C4090303BF13`
  - `0x1C18` = The first two byte are the UUID16, which are assigned numbers that can be found in [this official document]https://btprodspecificationrefs.blob.core.windows.net/assigned-values/16-bit%20UUID%20Numbers%20Document.pdf by the Bluetooth organization. For BThome BLE we use the so called `GATT Service` = `User Data` (`0x1C18`) for non-encrypted messages. For encrypted messages, we use `GATT Service` = `Bond Management` (`0x1E18`). More information about encryption can be found further down this page. This part should always be `0x1C18` (non-encrypted) or `0x1E18` (encrypted), as it is used to recognize a BThome BLE message.
  - `0x2302C409` = Temperature packet
  - `0x0303BF13` = Humidity packet

Let's explain how the last two data packets work. The temperature packet is used as example.

- The first byte `0x23` (in bits `00100011`) is giving information about:
  - The object length (bit 0-4): `00011` = 3 bytes (excluding the length byte itself)
  - The object format (bit 5-7) `001` = 1 = Signed Integer (see table below)

| type | bit 5-7 | format | Data type              |
| ---- | ------- | ------ | ---------------------- |
| `0`  | `000`   | uint   | unsingned integer      |
| `1`  | `001`   | int    | signed integer         |
| `2`  | `010`   | float  | float                  |
| `3`  | `011`   | string | string                 |
| `4`  | `100`   | MAC    | MAC address (reversed) |

- The second byte `0x02` is defining the type of measurement (temperature, see table below)
- The remaining bytes `0xC409` is the object value (little endian), which will be multiplied with the factor in the table below to get a sufficient number of digits.
  - The object length is telling us that the value is 2 bytes long (object length = 3 bytes minus the second byte) and the object format is telling us that the value is a Signed Integer (positive or negative integer).
  - `0xC409` as unsigned integer in little endian is equal to 2500.
  - The factor for a temperature measurement is 0.01, resulting in a temperature of 25.00°C

At the moment, the following sensors are supported. A preferred data type is given for your convenience, which should give you a short data message and at the same time a sufficient number of digits to display your data with high accuracy in Home Assistant. But you are free to use a different data type. If you want another sensor, let us know by creating a new issue on Github.

| Object id | Property    | Preferred data type | Factor | example          | result       | Unit in HA | Notes   |
| --------- | ----------- | ------------------- | ------ | ---------------- | ------------ | ---------- | ------- |
| `0x00`    | packet id   | uint8 (1 byte)      | 1      | `020009`         | 9            |            | [1] [2] |
| `0x01`    | battery     | uint8 (1 byte)      | 1      | `020161`         | 97           | `%`        |         |
| `0x02`    | temperature | sint16 (2 bytes)    | 0.01   | `2302CA09`       | 25.06        | `°C`       |         |
| `0x03`    | humidity    | uint16 (2 bytes)    | 0.01   | `0303BF13`       | 50.55        | `%`        |         |
| `0x04`    | pressure    | uint24 (3 bytes)    | 0.01   | `0404138A01`     | 1008.83      | `mbar`     |         |
| `0x05`    | illuminance | uint24 (3 bytes)    | 0.01   | `0405138A14`     | 13460.67     | `lux`      |         |
| `0x06`    | weight      | uint16 (2 byte)     | 0.01   | `03065E1F`       | 80.3         | `kg`       | [1] [3] |
| `0x07`    | weight unit | string (2 bytes)    | None   | `63076B67`       | "kg"         |            | [1] [3] |
| `0x08`    | dewpoint    | sint16 (2 bytes)    | 0.01   | `2308CA06`       | 17.386       | `°C`       | [1]     |
| `0x09`    | count       | uint                | 1      | `020960`         | 96           |            | [1]     |
| `0X0A`    | energy      | uint24 (3 bytes)    | 0.001  | `040A138A14`     | 1346.067     | `kWh`      |         |
| `0x0B`    | power       | uint24 (3 bytes)    | 0.01   | `040B021B00`     | 69.14        | `W`        |         |
| `0x0C`    | voltage     | uint16 (2 bytes)    | 0.001  | `030C020C`       | 3.074        | `V`        |         |
| `0x0D`    | pm2.5       | uint16 (2 bytes)    | 1      | `030D120C`       | 3090         | `kg/m3`    |         |
| `0x0E`    | pm10        | uint16 (2 bytes)    | 1      | `030E021C`       | 7170         | `kg/m3`    |         |
| `0x0F`    | boolean     | uint8 (1 byte)      | 1      | `020F01`         | 1 (True)     | `True`     | [1]     |
| `0x10`    | switch      | uint8 (1 byte)      | 1      | `021001`         | 1 (True)     | `on`       | [1]     |
| `0x11`    | opening     | uint8 (1 byte)      | 1      | `021100`         | 0 (false)    | `closed`   | [1]     |
| `0x12`    | co2         | uint16 (2 bytes)    | 1      | `0312E204`       | 1250         | `ppm`      |         |
| `0x13`    | voc         | uint16 (2 bytes)    | 1      | `03133301`       | 307          | `ug/m3`    |         |
|           | mac         | 6 bytes (reversed)  |        | `86A6808FE64854` | 5448E68F80A6 |            | [1] [4] |

**Notes**

Full example payloads are given in the test tests.

**_1. Not supported measurement type_**

The sensors with [1] is the last column are not yet supported in the official HA integration and will be added soon.
For these measurement types, use [BLE monitor](https://github.com/custom_components/ble_monitor) for the time being.

**_2. packet id (not supported in HA integration yet)_**

The `packet id` is optional and was used to filter duplicate data in BLE monitor. This functionality is not supported in the official Home Assistant integration.

**_3. weight (unit) (not supported in HA integration yet)_**

The `weight unit` is in `kg` by default, but can be set with the weight unit property. Examples of `weight unit` packets are:

- kg (`63076B67`)
- lbs (`64076C6273`)
- jin (`64076A696E`)

**_4. mac (not supported in HA integration yet)_**

The `mac` functionality is not yet supported in the official Home Assistant integration, but was developed for BLE monitor.
We will most likely add this in a future update.

You don't have to specify the `mac` address in the advertising payload, as it is already included in the [header](#header).
However, you can overwrite the `mac` by specifying it in the advertising payload.
To do this, set the first byte to `0x86` (meaning: object type = 4 (`mac`) and object length = 6), followed by the MAC in reversed order. No Object id is needed.

### BThome BLE data format (encrypted)

You can also choose to send the data in an encrypted way, which gives you extra security.
Unencrypted BLE advertisements can be read by everyone, even your neighbour with Home Assistant and BLE Monitor should in theory be able to receive your BLE data.
However, when you use encryption, it will be useless for anyone else, as long as he or she doesn't have the encryption key.
The encryption key should be 16 bytes long key (32 characters).
More information on how to encrypt your messages is demonstrated in [this script](https://github.com/custom-components/ble_monitor/blob/master/custom_components/ble_monitor/ble_parser/ha_ble_encryption.py).
BThome is using an AES encryption (CCM mode). Don't forget to set the encryption key in your Home Assistant device settings.
