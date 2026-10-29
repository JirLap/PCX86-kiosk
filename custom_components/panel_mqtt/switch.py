"""Monitor power switch."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import SIGNAL_STATUS, async_send_command, panel_device_info, panel_state


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([PanelMonitorSwitch(hass, entry)])


class PanelMonitorSwitch(SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "Monitor"
    _attr_icon = "mdi:monitor"

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.data['device_id']}_monitor"

    @property
    def device_info(self):
        return panel_device_info(self.hass, self.entry)

    @property
    def is_on(self):
        return panel_state(self.hass, self.entry).get("monitor") == "on"

    async def async_turn_on(self, **kwargs):
        await async_send_command(self.hass, self.entry, "wake")

    async def async_turn_off(self, **kwargs):
        await async_send_command(self.hass, self.entry, "sleep")

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_STATUS.format(self.entry.entry_id), self.async_write_ha_state))
