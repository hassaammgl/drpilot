# 14 — `modules/` — Every Git Submodule Explained

`modules/` contains other projects pinned as git submodules (`.gitmodules`).
**Rule:** never edit files here — everything is replaced by
`git submodule update --init --recursive`.

| Submodule | What it is | Used by |
|---|---|---|
| **ChibiOS** | the RTOS + STM32 drivers underneath the ChibiOS HAL; per-board configs under `modules/ChibiOS/os/hal/boards` or hwdef-generated | `AP_HAL_ChibiOS` |
| **waf** | the fork of the waf build tool ArduPilot builds with (auto-cloned during first configure) | `./waf`, `Tools/ardupilotwaf/` |
| **mavlink** | MAVLink C library + the XML message definitions + **pymavlink** (as nested submodule at `modules/mavlink/pymavlink`) | `GCS_MAVLink` (C generation), build-time codegen, MAVProxy (python impl is separate but same dialect) |
| **DroneCAN** | DroneCAN (UAVCAN v0) DSDL definitions + `dronecan_dsdlc` generator | `AP_DroneCAN` |
| **DroneCAN/dronecan_dsdlc** (inside above) | the C code generator for DroneCAN | same |
| **gtest** | GoogleTest C++ unit-test framework | `libraries/*/tests/` |
| **gbenchmark** | Google Benchmark | `benchmarks/` |
| **littlefs** | littlefs filesystem used on internal flash (onboard params/logs) | `AP_Filesystem`, board storage |
| **lwip** | lightweight IP stack — used by network-capable targets (e.g. ESP32 HAL, AP_Networking on some boards) | AP_Networking/HALs |
| **gsoap** | SOAP toolkit (ONVIF camera control protocol code generation) | `AP_ONVIF` |
| **Micro-CDR**, **Micro-XRCE-DDS-Client** | eProsima micro-CDR serialization + XRCE-DDS client | `AP_DDS` |

## Trick worth knowing
- First `./waf configure` may auto-fetch `modules/waf`; running
  `git submodule update --init --recursive` fixes EVERY missing submodule
  (this is what happened in this workspace during dep setup).
- To re-run MAVLink codegen after changing XML expectations: rebuild the
  library target; the build regenerates under `build/<board>/libraries/GCS_MAVLink/include/`.
- `modules/mavlink/pymavlink` isn't what `.venv`'s `pymavlink` is — venv has
  the released pip package. They serve the same purpose (MAVLink in Python).
