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
        key="cpu_percent", status_key="cpu_percent", name="CPU use",
        icon="mdi:cpu-64-bit", native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0, state_class="measurement",
    ),
    PanelSensorDescription(
        key="memory_percent", status_key="memory_percent", name="Memory use",
        icon="mdi:memory", native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0, state_class="measurement",
    ),
    PanelSensorDescription(
        key="memory_used_bytes", status_key="memory_used_bytes", name="Used memory",
        icon="mdi:memory", native_unit_of_measurement=UnitOfInformation.BYTES,
        state_class="measurement",
    ),
    PanelSensorDescription(
        key="disk_free_bytes", status_key="disk_free_bytes", name="Available storage",
        icon="mdi:harddisk", native_unit_of_measurement=UnitOfInformation.BYTES,
        state_class="measurement",
    ),
    PanelSensorDescription(
        key="uptime_seconds", status_key="uptime_seconds", name="Uptime",
        icon="mdi:timer-outline", native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class="duration", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="available_updates", status_key="available_updates", name="Updates available",
        icon="mdi:package-up", entity_category=EntityCategory.DIAGNOSTIC,
        state_class="measurement",
    ),
    PanelSensorDescription(
        key="cpu_temperature_c", status_key="cpu_temperature_c", name="CPU temperature",
        icon="mdi:thermometer", native_unit_of_measurement="°C",
        device_class="temperature", state_class="measurement",
    ),
    PanelSensorDescription(
        key="microphone_volume", status_key="microphone_volume", name="Microphone volume",
        icon="mdi:microphone", native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0, state_class="measurement",
    ),
    PanelSensorDescription(
        key="battery_percent", status_key="battery_percent", name="Battery level",
        icon="mdi:battery", native_unit_of_measurement=PERCENTAGE,
        device_class="battery", state_class="measurement",
    ),
    PanelSensorDescription(
        key="battery_voltage_v", status_key="battery_voltage_v", name="Battery voltage",
        icon="mdi:flash", native_unit_of_measurement="V", state_class="measurement",
    ),
    PanelSensorDescription(
        key="charging_status", status_key="charging_status", name="Charging status",
        icon="mdi:power-plug", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="ip_address", status_key="ip_address", name="IP address",
        icon="mdi:ip-network", entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PanelSensorDescription(
        key="wifi_signal_dbm", status_key="wifi_signal_dbm", name="Wi-Fi signal",
        icon="mdi:wifi", native_unit_of_measurement="dBm", state_class="measurement",
        entity_category=EntityCategory.DIAGNOSTIC,
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
