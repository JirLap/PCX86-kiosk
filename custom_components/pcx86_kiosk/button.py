"""Allow-listed panel actions and Wake-on-LAN."""

import socket

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import SIGNAL_STATUS, async_send_command, panel_device_info, panel_state
from .const import CONF_BROADCAST_ADDRESS, CONF_MAC_ADDRESS


COMMAND_BUTTONS = (
    ("kiosk_refresh", "Refresh kiosk page", "mdi:refresh"),
    ("chromium_restart", "Restart kiosk browser", "mdi:restart"),
    ("chromium_start", "Start kiosk browser", "mdi:play"),
    ("chromium_stop", "Stop kiosk browser", "mdi:stop"),
    ("suspend", "Sleep notebook", "mdi:sleep"),
    ("reboot", "Restart notebook", "mdi:restart-alert"),
    ("shutdown", "Shut down notebook", "mdi:power"),
    ("status", "Refresh status", "mdi:information-refresh"),
)


async def async_setup_entry(hass, entry, async_add_entities):
    entities = [PanelCommandButton(hass, entry, *item) for item in COMMAND_BUTTONS]
    if entry.data.get(CONF_MAC_ADDRESS):
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
        self._attr_unique_id = f"{entry.data['device_id']}_{command}"

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


class PanelWakeButton(ButtonEntity):
    """Send a magic packet; this remains pressable while the panel is asleep."""

    _attr_has_entity_name = True
    _attr_translation_key = "wake_system"
    _attr_icon = "mdi:lan-connect"

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.data['device_id']}_wake_system"

    @property
    def device_info(self):
        return panel_device_info(self.hass, self.entry)

    @property
    def available(self):
        return True

    async def async_press(self):
        mac = self.entry.data[CONF_MAC_ADDRESS]
        broadcast = self.entry.data.get(CONF_BROADCAST_ADDRESS, "255.255.255.255")
        await self.hass.async_add_executor_job(_send_magic_packet, mac, broadcast)


def _send_magic_packet(mac: str, broadcast: str) -> None:
    """Send a standard Wake-on-LAN packet over UDP broadcast."""
    address = bytes.fromhex(mac.replace(":", ""))
    packet = b"\xff" * 6 + address * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, (broadcast, 9))
