import dataclasses


@dataclasses.dataclass
class DeviceEntry:
    name: str
    model: str
    manufacturer: str


DEVICE_TYPES: dict[int, DeviceEntry] = {
    0x0001: DeviceEntry(
        name="ATC Temperature/Humidity Sensor",
        model="LYWSD03MMC",
        manufacturer="pvvx",
    ),
    0x0002: DeviceEntry(
        name="Plant Sensor",
        model="b-parasite",
        manufacturer="b-parasite",
    ),
}
