> ⚠️ **UPOZORNĚNÍ – PROJEKT JE VE VÝVOJI.** Zatím jej nestahujte ani neinstalujte. Integrace není dokončená ani ověřená na běžící instalaci Home Assistantu.

# PCX86-kiosk Home Assistant integration

Custom integration for a Debian XFCE/Chromium panel. This project is separate from `HAOS-kiosk`, which remains the Frigate camera display add-on.

## Status

This is a development preview. The MQTT entities, system controls, Sendspin player proxy, suspend/Wake-on-LAN handling, camera endpoint and voice integration still need testing on the target panel and Home Assistant instance. Do not add this repository in HACS or install it on a production system yet.

## Planned design

The integration uses the existing Home Assistant MQTT connection and the `panel/<device_id>/status` and `panel/<device_id>/command` topics. It is intended to expose panel status and system sensors, kiosk and screen controls, audio controls, optional Music Assistant Sendspin playback, camera endpoints and a Debian Wyoming voice satellite. MQTT credentials remain on the Debian panel.

Installation instructions will be published after the integration and Debian companion have been tested together.
