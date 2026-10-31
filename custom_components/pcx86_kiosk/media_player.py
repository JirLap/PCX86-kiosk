"""Optional Home Assistant media-player proxy for this panel's Sendspin player."""

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_state_change_event

from . import panel_device_info
from .const import CONF_MEDIA_PLAYER


async def async_setup_entry(hass, entry, async_add_entities):
    source = entry.options.get(CONF_MEDIA_PLAYER)
    if source:
        async_add_entities([PanelMediaPlayerProxy(hass, entry, source)])


class PanelMediaPlayerProxy(MediaPlayerEntity):
    """Route playback and volume to Music Assistant's Sendspin entity."""

    _attr_has_entity_name = True
    _attr_translation_key = "media_player"
    _attr_icon = "mdi:speaker"
    _attr_should_poll = False

    def __init__(self, hass, entry, source_entity_id):
        self.hass = hass
        self.entry = entry
        self.source_entity_id = source_entity_id
        self._attr_unique_id = f"{entry.data['device_id']}_media_player_proxy"
        self._attr_supported_features = MediaPlayerEntityFeature(0)

    @property
    def device_info(self):
        return panel_device_info(self.hass, self.entry)

    @property
    def source_state(self):
        return self.hass.states.get(self.source_entity_id)

    @property
    def available(self):
        state = self.source_state
        return state is not None and state.state != "unavailable"

    @property
    def state(self):
        state = self.source_state
        if state is None or state.state == "unavailable":
            return MediaPlayerState.OFF
        try:
            self._attr_supported_features = MediaPlayerEntityFeature(
                int(state.attributes.get("supported_features", 0))
            )
        except (TypeError, ValueError):
            self._attr_supported_features = MediaPlayerEntityFeature(0)
        return state.state

    @property
    def volume_level(self):
        value = self._attribute("volume_level")
        return float(value) if value is not None else None

    @property
    def is_volume_muted(self):
        return self._attribute("is_volume_muted")

    @property
    def media_title(self):
        return self._attribute("media_title")

    @property
    def media_artist(self):
        return self._attribute("media_artist")

    @property
    def media_album_name(self):
        return self._attribute("media_album_name")

    @property
    def media_content_id(self):
        return self._attribute("media_content_id")

    @property
    def media_duration(self):
        return self._attribute("media_duration")

    @property
    def media_position(self):
        return self._attribute("media_position")

    @property
    def media_position_updated_at(self):
        return self._attribute("media_position_updated_at")

    @property
    def shuffle(self):
        return self._attribute("shuffle")

    @property
    def repeat(self):
        return self._attribute("repeat")

    def _attribute(self, key):
        state = self.source_state
        return state.attributes.get(key) if state else None

    async def _call(self, service, **data):
        if not self.available:
            raise HomeAssistantError("The configured Sendspin player is unavailable")
        await self.hass.services.async_call(
            "media_player",
            service,
            {"entity_id": self.source_entity_id, **data},
            blocking=False,
        )

    async def async_media_play(self):
        await self._call("media_play")

    async def async_media_pause(self):
        await self._call("media_pause")

    async def async_media_stop(self):
        await self._call("media_stop")

    async def async_media_next_track(self):
        await self._call("media_next_track")

    async def async_media_previous_track(self):
        await self._call("media_previous_track")

    async def async_set_volume_level(self, volume):
        await self._call("volume_set", volume_level=volume)

    async def async_mute_volume(self, mute):
        await self._call("volume_mute", is_volume_muted=mute)

    async def async_media_seek(self, position):
        await self._call("media_seek", seek_position=position)

    async def async_set_shuffle(self, shuffle):
        await self._call("shuffle_set", shuffle=shuffle)

    async def async_set_repeat(self, repeat):
        await self._call("repeat_set", repeat=repeat)

    async def async_added_to_hass(self):
        @callback
        def source_changed(_event):
            self.async_write_ha_state()

        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self.source_entity_id], source_changed
            )
        )
