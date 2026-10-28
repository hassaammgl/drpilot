# 12 — `libraries/` — All ~157 Libraries, Grouped & Explained

Naming rules: `AP_*` = shared across vehicles, `AC_*` = mostly copter/quadplane
control, `AR_*` = rover-specific, no prefix = generic utility (e.g. `PID`,
`Filter`, `RC_Channel`). Every library dir typically contains: main class
`.h/.cpp`, `*_config.h` (feature defines), `tests/`, `examples/`, sometimes
`*_Backend.*` + multiple driver children, `Parameters.cpp` for its params.

## 1. Core plumbing / utilities
| Library | What it does |
|---|---|
| `AP_Common` | base types, `AP_Param`-adjacent helpers, singleton decl |
| `AP_Math` | vectors, matrices, quaternions, coordinate math |
| `AP_Param` | persistent parameter system (flash) — the backbone |
| `AP_HAL` | hardware abstraction interface (see 02) |
| `AP_Logger` | flash/SD dataflash logging (`.bin`) |
| `AP_MultiHeap` | multiple-heap allocator (separate fast/slow RAM) |
| `AP_Filesystem`, `AP_ROMFS` | file access; embedded read-only FS in flash |
| `AP_FlashStorage`, `AP_FlashIface`, `AP_RAMTRON` | parameter storage backends |
| `AP_GPIO`, `AP_DAC`, `AP_Button`, `AP_Relay`, `AP_SerialLED` | basic I/O: GPIO, DAC outputs, buttons, relays, NeoPixel/LED |
| `AP_BoardConfig` | board options (`BRD_*` params) |
| `AP_Scheduler` | cooperative task scheduling |
| `AP_RCProtocol` | RC input protocol decoding (SBUS, CRSF, DSM, FPort…) |
| `AP_RCTelemetry`, `AP_CRSF`, `AP_Frsky_Telem`, `AP_Hott_Telem`, `AP_IBus_Telem`, `AP_LTM_Telem`, `AP_Devo_Telem` | telemetry *output* to hobby RC radios (each brand has its own lib) |
| `AP_SBusOut`, `AP_RSSI`, `AP_RCMapper` | RC output/quality mapping |
| `AP_ServoRelayEvents` | servo/relay action events (camera triggers etc.) |
| `AP_Servo_Telem`, `AP_ESC_Telem`, `AP_RobotisServo`, `AP_BLHeli`, `AP_FETtecOneWire`, `AP_KDECAN` | ESC/servo telemetry & special ESC protocols |
| `AP_RPM` | RPM sensors |
| `AP_CSVReader`, `AP_JSON`, `AP_CSV`, `AP_Networking` | parsing/networking utilities |
| `AP_RTC`, `AP_Declination`, `AP_Stats` | time, magnetic declination, usage stats |
| `AP_InternalError`, `AP_CheckFirmware`, `AP_SmartBattery`(≈AP_BattMonitor below) | health/consistency |
| `AP_DirMonitor`(see `AP_Filesystem`) | — |
| `StorageManager` | flash storage regions dispatcher |
| `SRV_Channel`, `RC_Channel`, `Filter`, `PID` | servo-channel system, RC-channel abstraction, filters, base PID |
| `GCS_MAVLink` | the MAVLink messaging system (next to AP_Logger in importance) |
| `SITL` | simulated vehicle physics glue used with AP_HAL_SITL |
| `COLCON_IGNORE`, `doc` | ROS2 workspace marker & docs |

## 2. Sensing / perception
| Library | What it does |
|---|---|
| `AP_InertialSensor` | IMU driver backend system (BMI/ICM/MPU via HAL sensor bus) |
| `AP_Baro` | barometer drivers |
| `AP_Compass` | magnetometers (backend/driver split) |
| `AP_GPS` | GNSS receivers (UBLOX, NMEA, RTK base/rover, SBP…) — one of the biggest libs |
| `AP_Airspeed` | airspeed sensors (analog/I2C/digital incl. MS4525) |
| `AP_RangeFinder` | lidars/sonars (dozens of drivers) |
| `AP_Beacon` | indoor position beacons (Pozyx, Marvelmind) |
| `AP_OpticalFlow` | downward optical flow |
| `AP.VisualOdom` (`AP_VisualOdom`) | visual odomety (Vicon/VIO) |
| `AP_ExternalAHRS` | third-party AHRS/INS integration (VectorNav, Microstrain,捆 by CAN/serial) |
| `AP_IRLock` | IR lock sensors (e.g. IR-LOCK beacon landing) |
| `AP_Proximity` | obstacle distance sensors (lidar arrays etc.) |
| `AP_ADSB` | ADSB traffic (uAvionix Ping etc.) |
| `AP_AIS` | marine AIS ship traffic |
| `AP_WheelEncoder` | rover wheel odometry |
| `AP_ICEngine`, `AP_EFI` | internal combustion engine & electronic fuel injection |
| `AP_Generator`, `AP_BattMonitor` | generators, fuel/digital batteries |
| `AP_TemperatureSensor`, `AP_TempCalibration`, `AP_LeakDetector` | temperature, calibration, leak detection |
| `AP_LightWareSerial`, `AP_GSOF` | specialized serial sensors (Lightware lidar, Septentrio logs) |
| `AP_GyroFFT` | FFT-based gyro noise analysis + notch filter |

