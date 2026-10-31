"""Allow-listed panel actions, including MQTT display sleep/wake."""

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import SIGNAL_STATUS, async_send_command, panel_device_info, panel_state


COMMAND_BUTTONS = (
    ("kiosk_refresh", "Refresh kiosk page", "mdi:refresh"),
    ("chromium_restart", "Restart kiosk browser", "mdi:restart"),
    ("chromium_start", "Start kiosk browser", "mdi:play"),
    ("chromium_stop", "Stop kiosk browser", "mdi:stop"),
    ("sleep", "Sleep panel", "mdi:sleep"),
    ("reboot", "Restart notebook", "mdi:restart-alert"),
    ("shutdown", "Shut down notebook", "mdi:power"),
    ("status", "Refresh status", "mdi:information-refresh"),
)


async def async_setup_entry(hass, entry, async_add_entities):
    entities = [PanelCommandButton(hass, entry, *item) for item in COMMAND_BUTTONS]
    entities.append(PanelWakeButton(hass, entry))
    async_add_entities(entities)


class PanelCommandButton(ButtonEntity):
    """Publish one fixed command supported by the Debian agent."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass, entry, command, name, icon):
        self.hass = hass
        self.entry = entry
        self.command = command
        self._attr_translation_key = command
        self._attr_icon = icon
        # Retain the existing entity ID across the safer sleep-command change.
        unique_key = "suspend" if command == "sleep" else command
        self._attr_unique_id = f"{entry.data['device_id']}_{unique_key}"

    @property
    def device_info(self):
        return panel_device_info(self.hass, self.entry)

    @property
    def available(self):
        return panel_state(self.hass, self.entry).get("availability") == "online"

    async def async_press(self):
        await async_send_command(self.hass, self.entry, self.command)

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_STATUS.format(self.entry.entry_id),
                self.async_write_ha_state,
            )
        )


class PanelWakeButton(PanelCommandButton):
    """Restore the screen over MQTT; the notebook remains connected in sleep."""

    _attr_has_entity_name = True
    _attr_translation_key = "wake_system"
    _attr_icon = "mdi:monitor"

    def __init__(self, hass, entry):
        super().__init__(hass, entry, "wake", "Wake panel", "mdi:monitor")
        self._attr_translation_key = "wake_system"
        self._attr_unique_id = f"{entry.data['device_id']}_wake_system"
