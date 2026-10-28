# 02 — ArduPilot Firmware: How It Actually Works

## 1. Lifecycle of one firmware boot

1. **Bootloader** (`Tools/AP_Bootloader`) runs first on real boards, can
   upgrade to the main firmware stored in flash.
2. `main()` lives in the vehicle folder (e.g. `ArduCopter/Copter.cpp`
   contains `setup()` and `loop()` for Copter).
3. `setup()` constructs the singletons (singleton pattern everywhere:
   `AP_GPS::get_singleton()` etc.), initializes sensors, loads `AP_Param`
   values from flash, attaches the MAVLink GCS interface, and sets up the
   **scheduler task table**.
4. `loop()` runs `AP_Scheduler` forever. The scheduler runs named tasks at
   fixed tick rates — this is the entire "operating system".

## 2. The scheduler model (`libraries/AP_Scheduler`)

There is no free-running RTOS user-threads in flight code (though ChibiOS
is underneath). Flight logic is a **cooperative fixed-rate task table**
— e.g. in Copter's `Copter.cpp`:

| Task | Typical rate |
|---|---|
| `update_inertial_nav` / AHRS update | 400 Hz (fast loop) |
| attitude control / rate controllers | 400 Hz |
| position controllers, WP navigation | 50–200 Hz |
| EKF independent run | 100 Hz |
| baro, GPS, compass reads | configurable 10–50 Hz |
| telemetry / logging / GCS | adjustable |

**Why:** hard real-time guarantee. Every task is budgeted; `AP::scheduler`
notifies overruns, and the fast-loop time budget is checked at boot.
This design makes timing deterministic enough for a 400 Hz rate controller.

## 3. Estimation pipeline

```
IMUs ─┐
GPS ──┤
Baro ─┼→ AP_AHRS → vehicles read position/attitude/velocity
Mag ──┤      ↑
Airspeed, OF, VIO whatever enabled — EKF2/EKF3 fusions everything
```

- `AP_InertialSensor` collects raw IMU + performsPark-type vibration
  checks; `AP_GyroFFT` does notch filtering of noise.
- `AP_NavEKF3` (default; EKF2 kept as legacy) fuses them into a full nav
  state and emits **innovation/consistency** health metrics.
- `AP_AHRS` is the state facade + fallback to DCM (complementary filter)
  if EKF fails.
- Vehicles' `ekf_check.cpp` implements the *fail → switch away* logic
  (e.g. Copter lands-EKF failsafe).

## 4. Control pipeline (how a motor output happens)

Copter example, every fast tick:

```
desired attitude (from flight mode)
   → AC_AttitudeControl (angle → rate target)
     → AC_PID / rate controllers (P-I-D style)
       → AP_Motors (matrix layout & thrust linearization)
         → SRV_Channel/AP_IOMCU (PWM → hardware/DShot)
```

Planes: `AP_TECS` (total energy control for altitude/speed) +
`AP_L1_Control` (lateral path following) feed the roll/pitch controllers.
Rover: `AR_*` steering/motor libraries. Sub: vertical+horizontal thrusters.

**Flight mode implementations** are `mode_*.cpp` in each vehicle dir: each
mode is a class deriving from `Mode`/`ModeCopter`-family, with
`init/run/exit/_W_S_safe`-style pure virtuals. All vehicle modes are
registered in `mode.cpp`.

## 5. Persistence, parameters & logging

- **`AP_Param`** is the parameter system: every library declares a params
  table (e.g. `AP_NavEKF3` has EKF3_* params); each *vehicle* aggregates
  them in its `Parameters.cpp/h`. Values persist in flash-backed storage
  (`AP_FlashStorage`, or a `param.parm` file in sim). GCSs enumerate
  parameters at runtime — that's how Mission Planner builds its tuning UI.
- **`AP_Logger`** writes `.bin` (DataFlash) logs onboard (FMT/FMTU blocks).
  Each vehicle declares what it logs (e.g. `ArduCopter/Log.cpp` defines
  `CTUN` for control tuning, `IMU`, `GPS`, `RCIN`/`RCOU`, `AHR2`)
  . Log files become the ground truth for debugging crashes with
  Mission Planner's log analysis.

## 6. HAL (the abstraction trick)

`libraries/AP_HAL` is pure interface classes (UART, I2C, SPI, CAN, RC
in/out, storage, scheduler). Each backend (ChibiOS, SITL, ESP32, Linux,
QUERT, Empty, …) implements it:

| Backend | Real explanation |
|---|---|
| `AP_HAL_ChibiOS` | 'production' stack for STM32 boards (~thousands of boards via hwdef) |
| `AP_HAL_SITL` | runs the same interface against simulated serials, simulated GPS, physics engine |
| `AP_HAL_ESP32` | ESP32 microcontrollers |
| `AP_HAL_Linux` | BeagleBone/Pi-style SBC I/O |
| `AP_HAL_QURT` | Qualcomm hexagon DSP (virtual drone builds) |
| `AP_HAL_Empty` | skeleton to port to a new platform |

There is **one board definition per hardware target in
`libraries/AP_HAL_ChibiOS/hwdef/<board>/`**: pins, clocks, peripherals,
it even builds the matching bootloader. Adding a board = writing a hwdef.

## 7. Failsafes, safety, AP_Arming

- `AP_Arming[_Copter]` checks before unlock: GPS fix, compass, IMU, RC
  calibration, no failsafes active, barric condition, battery etc.
- Each vehicle has `failsafe.cpp`: battery/RXTX-loss/GPS-loss/EKF/terrain
  failsafes with configurable action params (e.g. LAND, RTL, alert).
- **Advanced failsafe** & "ArduPilot Flight Assisted Safety" parts are in
  `AP_AdvancedFailsafe` (AFS_*) — mostly for AATDesign-flavour use cases.

## 8. Extention points

- **AP_Scripting: Lua interpreter** (built into the firmware) with
  read/write access to vehicle state; scripts live on the SD card and can
  deeply customize behavior without recompiling.
- **AP_CustomControl / AC_CustomControl**: user-registered controllers
  (including compiled C++ custom controls and Lua).
- **AP_Module:** C-modules compiled in via hook callbacks (rare).
- **AP_SerialManager** routes GCS/UART mapping (SERIALx_PROTOCOL params).

## 9. Constants worth memorizing

- `AP::vehicle()`, `AP::ahrs()`, `AP::param()`, `AP::logger()` — global
  singletons (see `libraries/AP_Common/AP_FWVersion.cpp` and friends).
- `GCS_SEND_TEXT(MAV_SEVERITY, …)` is the correct way to print user info —
  it *must* go through GCS_MAVLink, **not** printf.
- Timing always via `AP_HAL::millis()/micros()` — never platform APIs.
