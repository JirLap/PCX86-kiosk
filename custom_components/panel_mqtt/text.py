"""Text controls reported by the panel agent."""

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import SIGNAL_STATUS, async_send_command, panel_device_info, panel_state


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([PanelKioskUrlText(hass, entry)])


class PanelKioskUrlText(TextEntity):
    """Edit the URL opened by the kiosk browser."""

    _attr_has_entity_name = True
    _attr_name = "Kiosk URL"
    _attr_icon = "mdi:link-variant"
    _attr_mode = TextMode.URL
    _attr_native_min = 1
    _attr_native_max = 2048

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.data['device_id']}_kiosk_url"

    @property
    def device_info(self):
        return panel_device_info(self.hass, self.entry)

    @property
    def native_value(self):
        return str(panel_state(self.hass, self.entry).get("kiosk_url", ""))

    @property
    def available(self):
        return panel_state(self.hass, self.entry).get("availability") == "online"

    async def async_set_value(self, value):
        await async_send_command(self.hass, self.entry, f"set_url:{value.strip()}")

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_STATUS.format(self.entry.entry_id),
                self.async_write_ha_state,
            )
        )
