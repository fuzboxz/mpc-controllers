---
name: mpc-controller-scripts
description: Write or debug MPC 3.10 Lua controller scripts (Akai MPC Live III / Force surfaces, MIDI controllers): the available API, what it cannot do, and verified quirks. Use when the user mentions MPC controller scripts, the Devices folder, script .ini/.lua, Q-links, clip matrix, aperture, mpc.force, or driving an MPC from a hardware controller.
---

# MPC 3.10 controller scripts

Start from the docs in this repo (paths relative to the repo root):
1. `docs/capabilities.md`: the API by task and install rules.
2. `docs/limitations.md`: check this **before** promising a feature (no state dump, no per-track MIDI input, no non-current-track editing).
3. `docs/findings/FINDINGS.md`: dated evidence; cite the finding number and firmware build.
4. `docs/findings/COMMUNITY.md`: findings from other people's scripts (Launchpad Pro MK3, Launch Control XL 3, nanoKONTROL on Force), incl. silent `.ini` failures and the `SetPosition` trap.
5. `examples/force-link/`, and the community scripts linked in `README.md`: full working controllers to copy patterns from.

Rules: claims are firmware-specific (3.10.0.49 / 3.10.1.8); say which build you are relying on. Never publish or
ask for the signing salt or Akai binaries. Scripts need a valid checksum on hardware.
