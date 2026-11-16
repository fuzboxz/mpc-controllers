# What a controller script cannot do

Each wall lists how we hit it and what (if anything) gets round it.

| Limit | Evidence | Way round |
|---|---|---|
| **No state dump**: `#GetState` / `mpc.GetState` are nil in a script (the registrar exists in the binary but doesn't reach Lua) | FINDINGS 19, 25 (device, 3.10.0.49) | Read MPC's memory from a preloaded shim (needs root) |
| **No LED/light state for Force controls**: scripts get no feedback for `mpc.force.*` buttons | FINDINGS 30 | Derive lights from state you can read, or dim/bright-while-held |
| **No per-track MIDI input**: `normalTracks[i]` has no input port/channel/monitor; the getters on `mpc.tracks` error | FINDINGS 33 (device, 3.10.1.8) | Set the track's input by hand in MPC, or a native shim |
| **Cannot drive a non-current track**: `aperture.SelectTrack` moves MPC's own current track; there is no separate controller track | FINDINGS 33 | As above |
| **Note editing only on the selected clip**: no per-clip events object | FINDINGS 33 | Select the clip first, or native route |
| **Scale/root of pad perform is invisible**: `padPerform`/`keyboardControl` are only the two buttons | FINDINGS 29 | Read from MPC's memory (offsets per build) |
| **`qlinks[i].GetPosition()` lags one change**; `Twist` wraps | FINDINGS 26 | Use MPC's own infinite-CC mapping; cap per-step deltas |
| **Q-link bank changes update all 16 at once** | FINDINGS 26 | Follow a bank only when exactly one Q-link changes |
| **No USB access** from Lua (e.g. Push 2 display is bulk USB) | FINDINGS 2 | A bridge device |
| **Gen 2 (Live III) has no stock root**: SSH needs an Akai-signed cert, rootfs signed | FINDINGS 2, 7, 30 | Out of scope here |
| **Latency over Wi-Fi** 30-50 ms TCP RTT | FINDINGS 31 | USB networking breaks the Force's own controller (hub mux); USB mode works (FINDINGS 32) |
