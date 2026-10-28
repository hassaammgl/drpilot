# 13 — `Tools/` — Every Subdirectory Explained

`Tools/` is where everything *not part of the flying firmware* lives.
2041 files — the biggest folder after `libraries/`.

## Firmware-adjacent tooling (build these like vehicles)
| Dir | What it is |
|---|---|
| `AP_Bootloader/` | bootloader firmware for every board; built from hwdefs |
| `AP_Periph/` | standalone CAN-peripheral firmware — turns an extra MCU into a node with GPS/compass/airspeed/ rangefinder etc. over DroneCAN |
| `IO_Firmware/` | firmware of the separate IOMCU coprocessor (classic Pixhawk) |
| `bootloaders/` | pre-built bootloader binaries per board |
| `cameras_gimbals/` | firmware presets/configs for AM32/style camera-gimbal nodes |

## Build system & CI
| Dir | What it is |
|---|---|
| `ardupilotwaf/` | the waf extension modules (board builds, hwdef processing, mavlink gen…) — waf's "plugins" |
| `scripts/` | CI helper scripts: `build_options.py` (every `AP_*_ENABLED` switch), `allowed_subsystems.py` (commit rules), astyle helpers, size-reporting |
| `CodeStyle/` | `astylerc` — the C++ formatting config |
| `environment_install/` | per-OS dependency installers (arch/ubuntu/mac/windows) |
| `gittools/` | git helpers (`git-subsystems-split`, make-better-commits) |
| `GIT_Test` | scratch for testing git tooling |

## Testing / simulation
| Dir | What it is |
|---|---|
| `autotest/` | **the** SITL integration-test framework: `autotest.py` runner, `arducopter.py`/`arduplane.py`/… per-vehicle test suites, `pysim/` simulated sensor streams, `models/` physical vehicle models (JSON dynamics), HIL simulations |
| `Replay/` | deterministic replays of logged data to reproduce real-flight attitudes offline |
| `renode/` | Renode full-system emulation peripherals (the C# files in this repo live here) |
| `simulink/` | Simulink model export/integration |
| `Vicon/` | motion-capture integration |
| `FilterTestTool` | standalone filter testing harness |
| `CPUInfo` | board CPU info collection |

## Autotest support bits
| Dir | What it is |
|---|---|
| `mavproxy_modules/` | extra MAVProxy plugins used by autotest (ARSPD, AP MotoTest, terrain, Welder…) — autotest loads these at runtime |
| `Frame_params/` | per-frame parameter sets loaded during autotest |
| `UDP_Proxy` | simple MAVLink UDP forwarder |
| `Hello` | sample empty target (hello world per board) |

## Peripherals & misc hardware
| Dir | What it is |
|---|---|
| `Pozyx` | Pozyx positioning integration scripts |
| `CHDK-Scripts` | CHDK camera scripting |
| `geotag` | picture geo-tagging tool |
| `Linux_HAL_Essentials` | user utilities needed for the Linux HAL (GPIO init, helpers) |
| `debug` | debug helper scripts (gdb, valgrind, ASAN launchers) |
| `completion` | bash/zsh completion for tools |
| `terrain-tools` | map/terrain SRTM helpers |
| `PrintVersion.py` | version string extraction |

## Other
| Dir | What it is |
|---|---|
| `ros2/` | ROS2 glue (black-boxed, uses `AP_DDS`) |
| `vagrant/` | dev-environment VM definitions |

## Which of these you'll actually touch
- **`autotest/`** when running/flights tests (`Python autotest.py copter`… see docs 16/18).
- **`ardupilotwaf/` + `scripts/build_options.py`** when adding a feature flag.
- **`AP_Periph/`** if you need extra CAN sensors.
- **`CodeStyle/`** before every PR (`Tools/CodeStyle/astyle` runs repo-wide? no — astyle only on your changed files).
