# 09 — Mission Planner (`gcs/MissionPlanner`)

> Verified against the actual clone at `gcs/MissionPlanner/` (the official
> `ArduPilot/MissionPlanner` repository, shallow-cloned). Directory names and
> file lists below were checked with `ls`; the repo also carries its own
> `README.md` and `CLAUDE.md`, which this doc cross-checks.

## 1. What Mission Planner is

**Mission Planner (MP)** is the official ArduPilot ground control station: a
huge **C# / .NET Windows Forms** desktop application used to

- **connect** to ArduPilot (or PX4) vehicles over serial/USB, telemetry radios,
  TCP/UDP, or Bluetooth, using the **MAVLink** protocol,
- **set up & configure** a vehicle (radio calibration, accelerometer/compass
  calibration, flight modes, firmware flash with vehicle/board selection,
  DroneCAN setup, failsafes, OSD, …),
- **plan missions** — waypoints on a map, survey/grid patterns, geofences, rallies,
- **monitor flights** live — HUD, map, telemetry graphs, battery/vibration/EKF
  status, video/OSD overlays,
- **analyze logs** — downloaded `.bin`/`.tlog` files with a browse/graph
  interface and log-message metadata.

One codebase ships for **Windows (primary, WinForms)**, **Android (Xamarin)**
and **macOS/iOS (experimental)**, and it *runs* on Linux under **Mono**. The
same source tree builds both the full desktop app (`MissionPlanner.csproj`,
`net472` executable) and a cross-platform library build
(`MissionPlannerLib.csproj`, `netstandard2.0`, compiled with a `LIB` define).

## 2. Architecture in one diagram

Mission Planner is a classic WinForms shell wrapped around a layered
MAVLink stack (the dependency flow is **transport → protocol → vehicle state → UI**):

```
┌───────────────────────────────────────────────────────┐
│ WinForms UI: MainV2 (main form, menu, toolbar)        │
│   screens: FlightData | FlightPlanner | InitialSetup  │
│            Configuration | Help | SITL                │
├───────────────────────────────────────────────────────┤
│ Vehicle state layer: MAVState / MAVList / CurrentState│
│ (telemetry model `cs` that the UI binds to)           │
├───────────────────────────────────────────────────────┤
│ Link layer: MAVLinkInterface — packet read/write,     │
│ param get/set, mission up/download, MAVFTP, commands  │
├───────────────────────────────────────────────────────┤
│ Protocol: MAVLink message structs, MavlinkParse, CRC  │
│ (ExtLibs/Mavlink, machine-generated from XML)         │
├───────────────────────────────────────────────────────┤
│ Transport: ICommsSerial — serial, TCP, UDP, BTLE,     │
│ NTRIP, WebSocket, WinUSB, file, pipes (ExtLibs/Comms) │
└───────────────────────────────────────────────────────┘
```

Facts verified in source:

- `Program.cs` is the process entry point (`StartupObject=MissionPlanner.Program`
  in the csproj) and installs global crash/exception handling.
- `MainV2.cs` (~194 KB) is the main `Form` and the central hub. It owns the
  active link as `MainV2.comPort` (a `MAVLinkInterface`, line ~417) plus a
  `List<MAVLinkInterface> Comports` for multiple links, hosts the menu, and
  swaps the `GCSViews` screens in and out of the window. Navigate by symbol,
  not top-to-bottom.
- `ExtLibs/ArduPilot/Mavlink/MAVLinkInterface.cs` implements the link logic;
  each connected vehicle is a `MAVState` whose `cs` (`CurrentState`,
  `ExtLibs/ArduPilot/CurrentState.cs`) is the decoded telemetry model.

## 3. Top-level layout of `gcs/MissionPlanner/`

### 3.1 Root `.cs` / solution files

