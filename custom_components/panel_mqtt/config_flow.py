"""Config flow for Panel MQTT."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .const import CONF_DEVICE_ID, DEFAULT_DEVICE_ID, DEFAULT_NAME, DOMAIN


class PanelMqttConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure a panel by its MQTT topic prefix identifier."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID].strip().lower()
            if not device_id or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for c in device_id):
                errors[CONF_DEVICE_ID] = "invalid_device_id"
            else:
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME].strip(),
                    data={CONF_DEVICE_ID: device_id, CONF_NAME: user_input[CONF_NAME].strip()},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PanelMqttOptionsFlow(config_entry)


class PanelMqttOptionsFlow(config_entries.OptionsFlow):
    """Options flow placeholder; topics are derived from the device ID."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return self.async_create_entry(title="", data={})
