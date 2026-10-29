"""Constants for the Panel MQTT integration."""

DOMAIN = "panel_mqtt"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"
CONF_NAME = "name"

DEFAULT_NAME = "Panel"
DEFAULT_DEVICE_ID = "patro"
CONFIRMATION_TIMEOUT = 10

PLATFORMS = ["sensor", "binary_sensor", "switch", "button"]

ATTR_AVAILABILITY = "availability"
ATTR_MONITOR = "monitor"
ATTR_CHROMIUM = "chromium"
ATTR_LAST_COMMAND = "last_command"
ATTR_RESULT = "result"

