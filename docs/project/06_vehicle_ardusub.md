# 06 — `ArduSub/` — File-by-File

Underwater ROVs/AUVs (typically BlueROV-style 6-/8-thruster frames).
Files in `ArduSub/`.

## Core & plumbing
| File | Role |
|---|---|
| `Sub.cpp` / `Sub.h` | `setup()`/`loop()`, `class Sub` |
| `config.h`, `defines.h`, `version.h`, `ReleaseNotes.txt`, `wscript` | plumbing |
| `Parameters.cpp/.h` | sub parameters (CAM_, SND_* etc.) |
| `GCS_Sub.cpp/.h`, `GCS_MAVLink_Sub.cpp/.h` | MAVLink handlers |
| `RC_Channel_Sub.cpp/.h` | RC input mapping |
| `UserCode.cpp`, `UserVariables.h`, `UserCode` | user patch slots |
| `AP_State.cpp` | persistent state |

## Safety & arming
| File | Role |
|---|---|
| `AP_Arming_Sub.cpp/.h` | arming checks |
| `failsafe.cpp`, `fence.cpp`, `ekf_check`(if present) | failsafes |
| `ap_mavlink` above | |

## Sub-specific control
| File | Role |
|---|---|
| `motors.cpp` | thruster setup (APMotors-style for sub layout) |
| `actuators.cpp/.h` | light / gripper / other actuator output |
| `Attitude.cpp` | sub attitude control glue |
| `joystick.cpp` | joystick handling (used by QGC-style control scheme) |
| `surface_bottom_detector.cpp` | detect surface/bottom contact |
| `turn_counter.cpp` | odometer-style rotation counting |
| `script_button.cpp/.h` | Lua-scripted button support |
| `inertia.cpp`, `commands.cpp/.h`, `commands_logic` | misc glue |
| `terrain.cpp` | terrain handling |
| `sensors.cpp`, `system.cpp`, `radio.cpp`, `Log.cpp` | standard glue |

## Flight modes
| File | Meaning |
|---|---|
| `mode.cpp/.h` | mode registry/base class |
| `mode_manual.cpp` | MANUAL — pilot direct thruster control |
| `mode_stabilize.cpp` | STABILIZE — pilot + attitude stabilization (held) |
| `mode_althold.cpp` | ALT_HOLD — stabilize + depth hold |
| `mode_poshold.cpp` | POSHOLD — depth + position hold (DVL-style pos) |
| `mode_acro.cpp` | ACRO |
| `mode_auto.cpp` | AUTO — mission |
| `mode_guided.cpp` | GUIDED |
| `mode_circle.cpp` | CIRCLE |
| `mode_surface.cpp` | SURFACE — ascend & surface |
| `mode_surftrak.cpp` | SURFTRAK — bottom-following (constant distance to terrain) |
| `mode_motordetect.cpp` | MOTOR_DETECT — detect gain from motor tests |

## Notable hardware protocols
- Pressure sensors, leak detectors přes `AP_LeakDetector`, water temperature
- BlueROV heavy frames defined via `AP_Motors6DOF` in `libraries/AP_Motors`

## Reading path
1. `Sub.cpp` task table
2. `motors.cpp` → `libraries/AP_Motors/AP_Motors6DOF.cpp`
3. `mode_althold.cpp` + `mode_poshold.cpp` (depth control chain)
4. `mode_surftrak.cpp` (bottom following, rangefinder-based)
