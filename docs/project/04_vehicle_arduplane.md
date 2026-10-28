# 04 — `ArduPlane/` (Plane firmware) — File-by-File

ArduPlane flies fixed-wing aircraft *and* VTOL/quadplanes (hybrid heli-tip
tilt-/tailsitters). Every file below is inside `ArduPlane/`.

## Core files
| File | Role |
|---|---|
| `Plane.cpp` | `setup()`/`loop()`, scheduling |
| `Plane.h` | `class Plane` |
| `config.h`, `defines.h`, `version.h`, `wscript` | plumbing |
| `createTags` | helper script/tool (see file header) |

## Vehicle plumbing
| File | Role |
|---|---|
| `Parameters.cpp/.h` | all vehicle params (FBW*, Q_*, TECS, etc.) |
| `GCS_Plane.cpp/.h`, `GCS_MAVLink_Plane.cpp/.h` | MAVLink handlers |
| `RC_Channel_Plane.cpp/.h` | RC switches, mode switch logic |
| `AP_Arming_Plane.cpp/.h` | arming checks (airspeed, throttle) |
| `AP_ExternalControl_Plane.cpp/.h` | external control API |
| `afs_plane.cpp/.h` | advanced-failsafe hooks |
| `Log.cpp` | vehicle log messages (CTUN, ATR, WAS, etc.) |

## Control & dynamics
| File | Role |
|---|---|
| `Attitude.cpp` | plane attitude controller glue (roll/pitch/yaw targets) |
| `altitude.cpp` | altitude/TECS glue; maintains altitude targets |
| `is_flying.cpp` | is-the-plane-actually-flying detection |
| `servos.cpp` | servo output mixing (control surface mixing)
| `navigation.cpp` | nav glue (bearing/waypoint handling) |
| `reverse_thrust.cpp` | reverse payload thrust (rare use case) |
| `VTOL_Assist.cpp/.h` | VTOL stabilizing assist (incl. instability handling) |

## Quadplane / VTOL subsystem (big chunk)
| File | Role |
|---|---|
| `quadplane.cpp/.h` | the whole VTOL subsystem: Q_ASSIST transitions |
| `tailsitter.cpp/.h` | tailsitter special-case config |
| `tiltrotor.cpp/.h` | tiltrotor mechanics |
| `qautotune.cpp/.h` | quadplane autotune |
| Transitions handled inside `quadplane.cpp` (Q_TRANS / quadplane transition)  |

## Flight modes (each file = one mode)
| File | Meaning |
|---|---|
| `mode.cpp/.h` | mode registry, enum, base `Mode` class |
| `mode_manual.cpp` | MANUAL — direct surface control |
| `mode_stabilize.cpp` | STABILIZE — pilot stick stabilized |
| `mode_training.cpp` | TRAINING — soft limits before stall |
| `mode_acro.cpp` | ACRO — aerobatic rate control |
| `mode_fbwa.cpp` | FBWA — fly-by-wire A (stabilized manual) |
| `mode_fbwb.cpp` | FBWB — stabilized + altitude hold |
| `mode_cruise.cpp` | CRUISE — hold heading/meter way level flight |
| `mode_loiter.cpp` | LOITER — circle over a point |
| `mode_auto.cpp` | AUTO — run mission |
| `mode_autotune.cpp` | AUTOTUNE — auto PID tuning |
| `mode_autoland.cpp` | AUTOLAND — structured mission-like land |
| `mode_circle.cpp` | CIRCLE — like Loiter but without navigation correction |
| `mode_guided.cpp` | GUIDED — fly to GCS-provided targets |
| `mode_rtl.cpp` | RTL — return-to-launch then loiter/land |
| `mode_takeoff.cpp` | TAKEOFF — automatic takeoff |
| `mode_thermal.cpp` | THERMAL — thermal soaring mode |
| `mode_avoidADSB.cpp` + `avoidance_adsb.cpp/.h` | ADSB-based avoidance |
| `mode_LoiterAltQLand.cpp` | Loiter-then-ALT-QLand helper mode |
| Quadplane modes: `mode_qacro.cpp`, `mode_qautotune.cpp`, `mode_qhover.cpp`, `mode_qland.cpp`, `mode_qloiter.cpp`, `mode_qrtl.cpp`, `mode_qstabilize.cpp` | the Q_* modes: VTOL-side flight types (STABILIZE/HOVER/LAND/LOITER/RTL/AUTOTUNE/ACRO) |

## Subsystems & safety
| File | Role |
|---|---|
| `commands.cpp`, `commands_logic.cpp` | mission/waypoint handling |
| `fence.cpp` | geo-fencing |
| `failsafe.cpp` | RC/gps etc. failsafes |
| `ekf_check.cpp` | EKF health |
| `events.cpp` | status text events |
| `parachute.cpp` | parachute deployment |
| `soaring.cpp` | soaring autonomy (AP_Soaring) |
| `motor_test.cpp` | motor/servo test |
| `radio.cpp` | RC input |
| `sensors.cpp` | airspeedSensor/Airspeed/Baro handling |
| `system.cpp` | misc. |
| `systemid.cpp/.h` | system identification excitation |
| `pullup.cpp/.h` | aerobatic pullup helper (auto mode) |
| `takeoff.cpp` | takeoff (runway) |
| `tuning.cpp/.h` | Tuning parameters |
| `transition.h` | transition interfaces (quadplane) |

## Interesting libraries with plane-specific behavior
- `AP_TECS` — total-energy altitude/airspeed controller
- `AP_L1_Control` — lateral navigation (bearing tracking where all the math fits)
- `AP_Soaring`, `AP_Landing` (incl. autoland glide), `AP_LandingGear`
- `AP_ServoRelayEvents` — servos acting as relays/retracts

## Reading path suggestion
1. `Plane.cpp` init/scheduler → `control_modes.cpp`
2. `Attitude.cpp` + `altitude.cpp` (TECS/L1 overview)
3. `servos.cpp` (control mapping)
4. `quadplane.cpp` if you care about VTOLs
5. `mode_guided.cpp` for GCS-driven waypoints
