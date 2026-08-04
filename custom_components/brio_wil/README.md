# BRiO WiL Pool Light

A native Home Assistant integration for the CCEI BRiO WiL underwater pool
light — no Node-RED required. This is a from-scratch reimplementation, using
the Node-RED flow at
[cRemE-fReSh/BRiO-WiL-Integration-for-Home-Assistant](https://github.com/cRemE-fReSh/BRiO-WiL-Integration-for-Home-Assistant)
purely as a reference for the wire protocol (it is the only public
documentation of how the device talks). No code from that project is reused.

Not affiliated with or endorsed by the manufacturer.

## What it gives you

- A `light` entity for the pool light itself:
  - Power on/off
  - Brightness (mapped from the device's 4 discrete levels)
  - Effect list covering all 17 named color/pattern modes (Warm white,
    White, Blue, Lagoon, Cyan, Purple, Magenta, Pink, Red, Orange, Green,
    Gradient, Rainbow, Parade, Techno, Horizon, Hazard, Magical)
- A `select` entity for the animated-pattern sequence speed (Slow/Medium/Fast)
- Configuration entirely through the UI (Settings → Devices & services → Add
  integration → "BRiO WiL Pool Light"), just a host/IP and port

## Status: unverified against real hardware

This was built by reverse-engineering the Node-RED flow's JavaScript
(`substring`/`parseInt` calls on the raw TCP response), not by observing a
real device. The protocol is believed to be:

- TCP, port 30302 by default.
- Sending an empty payload returns an ASCII status telegram; fixed
  character offsets in that telegram encode power state (offset 33),
  mode (offset 64-66, hex), sequence speed (offset 70, hex, -4) and
  brightness (offset 71, hex, /4).
- Sending a small JSON payload changes one thing: `{"prcn": <mode>}`,
  `{"plum": <0-3>}`, `{"pspd": <0-2>}`, `{"sprj": 0|1}`.
- There is no dedicated "set power" command, only a toggle — this
  integration only sends `sprj` when the desired power state differs from
  the last polled state, mirroring the Node-RED flow's guard logic.

If setup fails or entities report wrong/garbled values, enable debug
logging and capture the raw telegram:

```yaml
logger:
  logs:
    custom_components.brio_wil: debug
```

Then share the logged `BRiO WiL raw status from ...` line so the offsets in
`api.py` can be corrected against your actual device.

## Installing for local testing

This lives at `custom_components/brio_wil` on the `brio-wil-integration`
branch of this fork. Either:

- Add this fork as a HACS custom repository (category: Integration),
  pointed at the `brio-wil-integration` branch, or
- Copy `custom_components/brio_wil` directly into your Home Assistant
  config's `custom_components/` folder.

Then restart Home Assistant and add the integration from the UI.