| Item | Role |
|---|---|
| `MissionPlanner.sln` | The full solution — ~93 projects (verified in the sln: main app, MAVLink, Comms, GMap.NET, ClixAudio plugins, SikRadio, Updater, wix installer, …) |
| `MissionPlanner.csproj` | The main app (`net472`, `Exe`, WinForms, `AnyCPU`). Output deliberately written to `bin\Release\net461\` (`AppendTargetFrameworkToOutputPath=false`). Version field currently 1.3.83 |
| `MissionPlannerLib.csproj` | Cross-platform **library** build of the same sources for Android/Mac (`netstandard2.0`, `LIB` define) |
| `MissionPlannerLib.sln` | Solution for the Lib/shared build |
| `Program.cs` | Entry point: logging (log4net), splash, command-line args, global exception handlers, update check |
| `MainV2.cs` (+ `.Designer.cs`, many translated `.resx`) | The main window / application hub |
| `Splash.cs` | Startup splash screen |
| `Common.cs` | Shared cross-cutting helpers (theme/common UI wiring used by many screens) |
| `Script.cs` | **IronPython scripting host** (see §6.4) |
| `MagCalib.cs` | Compass/Magnetometer calibration wizard |
| `NativeMethods.cs`, `ZZZLibShims.cs` | P/Invoke declarations and cross-platform shims for the `LIB` build |
| `L10N.cs` / `ResEdit.cs` | Localization support: strings go via resource files; translations managed through Crowdin |
| `ParameterFactMetaData.xml`, `ParameterMetaDataBackup.xml` | On-disk parameter metadata (names, units, ranges, values) — parsed by `ExtLibs/Utilities/ParameterMetaDataParser.cs` and the `ParameterMetaDataRepository*.cs` classes; used to render every parameter screen |
| `mavcmd.xml`, `dataflashlog.xml`, `aircraft.xml`, `acsimplepids.xml`, `camerasBuiltin.xml`, `checklistDefault.xml`, `APMotorLayout.json`, `SerialOptionRules.json` | Declarative data describing MAVLink commands, DataFlash log fields, aircraft classes, camera definitions, motor layouts, connection serial rules |
| `app.config`, `appxmanifest.xml`, `nuget.config`, `mykey.snk` | App config (also where you can disable MP's own update check), MS Store packaging manifest, NuGet feeds, strong-name key |
| `build.bat`, `build - Clean.bat`, `build - debug.bat`, `build - Lib.ps1`, `createproj.bat`, `crowdin.bat`, `beta.bat` | Build/packaging scripts (see §5) |
| `MissionPlanner.sh` | Tiny Unix launcher |
| `vs2019.vsconfig`, `vs2022.vsconfig`, `vs2026.vsconfig` | Visual Studio workload/component import files |
| `mpdesktop.ico`, `.mpsystheme` files, `hud.html` | Icon, UI themes (driven by `Utilities/ThemeManager.cs`), and an HTML HUD |
| `README.md`, `CLAUDE.md`, `ChangeLog.txt`, `COPYING.txt`, `PRIVACY.md`, `FirmwareHistory.txt` | Docs, changelog, GPL license, privacy note (external-services table), firmware release notes |

### 3.2 Directories (verified with `ls`)

| Directory | Role |
|---|---|
| `Controls/` | Reusable WinForms controls: `ConnectionControl`/`ConnectionOptions`/`ConnectionStats` (the connect toolbar), `PrearmStatus`, `EKFStatus`, `Vibration`, `MAVLinkInspector`, `MavlinkCheckBox/ComboBox/NumericUpDown/BitMask` (parameter widgets that bind to param metadata), DroneCAN inspector/params/ftp UI, `ScriptConsole`, `Video`/`OSDVideo`/`VideoStreamSelector`, serial-output bridges (NMEA, CoT, pass-through, MovingBase), gimbal controls, `SpectrogramUI`, `fftui`, themes |
| `GCSViews/` | The top-level **screens**: `FlightData.cs`, `FlightPlanner.cs`, `InitialSetup.cs`, `Help.cs`, `SITL.cs`, `SoftwareConfig.cs` and the `ConfigurationView/` tree (see §3.3) |
| `ExtLibs/` | **~90 sub-projects** — the real functional core (see §3.4) |
| `MAVLink protocol` | Lives in `ExtLibs/Mavlink/` (project `MAVLink.csproj`), *not* a root-level `MAVLink/` folder |
| `ExtLibs/ArduPilot/` | ArduPilot domain model: `MAVLinkInterface.cs`, `MAVState.cs`, `MAVList.cs`, `CurrentState.cs`, firmware objects (`APFirmware`, `Firmwares`, `FirmwareFilter`), fences, `HW/` board files, `Camera.cs`, `DeviceInfo.cs` |
| `ExtLibs/Comms/` | All transports implementing `ICommsSerial`: `CommsSerialPort`, `CommsTCPSerial`, `CommsUdpSerial`(+`Connect`), `CommsBLE`, `CommsNTRIP`, `CommsWebSocket`, `CommsWinUSB`, `CommsFile`, `UDPStream`, with a `CircularBuffer` |
| `ExtLibs/Mavlink/` | Generated MAVLink structs (`MavlinkParse.cs`, `MAVLinkMessage.cs`, `MAVLinkParam.cs`, `MavlinkCRC.cs`), `message_definitions/` XML, and a vendored `pymavlink` copy |
| `Drivers/` | Windows USB driver INFs/CATs/installers (Cube, ChibiOS STM32 bootloader, Holybro, PX4, ublox, mRo, VRBrain, …) bundled for install |
| `Log/` | Log screens: `LogBrowse` (view .bin), `LogDownload`/`LogDownloadMavLink`/`MavLinkLog` (tlog download/management), metadata |
| `LogAnalyzer/` | Log analysis helpers (also a console plug at repo root) |
| `Utilities/` | App-level services: `Firmware.cs`, `Update.cs`, `Speech.cs`, `ThemeManager.cs`, `httpserver.cs`, `POI.cs`, `ImageMatch.cs`, `SSHTerminal.cs`, `BoardDetect.cs`, `CircleSurveyMission.cs`, `AirMarket.cs` |
| `Grid/` | Survey-grid engine: `GridPlugin.Column`, `GridUI`, `GridData`, camera footprints (`camerainfo.cs`) |
| `Plugin/` | Plugin infrastructure: `Plugin`, `PluginLoader`, `PluginUI` |
| `plugins/` and `Plugins/` | Built-in plugins and many `exampleNN-*.cs` templates (`plugins/` holds older ones, `Plugins/` newer ones incl. OpenDroneID2, TerrainMaker) — note both spellings exist |
| `Scripts/` | Sample IronPython scripts shipped with MP (see §6.4) |
| `Antenna/` | AntennaTracker support UI (`TrackerUI.cs`) |
| `APMPlannerXplanes/` | Old X-Plane HIL integration assets (excluded from the csproj `Compile`) |
| `SikRadio/` | Standalone configuration tool for 3DR/Sik/RFD900 telemetry radios (own `MainV2.cs`, `RFD900.cs` — its own csproj in the sln) |
| `Radio/`, `SikRadio/` | Radio setup UIs |
| `GeoRef/`, `NoFly/`, `MAC/`, `Msi/`, `wix/` | Georeferencing imagery UI, no-fly-zone KMZ data + `NoFly.cs`, macOS packaging, MSI/WiX installers |
| `Joystick/` | Joystick/action UIs (`Joy_Do_Set_Relay`, mode change, mount…) |
| `graphs/` | XML graph definitions for the telemetry graph (`mavgraphs.xml`, EKF graphs) |
| `m3u/` | Playlist files used to route video streams to HUD/map windows |
| `Updater/` | Small self-update executable project |
| `MissionPlannerTests/` | MSTest unit-test project (net472; board detect, firmware parsing etc. — not run in CI pipelines) |
| `Properties/`, `Resources/`, `resedit*` | Assembly properties, embedded resources/resources editor |
| `.github/workflows/` | CI: `main.yml` (Windows build), `android.yml`, `mac.yml`, `linux.yml` |
| `Linux/` | Linux packaging & build scripts (see §5.3) |

Other root items: `airports.csv`, `adb.exe`/`AdbWinApi.dll` (Android device
support via SharpAdbClient), `Lib.zip` (IronPython standard library for scripts),
and `temp.cs` (scratch code).

### 3.3 `GCSViews/ConfigurationView/` — the config screens

~56 `Config*.cs` panels, each one a setup wizard section:
`ConfigFirmware` (flash firmware), `ConfigRadioInput/Output` (RC calibration),
`ConfigAccelerometerCalibration`, `ConfigHWCompass(+2)`, `ConfigHWCAN`,
`ConfigDroneCAN`, `ConfigFlightModes`, `ConfigFailsafe`, `ConfigOSD`,
`ConfigSerial`, `ConfigPlanner(+Adv)`, `ConfigBatteryMonitoring(+2)`,
`ConfigMotorTest`, `ConfigMount` (gimbal), `ConfigESCCalibration`,
`ConfigFriendlyParams(+Adv)` (human-readable parameter views), `ConfigRawParams`,
`ConfigTerminal`, `ConfigREPL`, `ConfigArducopter/Arduplane/Ardurover/AntennaTracker`
(vehicle-specific pages), `ConfigAteryx/sSensors`, `ConfigGPSOrder`, and more.

### 3.4 Selected `ExtLibs/` sub-projects

| Path | Role |
|---|---|
| `ExtLibs/Core/`, `ExtLibs/Interfaces/` | Shared primitives, `ICommsSerial` contract, a `ServiceLocator` (lightweight DI, `ExtLibs/Interfaces/ServiceLocator.cs`) |
| `ExtLibs/GMap.NET.Core` / `.Drawing` / `.WindowsForms` | The map engine (Google/Bing/OSM providers, tile cache) |
| `ExtLibs/Maps/` | MP's own map/POI extras |
| `ExtLibs/GDAL`, `ExtLibs/ProjNet`, `ExtLibs/SharpKml`, `KMLib` | Projections, KML/KMZ |
| `ExtLibs/DroneCAN/`, `UAVCANFlasher/`, `NMEA2000` | CAN bus tooling |
| `ExtLibs/px4uploader/`, `NetDFULib/`, `Flasher/`, `Arduino/` | Firmware uploaders (PX4 bootloader, DFU, Arduino/AVR flashing) |
| `ExtLibs/GStreamerHud/`, `LibVLC.NET/`, `WebCamService/`, `Onvif/`, `AviFile/` | Video pipeline & recording |
| `ExtLibs/ZedGraph/`, `Exocortex.DSP`, `MissionPlanner.Stats` | Graphing/FFT/statistics |
| `ExtLibs/Xamarin/`, `Xamarin.Forms.Platform.WinForms`, `UsbSerialForAndroid`, `SharpAdbClient`, `solo/` | Android/Xamarin support |
| `ExtLibs/HIL/`, `ExtGuided/`, `ExtLibs/solo/` | Hardware-in-the-loop, guided-mode helpers, 3DR Solo |
| `ExtLibs/mono/` | Mono-specific glue (a git submodule in some setups) |
| `ExtLibs/wasm/`, `WebAPIs/` | Experimental web/WASM front ends |
| Vendored libs | `alglibnet`, `AStar`, `BSE.Windows.Forms` (skin), `ObjectListView`, `Transitions`, `Zeroconf`, `Ntrip`, `System.Data.SQLite`… |

## 4. How it talks to vehicles

### 4.1 Connect flow

1. The connect toolbar (`Controls/ConnectionControl.cs`) lists ports/bauds;
   `MainV2.doConnect(comPort, portname, baud, ...)` (line ~1456 in `MainV2.cs`)
   creates/configures the link.
2. `ExtLibs/Comms/` supplies the transport: hardware serial/USB
   (`CommsSerialPort`), **TCP**, **UDP** (both client and connect/listen
   variants), **Bluetooth LE**, WinUSB, WebSocket, NTRIP — all behind the
   `ICommsSerial` stream interface. UDP autodetect and network discovery
   (`ExtLibs/Zeroconf`) help find vehicles on WiFi.
3. `MAVLinkInterface` (`ExtLibs/ArduPilot/Mavlink/`) wires the stream to the
   protocol: parses RX bytes into `MAVLinkMessage`s (via `MavlinkParse`,
   validating per-message `MAVLink CRC` checksums and the v2 frame header in
   `MavlinkHeader`), and serializes TX messages.
4. Each detected vehicle (sysid/compid) becomes a `MAVState` appended to a
   `MAVList`; MP supports **multiple simultaneous links** (`MainV2.Comports`).
   A `CurrentState.cs` object (`cs`) accumulates the decoded telemetry that
   every UI element binds to (attitude, position, voltages, `mode`, `armed`…).
5. On connect MP requests streams, dismisses/handles heartbeats, checks the
   EKF/health state (`PrearmStatus`, `ControlSensorsStatus` controls), and
   downloads **all parameters** (MAVLink `PARAM_REQUEST_LIST` /
   `PARAM_VALUE`) once, cached into `MAVLinkParamList`.

### 4.2 Parameter upload / editing

Parameter screens (`ConfigFriendlyParams`, `ConfigRawParams`, the
`Mavlink*` bound widgets) use `ParameterMetaDataParser.cs` +
`ParameterMetaDataRepository*.cs` over `ParameterMetaDataBackup.xml` (4+ MB,
covers every vehicle's parameters) to show units, ranges and value labels.
Writes go out as `PARAM_SET` and are confirmed by `PARAM_VALUE` acks.
DroneCAN parameters are handled separately (`Controls/DroneCANParams.cs`)
via the DroneCAN protocol.

### 4.3 Mission planning & upload

- `GCSViews/FlightPlanner.cs` is the waypoint editor on the map grid; missions
  are modeled and exchanged with the vehicle as `MISSION_*` MAVLink messages
  (`ExtLibs/ArduPilot/Mavlink/mav_mission.cs`).
- Survey/grid missions come from `Grid/GridUI.cs` + `GridData.cs`
  (camera footprints, spacing, overlap); `Utilities/CircleSurveyMission.cs`
  adds circle survey; GeoFence and Rally points use the `Fence*.cs` classes.
- Waypoint commands and their parameters are described by `mavcmd.xml`.
- Log upload/download uses **MAVFTP** (`ExtLibs/ArduPilot/Mavlink/MAVFtp.cs`,
  `Controls/MavFTPUI.cs`) for modern firmware.

### 4.4 Commands & failsafe interactions

Guided-mode actions, `MAV_CMD` sending (`doCommand`/`command_long`), RC
override, mode changes, EKF/preflight dialogs, speech announcements
(`Utilities/Speech.cs`) — all flow through the same `MAVLinkInterface`.

## 5. Building it

### 5.1 Windows (the supported path)

Per the repo's own docs: **Visual Studio 2022 + MSBuild only.**

First, once: `git submodule update --init`. Then:

```bat
.nuget\nuget.exe restore MissionPlanner.sln
MSBuild.exe MissionPlanner.sln /restore /m /p:Configuration=Release
```

or simply open `MissionPlanner.sln` in Visual Studio and hit Build.

`build.bat` does exactly this (restore → MSBuild Release), then packages a
Windows `.appx` (makeappx + signtool) and rsyncs it to an ArduPilot server —
those last steps are maintainer-only. Variants: `build - debug.bat`, 
`build - Clean.bat`, `build - Lib.ps1` (Android/lib packaging).
`createproj.bat` regenerates the `<Compile>` item lists inside the csproj
by scanning the tree. `vs2022.vsconfig` imports the exact VS component set.

Output lands in `bin\Release\net461\` — the *folder name* `net461` is legacy;
`AppendTargetFrameworkToOutputPath=false` means the actual TFM is `net472`
(`.NET Framework 4.7.2`).

### 5.2 Target frameworks

| Project | TFM | Kind |
|---|---|---|
| `MissionPlanner.csproj` | `net472` (folder says net461) | WinForms Exe |
| `MissionPlannerLib.csproj` | `netstandard2.0` | Cross-platform library for Android/Mac (`#if LIB` code paths) |
| Support projects (`ExtLibs/*`) | mixed netstandard/netframework | MAVLink, Comms, Controls, Utilities, GMap.NET, … |
| `MissionPlannerTests/` | `net472`, MSTest | Unit tests |

