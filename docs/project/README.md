# drpilot — Project Documentation Hub

> **Note:** The original `docs/` folder at repo root contains ArduPilot's own legacy
> build scripts (`docs/build-*.sh`, `docs/config/*`). Those belong to upstream
> ArduPilot and were **not touched**. This documentation lives in
> `docs/project/` as a separate, self-contained doc set for this workspace.

## What this workspace is

This repository is an **ArduPilot firmware clone** (repo name `drpilot`,
remotes point to `git@github.com:hassaammgl/drpilot.git`) with three
**ground control station** repositories cloned alongside it in `gcs/`:

```
drpilot/
├── ArduCopter/        # Copter firmware (multirotor + helicopter)
├── ArduPlane/         # Plane firmware (fixed-wing + VTOL/quadplane)
├── Rover/             # Rover / boat firmware
├── ArduSub/           # Underwater rov firmware
├── Blimp/             # Blimp firmware
├── AntennaTracker/    # Antenna tracker firmware
├── libraries/         # ~157 shared libraries (the real bulk of the code)
├── Tools/             # build tooling, autotest, periph firmware, bootloader
├── modules/           # git submodules: ChibiOS, MAVLink, waf, gtest...
├── gcs/               # ▼ cloned ground control stations
│   ├── MissionPlanner/    # C# WinForms GCS
│   ├── qgroundcontrol/    # C++/Qt GCS
│   └── MAVProxy/          # Python GCS
├── .venv/             # Python virtualenv with pymavlink/MAVProxy/etc.
└── build/             # waf build output (SITL builds live here)
```

## Documentation index

| Doc | Contents |
|---|---|
| [01_overview.md](01_overview.md) | The whole architecture: firmware ↔ GCS ↔ MAVLink, how everything fits together |
| [02_ardupilot_firmware.md](02_ardupilot_firmware.md) | How the firmware actually works: boot, main loop, scheduler, HAL, EKF, logging, params |
| [03_vehicle_arducopter.md](03_vehicle_arducopter.md) | `ArduCopter/` — every file explained |
| [04_vehicle_arduplane.md](04_vehicle_arduplane.md) | `ArduPlane/` — every file explained (incl. quadplane/VTOL) |
| [05_vehicle_rover.md](05_vehicle_rover.md) | `Rover/` — every file explained |
| [06_vehicle_ardusub.md](06_vehicle_ardusub.md) | `ArduSub/` — every file explained |
| [07_vehicle_blimp.md](07_vehicle_blimp.md) | `Blimp/` — every file explained |
| [08_vehicle_antennatracker.md](08_vehicle_antennatracker.md) | `AntennaTracker/` — every file explained |
| [09_gcs_missionplanner.md](09_gcs_missionplanner.md) | `gcs/MissionPlanner/` — C# GCS full guide |
| [10_gcs_mavproxy.md](10_gcs_mavproxy.md) | `gcs/MAVProxy/` — Python GCS full guide |
| [11_gcs_qgroundcontrol.md](11_gcs_qgroundcontrol.md) | `gcs/qgroundcontrol/` — Qt GCS full guide |
| [12_libraries_guide.md](12_libraries_guide.md) | `libraries/` — all ~157 libraries, grouped & explained |
| [13_tools_guide.md](13_tools_guide.md) | `Tools/` — every subdirectory explained |
| [14_modules_guide.md](14_modules_guide.md) | `modules/` — every git submodule explained |
| [15_build_system.md](15_build_system.md) | waf, boards, build options, how to compile anything |
| [16_testing.md](16_testing.md) | SITL simulation, autotest framework, unit tests, Replay |
| [17_mavlink_integration.md](17_mavlink_integration.md) | How firmware and GCS talk to each other (MAVLink) |
| [18_dev_workflow.md](18_dev_workflow.md) | The exact workflow set up in THIS workspace (venv, SITL, GCS connect), day-to-day commands |
| [inventory/](inventory/README.md) | **Full file-by-file listing of all 25,356 firmware files** (gzipped; regenerate with one command) |

## Documentation coverage levels

| Area | Coverage |
|---|---|
| Vehicle folders (ArduCopter, ArduPlane, Rover, ArduSub, Blimp, AntennaTracker) | Every single file, individually described |
| `libraries/` (157 libs) & `Tools/` (33 subdirs) | Every library / subdirectory described (catalog level — not each `.cpp` inside) |
| Whole firmware tree | Every one of the 25,356 files *listed* in `inventory/ardupilot_files.txt.gz` |
| `gcs/` results | One full architecture + structure doc per GCS repo |

## Quick orientation

- **Firmware is the low-level autopilot** that runs on flight controllers
  (Pixhawk-class STM32 boards) or in a simulator. It flies the vehicle.
- **GCS (Mission Planner / QGC / MAVProxy) is the ground side**: map, mission
  planning, live telemetry, parameter editing, log analysis. It talks
  **MAVLink** over USB/serial/Wi-fi/telemetry radio.
- They are connected by **GCS_MAVLink** (firmware side) and the GCS's own
  MAVLink implementation. Protocol definitions live in `modules/mavlink/`.
- Everything in `libraries/` is shared between vehicles; each vehicle folder
  just picks the libraries and adds vehicle-specific logic (flight modes etc.).

Generated: October 2026. Sources inspected include exactly what is inside this
workspace (method of chronology: shallow look at the ArduPilot subsystem docs
in `AGENTS.md` + reading the listed source files).
