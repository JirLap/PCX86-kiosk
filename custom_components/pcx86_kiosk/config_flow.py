"""MQTT discovery flow for PCX86-kiosk panels."""

from __future__ import annotations

import json
import re
from ipaddress import ip_address
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import (
    CONF_AREA_ID,
    CONF_BROADCAST_ADDRESS,
    CONF_DEVICE_ID,
    CONF_MAC_ADDRESS,
    CONF_MEDIA_PLAYER,
    DEFAULT_NAME,
    DEVICE_METADATA_KEYS,
    DISCOVERY_ROOT,
    DOMAIN,
    TOPIC_ROOT,
)

_DEVICE_ID_RE = re.compile(r"^[a-z0-9_-]{1,64}$")
_MAC_RE = re.compile(r"^(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$")


class PCX86KioskConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Create a config entry from a retained MQTT announcement."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovered: dict[str, Any] = {}

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return optional settings kept outside the discovery confirmation."""
        return PCX86KioskOptionsFlow()

    async def async_step_user(self, user_input=None):
        """Tell manual setup users to wait for MQTT discovery."""
        return self.async_abort(reason="no_devices_found")

    async def async_step_mqtt(self, discovery_info):
        """Validate an MQTT announcement and ask the user to confirm it."""
        try:
            payload = discovery_info.payload
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")
            announcement = json.loads(payload)
        except (AttributeError, UnicodeDecodeError, ValueError, TypeError):
            return self.async_abort(reason="invalid_discovery")

        if not isinstance(announcement, dict):
            return self.async_abort(reason="invalid_discovery")

        device_id = announcement.get(CONF_DEVICE_ID)
        if not isinstance(device_id, str) or not _DEVICE_ID_RE.fullmatch(device_id):
            return self.async_abort(reason="invalid_discovery")

        topic_root = f"{TOPIC_ROOT}/{device_id}"
        if discovery_info.topic != f"{DISCOVERY_ROOT}/{device_id}":
            return self.async_abort(reason="invalid_discovery")
        if announcement.get("status_topic") != f"{topic_root}/status":
            return self.async_abort(reason="invalid_discovery")
        if announcement.get("command_topic") != f"{topic_root}/command":
            return self.async_abort(reason="invalid_discovery")

        mac_address = announcement.get(CONF_MAC_ADDRESS, "")
        if mac_address and (
            not isinstance(mac_address, str) or not _MAC_RE.fullmatch(mac_address)
        ):
            return self.async_abort(reason="invalid_discovery")

        await self.async_set_unique_id(device_id)
        updates = {
            key: announcement[key]
            for key in DEVICE_METADATA_KEYS
            if key in announcement and isinstance(announcement[key], (str, int, float))
        }
        updates[CONF_MAC_ADDRESS] = mac_address.lower() if mac_address else ""
        updates[CONF_BROADCAST_ADDRESS] = _valid_ipv4(
            announcement.get(CONF_BROADCAST_ADDRESS)
        )
        self._abort_if_unique_id_configured(updates=updates)

        self._discovered = {
            CONF_DEVICE_ID: device_id,
            CONF_MAC_ADDRESS: updates[CONF_MAC_ADDRESS],
            CONF_BROADCAST_ADDRESS: updates[CONF_BROADCAST_ADDRESS]
            or "255.255.255.255",
            "status_topic": f"{topic_root}/status",
            "command_topic": f"{topic_root}/command",
            **{
                key: value
                for key, value in updates.items()
                if key in DEVICE_METADATA_KEYS
            },
        }
        discovered_name = announcement.get("name") or announcement.get("hostname")
        if not isinstance(discovered_name, str) or not discovered_name.strip():
            discovered_name = DEFAULT_NAME
        self._discovered_name = discovered_name.strip()
        self.context["title_placeholders"] = {"name": self._discovered_name}
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None):
        """Ask only for the HA device name and its area."""
        if user_input is not None:
            name = user_input[CONF_NAME].strip() or self._discovered_name
            area_id = user_input.get(CONF_AREA_ID)
            self._discovered.update(
                {
                    CONF_NAME: name,
                    CONF_AREA_ID: area_id,
                    CONF_MEDIA_PLAYER: "",
                }
            )
            return self.async_create_entry(title=name, data=self._discovered)

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={"name": self._discovered_name},
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=self._discovered_name): str,
                    vol.Optional(CONF_AREA_ID): selector.AreaSelector(),
                }
            ),
        )


class PCX86KioskOptionsFlow(config_entries.OptionsFlow):
    """Configure an optional Music Assistant player after device discovery."""

    async def async_step_init(self, user_input=None):
        """Select the Sendspin media-player entity, if one is used."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_MEDIA_PLAYER,
                        default=self.config_entry.options.get(CONF_MEDIA_PLAYER),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="media_player")
                    ),
                }
            ),
        )


def _valid_ipv4(value: Any) -> str:
    """Return a valid IPv4 broadcast address, or an empty string."""
    if not isinstance(value, str):
        return ""
    try:
        return str(ip_address(value)) if ip_address(value).version == 4 else ""
    except ValueError:
        return ""