## 3. Estimation & attitude
| Library | What it does |
|---|---|
| `AP_NavEKF3` (and `AP_NavEKF2` legacy) | the 24-state EKF fusion core |
| `AP_AHRS` | attitude/heading facade + DCM fallback |
| `AP_InertialNav` | inertial navigation from EKF |
| `AP_CustomRotations` | rotated-mount IMU frames |
| `AP_Vehicle` | abstract vehicle interface everyone can use |

## 4. Control & navigation
| Library | What it does |
|---|---|
| `AC_AttitudeControl` (incl. `_Multi`, `_Heli`, `_Sub` variants) | attitude controllers |
| `AC_PID` | PID core used by control |
| `APM_Control` | legacy plane/rover roll-pitch controller |
| `AC_WPNav`, `AR_WPNav` | waypoint navigation (copter/rover) |
| `AP_L1_Control` | plane lateral navigation |
| `AP_TECS` | plane total energy altitude/speed |
| `AP_Navigation` | common nav interface |
| `AP_CustomControl`, `AC_CustomControl` | pluggable custom controllers |
| `AC_AutoTune`, `AP_Quicktune` | automatic PID tuning |
| `AC_InputManager` | pilot-input shaping (smooth/curve) |
| `AC_Autorotation` | heli autorotation controller |
| `AC_Sprayer`, `AP_Winch`, `AP_Gripper`, `AP_Camera`, `AP_Mount` | payload actuators — sprayer, winch, grippers, cameras, gimbals |
| `AP_LandingGear`, `AP_Parachute`, `AP_Soaring`, `AP_Landing` | gear, chute, soaring flight, autolanding logic |
| `AP_SmartRTL` | path-learning RTL |
| `AP_Follow` | follow a peer MAVLink vehicle |
| `AP_Mission` | mission storage & execution engine |
| `AP_Avoidance`, `AC_Avoidance`, `AP_AdvancedFailsafe` | avoidance & AFS |
| `AP_GroundEffect`, `AP_WindVane` | ground effect, wind estimation (sailboat) |
| `AP_OLC` | glider online-contest scoring |
| `AP_Constant`(none) | — |

## 5. Comms beyond MAVLink
| Library | What it does |
|---|---|
| `AP_DDS` | ROS2/DDS bridge (uXRCE-DDS) |
| `AP_DroneCAN` | the big CAN-node stack (UAVCAN v0) |
| `AP_CANManager` | CAN port management driver registry |
| `AP_PiccoloCAN` | Piccolo autopilot CAN compatibility |
| `AP_MSP` | MSP (Betaflight-style OSD) protocol client |
| `AP_ONVIF` | IP-camera video control protocol |
| `AP_VideoTX` | VTX (video transmitter) control |
| `AP_Torqeedo` | Torqeedo electric boat motors |
| `AP_OpenDroneID` | remote-ID broadcast |
| `AP_NMEA_Output` | output NMEA sentences |

## 6. SPI/flash / misc small ones
| Library | What it does |
|---|---|
| `AP_ADC` | raw ADC access |
| `AP_AccelCal` | calibration procedure framework |
| `AP_JSButton` | joystick buttons (linux) |
| `AP_Menu` | an optional interactive CLI menu |
| `AP_ExternalControl` | abstract external-control interface |
| `AP_IOMCU` | IO coprocessor (Pixhawk classic IOMCU) |
| `AP_Scripting` | embedded Lua runtime |
| `AP_Tuning` | runtime controller-tuning UI channel |
| `AP_AdvancedFailsafe` (see earlier) | |
| `AP_SerialManager` | maps SERIALx ports to protocols |
| `AP_Notify` | LEDs/buzzers/display events |
| `AP_OSD` | character OSD overlay |

## 7. HAL backends
| Library | Platforms |
|---|---|
| `AP_HAL_ChibiOS` | STM32 (all Pixhawk-class hardware; huge: hwdef/ per board) |
| `AP_HAL_SITL` | software-in-the-loop (simulation) |
| `AP_HAL_ESP32` | ESP32 |
| `AP_HAL_Linux` | Linux SBCs (BeagleBone, Pi, Navio, BBBmini…) |
| `AP_HAL_QURT` | Qualcomm Hexagon DSP target |
| `AP_HAL_Empty` | template for new ports |

## How to explore a library quickly
1. Read `<lib>_config.h` — what features are compile-time optional.
2. Read the top of `<lib>.h` — class docstring + singleton.
3. Grep `AP_GROUPINFO` in `Parameters.cpp` — what knobs it exposes.
4. Read `tests/` for the author's own usage examples.
