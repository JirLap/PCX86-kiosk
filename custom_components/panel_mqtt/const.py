"""Constants for the Panel MQTT integration."""

DOMAIN = "panel_mqtt"
CONF_DEVICE_ID = "device_id"
CONF_NAME = "name"
CONF_MAC_ADDRESS = "mac_address"
CONF_BROADCAST_ADDRESS = "broadcast_address"
CONF_MEDIA_PLAYER = "media_player_entity"

DEFAULT_NAME = "Panel"
DEFAULT_DEVICE_ID = "patro"
CONFIRMATION_TIMEOUT = 10

PLATFORMS = [
    "sensor", "binary_sensor", "switch", "button", "number", "text", "camera",
    "media_player",
]

ATTR_AVAILABILITY = "availability"
ATTR_MONITOR = "monitor"
ATTR_CHROMIUM = "chromium"
ATTR_LAST_COMMAND = "last_command"
ATTR_RESULT = "result"
ATTR_UPDATED = "updated"

