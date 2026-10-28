# 05 — `Rover/` — File-by-File

Ground vehicles: cars, boats, balance bots, sailboats. Files in `Rover/`.

## Core & plumbing
| File | Role |
|---|---|
| `Rover.cpp` / `Rover.h` | `setup()`/`loop()`, `class Rover` |
| `config.h`, `defines.h`, `version.h`, `ReleaseNotes.txt`, `wscript` | plumbing |
| `Parameters.cpp/.h` | all rover params |
| `GCS_Rover.cpp/.h`, `GCS_MAVLink_Rover.cpp/.h` | MAVLink handlers |
| `RC_Channel_Rover.cpp/.h` | RC switches, XYZ momentary buttons etc. |
| `createTags` | helper (see header) |
| `Steering.cpp` | steering logic — steering/throttle-vs-brake mixing |

## Arming, state, safety
| File | Role |
|---|---|
| `AP_Arming_Rover.cpp/.h` | arming checks (wheel encoder, boat, etc.) |
| `AP_Rally.cpp/.h` | rally points |
| `AP_ExternalControl_Rover.cpp/.h` | external-control API |
| `afs_rover.cpp/.h` | advanced failsafe |
| `crash_check.cpp` | crash/rollover detection |
| `ekf_check.cpp` | EKF health checks |
| `failsafe.cpp` | battery/RC/GPS/EKF/throttle failsafes |
| `fence.cpp` | fencing |
| `events.cpp` | status text events |

## Drive system
| File | Role |
|---|---|
| `balance_bot.cpp` | balance-bot (like segway balancing) |
| `sailboat.cpp/.h` | sailboat (tack / wind algorithms, `SAIL_*` params) |
| `motor_test.cpp` | motor/servo test |
| `precision_landing.cpp` | PRECland for rover |

## Guidance/sensor glue
| File | Role |
|---|---|
| `commands.cpp` | mission command handlers |
| `cruise_learn.cpp` | CRUISE_THROTTLE auto-learn |
| `radio.cpp`, `sensors.cpp`, `system.cpp` | RC / sensors / system glue |
| `Log.cpp` | vehicle log formats |

## Flight modes
| File | Meaning |
|---|---|
| `mode.cpp/.h` | mode registry / base class |
| `mode_manual.cpp` | MANUAL — raw user control |
| `mode_acro.cpp` | ACRO — rate-controlled steering |
| `mode_hold.cpp` | HOLD — stop & brake |
| `mode_loiter.cpp` | LOITER — position hold (GPS) |
| `mode_guided.cpp` | GUIDED — external (GCS) driving |
| `mode_steering.cpp` | STEERING — manual throttle, autopilot steering |
| `mode_circle.cpp` | CIRCLE — circle around point |
| `mode_auto.cpp` | AUTO — mission |
| `mode_simple.cpp` | SIMPLE — heading-crab-compensated manual |
| `mode_smart_rtl.cpp` | SMART_RTL — backtrack path home |
| `mode_rtl.cpp` | RTL |
| `mode_follow.cpp` | FOLLOW — follow another MAVLink vehicle |
| `mode_dock.cpp` | DOCK — drive to a docking beacon |

## Related libraries
- `AR_Motors` (`libraries/AR_Motors`) — drive-type abstraction (skid steer,
  omni, sailboat, regular steering+throttle)
- `AR_WPNav` (`libraries/AR_WPNav`) — waypoint navigation for ground/boat

## Reading path
1. `Rover.cpp` scheduler → `radio.cpp` (mode switch)
2. `Steering.cpp` + `libraries/AR_Motors` — how wheels get commands
3. `mode_guided.cpp` + `libraries/AR_WPNav` — path following
4. `sailboat.cpp` — most exotic corner (wind-vane math)
