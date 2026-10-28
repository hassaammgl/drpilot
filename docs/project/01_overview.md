# 01 — Whole-System Overview

## 1. The 30-second version

ArduPilot is a split-brain system:

1. **Autopilot firmware** (this repo's root) — C++ code that runs *on the
   vehicle* (or in a simulator) and does everything safety-critical:
   attitude control, navigation, EKF sensor fusion, failsafes, motor output.
2. **Ground Control Station (GCS)** — runs *on your laptop* and gives humans
   a window into the vehicle: maps, telemetry, mission planning, parameter
   tuning. Three are cloned here: MissionPlanner, QGroundControl, MAVProxy.

The bridge between the two halves is the **MAVLink protocol** — a binary
message protocol where every byte is defined in the XML files under
`modules/mavlink/`. Firmware side is implemented in `libraries/GCS_MAVLink/`,
GCS side by each GCS itself.

## 2. Layered architecture of the firmware

```
┌─────────────────────────────────────────────────────────┐
│  Vehicle layer: ArduCopter / ArduPlane / Rover / Sub /  │
│  Blimp / AntennaTracker                                 │
│  (flight modes, vehicle parameters, failsafe policies)  │
├─────────────────────────────────────────────────────────┤
│  Control & navigation libraries:                        │
│  AC_AttitudeControl, AC_WPNav, AP_TECS, AP_L1_Control,  │
│  AP_Mission, AP_Navigation, AP_SmartRTL …               │
├─────────────────────────────────────────────────────────┤
│  Estimation & sensing:                                  │
│  AP_NavEKF3 (EKF2 fallback), AP_AHRS, AP_GPS, AP_Baro,  │
│  AP_Compass, AP_InertialSensor, AP_RangeFinder …        │
├─────────────────────────────────────────────────────────┤
│  Services: AP_Param, AP_Logger, AP_Scheduler,           │
│  GCS_MAVLink, AP_Scripting, AP_Mount, AP_Camera …       │
├─────────────────────────────────────────────────────────┤
│  AP_HAL — Hardware Abstraction Layer (pure interface)   │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│ HAL_ChibiOS│ HAL_SITL │ HAL_ESP32│ HAL_Linux│ HAL_QURT … │
│ (STM32     │ (simu-   │ (ESP32)  │ (SBCs)   │ (virtual)  │
│  boards)   │  lation) │          │          │            │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
```

Key design decisions and **why** they are like this:

- **One firmware tree per vehicle type.** A quadcopter, a plane and a boat
  share 90% of libraries but have totally different control loops. Keeping
  the vehicle layer separate keeps each firmware small (embedded flash is a
  hard budget).
- **`libraries/` is the shared brain.** Anything that two vehicle types
  would both use goes here. Libraries never call into vehicle code — the
  dependency direction is strictly downward (vehicle → libraries → HAL).
- **AP_HAL exists because ArduPilot supports ~10 different OS/hardware
  stacks.** Firmware code never touches a register directly; it asks the
  HAL. The `sitl` board implements the same interface against simulated
  hardware — which is why the *same firmware code* can run in simulation
  and on real hardware.
- **EKF fusion (AP_NavEKF3)** is the heart of "where am I": it blends IMUs,
  GPS, compass, barometer, airspeed, optical flow etc. into one state
  estimate. AP_AHRS is the facade vehicles talk to.

## 3. The GCS landscape (`gcs/`)

| GCS | Language | Role in this ecosystem |
|---|---|---|
| **MissionPlanner** | C# (WinForms) | The most feature-complete desktop GCS; the de-facto Windows ground station; also used by ArduPilot devs for log analysis and firmware upload |
| **QGroundControl** | C++/Qt/QML | The cross-platform GCS (Linux/macOS/Android), MAVLink-standard centric, works with PX4/ArduPilot/etc. |
| **MAVProxy** | Python | Headless/console GCS. Not for humans — it is the *automation backbone*: ArduPilot's own autotest framework runs every CI flight test through MAVProxy |

All three speak the same MAVLink dialect, so any of them can talk to any
ArduPilot vehicle — or to SITL running on this machine.

## 4. How a typical session flows (this exact workspace)

```
 your laptop
 ┌──────────────────────────────────────────────────────┐
 │  .venv/bin/python ./waf configure --board sitl       │
 │  .venv/bin/python ./waf copter        → build/sitl/  │
 │                                                      │
 │  build/sitl/bin/arducopter  (SITL = fake drone)      │
 │      ↕ UDP 14550/14551 (MAVLink, simulated serial)   │
 │  MissionPlanner / QGC / MAVProxy                     │
 │  (connect your GCS to 14550, see live telemetry)     │
 └──────────────────────────────────────────────────────┘
```

The same firmware source, compiled with `--board` for real hardware
(e.g. `--board Pixhawk6C`), gives a `.apj`/`.bin` firmware that gets
flashed to a real flight controller — and the very same GCS then connects
over a real telemetry radio.

## 5. Repo gravitational centers (where to look for what)

| Question | Where the answer lives |
|---|---|
| "Why did my copter flip / what does ALTHOLD do?" | `ArduCopter/mode_althold.cpp`, `libraries/AC_AttitudeControl` |
| "How is GPS data turned into velocity?" | `libraries/AP_GPS` → `libraries/AP_NavEKF3` |
| "What are all the parameters (e.g. `ATC_RAT_RLL_P`)?" | `ArduCopter/Parameters.cpp` + each library's own `Parameters.cpp` |
| "What a vehicle logs (.bin files explained)" | `ArduCopter/Log.cpp` + `libraries/AP_Logger` |
| "What messages can the GCS send?" | `libraries/GCS_MAVLink/` (firmware side) and `modules/mavlink/message_definitions/` (XML truth) |
| "How does autotest decide a flight test passed?" | `Tools/autotest/autotest.py`, `Tools/autotest/state.py`, `tests/` |
| "Mission Planner's map/flight view code" | `gcs/MissionPlanner/GCSViews/`, `Controls/` |

## 6. House rules that make this codebase unusual

- **C++17/20**, no exceptions, no RTTI-ish patterns; heavy use of
  zero-initialized memory (ArduPilot overrides `new`/`malloc` to zero).
- **Style enforced by astyle** (`Tools/CodeStyle/astylerc`), Python by
  flake8. One-subsystem-per-commit via `Tools/scripts/allowed_subsystems.py`.
- **Everything optional is behind `AP_<FEATURE>_ENABLED`** defines so that
  tiny boards can compile firmware without,{
  e.g. scripting or cameras.
- **Parameters are the exposed control surface.** Nearly every tunable knob
  is an `AP_Param` (flash-stored) with a documented `@Param:` annotation —
  GCSs read these and generate their UIs automatically.
