# Space Mission Dataset — verified-only backend

A hackathon-ready **backend dataset** for space-mission design projects. **Strict mode:** everything public here was compared with, or ingested directly from, a *retrieved* authoritative source (JPL, NASA, ULA, ESA). Unverified, estimated and fictional values were removed.

**→ Start with [`HACKATHON.md`](HACKATHON.md).** Live site and API: https://kaungkhantko26.github.io/space-mission-dataset/

```bash
python3 tools/serve_api.py          # local backend on http://127.0.0.1:8000 (stdlib only)
make all && make test               # rebuild everything, 77 validation checks, 23 backend checks
```

## What you get (12,830 verified records)
| | Records | Source |
|---|---:|---|
| Sun, planets, dwarf planets, moons, asteroids (verified fields); orbital elements | 51 | JPL SSD, JPL SBDB, NASA NSSDC |
| Atmospheres (published text + parsed numbers) | 10 | NASA NSSDC fact sheets |
| Moon mean orbital elements | 461 | JPL (ingested directly) |
| NHATS accessible near-Earth targets (min Δv, durations) | 7,185 | JPL NHATS API |
| Near-Earth objects with measured diameter | 1,265 | JPL SBDB |
| **Spacecraft components** (thrusters, batteries, solar arrays, radios, antennas, reaction wheels, star trackers, computers, platforms, launch integration, ground systems…) | 1,724 rows / 99 tables | NASA Small Spacecraft SoA report 2026 (vendor-reported) |
| **Launch vehicle configurations** (dimensions, mass, thrust, capacities, cost, launch stats) | 532 | Launch Library 2 (aggregator) |
| **SpaceX launch record** | 743 | Launch Library 2 (aggregator); your 2010-2018 file agrees on 57/57 dates, 56/57 outcomes |
| **Missions / instruments** with NASA's descriptions | 39 / 181 | NASA NSSDC Master Catalog |
| **Fluid properties** (O₂, H₂, CH₄, Xe, N₂, He saturation tables) | 6 | NIST Chemistry WebBook |
| NASA facilities | 485 | official data.nasa.gov table (no contact data) |
| Engines/thrusters, launch vehicles, Saturn V stages, payload capacities, missions — **verified fields only** | 41 | NTRS papers, Apollo 11 press kit, NASA SLS page, ULA, ESA, NSSDC catalog |

Access: static JSON API (`docs/api/v1`), local backend (`tools/serve_api.py`), CSV + SQLite (`exports/`), one JSON (`verified/combined/`), website (`docs/`), JS and Python clients, OpenAPI spec.

## Trust model
* Records carry only their verified fields; each has `field_verification` (source text, URL, retrieval date, file SHA-256, tolerance) or a collection-level `provenance` block. A missing field means "not verified", never zero.
* Where a recalled value disagreed with its source, the **sourced value replaced it** (29 corrections, e.g. Saturn V S-IC dry mass 137,000 → 130,975 kg, BPT-4000 Isp 1850 → 2150 s, Eris radius, Uranus gravity). See `verified/quality_report.json` and the site's Quality tab.
* `validate_verified.py` re-reads values from the **raw retrieved files** and scans for any unverified/estimated/fictional marker.
* Source authority is stated: NASA/JPL/NIST/ESA/ULA documents and datasets; **vendor-reported** (NASA SoA tables); **aggregator** (Launch Library 2, `source_authority`, confidence medium).
* Not included: structured instrument mass/power specs (NASA's catalog only has prose), storable-propellant properties (RP-1, hydrazine, MMH, NTO), costs, and the cost/science optimizer (needs estimated/fictional values).

## Repository map
| Path | What |
|---|---|
| `verified/` | **the dataset** (per-collection JSON, `combined/`, `quality_report.json`, `validation_report.json`) |
| `exports/` | CSV per collection + `space_mission.sqlite` |
| `docs/` | website + static API (`docs/api/v1`), `client.js`, `advisor.js` |
| `data_raw/` | cached source pages (`retrieved/`, SHA-256 in `MANIFEST.json`) and two user-supplied files |
| `tools/` | pipeline: `fetch_sources.sh`, `verify_celestial.py`, `verify_launch.py`, `make_verified.py`, `validate_verified.py`, `make_api.py`, `export_data.py`, `serve_api.py`, `smoke_test.py` |
| `space-mission-research/` | **staging only** — maintainers' build containing unverified/estimated values; not served or exported (see its README) |
| `labs/` | retired synthetic-optimizer experiments, not part of the dataset |
| `examples/` | Python, Node and pandas quickstarts |

## Licence
Code MIT (`LICENSE`); compiled data CC BY 4.0 with third-party attributions in [`LICENSE-DATA.md`](LICENSE-DATA.md). NASA does not endorse this project.
