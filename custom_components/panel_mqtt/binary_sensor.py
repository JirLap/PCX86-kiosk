"""Panel availability sensor."""

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import SIGNAL_STATUS, panel_device_info, panel_state


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([PanelOnlineSensor(hass, entry)])


class PanelOnlineSensor(BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Online"
    _attr_device_class = "connectivity"

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.data['device_id']}_online"

    @property
    def device_info(self):
        return panel_device_info(self.hass, self.entry)

    @property
    def is_on(self):
        return panel_state(self.hass, self.entry).get("availability") == "online"

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_STATUS.format(self.entry.entry_id), self.async_write_ha_state))
