#!/usr/bin/env python3
"""Build docs/api-reference.md from a Lua table dump of the MPC script API.

Input: the dump in examples/mpc-launchpad-pro-mk3/docs/LUA-API-DUMP.md (by fuzboxz),
lines of `<table> key=type(value),...`, chunked at ~1500 chars.

    python3 tools/api_reference.py [dump.md] > docs/api-reference.md
"""
import re
import sys
from collections import OrderedDict

DUMP = "examples/mpc-launchpad-pro-mk3/docs/LUA-API-DUMP.md"
CHUNK = 1400  # a line at least this long continues on the next line with the same table name

# Hand-kept notes: what we know beyond "this name exists". Keys are normalised paths.
TABLE_NOTES = {
    "dev": "The device table, named after the script file. MPC calls the `Handle*` and `On*` functions; you define them.",
    "dev.clipMatrixAperture": "The script's own window on the clip matrix (verified FINDINGS 18, 30). `Show()`/`SetLabel()` draw it on the MPC screen.",
    "dev.clipMatrixAperture.clipProperties[c][r]": "Per-slot properties, listenable. `State` enum: 0 NoSlot, 1 Empty, 2 Ready, 3 WillPlay, 4 Playing, 5 WillStopPlaying, 6 WillRecord, 7 Recording, 8 WillStopRecording, 9 WillOverdub, 10 Overdubbing, 11 WillStopOverdubbing (COMMUNITY C2). The dump stops at depth 4, so the slot members aren't listed; `Colour`, `State`, `Selected` are verified.",
    "dev.clipMatrixAperture.sceneProperties[i]": "One per scene row; `State` covers the whole row, including columns outside the window (COMMUNITY C2).",
    "dev.mappings.script": "Only notes/CCs registered here reach `HandleMIDI*`. Verified on MIDI channels other than the first (COMMUNITY, LCXL3).",
    "dev.mappings.controlSurface.qlinks": "Hand a CC to an MPC Q-link natively. `AddInfiniteCCToQLink` verified (LCXL3, 16/16 mapped); check with `IsQLinkMappedInfinite`.",
    "dev.mappings.controlSurface": "`AddCCToControl(ch, cc, \"Tap Tempo\")` takes a control's display name (COMMUNITY C8).",
    "dev.midiOut": "`outputIndex` = order of the `output=` lines in the `.ini`. Sysex payload without F0/F7. Script-sent MIDI doesn't loop back through `mappings` (COMMUNITY C4).",
    "mpc.tracks": "**The `Get*/Set*` functions that take a track index error in every call form tried** (FINDINGS 30, 33). Use `normalTracks[i]` instead. Known to work: `GetCount`, `SizeNormalTracks`, `SetCurrentTrack` (global index, COMMUNITY C7).",
    "mpc.tracks.normalTracks[i]": "128 slots whatever the project holds; count with `SizeNormalTracks()`. Index = global clip-matrix column, but not the MPC UI's track number when non-mixable tracks exist (COMMUNITY C7).",
    "mpc.tracks.masterTracks[i]": "Same shape as `normalTracks[i]`. Presence only.",
    "mpc.tracks.currentTrack": "`Index` is global (normal tracks, then master). Plugin-preset calls present; confirm on hardware.",
    "mpc.controlSurface.qlinks[i]": "16, 0-based, column-major on the Live III (FINDINGS 26). `GetPosition` lags one change. **`SetPosition` only changes the displayed value** (COMMUNITY C3); use `Touch()` + `Twist(delta)`. `SetValue` is untested.",
    "mpc.controlSurface.pads": "Virtual pad indices are 1-64. `Tap` may ignore velocity; use `Press` + `Release`. No colour listener: poll `pads[i].GetColour()` (COMMUNITY C8).",
    "mpc.force": "Every Force button, pressable from any device. No LED/state readback (FINDINGS 30).",
    "mpc.engineMode": "`RequestModeChange(name)` takes menu-label names (COMMUNITY C11). Check `CurrentPopup` before project-scoped calls (COMMUNITY C6).",
    "mpc.clipMatrix.selectedClip.events": "Create/edit/delete only; no way to read or iterate events (FINDINGS 18, 25, 33).",
    "mpc.sequencer.quantiser": "Verified in LPP3/LCXL3.",
    "dev.timer": "`Start(ms)` sets the `HandleTimer` interval; `Now()` returns milliseconds (COMMUNITY C8).",
    "mpc.features": "`UseClipWorkflow` tells you whether the clip matrix is in use (COMMUNITY C8).",
}
BUTTON_MEMBERS = {"DoublePress", "Help", "Hold", "Press", "Release"}


def read_dump(path):
    text = open(path, encoding="utf-8").read()
    blocks = re.findall(r"```\n(.*?)```", text, re.S)
    lines = [l for b in blocks for l in b.splitlines() if l.strip()]
    tables = OrderedDict()
    prev_name, prev_len = None, 0
    for line in lines:
        if " = <cycle>" in line:
            prev_name = None
            continue
        name, _, rest = line.partition(" ")
        if name == prev_name and prev_len >= CHUNK:
            tables[name] += rest  # continuation splits mid-token: join without separator
        elif name not in tables:
            tables[name] = rest
        prev_name, prev_len = name, len(line)
    return tables


