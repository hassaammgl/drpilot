# 08 — `AntennaTracker/` — File-by-File

AntennaTracker is a *ground-side* autopilot: it steers a directional
antenna to follow a MAVLink-positioned vehicle. It is small by design.
Files in `AntennaTracker/`.

## Core & plumbing
| File | Role |
|---|---|
| `Tracker.cpp` / `Tracker.h` | `setup()`/`loop()`, `class Tracker` |
| `config.h`, `defines.h`, `version.h`, `ReleaseNotes.txt`, `AntennaTracker.txt`, `wscript` | plumbing |
| `Parameters.cpp/.h` | tracker params (PID mount params etc.) |
| `GCS_Tracker.cpp/.h`, `GCS_MAVLink_Tracker.cpp/.h` | MAVLink (receives vehicle position; sends its own status) |
| `RC_Channel_Tracker.cpp/.h`, `radio.cpp` | manual control / tuning inputs |

## Operational files
| File | Role |
|---|---|
| `AP_Arming_Tracker.h` | arming |
| `tracking.cpp` | the heart: PID tracking of bearing/elevation toward vehicle |
| `servos.cpp` | pan/tilt servo output |
| `sensors.cpp` | compass update (what "aim" is relative to) |
| `system.cpp`, `Log.cpp`, `mode.cpp` | standard glue |

## Flight/mount modes
| File | Meaning |
|---|---|
| `mode.h` | `Mode` base |
| `mode_manual.cpp` | MANUAL — RC moves pan/tilt directly |
| `mode_scan.cpp` | SCAN — prerotate between azimuths |
| `mode_servotest.cpp` | SERVOTEST — test sweep |
| `mode_auto.cpp` | AUTO — track vehicle from MAVLink position |
| `mode_guided.cpp` | GUIDED — aim at pointed coordinates |

## Why a separate vehicle?
It has completely different dynamics (a servo gimbal, no drone physics), so
an independent firmware must exist — but it *rides on the same libraries*
(AP_AHRS, AP_Param, GCS_MAVLink, AP_Mount-style control math).

## Reading path
1. `Tracker.cpp` task table
2. `tracking.cpp` → `servos.cpp` — position → gimbal math
3. `GCS_MAVLink_Tracker.cpp` — where vehicle positions arrive