### 5.3 Linux

**MSBuild is not available on Linux**; there is no supported *source* build on
Linux/macOS per `CLAUDE.md` — Linux *runs* prebuilt binaries under **Mono**:

- Runtime install: per `Linux/README.md`, download the
  `MissionPlanner-linux-x86_64.tar.gz` release, install Mono 6.8+ WinForms
  runtime deps + `libgdiplus` + fonts (exact `apt` line provided there, e.g.
  `mono-runtime libgdiplus libmono-system-windows-forms4.0-cil …`), then
  `./run.sh`. No SDK needed.
- Building from source on Linux: works via **.NET 10 SDK + mono-devel + rsync**
  using `Linux/build.sh` (the script handles the cross-compilation of the
  desktop targets into a Mono-runnable bundle) and `Linux/run.sh`; there is
  also a `SmokeTest.cs` and `test-package.sh`.
- Caveats: WinForms via Mono means not all features work (video/OSD, GDAL,
  Windows drivers are Windows-only); serial needs `dialout` membership.
- iOS/Android builds use `android.yml` / `mac.yml` CI, `build - Lib.ps1` and
  `ExtLibs/Xamarin`.

## 6. Relation to the ArduPilot firmware (the parent repo)

In this workspace, `gcs/MissionPlanner` sits inside the ArduPilot firmware
clone (`drpilot/`), but it is an **independent repository** (its own git
history, upstream `ArduPilot/MissionPlanner`) cloned alongside the firmware —
the parent only provides the context.

