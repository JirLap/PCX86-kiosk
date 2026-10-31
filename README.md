> ⚠️ **IN DEVELOPMENT — DO NOT INSTALL YET.** This integration and its Debian companion are still being developed and have not been validated as a complete release. Installation instructions are provided for development review only.

# PCX86-kiosk

![PCX86-kiosk wall-panel icon](custom_components/pcx86_kiosk/brand/icon.png)

A Home Assistant custom integration for a Debian XFCE/Chromium kiosk panel. Its companion Debian installer and MQTT agent are maintained in [PCX86-kiosk-debian](https://github.com/JirLap/PCX86-kiosk-debian).

This project is independent of [HAOS-kiosk](https://github.com/JirLap/HAOS-kiosk), which is used to display Frigate cameras.

## Discovery and setup

The panel announces itself over the MQTT broker already configured in Home Assistant. After installing this repository through HACS and restarting Home Assistant, a running Debian agent publishes a retained discovery message. Home Assistant then offers the panel for confirmation. The dialog asks only for a device name and an optional area; the device ID, MAC address, IP address, and MQTT topics come from the announcement.

Requirements:

- Home Assistant with its built-in MQTT integration connected to the same broker as the panel.
- The PCX86-kiosk integration installed through HACS.
- The [Debian companion](https://github.com/JirLap/PCX86-kiosk-debian) installed and configured with a unique device ID.

The setup sequence is:

1. Add `https://github.com/JirLap/PCX86-kiosk` to HACS as an **Integration** repository and install **PCX86-kiosk**.
2. Restart Home Assistant so it loads the integration's MQTT discovery subscription.
3. Install the Debian companion and enter the same MQTT broker details used by Home Assistant.
4. When the panel is online, confirm the discovered device and choose its name and area.

The retained discovery announcement is replayed when Home Assistant subscribes, so the panel does not need to be reconfigured if it started before the integration was installed. MQTT's native discovery prefix does not need to be changed; this integration uses Home Assistant's custom-integration MQTT discovery hook.

The previous experimental integration used the domain `panel_mqtt`. Remove that old integration entry before installing this renamed `pcx86_kiosk` component; Home Assistant cannot automatically migrate config entries across domains.

## Entities

The integration exposes the status and controls reported by the Debian agent, including CPU, memory, storage, temperature and battery sensors; network and operating-system details; browser, camera and display status; kiosk URL and refresh; screen brightness; audio volume and mute; and fixed safe actions for browser restart, suspend, reboot and shutdown. After device discovery, the integration's optional settings can link a Music Assistant Sendspin media-player entity without adding fields to the initial discovery dialog.

Some features depend on the laptop hardware or other services. Camera snapshots and RTSP streaming require a separately configured camera backend. Voice Assist uses Wyoming rather than MQTT. Whole-system suspend and Wake-on-LAN depend on Wi-Fi adapter, firmware, network and router support; `sleep` and `wake` only blank or restore the display.

## Language and appearance

The integration includes English and Czech translations in `custom_components/pcx86_kiosk/translations/en.json` and `cs.json`. Home Assistant selects the applicable translations; no separate HACS language package is needed. Configuration labels and entity names use these translations. Entity IDs and names explicitly customized by the user are preserved.

The original wall-panel icon is bundled in `custom_components/pcx86_kiosk/brand/` (256 and 512 pixel PNGs, plus an editable SVG source). Home Assistant 2026.3 or newer loads the local integration brand icon. External clients with their own brand caches may refresh it separately.

The discovery flow has one integration-specific name/area form. Home Assistant can also show its own final device/area assignment summary after the entry is created. Do not remove a working device solely to repeat discovery.

## MQTT topics

For a device ID such as `kiosk`, the Debian agent publishes a retained announcement to `pcx86_kiosk/discovery/kiosk`, publishes retained status to `pcx86_kiosk/kiosk/status`, and listens for commands on `pcx86_kiosk/kiosk/command`. The discovery announcement and status include available device details such as hostname, MAC and IP addresses, interface, Wi-Fi signal, operating system, kernel, architecture and hardware model. Values unavailable on a particular laptop are omitted.

MQTT credentials remain on the Debian panel. Use broker ACLs to restrict each panel to its own discovery, status and command topics.

## Development status

The component is a development preview. Controls, camera streaming, Wyoming voice and full-system suspend/wake still need validation on target hardware and a Home Assistant installation. Do not use it for a production or unattended kiosk yet.
