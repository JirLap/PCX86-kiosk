"""MQTT integration for Debian kiosk panels."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.components import mqtt

from homeassistant.const import CONF_NAME

from .const import CONF_DEVICE_ID, DOMAIN, PLATFORMS

SIGNAL_STATUS = "panel_mqtt_status_{}"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one panel and subscribe to its retained status topic."""
    device_id = entry.data[CONF_DEVICE_ID]
    topic_root = f"panel/{device_id}"
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "device_id": device_id,
        "name": entry.data[CONF_NAME],
        "topic_root": topic_root,
        "status": {},
    }

    async def status_received(msg):
        try:
            payload = msg.payload
            if isinstance(payload, bytes):
                payload = payload.decode()
            import json
            state = json.loads(payload)
            if not isinstance(state, dict):
                return
        except (ValueError, UnicodeDecodeError):
            return
        hass.data[DOMAIN][entry.entry_id]["status"] = state
        async_dispatcher_send(hass, SIGNAL_STATUS.format(entry.entry_id))

    await mqtt.async_subscribe(hass, f"{topic_root}/status", status_received, qos=1)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a panel."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


def panel_device_info(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    """Return shared device registry information."""
    data = hass.data[DOMAIN][entry.entry_id]
    return {
        "identifiers": {(DOMAIN, data["device_id"])},
        "name": data["name"],
        "manufacturer": "Debian kiosk",
        "model": "XFCE / Chromium panel",
    }


def panel_state(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    """Return the last reported state."""
    return hass.data[DOMAIN][entry.entry_id]["status"]


async def async_send_command(hass: HomeAssistant, entry: ConfigEntry, command: str) -> None:
    """Publish one allow-listed command supported by the existing agent."""
    await mqtt.async_publish(
        hass,
        f"panel/{entry.data[CONF_DEVICE_ID]}/command",
        command,
        qos=1,
        retain=False,
    )