In operation they form a strict client/server pair over MAVLink:

| Concern | Firmware (parent repo) | Mission Planner |
|---|---|---|
| MAVLink dialect XML | `modules/mavlink/message_definitions/v1.0/*.xml` | `ExtLibs/Mavlink/message_definitions/` + vendored `pymavlink` — the C# structs are **code-generated from the same XML** |
| MAVLink impl | `libraries/GCS_MAVLink/` | `ExtLibs/ArduPilot/Mavlink/MAVLinkInterface.cs` + protocol in `ExtLibs/Mavlink/` |
| Parameters | `libraries/AP_Param/`, per-vehicle defaults | Reads/writes via `PARAM_*` messages; UI metadata from `ParameterMetaDataBackup.xml` |
| Missions/fences | `libraries/AP_Mission/`, `AP_Fence`, `AP_Rally` | `FlightPlanner`, `Grid/`, `Fence*.cs`, `mav_mission.cs` |
| Logs | `libraries/AP_Logger` (.bin DataFlash) | `Log/` screens + `dataflashlog.xml` field metadata + `LogAnalyzer/` |
| Firmware images | Built & published by ArduPilot CI | **Downloads** them and flashes: `Utilities/Firmware.cs`, `Controls/FirmwareSelectionForm.cs`, `ExtLibs/Flasher/`, `px4uploader` |
| SITL | This repo's SITL binaries | `GCSViews/SITL.cs` can launch them (also `Scripts/example9 - sitl.py`) |

