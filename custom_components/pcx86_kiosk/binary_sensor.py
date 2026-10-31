"""Connectivity and capability status."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import SIGNAL_STATUS, panel_device_info, panel_state


ENTITIES = (
    ("availability", "Online", "connectivity", "mdi:lan-connect"),
    ("monitor", "Screen", "power", "mdi:monitor"),
    ("chromium", "Kiosk browser", None, "mdi:web"),
    ("camera", "Camera", None, "mdi:camera"),
    ("microphone_muted", "Microphone muted", None, "mdi:microphone-off"),
)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [PanelStateBinarySensor(hass, entry, *description) for description in ENTITIES]
    )


class PanelStateBinarySensor(BinarySensorEntity):
    """Map boolean-like values in the agent's status JSON."""

    _attr_has_entity_name = True

    def __init__(self, hass, entry, key, name, device_class, icon):
        self.hass = hass
        self.entry = entry
        self.key = key
        self._attr_translation_key = key
        self._attr_device_class = device_class
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.data['device_id']}_{key}"

    @property
    def device_info(self):
        return panel_device_info(self.hass, self.entry)

    @property
    def is_on(self):
        value = panel_state(self.hass, self.entry).get(self.key)
        if self.key == "availability":
            return value == "online"
        if self.key == "monitor":
            return value == "on"
        if self.key == "chromium":
            return value in ("running", "on", True)
        if self.key == "camera":
            return value in ("on", "running", True)
        if self.key == "microphone_muted":
            return value in (True, "on", "muted")
        return None

    @property
    def available(self):
        state = panel_state(self.hass, self.entry)
        if self.key == "availability":
            return True
        return state.get("availability") == "online" and self.key in state

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_STATUS.format(self.entry.entry_id),
                self.async_write_ha_state,
            )
        )
