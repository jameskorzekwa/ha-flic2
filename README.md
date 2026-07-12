# Flic 2 Bluetooth for Home Assistant

Pair Flic 2 buttons directly with Home Assistant through its native Bluetooth
integration—including ESPHome Bluetooth proxies. No Flic Hub and no `flicd`
daemon are required.

## Status

This is an early hardware-test release. The protocol, cryptography, packet
framing, and event decoding are implemented and unit tested, but it still needs
validation against physical buttons and ESPHome proxies before production use.

Supported:

- Flic 2 buttons
- Flic Duo's main button through the base Flic 2 protocol
- Single, double, and hold events
- ESPHome Bluetooth proxy connection routing and failover
- On-demand connections with a 60-second idle disconnect to conserve proxy slots
- Battery voltage reporting

Not supported:

- Original Flic 1 buttons (their protocol is not publicly documented)
- Flic Duo twist/small-button extensions
- Firmware updates
- HID/MIDI configuration

## Installation

### Manual

1. Copy `custom_components/flic2` into `/config/custom_components/flic2`.
2. Restart Home Assistant.
3. Remove the target Flic 2 from any Flic Hub that should no longer own it.
4. Hold the Flic for at least 6 seconds to enter public pairing mode.
5. Go to **Settings → Devices & services → Add integration** and choose
   **Flic 2 Bluetooth**.

### HACS

Add this repository as a custom integration repository, install it, and restart
Home Assistant.

## ESPHome proxy requirements

The proxy nearest each button must have active connections enabled. Current
ESPHome defaults to active connections with three slots:

```yaml
bluetooth_proxy:
  active: true
  connection_slots: 3
```

The integration connects when a disconnected Flic advertises after a press,
retrieves queued button events, and lets the button disconnect after 60 seconds
of inactivity. This avoids permanently reserving one proxy slot per button.

## Event automations

Each button creates an Event entity with event types `single`, `double`, and
`hold`. Use that Event entity as an automation trigger in the Home Assistant UI.

## Security and protocol provenance

This project implements the officially published
[Flic 2 Protocol Specification](https://github.com/50ButtonsEach/flic2-documentation/wiki/Flic-2-Protocol-Specification).
It does not use, modify, decompile, or reverse engineer the proprietary `flicd`
binary.

The Chaskey packet-authentication code was translated from Shortcut Labs AB's
permissively licensed Android reference library. See `NOTICE` and
`FLIC_LICENSE.txt`.

