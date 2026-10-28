# 18 — THIS Workspace's Dev Workflow (everything we set up)

This doc captures *what was set up in `~/Projects/drpilot` for you* and the
commands that work here. It assumes Python deps are in `.venv/` and system
packages you installed yourself with pacman.

## What exists here that is not stock ArduPilot
| Item | Notes |
|---|---|
| `AGENTS.md` | AI-contributor rules for ArduPilot (upstream style, kept at root) |
| `gcs/` | `MissionPlanner`, `MAVProxy`, `qgroundcontrol` shallow clones (`--depth 1` master) |
| `.venv/` | Python venv (system untouched) |
| `docs/project/` | this documentation set |
| `build/sitl/` | SITL build output (partially built; run builds yourself) |

## Environment quick facts (this machine)
```
OS          Arch Linux
Python      3.14.8  (system); .venv is the project env
Compiler    GCC 16.2.1 (works for SITL builds)
Docker      present — handy if you ever want the upstream Dockerfile builds
MCU.Builder note: hardware builds (ChibiOS boards) are untested here; SITL is the primary target
```

## Day-to-day commands

### Build SITL (venv-scoped)
```bash
cd ~/Projects/drpilot
.venv/bin/python ./waf configure --board sitl
.venv/bin/python ./waf copter -j8         # arduplane / ardurover / ardusub / ardu-blimp
```
Output: `build/sitl/bin/arducopter`

### Run the sim vehicle
```bash
build/sitl/bin/arducopter -w
# first run: -w resets params; afterwards plain `build/sitl/bin/arducopter`
```
Sim vehicle listens:
- TCP 5760 — primary link
- UDP 14550, 14551 — GCS links

### Connect a GCS
**MAVProxy (headless, has map GUI with `--map`):**
```bash
.venv/bin/mavproxy.py --master=127.0.0.1:14550 --console --map
```

**Mission Planner (Linux via Mono, or Windows)** — Connection dialog →
dropdown → `UDP` → hit Connect (port 14550).
*(see docs 09 for Linux build instruction)*

**QGC (Linux build, see docs 11)** — runs its own autoconnect; SITL at
14550 should be picked up automatically.

### Autotest a single scenario (once you're ready)
```bash
.venv/bin/python Tools/autotest/autotest.py build.Copter test.Copter.RTLYaw
```

### Unit tests
```bash
.venv/bin/python ./waf --targets tests/AP_Math_tests   # an example target listing
# the resulting test binaries in build/sitl/tests/ run directly
```

## Conventions when you change code
- astyle your files: `Tools/CodeStyle/astylerc` settings (1-space-read the
  file; typical usage: `astyle --options=Tools/CodeStyle/astylerc <files>`).
- Python files opt into linting with `# AP_FLAKE8_CLEAN` marker.
- Commits `Subsystem: short change` (see AGENTS.md §7; tooling
  `Tools/gittools/git-subsystems-split` splits multi-subsystem commits).
- For PRs: fork → branch → rebase on `master` → your testing evidence.

## Rebuilding when something looks stuck
```bash
git submodule update --init --recursive   # missing headers? fix this first
./waf clean                                # for changed feature flags
./waf distclean                            # nuclear: also drops build config
```

## Housekeeping caveats (already fixed here, but remember)
- Never mix `pip --user`/`--break-system-packages` installs — keep to `.venv`.
- The `docs/` original folder (build scripts) must stay untouched; new docs
  belong in `docs/project/`.
- Runtime-generated artifacts (`build/`, `.venv/`) are gitignored — recreate
  with the commands above.
