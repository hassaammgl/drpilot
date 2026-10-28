# 17 — MAVLink Integration: How Firmware ↔ GCS Talk

## 1. Where MAVLink lives *here*
- **Ground truth (XML):** `modules/mavlink/message_definitions/v1.0/*.xml`
  — `ardupilotmega.xml` + `common.xml` define every message/enum/command.
- **Firmware C-side:** `libraries/GCS_MAVLink/` builds the C structs at
  build time into `build/<board>/libraries/GCS_MAVLink/include/mavlink/v2.0/…`
  (`modules/mavlink/` provides the C implementation).
- **GCS side:** each GCS implements it in its own language — MAVProxy /
  Mission Planner via pymavlink-style dialect, QGC via its own MAVLink lib.

## 2. Physical linking
| Layer | On firmware | On GCS |
|---|---|---|
| UART/UDP/TCP/BLE port | `AP_SerialManager` maps `SERIAL1_PROTOCOL=2 MAVLink1`, `SERIAL2_PROTOCOL=-1 MAVLink2`, baud `SERIAL1_BAUD` | connection manager picks transport |
| Routing | `GCS_MAVLink` streams (up to `MAVLINK_COMM_NUM_BUFFERS`) | link objects per endpoint |
| Message rate | `SRx_*`-style `enums` (e.g. `GCS_Internals`) & `SCHED_LOOP_RATE`-linked stream rates | the GCS requests via `MAV_CMD_REQUEST_MESSAGE`/svr streams |

## 3. The interesting patterns
- **Mission protocol** — `MISSION_ITEM_INT` etc. AP_Mission validates/saves
  to EepromStorage; GCS uploads waypoints this way.
- **Parameter protocol** — `PARAM_SET`/`PARAM_VALUE` reading/writing any
  AP_Param directly; also `parameter editors` in every GCS.
- **Fence** — `FENCE_POINT` (legacy) / `MAV_CMD_*` polygon uploads.
- **Heartbeat** — every 1 Hz; the *mode, armed* state comes from here.
- **DataFlash log download** — MAVFTP-based on newer firmware; plain
  dataflash-over-MavLink for old.
- **Long-running ops** — `MAV_CMD` with ACK progress pattern
  (e.g. land start), via `AP_Mission`-independent command handlers.

## 4. Adding a NEW MAVLink message (firmware side)
The upstream-truth route:
1. XML change occurs upstream in `mavlink` repo (or you add private message
   via XML dialect — only when ArduPilot accepts upstream).
2. `libraries/GCS_MAVLink/GCS.h` exposes it via `handle_message()` and
   `GCS_Common.cpp` handles packing.
3. On serialize side, send from `GCS_MAVLink/Bailout*` stream table.
4. GCS side: interpret the new MAVLink id in MAVPlanner etc.

**Never invent message IDs locally** — they must exist in the MAVLink XML
dialect or every other GCS will reject them.

## 5. Debug tips
- In SITL, ports: TCP 5760 *is* the "sim master" link (MAVProxy uses it);
  UDP 14550/14551 are the two GCS-companion pages.
- `param set SERI2_PROTOCOL 2` etc. can open *new* MAVLink links at runtime.
- Connect MAVProxy in "verbose" mode with `--console --map` to visualize.
- On the firmware side, `param set LOG_DISARMED 1` will log before arming,
  so you can inspect GCS-driven traffic effects.