Offline-support asymmetry: MP caches SRTM terrain, map tiles, parameter
metadata (`*.pdef.xml`) and DataFlash log-message XML under
`C:\ProgramData\Mission Planner\` (Windows) or
`~/.local/share/Mission Planner/` (Linux) so it works without internet.

## 7. Screens, plugins, scripting, OEM customization

### 7.1 Flight Data vs Flight Plan

| Screen (`GCSViews/`) | Purpose |
|---|---|
| **FlightData** (`FlightData.cs`) | *In-flight* dashboard: artificial horizon **HUD**, live map (`GMap.NET`), roll/pitch/yaw readouts, battery/status panels, video-and-OSD overlay, quick actions (arm/disarm, guided, modes), tabbed telemetry graph (XML scripts in `graphs/`) |
| **FlightPlanner** (`FlightPlanner.cs`) | *Pre-flight* mission editor: waypoint list + map side by side, insert/move/reorder WPs, grid/survey generation, geofence & rally editing, read/write mission from vehicle or file, undo/redo, terrain preview |

Both are ordinary `UserControl`s swapped into `MainV2`'s window by the menu —
not separate windows. Other screens: **Initial Setup** (firmware, calibration,
frame setup), **Config/Tuning** (`ConfigurationView` panels), **Help**, **SITL**.

### 7.2 Themes & customization

- Theming: `Utilities/ThemeManager.cs` + `*.mpsystheme` files
  (`BurntKermit.mpsystheme`, `HighContrast.mpsystheme` at root);
  `Controls/ThemeEditor.cs` lets users edit them.
- The branding/logos (`Program.cs`'s `Logo`/`Logo2`) and shell layout are plain
  C# — there is no formal "OEM" config layer in this OSS tree; custom-build
  vendors fork the source, change branding/defaults, and (in practice) add a
  private plugin — see next.

### 7.3 Plugins

Two plugin spellings exist and are both real:

- `Plugin/Plugin.cs` + `PluginLoader.cs` — the runtime loader (scans a
  `plugins/` folder next to the exe for `.cs`/DLLs, instantiates `Plugin`
  subclasses, injecting `PluginUI` windows, loop hooks, etc.).
- `Plugins/` and `plugins/` at repo root — templates & built-ins:
  forwarding/telemetry relay, Herelink, HUD on/off, map icon descriptors,
  CAN RTCM injection, font sizing, menu removal, persistent state,
  external API exposure, tethered mass/LED examples, OpenDroneID2,
  TerrainMaker, Dowding, FaceMap, Shortcuts, generator.

### 7.4 Python scripting inside MP

- Host: `Script.cs` embeds **IronPython** (`Lib.zip` supplies stdlib).
  Exposed globals include `MainV2`, `Flight_planner`/`FlightData` singletons,
  `Ports`, `MAV` (the active link), `cs` (telemetry), `Joystick`, `mavutil`.
- User entry points: `Controls/ScriptConsole.cs` and the Python tab on the
  Flight Data screen; auto-run of `Scripts/StartUp.py`-style scripts at boot.
- Shipped examples in `Scripts/`: `example1.py` … `example10.py`,
  `TAKEOFF.py`, `rc - heli.py`, `PARACHUTE LANDING APPROACH.py`,
  `wipe.py`, `ui.py`, `cubeorange.py` — matching helper modules
  `mavextra.py`, `mavutil.py`, `rotmat.py`, `quaternion.py` at repo root.
  This is MP's classic (older) scripting path, distinct from the firmware-side
  `AP_Scripting` in the parent repo.

## 8. Quick file-finding cheat sheet

| I want to touch… | Look in… |
|---|---|
| App startup / crash handling / update check | `Program.cs`, `Utilities/Update.cs` |
| Menu, connection lifecycle, global state | `MainV2.cs` (search by symbol: `doConnect`, `comPort`) |
| A specific screen | `GCSViews/FlightData.cs`, `GCSViews/FlightPlanner.cs`, `GCSViews/ConfigurationView/Config*.cs` |
| Serial/UDP/TCP transport | `ExtLibs/Comms/` |
| MAVLink packet parse/write | `ExtLibs/Mavlink/MavlinkParse.cs`, `Mavlink` struct generation |
| Link behavior (params, missions, FTP) | `ExtLibs/ArduPilot/Mavlink/MAVLinkInterface.cs`, `MAVFtp.cs` |
| Telemetry values shown in UI | `ExtLibs/ArduPilot/CurrentState.cs` |
| Parameter metadata parsing | `ExtLibs/Utilities/ParameterMetaDataParser.cs` + `ParameterMetaDataRepository*.cs` |
| Firmware flash/download | `Utilities/Firmware.cs`, `Controls/FirmwareSelectionForm.cs`, `ExtLibs/Flasher/`, `ExtLibs/px4uploader/` |
| Survey/grid missions | `Grid/GridUI.cs`, `Grid/GridData.cs`, `Utilities/CircleSurveyMission.cs` |
| Map | `ExtLibs/GMap.NET.*`, `ExtLibs/Maps/` |
| Video / OSD | `Controls/Video.cs`, `Controls/OSDVideo.cs`, `ExtLibs/GStreamerHud/` |
| Log browse/download/analysis | `Log/*.cs`, `LogAnalyzer/`, `dataflashlog.xml` |
| Plugin system | `Plugin/PluginLoader.cs`, `plugins/`, `Plugins/` |
| Python scripting | `Script.cs`, `Controls/ScriptConsole.cs`, `Scripts/` |
| Build scripts (Windows) | `build.bat`, `createproj.bat` |
| Linux packaging | `Linux/build.sh`, `Linux/run.sh`, `Linux/README.md` |
