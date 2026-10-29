"""Allow-listed kiosk action buttons."""

from homeassistant.components.button import ButtonEntity

from . import async_send_command, panel_device_info


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([
        PanelCommandButton(hass, entry, "chromium_restart", "Restart Chromium", "mdi:restart"),
        PanelCommandButton(hass, entry, "chromium_start", "Start Chromium", "mdi:play"),
        PanelCommandButton(hass, entry, "chromium_stop", "Stop Chromium", "mdi:stop"),
        PanelCommandButton(hass, entry, "status", "Refresh status", "mdi:refresh"),
    ])


class PanelCommandButton(ButtonEntity):
    _attr_has_entity_name = True

    def __init__(self, hass, entry, command, name, icon):
        self.hass = hass
        self.entry = entry
        self.command = command
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.data['device_id']}_{command}"

    @property
    def device_info(self):
        return panel_device_info(self.hass, self.entry)

    async def async_press(self):
        await async_send_command(self.hass, self.entry, self.command)
