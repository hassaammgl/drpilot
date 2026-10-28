# Full File Inventory

`ardupilot_files.txt.gz` contains a sorted, gzipped listing of EVERY file
in the ArduPilot firmware tree — 25,356 files total, broken down:

| Top dir | Files |
|---|---|
| `modules/` (submodules, checked out) | 16,936 |
| `libraries/` | 5,966 |
| `Tools/` | 2,054 |
| `ArduCopter/` | 94 |
| `ArduPlane/` | 89 |
| `Rover/` | 55 |
| `ArduSub/` | 52 |
| `docs/` (original build scripts) | 33 |
| `AntennaTracker/` | 30 |
| `Blimp/` | 40 |
| `tests/` | 6 |
| `benchmarks/` | 1 |

Regenerate anytime:
    find ArduCopter ArduPlane ArduSub Rover Blimp AntennaTracker libraries Tools modules tests benchmarks docs \
         -type f -not -name ".git*" | sort | gzip > docs/project/inventory/ardupilot_files.txt.gz

Read it:
    zcat docs/project/inventory/ardupilot_files.txt.gz | less

Note: file counts by language as of Oct 29 2026 — ~1,683 .cpp, ~1,625 .h,
351 .py in the firmware tree alone.
