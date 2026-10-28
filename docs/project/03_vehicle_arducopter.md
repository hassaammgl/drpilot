# 03 — `ArduCopter/` (Copter firmware) — File-by-File

Copter is the largest vehicle: multirotors (quad/hex/octo/y6/x8, tradheli).
Every file below is in `ArduCopter/`. Larger groupings first, then A→Z.

## Core vehicle files
| File | Role |
|---|---|
| `Copter.cpp` | `setup()`/`loop()`, scheduler task table, main init |
| `Copter.h` | `class Copter` — the god-object holding everything |
| `config.h` | compile-time feature switches (`AP_COPTER_*`) |
| `defines.h` | enum constants (mode numbers, failsafe ids) |
| `version.h` | firmware version strings |
| `wscript` | which libraries this vehicle links (waf) |

## Parameters / interface plumbing
| File | Role |
|---|---|
| `Parameters.cpp/.h` | every `CAM_*`/`PLND_*` etc. param; the full grid of parameter objects |
| `UserParameters.cpp/.h`, `UserVariables.h`, `UserCode.cpp` | deliberate empty slots for user patches |
| `RC_Channel_Copter.cpp/.h` | RC input mapping to vehicle actions (switches, buttons) |
| `GCS_Copter.cpp/.h` | GCS message subclasses (capabilities, status text) |
| `GCS_MAVLink_Copter.cpp/.h` | Copter-side MAVLink message handlers (command_long → action) |

## Arming, failsafe, EKF, sensors
| File | Role |
|---|---|
| `AP_Arming_Copter.cpp/.h` | pre-flight checks specific to copters |
| `AP_Rally.cpp/.h` | rally points (fallback loiter positions) |
| `AP_State.cpp` | misc persistent state |
| `AP_ExternalControl_Copter.cpp/.h` | external control interface (offboard setpoints over MAVLink/DDS) |
| `baro_ground_effect.cpp` | pressure bump near ground correction |
| `compassmot.cpp` | compass-motor interference calibration routine |
| `crash_check.cpp` | crash/blackbox detection (CRASH_FLIP, LAND_REPAIR) |
| `ekf_check.cpp` | EKF variance failsafe logic |
| `esc_calibration.cpp` | ESC calibration routine |
| `events.cpp` | event notifications (switch warnings, etc.) |
| `failsafe.cpp` | copter-wide failsafe state machine ( Batt/RC/GPS/EKF) |
| `fence.cpp` | fence handling (polygon/cylinder) |
| `heli.cpp` | helicopter-specific: rotor run-up, dynamic tuning |
| `inertia.cpp` | IMU/INS setup |
| `land_detector.cpp` | ground detection logic (used by althold etc.) |
| `landing_gear.cpp` | retractable landing gear control |
| `motors.cpp` | motor setup/arm/output glue into `AP_Motors` |
| `motor_test.cpp` | MOT_* test/protocol for spinning motors |
| `navigation.cpp` | waypoint/nav misc utilities |
| `precision_landing.cpp` | PRECland coordinate providing |
| `radio.cpp` | RC input handling (flight-mode switch logic) |
| `rate_thread.cpp` | optional helper thread for rate control |
| `sensors.cpp` | sensor update dispatch |
| `standby.cpp` | standby mode (e.g. lifted off after being parked) |
| `surface_tracking.cpp` | terrain/surface altitude tracking |
| `system.cpp` | system-level tasks (arming, LED, etc.) |
| `takeoff.cpp`, `takeoff_check.cpp` | takeoff logic (throttle check + takeoff path) |
| `terrain.cpp` | terrain following handling (AP_Terrain front-end) |
| `toy_mode.cpp/.h` | toy/OTC mode (OEM toy copters: gesture-handshake — rarely used) |
| `tuning.cpp` | autonomous tuning (AutoTune quick tuning) |
| `avoidance.cpp`, `avoidance_adsb.cpp/.h` | ADSB & obstacle-avoidance wrappers |
| `afs_copter.cpp/.h` | advanced failsafe hooks |

