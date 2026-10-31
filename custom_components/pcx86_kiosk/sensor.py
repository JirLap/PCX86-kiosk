"""System and kiosk telemetry reported by the Debian agent."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfInformation, UnitOfTime
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import SIGNAL_STATUS, panel_device_info, panel_state


@dataclass(frozen=True, kw_only=True)
class PanelSensorDescription(SensorEntityDescription):
    """Description for a status key published by the Debian agent."""

    status_key: str


SENSORS = (
    PanelSensorDescription(
        key="cpu_percent", status_key="cpu_percent", translation_key="cpu_percent",
        icon="mdi:cpu-64-bit", native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0, state_class="measurement",
    ),
    PanelSensorDescription(
        key="memory_percent", status_key="memory_percent", translation_key="memory_percent",
        icon="mdi:memory", native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0, state_class="measurement",
    ),
    PanelSensorDescription(
        key="memory_used_bytes", status_key="memory_used_bytes", translation_key="memory_used_bytes",
        icon="mdi:memory", native_unit_of_measurement=UnitOfInformation.BYTES,
        state_class="measurement",
    ),
    PanelSensorDescription(
        key="disk_free_bytes", status_key="disk_free_bytes", translation_key="disk_free_bytes",
        icon="mdi:harddisk", native_unit_of_measurement=UnitOfInformation.BYTES,
        state_class="measurement",
    ),
    PanelSensorDescription(
        key="uptime_seconds", status_key="uptime_seconds", translation_key="uptime_seconds",
        icon="mdi:timer-outline", native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class="duration", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="available_updates", status_key="available_updates", translation_key="available_updates",
        icon="mdi:package-up", entity_category=EntityCategory.DIAGNOSTIC,
        state_class="measurement",
    ),
    PanelSensorDescription(
        key="cpu_temperature_c", status_key="cpu_temperature_c", translation_key="cpu_temperature_c",
        icon="mdi:thermometer", native_unit_of_measurement="°C",
        device_class="temperature", state_class="measurement",
    ),
    PanelSensorDescription(
        key="microphone_volume", status_key="microphone_volume", translation_key="microphone_volume",
        icon="mdi:microphone", native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0, state_class="measurement",
    ),
    PanelSensorDescription(
        key="battery_percent", status_key="battery_percent", translation_key="battery_percent",
        icon="mdi:battery", native_unit_of_measurement=PERCENTAGE,
        device_class="battery", state_class="measurement",
    ),
    PanelSensorDescription(
        key="battery_voltage_v", status_key="battery_voltage_v", translation_key="battery_voltage_v",
        icon="mdi:flash", native_unit_of_measurement="V", state_class="measurement",
    ),
    PanelSensorDescription(
        key="charging_status", status_key="charging_status", translation_key="charging_status",
        icon="mdi:power-plug", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="ip_address", status_key="ip_address", translation_key="ip_address",
        icon="mdi:ip-network", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="mac_address", status_key="mac_address", translation_key="mac_address",
        icon="mdi:network", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="hostname", status_key="hostname", translation_key="hostname",
        icon="mdi:identifier", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="network_interface", status_key="network_interface", translation_key="network_interface",
        icon="mdi:ethernet", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="broadcast_address", status_key="broadcast_address", translation_key="broadcast_address",
        icon="mdi:ip-network-outline", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="wifi_ssid", status_key="wifi_ssid", translation_key="wifi_ssid",
        icon="mdi:wifi", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="wifi_signal_dbm", status_key="wifi_signal_dbm", translation_key="wifi_signal_dbm",
        icon="mdi:wifi", native_unit_of_measurement="dBm", state_class="measurement",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="os_name", status_key="os_name", translation_key="os_name",
        icon="mdi:linux", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="os_version", status_key="os_version", translation_key="os_version",
        icon="mdi:package-variant", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="kernel_version", status_key="kernel_version", translation_key="kernel_version",
        icon="mdi:chip", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="architecture", status_key="architecture", translation_key="architecture",
        icon="mdi:cpu-64-bit", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="manufacturer", status_key="manufacturer", translation_key="manufacturer",
        icon="mdi:factory", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="model", status_key="model", translation_key="model",
        icon="mdi:laptop", entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([PanelTelemetrySensor(hass, entry, description) for description in SENSORS])


class PanelTelemetrySensor(SensorEntity):
    """Expose one telemetry field from the agent's JSON status."""

    _attr_has_entity_name = True

    def __init__(self, hass, entry, description):
        self.hass = hass
        self.entry = entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.data['device_id']}_{description.key}"

    @property
    def device_info(self):
        return panel_device_info(self.hass, self.entry)

    @property
    def native_value(self):
        return panel_state(self.hass, self.entry).get(self.entity_description.status_key)

    @property
    def available(self):
        state = panel_state(self.hass, self.entry)
        return (
            state.get("availability") == "online"
            and self.entity_description.status_key in state
        )

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_STATUS.format(self.entry.entry_id),
                self.async_write_ha_state,
            )
        )
