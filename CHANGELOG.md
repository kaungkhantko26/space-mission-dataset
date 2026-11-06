# Changelog

## v2.0.0 — strict mode: verified data only
* **Public dataset is now `verified/`**; everything exposed (API, CSV/SQLite, backend, website) is verified. Removed from public output: instruments, components, propellants, atmospheres, ground stations, unverified vehicle/engine fields, mission masses/costs, the user-supplied SpaceX table, and the estimated/fictional optimizer.
* **Real datasets ingested directly:** JPL NHATS (7,185 targets), JPL SBDB NEOs with measured diameter (1,265), JPL satellite mean elements (461), official NASA Facilities (485, no contact data); user NASA facilities file cross-checked (485/485 agree).
* New: `tools/make_verified.py`, `tools/validate_verified.py` (51 checks re-reading raw files), strict local backend (NHATS search, Hohmann, light time), new website tabs (asteroid targets, facilities).
* `space-mission-research/` is now **staging only**; the synthetic optimizer moved to `labs/`.


## v1.0.0 — hackathon release
* **Data:** 25 celestial bodies, 24 engines/thrusters, 16 launch vehicles, stages/boosters, 23 component classes, 16 instruments, 14 historical missions, 8 ground stations, 80 constraints; user-supplied SpaceX launch table (2010-2018) and 485 NASA facilities.
* **Verification against retrieved sources** (JPL SSD/SBDB, NASA NSSDC + mission catalog, NASA SLS page, Apollo 11 press kit, NTRS papers, ULA, ESA): 32 records verified; 29 wrong/outdated recalled values replaced; 86 launch/mission field checks + 217 celestial field checks recorded with source text and file hashes.
* **Analysis & optimization:** Δv, power, communications, mass accounting; exact optimizer (3 scenarios × 9 objectives), Pareto fronts, sensitivity, Monte Carlo, solver benchmarks; vectorized exact solver.
* **Backend & access:** static JSON API (`docs/api/v1`), local backend `tools/serve_api.py`, CSV + SQLite exports, JS and Python clients, OpenAPI spec.
* **Web explorer:** explorer, compare with winners, mission fit, calculators, optimizer with balance controls, Monte Carlo simulator with suggestions, launch & facilities, API tab, benchmarks, quality.
* **Quality:** 82 automated validation checks; JS↔Python optimizer parity; backend smoke test; CI workflow.
* **Known gaps:** Falcon/Starship/Electron/most engines, spacecraft components, instruments and mission masses/costs are unverified; optimizer catalog is estimated/fictional; SpaceX table ends June 2018.
