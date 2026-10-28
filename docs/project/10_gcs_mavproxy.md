# MAVProxy — Python Ground Control Station

*Source of truth for this document: `gcs/MAVProxy` in this repository (a checkout of
[ArduPilot/MAVProxy](https://github.com/ArduPilot/MAVProxy), version **1.8.75** per `setup.py`,
GPLv3, lead developers Andrew Tridgell and Peter Barker).*

## 1. What MAVProxy is

MAVProxy is a **MAVLink proxy and ground station written in Python**, built around
[pymavlink](https://github.com/ArduPilot/pymavlink). Per its own `setup.py` long
description: *"A MAVLink protocol proxy and ground station. MAVProxy is oriented
towards command line operation, and is suitable for embedding in small autonomous
vehicles or for using on ground control stations."*

Key characteristics:

- **Console / network oriented** — a terminal program with a shell-style command line
  (`arm`, `wp list`, `param fetch …`); GUIs (map, console, graphs) are optional plugins.
- **Proxy by design** — it forwards received MAVLink traffic to any number of
  `--out` links, acting as the Python predecessor of the C++ `mavlink-router`.
- **Extremely modular** — every feature above the raw link lives in a runtime-loadable
  module; multi-link and multi-vehicle capable (HEARTBEAT-driven detection, sysid routing).
- Developed by the CanberraUAV team for the 2012 Outback Challenge; still the GCS used
  by the ArduPilot autotest system.

Repository layout (top level):

```
gcs/MAVProxy/
├── MAVProxy/           # the Python package
│   ├── mavproxy.py     # main entry point / scheduler
│   ├── modules/        # all loadable modules (mavproxy_*.py) + lib/ helpers
│   └── tools/          # MAVExplorer log analysis, mavflightview, mavvidplay…
├── tests/              # pytest tests (GUI, camera, ftp, map…)
├── docs/, scripts/, windows/   # JOYSTICKS.md, flake8 script, PyInstaller build
├── MAVProxyWinUSB.bat / MAVProxyWinLAN.bat   # Windows launchers
├── requirements.txt    # minimal runtime deps (pymavlink, pyserial, numpy)
└── setup.py            # packaging, version 1.8.75
```

## 2. Package structure

### 2.1 Entry point: `MAVProxy/mavproxy.py` (~2100 lines)

Single-file (~2100 lines) main program containing:

- **`MPStatus`** — vehicle/link status (GPS, armed state, flightmode, message and byte
  counters, `msgs{}` cache of the last packet of each type, heartbeat bookkeeping).
- **`load_module()` / `unload_module()`** — the plugin loader (see §3).
- **`process_stdin()`** — the command interpreter: shlex splitting, alias expansion,
  dispatch into the `mpstate.command_map` populated by `add_command()`, plus the
  built-ins (`help`, `set`, `status`, `watch`, `module`, `alias`…). In `--setup` mode
  raw lines are written straight to the master (legacy autopilot CLI).
- **`main_loop()`** — the `select()` event loop over every master/out fd; processes
  input lines (`;`-separated commands supported), runs `periodic_tasks()` (heartbeats,
  stream rates, module `idle_task()` calls), and inhibits the screensaver while armed.
- **Startup scripts**: `~/.mavinit.scr`, per-aircraft `mavinit.scr` and `--cmd`
  strings run at boot unless `--no-startup-scripts`.

### 2.2 Base class: `MAVProxy/modules/lib/mp_module.py`

Every module subclasses `MPModule`, constructed as
`__init__(self, mpstate, name, description=None, public=False, multi_instance=False,
multi_vehicle=False)`. Overrides that a module can/should provide:

| Hook | Purpose |
|---|---|
| `mavlink_packet(packet)` | called for every MAVLink packet routed to the module |
| `idle_task()` | called periodically from the main loop (GUI polling, retries) |
| `unknown_command(args)` | return True if the module handled an unknown command |
| `unload()` | cleanup on `module unload` |

Helper properties (`status`, `settings`, `mav_param`, `master`, `target_system`,
`vehicle_type`, `sitl_output`, `console`…) are provided by the base class.
Construction flags: `public=True` makes the instance findable via
`self.module('name')`; `multi_instance=True` allows repeated loads (names become
`map2`, `map3`, …); `multi_vehicle=True` opts into packets from *other* sysids
(beyond the primary vehicle). Modules also register commands with
`add_command()` and tab-completion hinters with `add_completion_function()`.

### 2.3 The modules (`MAVProxy/modules/mavproxy_*.py`)

Verified by `ls MAVProxy/modules` — ~98 module files (names below are the real
ones; historical names such as `MyGridUI`, `ystick`/`mavproxy_joystick.py`,
`realtime_logging` or `sigpearms` do **not** exist in this tree — joystick is the
package `mavproxy_joystick/`, and console/map are as listed):

| Module(s) | Role (from code/docstrings) |
|---|---|
| `mavproxy_link.py` | **run-time add/remove of master links** (`link add/list/ports/remove`), vehicle detection, broadcast to `--out` links, `mavfwd`/`mavfwd_rate` forwarding settings, `ping`, `alllinks`; the heart of the router behaviour |
| `mavproxy_output.py` | **run-time UDP output clients**, the runtime `--out` equivalent (`output add/list/remove/sysid/discardcompid`) |
| `mavproxy_console.py`, `mavproxy_map/` (pkg), `mavproxy_map3d/`, `mavproxy_mmap/`, `mavproxy_cesium/` | GUIs: wxWidgets status console; slipmap satellite map (vehicle position, waypoints, fences, mission editing, SRTM elevation); newer VTK 3D terrain map; alternative map app; browser-based Cesium globe |
| `mavproxy_arm.py`, `mavproxy_mode.py`, `mavproxy_cmdlong.py`, `mavproxy_calibration.py` | vehicle commands: `arm`/`disarm`; flight modes (`mode loiter…`); long commands (`guided/takeoff/land/position/goto…`); accelerometer/compass calibration |
| `mavproxy_wp.py`, `mavproxy_fence.py`, `mavproxy_rally.py`, `mavproxy_misseditor/` (pkg), `mavproxy_kmlgen.py`, `mavproxy_kmlread.py` | mission handling — waypoints, geofence, rally all built on the shared `lib/mission_item_protocol.py` base; `wp load/save/list/set/remove/loop`; GUI mission editor; KML generation / map layers |
| `mavproxy_param.py`, `mavproxy_paramedit/` (pkg), `mavproxy_ftp.py`, `mavproxy_log.py`, `mavproxy_dataflash_logger.py` | parameter get/set/fetch (`param fetch *`), GUI editor, MAVLink FTP, log download/erase, tlog logging |
| `mavproxy_rc.py`, `mavproxy_rcsetup.py`, `mavproxy_joystick/` (pkg), `mavproxy_battery.py`, `mavproxy_relay.py`, `mavproxy_sensors.py`, `mavproxy_warning.py` | RC override/capture (end-point calibration); "flexible joystick driver" with YAML definitions in `joysticks/*.yml` (pygame); battery status; relay/servo control; sensor monitoring & failure announcements |
| `mavproxy_GPSInject.py`, `mavproxy_GPSInput.py`, `mavproxy_fakegps.py`, `mavproxy_nmeagps.py`, `mavproxy_nmeaout.py`, `mavproxy_DGPS.py`, `mavproxy_ublox/` (pkg), `mavproxy_ucenter.py` | GPS injection (incl. fake GPS via GPS_INPUT), NMEA in/out, DGPS, u-blox configuration |
| `mavproxy_nsh.py`, `mavproxy_serial.py`, `mavproxy_ntrip.py`, `mavproxy_signing.py`, `mavproxy_timesync.py`, `mavproxy_system_time.py`, `mavproxy_message.py`, `mavproxy_messagerate.py`, `mavproxy_msg.py` | NuttX remote shell; SERIAL_CONTROL handling; NTRIP→RTCM injection (RTK); MAVLink2 signing; TIMESYNC; UTC sync; message-rate control; trigger arbitrary messages |
| `mavproxy_graph.py`, `mavproxy_horizon.py`, `mavproxy_checklist.py`, `mavproxy_speech.py`, `mavproxy_notes.py`, `mavproxy_layout.py`, `mavproxy_useralerts.py` | live grapher; artificial horizon; pre-arm checklist; text-to-speech `say()`; notes sidebar; window-layout save/load; periodic user alerts |
| `mavproxy_terrain.py`, `mavproxy_adsb.py`, `mavproxy_proximity.py` | terrain handling (`terrain list/check/download`); ADSB display & threat warnings; proximity sensors |
| `mavproxy_tracker.py`, `mavproxy_gimbal.py`, `mavproxy_gopro.py`, `mavproxy_SIYI/` (pkg), `mavproxy_cameraview.py`, `mavproxy_camera/` (pkg), `mavproxy_smartcamera/` (pkg) | antenna-tracker control (`tracker set/start/arm`); camera & gimbal control (Solo, GoPro, SIYI, camera protocol, OpenCV smart tracking) |
| `mavproxy_mqtt.py`, `mavproxy_restserver.py`, `mavproxy_chat.py`, `mavproxy_ppp.py`, `mavproxy_devop.py`, `mavproxy_firmware.py` | integrations & ops: MQTT, flask REST (`[server]` extra), chat, PPP-over-MAVLink, remote device operations, firmware handling |
| `mavproxy_ais.py`, `mavproxy_asterix.py`, `mavproxy_magical/` (pkg), `mavproxy_optitrack/` (pkg), `mavproxy_nokov/` (pkg), `mavproxy_vicon.py`, `mavproxy_OpenDroneID.py`, `mavproxy_anufireproject/` (pkg), `mavproxy_fieldcheck/` (pkg) | AIS ship tracking; ASTERIX surveillance; 3D WebGL "magical" world; motion capture (OptiTrack/Nokov/Vicon); OpenDroneID RemoteID; CanberraUAV search-and-rescue heritage |
| `mavproxy_misc.py`, `mavproxy_auxopt.py`, `mavproxy_tuneopt.py`, `mavproxy_movinghome.py`, `mavproxy_followtest.py`, `mavproxy_swarm.py`, `mavproxy_sail.py`, `mavproxy_park.py`, `mavproxy_soar.py`, `mavproxy_HIL.py`, `mavproxy_heliplane.py`, `mavproxy_genobstacles.py`, `mavproxy_gasheli.py`, `mavproxy_generator.py`, `mavproxy_emuecu.py`, `mavproxy_silvus.py`, `mavproxy_antenna.py`, `mavproxy_osd.py`, `mavproxy_setpos.py`, `mavproxy_oldwp.py`, `mavproxy_test.py`, `mavproxy_help.py` | remaining utility and niche modules (misc commands, aux/tune options, follow-me, swarm, sail, HIL, Silvus radio stats, on-screen display, …) — `mavproxy_example.py` is the reference template for module authors |

Shared helper libraries live in `MAVProxy/modules/lib/`: `mp_util.py`, `mp_settings.py`,
`mp_menu.py`, `mp_widgets.py`, `wxconsole.py`, `mp_elevation.py`, `srtm.py`,
`mission_item_protocol.py`, `grapher.py`, `multiproc.py`, `sitl_output.py`,
`textconsole.py`, `rline.py` (readline wrapper), etc. Tools shipped as scripts:
`tools/MAVExplorer.py` (offline dataflash log analysis), `tools/mavflightview.py`,
`tools/mavvidplay.py`, `tools/mavpicviewer/`.

## 3. Module plugin system

Loading (from `mavproxy.py::load_module`):

1. Candidate import paths: `MAVProxy.modules.mavproxy_<name>`, then `<name>`
   directly — so out-of-tree (pip-installed or --load-path) packages can supply
   modules too.
2. The package is imported and **reloaded**, then its package-level `init(mpstate,
   **kwargs)` is called; the returned object must be an `MPModule` subclass
   instance, otherwise the load fails.
3. Loaded instances are kept on `mpstate.modules` as `(module, package)` tuples;
   each module's `add_command()` fills the shared `mpstate.command_map`
   (`cmd -> (callback, description)`), which `process_stdin` consults.
4. `module list` shows loaded modules; `module load/unload/reload` change the set at
   runtime (unload runs each `unload()` with a 5s join so a wedged GUI can't hang
   MAVProxy forever). Keyword args are supported: `module load map instance=2`.
5. The default module list comes from `--default-modules` (log, signing, wp, rally,
   fence, ftp, param, relay, tuneopt, arm, mode, calibration, rc, auxopt, misc,
   cmdlong, battery, terrain, output, adsb, layout). `link` is always loaded first.

## 4. Connection handling

### CLI options

```
--master DEVICE[,BAUD]   # repeatable: add a MAVLink master link
--out DEVICE[,BAUD]      # repeatable: add a forwarding output link
--baudrate 57600         # default serial baud
--sitl HOST:PORT|uds:PATH# SITL RC output (sim RC in)
--source-system 255 --source-component 230      # GCS sysid/compid
--target-system 0 --target-component 0          # auto- first vehicle
--streamrate 4 --heartbeat-rate 1
--mav10/--mav20/--mavversion 1.0|2.0 --dialect all
--force-connected --retries N --rtscts --nodtr
--daemon / --non-interactive / --nowait --continue
--logfile mav.tlog / -a / --append-log / --aircraft NAME / --state-basedir
--load-module NAME[,NAME] / --default-modules LIST
--cmd 'console' (run console command(s) after startup) / --setup
```

`--master` accepts anything pymavlink's `mavutil.mavlink_connection` understands:
`/dev/ttyUSB0:115200`, `COM3:57600`, UDP (`udpin:0.0.0.0:14550`,
`udpout:…`, `udp:HOST:PORT`), TCP (`tcpin:…`, `tcp:HOST:PORT` client), multicast
`mcast:`, and unix domain sockets (`uds:PATH`). Connections use
`mavlink_connection(autoreconnect=True, retries=…, force_connected=…)`, so dead
ports retry transparently. Devices with one `device:baud` pair are re-interpreted
as serial ports if the device matches an auto-detected port; links may also carry
JSON attributes after a `:{`, e.g. `udpin:127.0.0.1:9877:{"foo":"bar"}` —
parsed attributes are `setattr`-ed onto the connection, exactly what
`link attributes (LINK) (ATTRIBUTES)` does at runtime.

### Link object bookkeeping (`mavproxy_link.py`)

`link_add(descriptor)` builds the connection via `mavlink_connection()` and stamps
`linknum, linkerror, link_delayed, last_heartbeat, last_message, target_system` on
it, registering its fd in the main select loop (`child_fd_list_add`). `link list`,
`link ports`, `link remove N` and `link resetstats` operate at runtime; `vehicle …`,
`alllinks <command>` and `ping` run commands/pings across every link.

### Forwarding (the `--out` path)

`LinkModule.master_callback()` is the single sink for input from any master link:

1. On every relevant HEARTBEAT, record the sysid/compid → link mapping
   (`mpstate.vehicle_link_map`) and print `Detected vehicle 1:1 on link 1`.
2. If the source system has a dedicated sysid connection (`output sysid N DEVICE`),
   everything from it is streamed there and processing stops (secondary-vehicle mode).
3. The packet is timestamped and logged to the tlog (link number stashed in the low
   bits for later packet-delay analysis), cached in `status.msgs[mtype]` and counted.
4. `linkerror` is cleared when activity packets arrive; the `link_delayed` /
   `checkdelay` logic suppresses duplicated position/status reporting when a slow
   secondary link runs in parallel with the primary.
5. **Broadcast**: any non-`BAD_DATA` packet is written to all `mav_outputs`
   (`--out` links), gated by `mavfwd` (enable forwarding at all), `mavfwd_rate`
   (`REQUEST_DATA_STREAM` is suppressed unless enabled, so a second GCS can't fight
   over stream rates), per-output `discard_comps` exclusions and websocket-open
   checks.
6. With the `fwdpos` setting, `GLOBAL_POSITION_INT` is also echoed to the other
   *master* links; then the packet is handed to each module's `mavlink_packet()`
   (non-multi-vehicle modules receive primary-vehicle traffic only, with special
   handling for SiK radio RADIO/RADIO_STATUS from sysid 51).
7. The reverse direction: packets arriving on an `--out` link are decoded in
   `mavproxy.py::process_mavlink()` ("slaves") and, if allowed, re-emitted to the
   master link — gated by `mavfwd`, optionally always permitted while disarmed
   (`mavfwd_disarmed`), optionally restricted to a chosen `mavfwd_link`, with
   re-signing support. This closes the loop, making MAVProxy a full in/out router.

Integrations can also hook extra fds into the select loop via
`mpstate.select_extra`; startup (`mavinit.scr`) scripts support `${VAR}`
substitution with `${VAR:default}` defaults via `mp_substitute.MAVSubstitute`.

## 5. CLI commands

Dispatch is `cmd -> handler` over all loaded modules; built-ins first:

```
help / status / set <setting> [v] / watch MSG_PATTERN / module load|unload|reload|list
alias add|remove|list / setup (legacy serial CLI, '.' to leave) / exit
```

Typical module commands (all tab-completable):
| Command | Module |
|---|---|
| `arm [check] …` `disarm` | arm |
| `mode loiter`, `mode guided AGL` | mode |
| `wp load foo.txt`, `wp list`, `wp set 7`, `wp removeall`, `wp loop` | wp (also drives `fence …` / `rally …` via mission_item_protocol) |
| `param fetch *`, `param set ARMING_CHECK 1`, `param download <regex>` | param |
| `output add 127.0.0.1:14550`, `output sysid 5 udpin:0.0.0.0:14551`, `output remove 1` | output |
| `link add /dev/ttyUSB0:115200`, `link list`, `link remove 2`, `alllinks arm`, `ping` | link |
| `guided ALT 30`, `takeoff 20`, `land`, `loiter`, `position coords …` | cmdlong |
| `terrain list|check|download`, `log status|download|erase`, `ftp ls|get|put …` | terrain / log / ftp |
| `graph <message field>`, `layout save <name>`, `joystick status|set|probe`, `tracker start` | graph / layout / joystick / tracker |

`--cmd` / `mavinit.scr` scripts can run any of these at startup, e.g.
`module load map; module load console; param fetch *; wp list`.

## 6. Installation & running

### From pip or a checkout

```sh
pip install MAVProxy                # core
pip install MAVProxy[recommended]   # + flask, PyYAML, wxpython, Pygame, PyAV…
pip install MAVProxy[map3d]         # explicit VTK 3D-map set (quantized-mesh-tile, vtk…)
pip install MAVProxy[cesium]        # Cesium globe server (tornado)

# alternatively, from a checkout (this repo):
cd gcs/MAVProxy && python -m pip install -e .
```

`setup.py` adds platform-aware requirements (wxPython/matplotlib on macOS,
prompt_toolkit/requests on Windows) and PEP-508 markers so the optional VTK-based
`map3d` stays dormant on unsupported platforms. The minimal core runtime deps
(`requirements.txt`): `pymavlink>=2.4.14`, `pyserial>=3.0`, `numpy`.

### With ArduPilot SITL

After `sim_vehicle.py -v ArduCopter` starts (which itself launches MAVProxy, see
§7), or pointing at an already-running sim/vehicle:

```sh
mavproxy.py --master=127.0.0.1:14550 --console --map
```

Useful real-world recipes:

```sh
# serial vehicle, GUI, plus a second GCS listening on UDP
mavproxy.py --master=/dev/ttyUSB0:57600 --out=udp:192.168.1.3:14550 --map --console

# SITL TCP master, RC output to SITL (essentially what sim_vehicle runs)
mavproxy.py --master=tcp:127.0.0.1:5760 --sitl=127.0.0.1:5501 --map --console

# headless router (multiple field laptops listening)
mavproxy.py --master=/dev/ttyACM0:921600 --out=10.0.0.2:14550 --out=10.0.0.3:14550 \
            --daemon --non-interactive --no-console
```

Windows launchers `MAVProxyWinUSB.bat` / `MAVProxyWinLAN.bat` wrap common cases;
a PyInstaller build (`windows/mavproxy.spec`) produces a standalone `mavproxy.exe`.

## 7. How ArduPilot autotest uses MAVProxy

The parent ArduPilot repo (`Tools/autotest/`) installs MAVProxy and treats it as the
control plane for every SITL test:

- `Tools/autotest/sim_vehicle.py` — the SITL launcher. Its `start_mavproxy()` shells
  out to `mavproxy_cmd()` (`which mavproxy`) with: `--master tcp:127.0.0.1:5760+10*i`
  (or `udpin:` with `--udp`, `uds:` with unix sockets, `mcast:` with `--mcast`),
  `--sitl 127.0.0.1:5501+10*i` for RC injection, extra `--out 127.0.0.1:14550+10*i`
  (or WSL2/vagrant host forwarding), `--retries 5|10`, optional `--load-module
  tracker|gimbal`, `--map`, `--console`, and any user `--mavproxy-args` pass-through.
- Per-vehicle suites (`arducopter.py`, `arduplane.py`, `ardusub.py`, `rover.py`,
  `quadplane.py`, `blimp.py`) drive that single running MAVProxy instance with
  MAVLink commands — e.g. `vehicle_test_suite.py` calls
  `send_mavlink_arm_command()` / `send_mavlink_disarm_command()` which send arm/disarm
  *from* MAVProxy — so the tests exercise the GCS itself as well as the vehicle.
- `vehicle_test_suite.py` also imports helpers straight from the package
  (`from MAVProxy.modules.lib import mp_elevation, mp_util`), and `sim_vehicle.py`
  imports `MAVProxy.modules.mavproxy_map.srtm` for elevation data; the antenna-tracker
  SITL integration runs via MAVProxy (`module load map; tracker set port …;
  tracker start; tracker arm;`).

In short: **no autotest run happens without MAVProxy** — it is simultaneously the
MAVLink router between sim/vehicle/GCS clients, the test driver, and the GUI the
developer watches.

*Written for `drpilot`; all module names verified against the actual tree on 2026-10-29.*
