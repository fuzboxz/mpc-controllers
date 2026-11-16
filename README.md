# mpc-controllers

What an MPC 3.10 **controller script** (the Lua layer) can and cannot do, found by testing on real hardware,
written down so you can build your own controller support without redoing the digging.

- **[docs/capabilities.md](docs/capabilities.md)**: the API surface, by what you want to do.
- **[docs/limitations.md](docs/limitations.md)**: the hard walls, each with the evidence.
- **[docs/recipes/](docs/recipes/)**: short how-tos for things that took effort to get right.
- **[docs/findings/](docs/findings/)**: the raw dated research log (firmware 3.9.1 to 3.10.1.8).
- **[skill/](skill/)**: a Claude skill that points an AI agent at the docs above.
- **[examples/force-link](examples/force-link)**: a complete working controller (an Akai Force as a surface for an MPC Live III), as a git submodule.

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
