"""Constants for the PCX86-kiosk integration."""

DOMAIN = "pcx86_kiosk"
DISCOVERY_ROOT = "pcx86_kiosk/discovery"
TOPIC_ROOT = "pcx86_kiosk"

CONF_DEVICE_ID = "device_id"
CONF_NAME = "name"
CONF_AREA_ID = "area_id"
CONF_MAC_ADDRESS = "mac_address"
CONF_BROADCAST_ADDRESS = "broadcast_address"
CONF_MEDIA_PLAYER = "media_player_entity"

DEFAULT_NAME = "PCX86 kiosk"
CONFIRMATION_TIMEOUT = 10

PLATFORMS = [
    "sensor", "binary_sensor", "switch", "button", "number", "text", "camera",
    "media_player",
]

DEVICE_METADATA_KEYS = (
    "hostname",
    "ip_address",
    "network_interface",
    "broadcast_address",
    "mac_address",
    "wifi_ssid",
    "wifi_signal_dbm",
    "os_name",
    "os_version",
    "kernel_version",
    "architecture",
    "manufacturer",
    "model",
)

ATTR_AVAILABILITY = "availability"
ATTR_MONITOR = "monitor"
ATTR_CHROMIUM = "chromium"
ATTR_LAST_COMMAND = "last_command"
ATTR_RESULT = "result"
ATTR_UPDATED = "updated"