MEMBER = re.compile(r"(?:^|,)([A-Za-z_][A-Za-z0-9_]*|\d+)=(function|table|userdata\((.*?)\))(?=,(?:[A-Za-z_][A-Za-z0-9_]*|\d+)=|$)")


def parse(rest):
    funcs, props, subs, idx = [], OrderedDict(), [], set()
    for m in MEMBER.finditer(rest):
        key, kind, val = m.group(1), m.group(2), m.group(3)
        if key.isdigit():
            idx.add(int(key))
        elif kind == "function":
            if key not in funcs:
                funcs.append(key)
        elif kind == "table":
            subs.append(key)
        else:
            props[key] = val
    return funcs, props, subs, idx


def norm(name):
    """MPC.tracks.normalTracks.5 -> mpc.tracks.normalTracks[i]; clipProperties.3 -> [c]."""
    name = re.sub(r"^MPC(KEYS)?", "mpc", name)
    name = re.sub(r"^DEV", "dev", name)
    name = re.sub(r"clipProperties\.\d+", "clipProperties[c][r]", name)
    name = re.sub(r"\.\d+$", "[i]", name)
    return name


def main():
    tables = read_dump(sys.argv[1] if len(sys.argv) > 1 else DUMP)
    merged = OrderedDict()
    for raw, rest in tables.items():
        if raw == "MPCKEYS":
            continue
        n = norm(raw)
        if n in merged:
            continue  # indexed siblings share one shape; first one wins
        merged[n] = parse(rest)

    # collapse plain buttons (Press/Release/Hold/DoublePress) into one list per namespace
    buttons = {"mpc.controlSurface": [], "mpc.force": []}
    for n, (f, p, s, i) in list(merged.items()):
        parent, _, leaf = n.rpartition(".")
        if parent in buttons and set(f) == BUTTON_MEMBERS and not p and not s:
            buttons[parent].append(leaf)
            del merged[n]

    out = []
    w = out.append
    w("# MPC 3.10.1.8 script API reference\n")
    w("Every table, function and property a controller script can see on **MPC 3.10.1.8 (build 38fdde70994), Live III**,")
    w("with what we know about each. Generated by `tools/api_reference.py` from the table dump in")
    w("[mpc-launchpad-pro-mk3/docs/LUA-API-DUMP.md](https://github.com/fuzboxz/mpc-launchpad-pro-mk3/blob/main/docs/LUA-API-DUMP.md)")
    w("by [@fuzboxz](https://github.com/fuzboxz) (captured 2026-11-17 from inside a running script, depth 4).")
    w("Notes come from [FINDINGS](findings/FINDINGS.md) and [COMMUNITY](findings/COMMUNITY.md).\n")
    w("**Present is not the same as working.** A name here only means the table has it. Several functions error or do")
    w("nothing when called (see the notes); anything without a note is untested. Property values are what the dump")
    w("saw on an empty project; read and write them through `.value`, and most can be listened to with")
    w("`prop:listen(fn, deviceName)`.\n")
    w("`[i]` = an indexed table (all entries share the shape shown). `dev` = your device table.\n")

    def section(title, names):
        w(f"## {title}\n")
        for n in names:
            f, p, s, i = merged[n]
            w(f"### `{n}`")
            if n in TABLE_NOTES:
                w(TABLE_NOTES[n])
            f = [x for x in f if x != "Help"]
            if i:
                w(f"- **Indexed:** {min(i)}..{max(i)}")
            if f:
                w("- **Functions:** " + ", ".join(f"`{x}`" for x in f))
            if p:
                w("- **Properties:** " + ", ".join(f"`{k}`" + (f" ({v})" if v not in ("",) else "") for k, v in p.items()))
            if s:
                w("- **Sub-tables:** " + ", ".join(f"`{x}`" for x in s))
            w("")

    dev = [n for n in merged if n.startswith("dev")]
    section("Device table (`dev`)", dev)
    groups = OrderedDict([
        ("Tracks", "mpc.tracks"), ("Clip matrix", "mpc.clipMatrix"), ("Master clip matrix", "mpc.masterClipMatrix"),
        ("Aperture (global)", "mpc.clipMatrixAperture"), ("Sequencer and transport", "mpc.sequencer"),
        ("Sequence and song", "mpc.currentSequence"), ("Control surface", "mpc.controlSurface"), ("Force buttons", "mpc.force"),
        ("Project", "mpc.project"), ("Engine and modes", "mpc.engine"), ("UI", "mpc.ui"),
    ])
    done = set(dev)
    for title, prefix in groups.items():
        names = [n for n in merged if (n == prefix or n.startswith(prefix + ".") or n.startswith(prefix + "["))
                 and n not in done]
        if title == "Sequence and song":
            names += [n for n in merged if n.startswith("mpc.song") and n not in done]
        if title == "Engine and modes":
            names += [n for n in merged if n.startswith("mpc.engineMode") or n.startswith("mpc.modeMenu")]
        names = list(OrderedDict.fromkeys(x for x in names if x not in done))
        if not names:
            continue
        section(title, names)
        done.update(names)
        if prefix in buttons and buttons[prefix]:
            w(f"**Buttons** (each has `Press`, `Release`, `Hold`, `DoublePress`): "
              + ", ".join(f"`{b}`" for b in sorted(buttons[prefix], key=str.lower)) + "\n")
    rest = [n for n in merged if n not in done]
    section("Everything else", rest)
    print("\n".join(out).rstrip() + "\n")


if __name__ == "__main__":
    main()
