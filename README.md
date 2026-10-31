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

The integration exposes the status and controls reported by the Debian agent, including CPU, memory, storage, temperature and battery sensors; network and operating-system details; browser, camera and display status; kiosk URL and refresh; screen brightness; audio volume and mute; and fixed safe actions for browser restart, display sleep/wake, reboot and shutdown. After device discovery, the integration's optional settings can link a Music Assistant Sendspin media-player entity without adding fields to the initial discovery dialog.

Some features depend on the laptop hardware or other services. Camera snapshots and RTSP streaming require a separately configured camera backend. Voice Assist uses Wyoming rather than MQTT. Sleep panel uses the Debian agent's display sleep mode: the display/backlight turn off and Chromium stops rendering, while Linux, Wi-Fi, MQTT and the separate Sendspin player remain running. Wake panel restores brightness and the previous browser state over MQTT. No magic packet or whole-system suspend is used.

## Language and appearance

The integration includes English and Czech translations in `custom_components/pcx86_kiosk/translations/en.json` and `cs.json`. Home Assistant selects the applicable translations; no separate HACS language package is needed. Configuration labels and entity names use these translations. Entity IDs and names explicitly customized by the user are preserved.

The original wall-panel icon is bundled in `custom_components/pcx86_kiosk/brand/` (256 and 512 pixel PNGs, plus an editable SVG source). Home Assistant 2026.3 or newer loads the local integration brand icon. External clients with their own brand caches may refresh it separately.

The discovery flow has one integration-specific name/area form. Home Assistant can also show its own final device/area assignment summary after the entry is created. Do not remove a working device solely to repeat discovery.

## MQTT topics

For a device ID such as `kiosk`, the Debian agent publishes a retained announcement to `pcx86_kiosk/discovery/kiosk`, publishes retained status to `pcx86_kiosk/kiosk/status`, and listens for commands on `pcx86_kiosk/kiosk/command`. The discovery announcement and status include available device details such as hostname, MAC and IP addresses, interface, Wi-Fi signal, operating system, kernel, architecture and hardware model. Values unavailable on a particular laptop are omitted.

MQTT credentials remain on the Debian panel. Use broker ACLs to restrict each panel to its own discovery, status and command topics.

## Development status

The component is a development preview. Controls, camera streaming, Wyoming voice and long-term display sleep/wake reliability still need validation on target hardware and a Home Assistant installation. Do not use it for a production or unattended kiosk yet.

## Updating display sleep/wake

Update the Debian companion and restart its desktop agent before updating this integration to 0.3.4 or newer. Older companion agents only blank the screen for MQTT `sleep`; the new agent additionally preserves brightness, stops/restores Chromium and recovers its MQTT worker after errors. The old `suspend` command is a safe display-sleep alias on the new agent, so an older HA installation cannot request whole-system suspend after the agent update.

Existing sleep/wake entity unique IDs are preserved. Wake is an ordinary MQTT command and is available while the panel is connected, including display sleep. It cannot turn on a powered-off or physically suspended computer.

## Automatic screensaver

The device includes a **Screensaver** configuration switch, a **Screensaver timeout** setting (1–240 minutes), and a **Screensaver active** indicator. These are Home Assistant entities; HACS distributes the integration. Automatic display sleep is disabled by default, with a stored timeout of 10 minutes. Enable it explicitly to use the timer.

The Debian agent disables independent X11/DPMS timers and measures actual keyboard/touch inactivity with `xprintidle`. This works even when browser video inhibits desktop power saving. On timeout it enters the same display/backlight/browser sleep mode as Sleep panel, while the network and separate audio/voice services stay online. Normal local input wakes automatic screensaver sleep and restores the browser; explicit manual Sleep panel still uses the Wake button or Screen switch. The **Screen** switch follows the actual DPMS state; turning it on, or pressing **Wake panel**, clears the screensaver and resets its idle timer. Display transitions are checked every two seconds and pushed to Home Assistant. Telemetry otherwise retains its configured interval. The configured timer is persisted across reboot. Updating the companion installer also installs its small `xprintidle` dependency.
