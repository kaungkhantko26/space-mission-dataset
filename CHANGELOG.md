# Changelog

## v1.0.0 — hackathon release
* **Data:** 25 celestial bodies, 24 engines/thrusters, 16 launch vehicles, stages/boosters, 23 component classes, 16 instruments, 14 historical missions, 8 ground stations, 80 constraints; user-supplied SpaceX launch table (2010-2018) and 485 NASA facilities.
* **Verification against retrieved sources** (JPL SSD/SBDB, NASA NSSDC + mission catalog, NASA SLS page, Apollo 11 press kit, NTRS papers, ULA, ESA): 32 records verified; 29 wrong/outdated recalled values replaced; 86 launch/mission field checks + 217 celestial field checks recorded with source text and file hashes.
* **Analysis & optimization:** Δv, power, communications, mass accounting; exact optimizer (3 scenarios × 9 objectives), Pareto fronts, sensitivity, Monte Carlo, solver benchmarks; vectorized exact solver.
* **Backend & access:** static JSON API (`docs/api/v1`), local backend `tools/serve_api.py`, CSV + SQLite exports, JS and Python clients, OpenAPI spec.
* **Web explorer:** explorer, compare with winners, mission fit, calculators, optimizer with balance controls, Monte Carlo simulator with suggestions, launch & facilities, API tab, benchmarks, quality.
* **Quality:** 82 automated validation checks; JS↔Python optimizer parity; backend smoke test; CI workflow.
* **Known gaps:** Falcon/Starship/Electron/most engines, spacecraft components, instruments and mission masses/costs are unverified; optimizer catalog is estimated/fictional; SpaceX table ends June 2018.
