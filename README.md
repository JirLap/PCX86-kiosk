# PCX86-kiosk

A Home Assistant custom integration for the Debian XFCE kiosk panels. It uses the existing MQTT agent; it does not modify or replace HAOS-kiosk, which remains the Frigate camera display add-on.

## Install with HACS

1. In HACS, open **Integrations → Custom repositories**.
2. Add `https://github.com/JirLap/PCX86-kiosk` as an **Integration** and install it.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration** and select **Panel MQTT**.
5. Enter a device name and MQTT device ID: `patro` for Panel-patro. Add `prizemi` when Panel-přízemí uses the matching topic prefix.

The built-in MQTT integration must already connect to the broker.

## Entities and MQTT contract

For ID `patro`, the agent publishes retained JSON on `panel/patro/status` and receives plain-text commands on `panel/patro/command`. Supported commands: `wake`, `sleep`, `chromium_start`, `chromium_stop`, `chromium_restart`, `status`.

The device provides reported availability and status, a monitor switch, and Chromium action buttons. Commands are allow-listed; arbitrary command strings are never executed.

The currently verified payload reports `availability`, `monitor`, `chromium`, `last_command` and `result` only. CPU, memory, disk, temperature and system volume entities are not included. Retained online status may become stale after a sudden power or network loss until the agent publishes offline.

Music Assistant handles Sendspin playback and its player controls separately; this integration does not proxy audio.

## Manual install

Copy `custom_components/panel_mqtt` to `/config/custom_components/panel_mqtt`, restart Home Assistant, and add the integration as above.
