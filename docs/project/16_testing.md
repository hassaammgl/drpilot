# 16 — Testing: SITL, Autotest, Unit Tests, Replay

ArduPilot has 3 testing layers. This doc explains each and what's runnable
in this workspace right now.

## 1. Unit tests (GTest)
- Location: `libraries/<lib>/tests/` (e.g. `libraries/AP_Math/tests/`).
- Uses `modules/gtest`, with helper `tests/AP_gtest.h`.
- Build one: `.venv/bin/python ./waf --targets tests/AP_Math_tests`
- Run: the built test binary executes directly (fast, no vehicle).
- Some pure-python tests live in `tests/` (CI tooling tests) and
  `Tools/autotest/unittest/`.

**When:** you add/modify math or a library — write/maintain a unit test
under that library's `tests/` dir.

## 2. SITL (software-in-the-loop) — manual flying without hardware
SITL builds the *firmware itself* to run on Linux against simulated
hardware created by `AP_HAL_SITL` + physics models in `SITL/` and
`Tools/autotest/models/`.

Run it manually (this workspace):
```bash
build/sitl/bin/arducopter -w     # -wipe parameter file on first run
# outputs:
#  TCP 5760 (raw MAVLink sim master)
#  UDP 14550 / 14551 (GCS ports, like real telemetry)
```
Then connect any GCS:
- **Mission Planner** (Windows or Mono/Linux): Connection dialog →
  UDP 14550
- **MAVProxy:**
  `.venv/bin/mavproxy.py --master=127.0.0.1:14550 --console --map`
- **QGC:** auto-detects UDP 14500/14550 streams typically; either set
  explicit link or use autoconnect.

Camera/video, wind, ships/jeeps moving models etc. are all scriptable;
see `Tools/autotest/pysim/` for simulated sensors (e.g. to inject fake GPS).

**Why SITL matters:** the *same* C++ code path runs; only HAL changes. It
is the only safe way to behaviors-test flight logic.

## 3. Autotest (scripted full scenarios)
`Tools/autotest/autotest.py` orchestrates: build → launch SITL → drive
MAVProxy (loaded with plugins from `Tools/mavproxy_modules/`) through
scripted flights (`arducopter.py`'s organized `TestSuite` classes) and
verifies outcomes via mavlink state + dataflash logs.

```bash
# in venv so MAVProxy + pexpect resolve:
.venv/bin/python Tools/autotest/autotest.py build.Copter test.Copter.RTLYaw
# (needs MAVLink-related deps already in your venv)
```
- Tests are grouped per vehicle in `ardurover.py`, `arduplane.py`, …
- Scenario methods live inside classes; `test.Copter` runs the whole suite.
- This is what CI executes per PR (see `.github/workflows/`).

## 4. Replay
`Tools/Replay` deterministically feeds a real flight's dataflash log back
through the EKF to reproduce attitude estimates — for debugging specific
in-flight events after the fact.

## 5. CI checks per PR (summary)
SITL autotest per vehicle, unit-test build matrix (gcc+clang), ChibiOS
hwdef builds, astyle, flake8, commit-message subsystem checks (see AGENTS.md),
binary size check, pre-commit (line endings, codespell…).

## Practical matrix for this workspace
| I want to… | Do |
|---|---|
| fly around myself | SITL + any GCS |
| verify one control behavior automatically | autotest single test |
| write library math | add/extend GTest file |
| debug a real-flight log | Replay or Mission Planner Log analyze |
| full CI-like verification | run vehicle test suites via autotest |
