# 15 — Build System (waf) — Refresher for THIS Workspace

## The 60-second explanation
ArduPilot's build system is **waf** (the `./waf` bootstrap script + the real
engine in `modules/waf/` + ArduPilot extensions in `Tools/ardupilotwaf/`).
Everything compiles into `build/<BOARD>/`; binaries end up in
`build/<BOARD>/bin/`.

## The two steps you always do
```bash
# step 1 — pick your board (this persists into build/*/):
.venv/bin/python ./waf configure --board sitl

# step 2 — build firmware for one vehicle:
.venv/bin/python ./waf copter
# other vehicle targets: plane, rover, sub, blimp, antennatracker,
# AP_Periph (Tools/AP_Periph), bootloader (Tools/AP_Bootloader)…
```

> **Why the venv prefix?** During configure, waf *records* which python
> binary it was launched with and uses that absolute path for code
> generators (MAVLink, DroneCAN DSDL). If you configure with system
> python, its missing-sys-lib runs cause `pexpect`-or-empy errors —
> with `.venv/bin/python` everything generator-related uses the venv's
> packages. Use the venv prefix for *both* commands.

## Useful variants
```bash
./waf list_boards               # see all boards (thousands, from hwdef/)
./waf configure --board sitl --enable-scripting            # optional feature on
./waf copter --target bin/arducopter                       # incremental-ish
./waf clean && ./waf distclean                             # cleanup levels
./waf --targets tests/AP_Math_tests                        # build one unit test
```

## Boards you'll use in this workspace
| Board | Meaning |
|---|---|
| `sitl` | software-in-the-loop, runs on your PC, output `build/sitl/bin/arducopter` |
| e.g. `Pixhawk6C`, `MatekH743`… | real hardware targets producing `.apj` (flashable via GCS) and `.bin` |

## Build outputs map
```
build/sitl/
├── bin/arducopter          # SITL copter executable  ← run this
├── bin/arduplane, ardurover, ardusub, antenna-tracker, ardu-blimp…
├── libraries/GCS_MAVLink/include/mavlink/v2.0/…   # generated MAVLink C
├── modules/DroneCAN/libcanard/dsdlc_generated/    # generated CAN code
└── ArduCopter/*.o etc.     # object tree
```

## Where compile-time features come from
- `Tools/scripts/build_options.py` lists every `AP_<X>_ENABLED` flag; waf
  exposes them via `--enable-*` / `--disable-*`. Boards default certain
  flags via their hwdef `*.dsp`/ `default_parameters` or `allowed_sram` prefs.
- Vehicle-side switches live in each vehicle's `config.h`.
- HAL-internal boards defaults are in `libraries/AP_HAL_ChibiOS/hwdef/<board>/hwdef.dat`.

## SLow first build vs incremental
- First SITL copter build: ~5–10 min (compiles ~2000 files).
- Any change: `./waf copter` only recompiles affected objects (typ. <10s).
- Re-run `./waf configure` only when switching boards or features.

## Cross-building one line summary for real boards
```bash
./waf configure --board Pixhawk6C
./waf copter
# → build/Pixhawk6C/bin/arducopter.apj — upload via MissionPlanner/QGC firmware tab
```
