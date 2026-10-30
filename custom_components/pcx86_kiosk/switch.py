"""Panel screen, kiosk, camera, and microphone controls."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import SIGNAL_STATUS, async_send_command, panel_device_info, panel_state


SWITCHES = (
    ("screen", "Screen", "monitor", "wake", "sleep", "mdi:monitor"),
    ("kiosk", "Kiosk browser", "chromium", "kiosk_start", "kiosk_stop", "mdi:web"),
    ("camera", "Camera", "camera", "camera_start", "camera_stop", "mdi:camera"),
    (
        "microphone",
        "Microphone",
        "microphone_muted",
        "mic_unmute",
        "mic_mute",
        "mdi:microphone",
    ),
    (
        "audio_mute",
        "Mute speakers",
        "system_muted",
        "audio_mute",
        "audio_unmute",
        "mdi:volume-mute",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        [PanelControlSwitch(hass, entry, *description) for description in SWITCHES]
    )


class PanelControlSwitch(SwitchEntity):
    """An allow-listed switch backed by one agent-reported status key."""

    _attr_has_entity_name = True

    def __init__(self, hass, entry, key, name, status_key, command_on, command_off, icon):
        self.hass = hass
        self.entry = entry
        self.key = key
        self.status_key = status_key
        self.command_on = command_on
        self.command_off = command_off
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.data['device_id']}_{key}"

    @property
    def device_info(self):
        return panel_device_info(self.hass, self.entry)

    @property
    def is_on(self):
        value = panel_state(self.hass, self.entry).get(self.status_key)
        if self.key == "microphone":
            return value not in (True, "on", "muted")
        if self.key == "audio_mute":
            return value in (True, "on", "muted")
        if self.status_key == "monitor":
            return value == "on"
        return value in ("running", "on", True)

    @property
    def available(self):
        state = panel_state(self.hass, self.entry)
        if self.key == "screen":
            return state.get("availability") == "online"
        return state.get("availability") == "online" and self.status_key in state

    async def async_turn_on(self, **kwargs):
        await async_send_command(self.hass, self.entry, self.command_on)

    async def async_turn_off(self, **kwargs):
        await async_send_command(self.hass, self.entry, self.command_off)

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_STATUS.format(self.entry.entry_id),
                self.async_write_ha_state,
            )
        )
