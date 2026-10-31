"""Numeric controls for supported panel capabilities."""

from homeassistant.components.number import NumberEntity
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import SIGNAL_STATUS, async_send_command, panel_device_info, panel_state


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([
        PanelVolumeNumber(hass, entry),
        PanelMicrophoneVolumeNumber(hass, entry),
        PanelBrightnessNumber(hass, entry),
    ])


class PanelVolumeNumber(NumberEntity):
    """Set the Debian output volume using the agent's validated command."""

    _attr_has_entity_name = True
    _attr_translation_key = "system_volume"
    _attr_icon = "mdi:volume-high"
    _attr_native_min_value = 0
    _attr_native_max_value = 150
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.data['device_id']}_system_volume"

    @property
    def device_info(self):
        return panel_device_info(self.hass, self.entry)

    @property
    def native_value(self):
        value = panel_state(self.hass, self.entry).get("system_volume")
        return float(value) if value is not None else None

    @property
    def available(self):
        state = panel_state(self.hass, self.entry)
        return state.get("availability") == "online" and "system_volume" in state

    async def async_set_native_value(self, value):
        await async_send_command(
            self.hass, self.entry, f"volume_set:{round(value)}"
        )

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_STATUS.format(self.entry.entry_id),
                self.async_write_ha_state,
            )
        )


class PanelBrightnessNumber(PanelVolumeNumber):
    """Set the laptop panel backlight when its driver exposes a control."""

    _attr_translation_key = "screen_brightness"
    _attr_icon = "mdi:brightness-6"
    _attr_native_max_value = 100
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, hass, entry):
        super().__init__(hass, entry)
        self._attr_unique_id = f"{entry.data['device_id']}_screen_brightness"

    @property
    def native_value(self):
        value = panel_state(self.hass, self.entry).get("screen_brightness")
        return float(value) if value is not None else None

    @property
    def available(self):
        state = panel_state(self.hass, self.entry)
        return state.get("availability") == "online" and "screen_brightness" in state

    async def async_set_native_value(self, value):
        await async_send_command(
            self.hass, self.entry, f"brightness_set:{round(value)}"
        )


class PanelMicrophoneVolumeNumber(PanelVolumeNumber):
    """Set microphone capture gain when PulseAudio/PipeWire exposes a source."""

    _attr_translation_key = "microphone_volume"
    _attr_icon = "mdi:microphone"

    def __init__(self, hass, entry):
        super().__init__(hass, entry)
        self._attr_unique_id = f"{entry.data['device_id']}_microphone_volume"

    @property
    def native_value(self):
        value = panel_state(self.hass, self.entry).get("microphone_volume")
        return float(value) if value is not None else None

    @property
    def available(self):
        state = panel_state(self.hass, self.entry)
        return state.get("availability") == "online" and "microphone_volume" in state

    async def async_set_native_value(self, value):
        await async_send_command(
            self.hass, self.entry, f"mic_volume_set:{round(value)}"
        )

