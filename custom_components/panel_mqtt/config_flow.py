"""Config flow for Panel MQTT."""

from __future__ import annotations

from ipaddress import ip_address

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME

from .const import (
    CONF_BROADCAST_ADDRESS,
    CONF_DEVICE_ID,
    CONF_MAC_ADDRESS,
    CONF_MEDIA_PLAYER,
    DEFAULT_DEVICE_ID,
    DEFAULT_NAME,
    DOMAIN,
)


class PanelMqttConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure a panel by its MQTT topic prefix identifier."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID].strip().lower()
            mac_address = user_input.get(CONF_MAC_ADDRESS, "").strip().lower()
            if not device_id or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for c in device_id):
                errors[CONF_DEVICE_ID] = "invalid_device_id"
            elif mac_address and not _valid_mac(mac_address):
                errors[CONF_MAC_ADDRESS] = "invalid_mac_address"
            elif not _valid_broadcast(user_input.get(CONF_BROADCAST_ADDRESS, "255.255.255.255").strip()):
                errors[CONF_BROADCAST_ADDRESS] = "invalid_broadcast_address"
            elif user_input.get(CONF_MEDIA_PLAYER, "").strip() and not user_input[CONF_MEDIA_PLAYER].startswith("media_player."):
                errors[CONF_MEDIA_PLAYER] = "invalid_media_player"
            else:
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME].strip(),
                    data={
                        CONF_DEVICE_ID: device_id,
                        CONF_NAME: user_input[CONF_NAME].strip(),
                        CONF_MAC_ADDRESS: mac_address,
                        CONF_BROADCAST_ADDRESS: user_input.get(
                            CONF_BROADCAST_ADDRESS, "255.255.255.255"
                        ).strip(),
                        CONF_MEDIA_PLAYER: user_input.get(CONF_MEDIA_PLAYER, "").strip(),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID): str,
                    vol.Optional(CONF_MAC_ADDRESS, default=""): str,
                    vol.Optional(
                        CONF_BROADCAST_ADDRESS, default="255.255.255.255"
                    ): str,
                    vol.Optional(CONF_MEDIA_PLAYER, default=""): str,
                }
            ),
            errors=errors,
        )

def _valid_mac(value: str) -> bool:
    """Return whether value is a six-octet MAC address."""
    parts = value.split(":")
    return len(parts) == 6 and all(
        len(part) == 2 and all(char in "0123456789abcdef" for char in part)
        for part in parts
    )


def _valid_broadcast(value: str) -> bool:
    """Accept IPv4 broadcast targets only; Wake-on-LAN uses UDP/9."""
    try:
        return ip_address(value).version == 4
    except ValueError:
        return False
