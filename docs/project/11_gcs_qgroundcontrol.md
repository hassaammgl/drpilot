# 11 — `gcs/qgroundcontrol/` — QGroundControl Guide

## What it is
QGroundControl (QGC) is the cross-platform MAVLink ground control station
(Linux / macOS / Windows / Android), written in **C++ with Qt 6 + QML**.
It is MAVLink-standard-centric: it works with ArduPilot, PX4, and other
autopilots, and is the reference client for the MAVLink **Microsites**-grade
implementations (component information, parameter standards, RTK base).

Cloned here as shallow master of `https://github.com/mavlink/qgroundcontrol`
into `gcs/qgroundcontrol` (198 MB).

## Architecture (verified subdirectories of `src/`)
| `src/` dir | Role |
|---|---|
| `Comms/LinkManager, LinkInterface, LinkConfiguration` | transport layer: serial, UDP, TCP, Bluetooth links; autoconnect logic |
| `MAVLink/` | MAVLink protocol core (signing, log replay, MAVLinkInspector) |
| `Vehicle/` | `Vehicle` object: one per connected autopilot; FactGroups, FTPController (MAVFTP), Autotune |
| `FactSystem/` | the "Fact" data-binding system: parameters/telemetry exposed as bindable properties for QML |
| `FirmwarePlugin/` | per-autopilot behavior differences (ArduPilot vs PX4 plugins) |
| `AutoPilotPlugins/` | per-vehicle setup pages (ArduPilot/PX4 config UIs) |
| `MissionManager/` | mission upload/download, geofence, rally points |
| `PlanView/` | mission planning map UI (QML) |
| `FlyView/`, `FlightMap/`, `GeoMap/` | live flight display & map engine |
| `PositionManager/` | vehicle position updates & simulated home positions |
| `VideoManager/` | video streaming (GStreamer, UVC, RTSP) |
| `AnalyzeView/` | MAVLink inspector, log download, GeoTagging, console |
| `Terrain/` | terrain elevation database handling |
| `QmlControls/` | shared QML widgets |
| `QtLocationPlugin/` | custom map provider plugin |
| `Settings/`, `AppSettings/` | persistent app settings |
| `Joystick/` | RC/gamepad input |
| `Gimbal/`, `Camera/`, `ADSB/`, `GPS/`, `FollowMe/`, `LogManager/`, `Viewer3D/`, `Toolbar/`, `Utilities/`, `MainWindow/`, `FirstRunPromptDialogs/`, `Android/`, `API/` | the obvious matching subsystems |

Root has `main.cc`, `QGCApplication.{h,cc}`, CMake files, `justfile`,
`CMakePresets.json`, `AGENTS.md`, `CLAUDE.md`, `docs/`, `custom-example/`
(vendor customization template), `resources/`, `translations/`.

## Build on Linux (as of this clone)
Requirements: **Qt 6.8+** development packages, cmake ≥3.22, ninja
(recommended), gcc. Get them via pacman:
```bash
sudo pacman -S --needed qt6-base qt6-declarative qt6-serialport qt6-positioning \
      qt6-speech qt6-multimedia qt6-charts qt6-svg qt6-imageformats cmake ninja
```
Then:
```bash
cd gcs/qgroundcontrol
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release
cmake --build build -j8
./build/qgroundcontrol   # or install to run
```
(A `justfile` and `CMakePresets.json` exist with project blessed recipes —
inspect `justfile` for the canonical `just build` style commands.)

## How it connects to ArduPilot
- Link layer auto-connects to serial devices (Pixhawk USB) and UDP 14550.
- With SITL in this workspace: SITL broadcasts UDP 14550/14551 → QGC
  typically autoconnects without configuration.
- After connection, QGC reads **parameters** via MAVLink (FactSystem),
  **missions** via the mission protocol (`MissionManager`), and supports
  MAVFTP (`Vehicle/FTPController`) for log download.
- `FirmwarePlugin/ArduPilot/` + `AutoPilotPlugins/APM/` contain all
  ArduPilot-specific pages (modes, setup, calibration specifics).

## Relation to the parent repo
- Protocol compatibility is maintained against the **same MAVLink XML
  dialect** (`modules/mavlink/` in the firmware clone).
- Firmware-side counterpart code: `libraries/GCS_MAVLink/` (see doc 17).
- QGC's `custom-example/` shows how vendors fork/brand QGC without
  upstream divergence — useful if drpilot ever needs a custom GCS skin.

## When to choose QGC vs MissionPlanner
| Need | Use |
|---|---|
| Linux/Android first-class support | QGC |
| MAVLink-standards behaviors (component info, MAVFTP-first) | QGC |
| ArduPilot log analysis (dataflash), richest AP tuning UI | MissionPlanner |
| Scripted CI/automation | MAVProxy, not QGC/MP manually |
