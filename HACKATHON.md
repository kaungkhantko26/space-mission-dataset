# Hackathon quick start (5 minutes) — verified-only dataset

**Strict mode:** everything public in this repo (`verified/`, the API, the CSV/SQLite exports, the local backend, the website) contains **only values that were compared with, or ingested directly from, a retrieved authoritative source**. Anything unverified, estimated or fictional was removed. Each record says how it was verified (`field_verification` or a collection-level `provenance` with URL, retrieval date and SHA-256 of the raw file).

| You want… | Do this | Needs |
|---|---|---|
| **A live API** (any language, CORS open) | `GET https://kaungkhantko26.github.io/space-mission-dataset/api/v1/index.json` — guide: [`docs/api.html`](docs/api.html) | internet |
| **A local backend** with filtering, NHATS search, Hohmann and Δv | `python3 tools/serve_api.py` → http://127.0.0.1:8000 | Python 3.10+ only |
| **Spreadsheets / pandas / SQL** | `exports/csv/*.csv` or `exports/space_mission.sqlite` | nothing |
| **One JSON file** | `verified/combined/verified_space_mission_data.json` (1 MB) | nothing |
| **Browser app** | the site (`docs/index.html`) or `make site` | a browser |

## Try it now
```bash
python3 tools/serve_api.py &
curl "localhost:8000/collections"
curl "localhost:8000/nhats/best?max_delta_v=6&min_size_m=100&limit=10"        # real JPL NHATS asteroid targets, lowest delta-v first
curl "localhost:8000/collections/moon_mean_elements?satellite=Io"             # JPL mean elements
curl "localhost:8000/collections/electric_propulsion?sort=-isp_vac_s&fields=id,name,isp_vac_s,thrust_vac_n,power_w"
curl -X POST localhost:8000/hohmann -d '{"body":"earth","altitude1_km":400,"altitude2_km":35786}'
curl "localhost:8000/light-time?target=mars"
```
Examples: [`examples/python_quickstart.py`](examples/python_quickstart.py), [`examples/node_quickstart.mjs`](examples/node_quickstart.mjs), [`examples/pandas_demo.py`](examples/pandas_demo.py).

## What is in the dataset (all verified)
| Collection | Records | Source |
|---|---:|---|
| `planets` (Sun, 8 planets, 3 dwarf planets), `moons` (11), `asteroids` (Bennu, Vesta), `orbital_elements` | 12 / 11 / 2 / 13 | JPL SSD physical parameters, JPL approximate elements, NASA NSSDC fact sheets, JPL SBDB — field-by-field checks |
| `moon_mean_elements` | 461 | JPL planetary-satellite mean elements (ingested directly) |
| `nhats_targets` | 7,185 | JPL NHATS API: accessible near-Earth targets, min delta-v (km/s), trip durations (days) |
| `neo_catalog` | 1,265 | JPL SBDB query: near-Earth objects with measured diameter |
| `nasa_facilities` | 485 | official NASA Facilities table on data.nasa.gov (contact names/phones **not** ingested) |
| `rocket_engines` (5), `electric_propulsion` (3: NEXT, NSTAR, BPT-4000) | verified fields only | NASA NTRS, NASA SLS page, Apollo 11 press kit, ULA |
| `launch_vehicles` (7), `rocket_stages` (Saturn V ×3), `boosters`, `payload_capabilities` (11) | verified fields only | Apollo 11 press kit, NASA SLS page, ULA, ESA |
| `missions` (11) | launch date / vehicle family only | NASA NSSDC mission catalog |

Records contain **only their verified fields**; absent field = not verified (never zero). `unverified_fields` / `verified_fields` lists make that explicit.

## ⚠ What is deliberately not here
Instruments, spacecraft components, propellants, atmospheres, ground stations, Falcon/Starship/Electron and most engine specs, mission masses/costs, the SpaceX launch table, and the cost/science optimizer (it needed estimated and fictional values). Say so on your slide: *"verified-only; partial by design."* The staging build (`space-mission-research/`) still contains those values for maintainers, but nothing there is served or exported.

## Local backend endpoints
| Endpoint | What |
|---|---|
| `GET /collections` | 16 collections and counts |
| `GET /collections/{c}?q=&field=value&field_gte=&field_lte=&sort=-field&limit=&offset=&fields=a,b` | search / filter / sort / project (dotted paths allowed, e.g. `derived.escape_velocity_m_s_gte=5000`) |
| `GET /collections/{c}/{id}` | one record (with `field_verification`) |
| `GET /nhats/best?max_delta_v=&min_size_m=&limit=` | NHATS targets, lowest delta-v first |
| `GET /light-time?target=` | one-way light-time range from verified orbits (derived) |
| `POST /delta-v` | rocket equation (ideal) |
| `POST /hohmann` | Hohmann transfer around any verified body (verified GM + radius) |

## Project ideas that fit this data
* **Asteroid mission picker:** NHATS delta-v vs trip time vs size, with SBDB diameters; add rocket-equation propellant using verified Isp values (NEXT 4190 s, BPT-4000 2150 s, NSTAR ≈3300 s).
* **Moon/Mars transfer planner:** Hohmann and light-time from verified constants; show Saturn V stage masses and verified launch capacities.
* **Moon explorer:** all JPL satellite mean elements with orbit visualizations.
* **Ground-infrastructure map:** official NASA facilities by center/status.
* **Trust UI:** show `field_verification` source text and file hash for each number.

## Rebuild / extend
```bash
make setup    # pip install -r requirements.txt (jsonschema, numpy)
make all      # staging build -> strict verified dataset -> 51 validation checks -> API -> CSV/SQLite
make test     # + backend smoke test (16 endpoint checks)
make fetch    # re-download source pages (needs network access to JPL/NASA/ULA/ESA)
make verify   # re-run verification on cached pages, then make all
```
To add data: obtain a retrievable source, add a parser in `tools/verify_*.py` (or ingest it in `tools/make_verified.py`), keep the raw file in `data_raw/retrieved/` and make sure `make test` passes. Unverifiable data must not enter `verified/`.

## FAQ
* **Is it NASA-approved?** No. Values come from NASA/JPL/ESA/ULA pages and documents; see [`LICENSE-DATA.md`](LICENSE-DATA.md).
* **Port busy?** `python3 tools/serve_api.py --port 8010`.
* **Where did the optimizer go?** Kept only as an internal synthetic demo (`tools/opt_model.py`, `labs/`), not part of the dataset or site.
