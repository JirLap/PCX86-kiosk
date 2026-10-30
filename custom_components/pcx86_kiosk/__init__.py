"""MQTT integration for Debian kiosk panels."""

from __future__ import annotations

import json

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.components import mqtt

from .const import (
    CONF_AREA_ID,
    CONF_BROADCAST_ADDRESS,
    CONF_DEVICE_ID,
    CONF_MAC_ADDRESS,
    CONF_NAME,
    DOMAIN,
    PLATFORMS,
    TOPIC_ROOT,
)

SIGNAL_STATUS = "pcx86_kiosk_status_{}"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a discovered panel and subscribe to its retained status topic."""
    if not await mqtt.async_wait_for_mqtt_client(hass):
        return False

    device_id = entry.data[CONF_DEVICE_ID]
    topic_root = f"{TOPIC_ROOT}/{device_id}"
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
                payload = payload.decode("utf-8")
            state = json.loads(payload)
            if not isinstance(state, dict):
                return
        except (ValueError, UnicodeDecodeError, TypeError):
            return

        hass.data[DOMAIN][entry.entry_id]["status"] = state
        _async_update_device_registry(hass, entry, state)
        async_dispatcher_send(hass, SIGNAL_STATUS.format(entry.entry_id))

    hass.data[DOMAIN][entry.entry_id]["unsubscribe"] = await mqtt.async_subscribe(
        hass, f"{topic_root}/status", status_received, qos=1
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _async_update_device_registry(hass, entry, entry.data)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a panel."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data = hass.data[DOMAIN].pop(entry.entry_id)
        data["unsubscribe"]()
    return unload_ok


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entities after an optional media-player selection changes."""
    await hass.config_entries.async_reload(entry.entry_id)


def _async_update_device_registry(
    hass: HomeAssistant, entry: ConfigEntry, metadata: dict
) -> None:
    """Keep the HA device record current as MQTT reports network details."""
    registry = dr.async_get(hass)
    device = registry.async_get_device(identifiers={(DOMAIN, entry.data[CONF_DEVICE_ID])})
    if device is None:
        return

    changes = {}
    mac_address = metadata.get(CONF_MAC_ADDRESS)
    if isinstance(mac_address, str) and mac_address:
        changes["connections"] = {(dr.CONNECTION_NETWORK_MAC, mac_address.lower())}
    area_id = entry.data.get(CONF_AREA_ID)
    if area_id:
        changes["area_id"] = area_id
    for key in ("manufacturer", "model"):
        if metadata.get(key):
            changes[key] = str(metadata[key])
    os_version = metadata.get("os_version")
    if os_version:
        changes["sw_version"] = str(os_version)
    if changes:
        registry.async_update_device(device.id, **changes)


def panel_device_info(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    """Return the shared device registry information."""
    data = hass.data[DOMAIN][entry.entry_id]
    state = data["status"]
    mac_address = state.get(CONF_MAC_ADDRESS) or entry.data.get(CONF_MAC_ADDRESS)
    manufacturer = state.get("manufacturer") or entry.data.get("manufacturer")
    info = {
        "identifiers": {(DOMAIN, data["device_id"])},
        "name": data["name"],
        "model": state.get("model") or entry.data.get("model") or "Debian kiosk",
        "sw_version": state.get("os_version") or entry.data.get("os_version"),
    }
    if manufacturer:
        info["manufacturer"] = manufacturer
    if mac_address:
        info["connections"] = {(dr.CONNECTION_NETWORK_MAC, mac_address.lower())}
    return info


def panel_state(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    """Return the last reported state."""
    return hass.data[DOMAIN][entry.entry_id]["status"]


async def async_send_command(hass: HomeAssistant, entry: ConfigEntry, command: str) -> None:
    """Publish one allow-listed command supported by the Debian agent."""
    await mqtt.async_publish(
        hass,
        f"{TOPIC_ROOT}/{entry.data[CONF_DEVICE_ID]}/command",
        command,
        qos=1,
        retain=False,
    )
