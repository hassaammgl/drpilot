# 19 — Plan: Removing C# (Mission Planner) From the Loop — 100% Python GCS

Status: **plan only** (user-approved direction: Python-first, C# elimination,
MVP later). Nothing here requires MissionPlanner to survive; MissionPlanner
stays cloned only as reference.

## 0. The core idea — don't rewrite, compose

Mission Planner is ~150k lines of C#. Everything it does is already
achievable in Python by **composing three building blocks that already
exist** in this workspace:

| Building block | Already at | What it gives us |
|---|---|---|
| **pymavlink** | `.venv` (installed) | raw protocol, command helpers, XML message classes, mission-protocol primitives, **DataFlash `.bin` log reader**, MAVFTP client |
| **MAVProxy** | `gcs/MAVProxy` (submodule) | a running, modular, headless-capable Python GCS: link management, telemetry console, live map (`--map`), param `gcs console`, scripting API — loadable modules are plugins |
| **ArduPilot autotest's own tooling** | `Tools/autotest/` | `sim_vehicle.py` launch wrappers, `pexpect`-driven automation, subsystem state assertions — the exact patterns CI uses |

Therefore: **the new product = a small Python package + a set of CLI
commands + (optional, later) one GUI**, NOT a from-scratch GCS.

## 1. Feature mapping: Mission Planner → Python equivalent

| MP feature | Python replacement | Effort |
|---|---|---|
| Connect (serial/UDP/TCP auto-detect) | `pymavlink.mavutil.mavlink_connection()` (handles all transports incl. auto-reconnect) | tiny |
| Live telemetry HUD (att/alt/bat/gps) | read `.position/.attitude/.messages` dicts; CLI `watch`-style printer first | small |
| Map overlay (positions, paths, waypoints) | `MAVProxy --map` already does this; for custom: `folium`/`leaflet` HTML or `pyqtgraph` | none / medium |
| Flight-mode switching, arm/disarm, takeoff/land commands | `mavutil.set_mode_*`, `$mav.*` one-liners | tiny |
| Parameter browse + set | `connection.param_fetch_all()`, `param_set_send()` — full enumeration matches MP behavior | tiny |
| Mission planning + upload/download | pymavlink `mission_*` protocol helpers (WP upload/download, rally, fence); authoring = simple waypoint tables + geopandas/shapely for polygons | medium |
| Geofence, rally points | same mission protocol (`MAV_CMD` fenceloader helpers exist) | small |
| **Log download & analysis (`.bin`)** | **pymavlink `DFReader`** parses dataflash logs; MP's graphs = `matplotlib` over `DFReader` messages | small / medium (nice graphs take time) |
| Firmware upload / flashing | firmware-side exists in Python in **this repo already**: `Tools/AP_Bootloader/upload.py`, plus `.apj` upload logic MP implements via MAVLink is also scriptable | small |
| SITL launch management | `Tools/autotest/sim_vehicle.py` (pure CLI, mature) | none |
| Follow-me / joystick control | MAVProxy `mavproxy_joystick/`, `follow` module | none |
| Video/stream overlays | out of C# scope too (MP uses GStreamer too); defer | n/a |

**Bottom line:** nothing on the list requires C# at all.

## 2. Recommended architecture

```
drpilot-gcs/                     (new Python package, lives at workspace root)
├── pyproject.toml               (deps: pymavlink, pyserial, rich, shapely, matplotlib)
├── src/drpilot_gcs/
│   ├── link.py                  # connection manager (mavlink_connection wrapper,
│   │                            #   heartbeat monitoring, reconnect, multiple links)
│   ├── vehicle.py               # stateful model: armed, mode, RPYT position, battery,
│   │                            #   streams-telem; event hooks (thread-safe async ok later)
│   ├── params.py                # enumerate/get/set/save-to-file, diff vs default
│   ├── mission.py               # build/load/verify/upload/download missions (WP+rally+fence)
│   ├── cmdline.py               # single `drpilot` CLI with subcommands (see §3)
│   ├── logs.py                  # .bin/.tlog reader + report/graph exporters
│   └── flash.py                 # firmware upload (wraps Tools/AP_Bootloader/upload.py)
├── tests/                       # pytest; first test = round-trip through SITL
└── README.md
```