## Attitude & guidance
| File | Role |
|---|---|
| `Attitude.cpp` | copter-specific attitude control glue (angle/rate targets) |
| `autoyaw.cpp` | desired-yaw logic per mode |
| `commands.cpp` | mission command handling (pipelining into AP_Mission) |

## MAVLink log facilites
| File | Role |
|---|---|
| `Log.cpp` | vehicle-specific log messages (CTUN, MOT, PMON,plta…) |

## Flight modes (every file = one mode class)
| File | Mode | Meaning |
|---|---|---|
| `mode.cpp/.h` | plumbing | mode registry, base class helpers |
| `mode_acro.cpp` | ACRO | rate-controlled acrobatics |
| `mode_acro_heli.cpp` | ACRO (heli) | heli-specific acro |
| `mode_althold.cpp` | ALT_HOLD | altitude hold w/ manual roll-pitch |
| `mode_auto.cpp` | AUTO | run saved mission (waypoints) |
| `mode_autorotate.cpp` | AUTOROTATE | heli autorotation on engine failure |
| `mode_autotune.cpp` | AUTOTUNE | live PID tuning |
| `mode_avoid_adsb.cpp` | AVOID_ADSB | ADSB avoidance flight |
| `mode_brake.cpp` | BRAKE | full stop|
| `mode_circle.cpp` | CIRCLE | loiter around a point |
| `mode_drift.cpp` | DRIFT | simplified "gamepad-like" flight |
| `mode_flip.cpp` | FLIP | 360 roll/pitch maneuver |
| `mode_flowhold.cpp` | FLOWHOLD | optical-flow position hold w/o GPS |
| `mode_follow.cpp` | FOLLOW | follow another vehicle (AP_Follow) |
| `mode_guided.cpp` | GUIDED | external setpoint control (GCS command) |
| `mode_guided_custom.cpp` | GUIDED_CUSTOM | quadsPL-style custom guided controller |
| `mode_guided_nogps.cpp` | GUIDED_NOGPS | guided w/o GPS (flow/vision-based) |
| `mode_land.cpp` | LAND | descend & land |
| `mode_loiter.cpp` | LOITER | GPS position hold |
| `mode_poshold.cpp` | POSHOLD | position hold w/ loiter + manual altitude |
| `mode_rtl.cpp` | RTL | return to launch |
| `mode_smart_rtl.cpp` | SMART_RTL | RTL along learned path |
| `mode_sport.cpp` | SPORT | heading-locked rate mode |
| `mode_stabilize.cpp` | STABILIZE | manual stabilized |
| `mode_stabilize_heli.cpp` | STABILIZE (heli) | heli variant |
| `mode_systemid.cpp` | SYSTEMID | excitation injection for engineering |
| `mode_throw.cpp` | THROW | launch into air from hand |
| `mode_turtle.cpp` | TURTLE | upside-down (turtle mode) |
| `mode_zigzag.cpp` | ZIGZAG | sweep navigation (spraying) |

## Related libraries you'll see in above files
- `libraries/AP_Motors*` — Throttle (thrust linearization + motor mix)
- `libraries/AC_AttitudeControl*` — angle/rate control, incl. `AC_AttitudeControl_Multi` and `AC_AttitudeControl_Heli`
- `libraries/AC_WPNav*` — waypoint/loiter navigation
- `libraries/AC_AutoTune`, `AC_Autorotation`, `AC_PrecLand` — modes glue
- `libraries/GCS_MAVLink` — command_long implementations on vehicle side

## Where to start reading (recommended path)
1. `Copter.cpp` → scheduler table → `update_flight_modes()`
2. `mode_stabilize.cpp` + `libraries/AC_AttitudeControl/AC_AttitudeControl_Multi.cpp`
3. `motors.cpp` + `libraries/AP_Motors/AP_MotorsMulticopter.cpp`
4. `mode_guided.cpp` (how the GCS drives position/targets)
5. `failsafe.cpp` + `ekf_check.cpp` (safety chain)
