# mpc-controllers

What an MPC 3.10 **controller script** (the Lua layer) can and cannot do, found by testing on real hardware,
written down so you can build your own controller support without redoing the digging.

- **[docs/capabilities.md](docs/capabilities.md)**: the API surface, by what you want to do.
- **[docs/limitations.md](docs/limitations.md)**: the hard walls, each with the evidence.
- **[docs/recipes/](docs/recipes/)**: short how-tos for things that took effort to get right.
- **[docs/findings/](docs/findings/)**: the raw dated research log (firmware 3.9.1 to 3.10.1.8).
- **[skill/](skill/)**: a Claude skill that points an AI agent at the docs above.
- **[examples/force-link](examples/force-link)**: a complete working controller (an Akai Force as a surface for an MPC Live III), as a git submodule.

## Why this exists
Controller support on MPC is thinly documented. Akai ships a handful of MPK mini scripts and no API reference, so
anyone who wants a Push, a Launchpad or a second Force to drive an MPC has to reverse-engineer what a script can reach.
We did that while building [force-link](examples/force-link) (a Force as an extra surface for a Live III), and kept
notes on every wall we hit. This repo publishes those notes so the next person can start from what works and what
doesn't, instead of rediscovering it. force-link is the worked example.

## What changed between 3.9 and 3.10
Both firmwares have a Lua controller-script loader (found by reading the binaries; checked on device for 3.10).
3.10 is where it becomes useful for state-aware surfaces. (FINDINGS 5, 8, 11)

| | 3.9.1 | 3.10 |
|---|---|---|
| Script loader | present, **no checksum** (unsigned scripts should load; untested on 3.9.1) | present, **signed**: `checksum = sha256(lua + salt)` |
| API | mapping only: `AddNoteToMpcPad/ForcePad`, `AddNoteToControl`, `AddInfiniteCCToQLink`, `SendMIDI*`, `timer`, `TapVirtual` | adds everything below |
| Clip grid (`clipMatrixAperture`, clip colour/state) | no | yes |
| Per-track mute / solo / rec arm properties | no (a button press can be mapped, but there's no state back) | yes |
| Q-link names (`TargetName`, `ValueString`) | no, so no way to know what a knob controls | yes |
| Sysex into the script (`HandleMIDISysex`) | no | yes |
| Mode change, TUI feedback, `AddNoteToVirtualPad` | no | yes |
| `mpc.force.*` (one control per Force button) | not seen | yes (3.10.1.8) |
| Note editing on the selected clip | no | yes |

In practice: on 3.9.1 a controller is an **input surface** (pads, buttons, knobs) with no clip colours or knob names.
On 3.10 it can be **state-aware**: a clip grid with live colours, mute/solo/arm rows, named Q-links. Even on 3.10
there are real limits (no state dump, no per-track MIDI input, no non-current-track editing): see
[limitations](docs/limitations.md).

## Scope
Verified on **MPC 3.10.0.49 and 3.10.1.8** (Live III, Gen 2) unless a note says otherwise. Each claim is tagged with the
build it was checked on; behaviour may change in later firmware. Some findings are about the Force (MPC 3.9.1) and
say so. Re-test before relying on anything here.

## Ground rules
Akai's software is not included and must not be added. Findings describe behaviour and give offsets for people who
own the firmware; they do not redistribute code, and the script-signing salt is deliberately not published.
Use at your own risk: several routes need root and restart MPC (which closes the open project).

## Contributing
Corrections and new findings welcome: say the firmware build, the device, and how you checked.

Licence: documentation CC-BY-4.0; code samples MIT.
