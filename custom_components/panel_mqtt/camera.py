"""Laptop camera exposed from the Debian agent's HTTP/RTSP endpoints."""

from aiohttp import ClientError, ClientTimeout

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import SIGNAL_STATUS, async_send_command, panel_device_info, panel_state


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([PanelCamera(hass, entry)])


class PanelCamera(Camera):
    """Camera entity whose media transport is HTTP snapshot plus RTSP stream."""

    _attr_has_entity_name = True
    _attr_name = "Laptop camera"
    _attr_icon = "mdi:camera"
    _attr_supported_features = CameraEntityFeature.STREAM | CameraEntityFeature.ON_OFF

    def __init__(self, hass, entry):
        super().__init__()
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.data['device_id']}_camera"
        self.content_type = "image/jpeg"

    @property
    def device_info(self):
        return panel_device_info(self.hass, self.entry)

    @property
    def available(self):
        state = panel_state(self.hass, self.entry)
        return state.get("availability") == "online" and bool(state.get("camera_snapshot_url"))

    @property
    def supported_features(self):
        state = panel_state(self.hass, self.entry)
        features = CameraEntityFeature.ON_OFF if state.get("camera_snapshot_url") else CameraEntityFeature(0)
        if state.get("camera_stream_url"):
            features |= CameraEntityFeature.STREAM
        return features

    @property
    def is_on(self):
        return panel_state(self.hass, self.entry).get("camera") in ("on", "running", True)

    async def async_camera_image(self, width=None, height=None):
        url = panel_state(self.hass, self.entry).get("camera_snapshot_url")
        if not url:
            return None
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(url, timeout=ClientTimeout(total=10)) as response:
                response.raise_for_status()
                return await response.read()
        except (ClientError, TimeoutError):
            return None

    async def stream_source(self):
        return panel_state(self.hass, self.entry).get("camera_stream_url")

    async def async_turn_on(self):
        await async_send_command(self.hass, self.entry, "camera_start")

    async def async_turn_off(self):
        await async_send_command(self.hass, self.entry, "camera_stop")

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_STATUS.format(self.entry.entry_id),
                self._status_updated,
            )
        )

    def _status_updated(self):
        self.__dict__.pop("is_on", None)
        self.async_write_ha_state()
