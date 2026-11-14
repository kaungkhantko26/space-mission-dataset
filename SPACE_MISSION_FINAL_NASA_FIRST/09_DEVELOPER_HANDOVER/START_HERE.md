# Developer handover - NASA-first Sun-Earth-Moon and Sun-Earth-Mars

This is the **cleaned, source-restricted integration and research foundation**, not a complete running game or full mission solution.

## Start in this order

1. `01_COMMON_FOUNDATION/`: common NASA NAIF ephemeris kernel and time/units science references.
2. `04_LAUNCH_AND_ASCENT/`: NASA-source SLS ascent reference only, atmosphere and launch physics helper functions.
3. `05_DEVELOPER_SPECIFICATION/`: JSON Schemas, TypeScript interfaces, telemetry and scene mapping.
4. `02_SUN_EARTH_MOON/`: NASA Sun/Earth/Moon foundation; processed CSVs are QA-held for timestamp drift.
5. `03_SUN_EARTH_MARS/`: NASA JPL Horizons Earth/Mars 30-day geometric TDB ECLIPJ2000 states (Sun vectors not yet matched); not a transfer trajectory.
6. `08_VALIDATION_AND_QA/`: source restrictions, detected defects and integration gaps.

## Must not claim as completed

- Lunar/Martian transfer research from your teammate has not been included or validated.
- No live or real-time physics solver, integration, or complete game has been built.
- User-provided stage engineering data originally cited external manufacturers and was filtered out unless NASA supported.
- The final ZIP does not contain the original full archival upload; preserve the user's original upload as separate raw backup.

## Installing on Windows

Extract the ZIP contents to `D:\space mission data\` on your computer. ChatGPT cannot write directly to a local D: drive.

All source files are preserved in the original uploaded ZIP, which should remain outside the approved developer delivery until individually cleared.
