# Space Mission Dataset — verified-only backend

A hackathon-ready **backend dataset** for space-mission design projects. **Strict mode:** everything public here was compared with, or ingested directly from, a *retrieved* authoritative source (JPL, NASA, ULA, ESA). Unverified, estimated and fictional values were removed.

**→ Start with [`HACKATHON.md`](HACKATHON.md).** Live site and API: https://kaungkhantko26.github.io/space-mission-dataset/

```bash
python3 tools/serve_api.py          # local backend on http://127.0.0.1:8000 (stdlib only)
make all && make test               # rebuild everything, 51 validation checks, 16 backend checks
```

## What you get (all verified)
| | Records | Source |
|---|---:|---|
| Sun, planets, dwarf planets, moons, asteroids (verified fields) | 40 | JPL SSD, JPL SBDB, NASA NSSDC |
| Moon mean orbital elements | 461 | JPL (ingested directly) |
| NHATS accessible near-Earth targets (min Δv, durations) | 7,185 | JPL NHATS API (ingested directly) |
| Near-Earth objects with measured diameter | 1,265 | JPL SBDB (ingested directly) |
| NASA facilities | 485 | official data.nasa.gov table (no contact data) |
| Engines/thrusters, launch vehicles, Saturn V stages, payload capacities, missions — **verified fields only** | 41 | NTRS papers, Apollo 11 press kit, NASA SLS page, ULA, ESA, NSSDC catalog |

Access: static JSON API (`docs/api/v1`), local backend (`tools/serve_api.py`), CSV + SQLite (`exports/`), one JSON (`verified/combined/`), website (`docs/`), JS and Python clients, OpenAPI spec.

## Trust model
* Records carry only their verified fields; each has `field_verification` (source text, URL, retrieval date, file SHA-256, tolerance) or a collection-level `provenance` block. A missing field means "not verified", never zero.
* Where a recalled value disagreed with its source, the **sourced value replaced it** (29 corrections, e.g. Saturn V S-IC dry mass 137,000 → 130,975 kg, BPT-4000 Isp 1850 → 2150 s, Eris radius, Uranus gravity). See `verified/quality_report.json` and the site's Quality tab.
* `validate_verified.py` re-reads values from the **raw retrieved files** and scans for any unverified/estimated/fictional marker.
* Not included: instruments, spacecraft components, propellants, atmospheres, ground stations, Falcon/Starship/Electron and most engine specs, costs, the SpaceX launch table, and the cost/science optimizer (those need values that could not be verified).

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
