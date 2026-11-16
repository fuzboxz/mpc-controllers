# What an MPC 3.10 controller script can do

MPC 3.10 has an official controller-script layer: **Lua 5.4 (sol2)** inside the MPC binary. Akai ships example scripts
for its MPK mini (`/usr/share/Akai/SME0/Devices/Akai/`). Source: registered names and docstrings in the binary, then
device tests. Verified on 3.10.0.49 and 3.10.1.8 unless noted.

## Installing a script
- A script is a `.ini` + `.lua` pair. The `.ini` has `input=` / `output=` port-name matches (order = port index),
  `script=` and `checksum=`.
- Search dirs: `/usr/share/Akai/SME0/Devices` and `<user root>/MPC Documents/Devices` (user root is `/storage`,
  `/data/UserData`, `/nvme` or `/sdcard` depending on the device).
- **Checksum = sha256(lua bytes || 36-char salt)**. The salt lives in the MPC binary; read it from your own copy, never publish it.
  The checksum check is skipped when the hardware product code is 0 (desktop software).
- The same salt worked on 3.10.0.49 and 3.10.1.8 (FINDINGS 30).

## API by task
| Want to | Use |
|---|---|
| Clip grid (launch, state, colours) | `clipMatrixAperture` (`SetColumns/SetRows` up to 16x16, `TriggerClip`, `TriggerRow`, `StopClipsOnTrack`, `SelectClip`, `SelectTrack`, `MoveToColumn`), `clipProperties[c][r].Colour/State/Selected` (listenable) |
| Mute / solo / rec arm / pan / volume / sends | `mpc.tracks` and `tracks.normalTracks[i]` (colour, name, mute, solo, rec arm, pan, volume, sends 1-4, type) |
| Q-links | `qlinks.AddInfiniteCCToQLink` (1-63 cw, 64-127 ccw), `SetQLinkFineAdjust`, `qlinks[i].GetPosition/SetPosition/TargetName/ValueString/IsTouched/Rotate` |
| Pads | `pads.AddNoteToMpcPad` (pad <= 15, current bank), `AddNoteToForcePad` (<= 63), `AddNoteToVirtualPad` (<= 127, absolute program pad); `pads.Tap/Press/ReleaseVirtual` (1-64); `pads.LightRGBColor/LightBrightness`; `pads.CurrentBank` |
| Press Force buttons from a script | `mpc.force.<name>` (every Force button: `Press/Release/Hold/DoublePress/Help`) |
| Edit notes | `selectedClip.events`: `CreateNoteEvent`, `DeleteEvent`, `SetNote`, `SetNoteVelocity`, `MoveEvent`, `SetNoteRatchet` |
| Transport / undo | `sequencer.*`, `commandManager.Undo/Redo`, `clipMatrix.StopAllClips` |
| Send MIDI out (LEDs, sysex) | `midiOut.SendMIDINoteOn/CC/Sysex(outputIndex)` |
| Receive MIDI | callbacks `HandleMIDINoteOn/Off`, `HandleMIDICC`, `HandleMIDISysex`, `HandleTimer` |
| Show feedback | `ui.ShowTUIFeedback`, `popups.*`, aperture `Show()/SetLabel()` |

## Useful facts
- **Q-link numbering is column-major** on the Live III: knob j (0-3, left to right) in bank b is Q-link `4*(3-j)+b` (FINDINGS 26).
- Drum NOTE layout on a 64-pad Force: banks A-D are 4x4 quadrants, A bottom-left, B bottom-right, C top-left, D top-right (FINDINGS 20).
- Pads, step sequencer, Force buttons, per-track state are all reachable; see [recipes](recipes/).
