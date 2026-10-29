"""Panel status sensors."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import SIGNAL_STATUS, panel_device_info, panel_state
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([PanelStatusSensor(hass, entry)])


class PanelStatusSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Reported status"
    _attr_icon = "mdi:information-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.data['device_id']}_reported_status"

    @property
    def device_info(self):
        return panel_device_info(self.hass, self.entry)

    @property
    def native_value(self):
        value = panel_state(self.hass, self.entry).get("result")
        return str(value) if value is not None else None

    @property
    def extra_state_attributes(self):
        return {key: panel_state(self.hass, self.entry).get(key) for key in ("last_command", "monitor", "chromium")}

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_STATUS.format(self.entry.entry_id), self.async_write_ha_state))