Design rules (learn the ArduPilot way):
- **stateless core, stateful wrappers**: link/encoding primitives map 1:1
  to pymavlink; model object only caches.
- **Every feature CLI-first, GUI-second.** MP's bloat mostly comes from
  GUI logic constraints; a CLI-first design keeps the GUI thin.
- **Testing target = SITL in this workspace** (`build/sitl/bin/arducopter`),
  so any protocol feature is verified same-day without hardware.

## 3. Day-to-day CLI sketch (MVP surface)

```bash
drpilot connect udp:127.0.0.1:14550        # or --auto (serial)/ tcp:...
drpilot status                             # one-shot telemetry summary
drpilot watch                              # curses-style live telemetry
drpilot arm --mode GUIDED                  # mode switch + arm
drpilot goto --lat 37.1 --lon -122.1 --alt 50
drpilot params list | get | set FENCE_ENABLE 1 | diff | pull params.parm
drpilot mission plan route.csv | mission upload | mission download
drpilot logs fetch /var/log/ap               # MAVFTP
drpilot logs read CTUN.bin --plot CTUN.ThI,CTUN.DBar
drpilot flash firmware .apj --baud 57600    # real board upload
drpilot sitl copter                          # wraps sim_vehicle.py
```

## 4. Phased plan

| Phase | Goal | Acceptance test |
|---|---|---|
| **P0 (week 1)** | link + heartbeat + status + watch + arm/mode/goto via `vehicle.py` | `drpilot connect` against SITL, see live telemetry stream; GPS-lock simulation passes |
| **P1 (week 2)** | params (enumerate/set/diff/save) + `logs read` (DFReader) | round-trip params with SITL; a real MP-downloaded `.bin` parses into pandas |
| **P2 (week 3)** | missions: upload/download/rally/fence + simple CSV authoring | plan a 5-WP mission in csv, upload to SITL, fly it, download identical |
| **P3 (week 4)** | firmware flash upload + `drpilot sitl` launcher | flash a real board OR dry-run the flasher against SITL; upload `.apj` path verified |
| **P4 (later, optional)** | thin GUI (pyqt6/PySide6 or local web) reusing the same lib | 1-screen map/telemetry HUD |
| **P5 (optional)** | MAVProxy bridge: if user wants *experienced-GCS features for free*, transparent link forwarder that still exposes our CLI | `drpilot connect --forward-ipc` feeding MAVProxy modules our state |

*P5 note: MAVProxy is the "free 9000-line head start" — if you're OK with a
hybrid (our CLI dominant, MAVProxy as map), we skip most of the GUI work
permanently.*

## 5. Risks & caveats

1. **Windows hardware quirks** (COM ports, some radios) are Linux-style in
   our python — fine for this workspace (Arch), CI uses Linux anyway.
2. **Geo/map niceties** (MP's map tiles, elevation profiles) are
   visual polish; not blockers for "out of the loop".
3. **APJ/board flash edge cases** (some boards need reset sequences) —
   upload.py covers the standard Pixhwaks; expect a board-specific gap.
4. Keep MissionPlanner **read-only** for the first months as reference
   (its logic for corner cases like HIL /antilag etc. is valuable); delete
   the clone only after P4.

## 6. What we DON'T need to replace

- `gcs/MAVProxy` submodule stays — it *is* Python and becomes part of our
  artifact chain.
- `docs/project/09_gcs_missionplanner.md` stays as an architecture study.
- Anything C#-based in the workspace is reference-only.

## 7. Definition of "C# out of the loop"

- Standard flight session (connect → fly → params → log analysis) fully
  inside Python tooling, SITL or hardware — **zero MP usage** for 1 week.
- MP not opened at all during CI/autotest development.
- Firmware flash path works without MP (upload.py / drpilot flash).
