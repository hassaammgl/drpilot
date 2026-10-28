# 07 — `Blimp/` — File-by-File

Lighter-than-air vehicles. Notably Blimp's architecture is **different** from
the other vehicles: it has no AP_Motors, instead "fins" + vectored
thrusters, and a velocity-oriented control stack. Files in `Blimp/`.

## Core & plumbing
| File | Role |
|---|---|
| `Blimp.cpp` / `Blimp.h` | `setup()`/`loop()`, `class Blimp` |
| `config.h`, `defines.h`, `version.h`, `wscript` | plumbing |
| `Parameters.cpp/.h` | blimp params |
| `GCS_Blimp.cpp/.h`, `GCS_MAVLink_Blimp.cpp/.h` | MAVLink |
| `RC_Channel_Blimp.cpp/.h` | RC mapping |
| `AP_Arming_Blimp.cpp/.h` | arming |
| `AP_State.cpp`, `commands.cpp`, `inertia.cpp`, `sensors.cpp`,`system.cpp`, `radio.cpp`, `Log.cpp` | standard glue |
| `failsafe.cpp`, `events.cpp`, `ekf_check.cpp` | safety |

*(`Rover/`-specific files like `sailboat` absent; Blimp has a flat file set.)*

## Control system
| File | Role |
|---|---|
| `Fins.cpp/.h` | fin vectored-thrust output mixing — the blimp analog of motors |
| `motors.cpp` | thrust-only (no attitude-hold) pressure setpoint logic |
| `Loiter.cpp/.h` | velocity XY hold controller |

## Flight modes
| File | Meaning |
|---|---|
| `mode.cpp/.h` | registry/base class |
| `mode_manual.cpp` | MANUAL |
| `mode_velocity.cpp` | VELOCITY — inertial velocity command mode |
| `mode_loiter.cpp` | LOITER — position hold |
| `mode_hold.cpp` | HOLD — keep station |
| `mode_land.cpp` | LAND |
| `mode_rtl.cpp` | RTL |
| `mode_auto.cpp` | AUTO |

## Reading path
1. `Blimp.cpp` scheduler
2. `Fins.cpp` — fin mixing math
3. `Loiter.cpp` — velocity holding
4. `mode_velocity.cpp` — inertial velocity command path
