# Hackathon quick start (5 minutes)

This repo is a ready-to-use **backend dataset** for a space-mission-design project: real celestial/launch/propulsion data with provenance, mission analysis, and an exact design optimizer. Pick *one* way to access it.

| You want… | Do this | Needs |
|---|---|---|
| **A live API, no install** (frontend / any language) | `GET https://kaungkhantko26.github.io/space-mission-dataset/api/v1/index.json` (CORS open) — guide: [`docs/api.html`](docs/api.html) | internet |
| **A local backend with filtering + optimizer + Monte Carlo** | `python3 tools/serve_api.py` → http://127.0.0.1:8000 | Python 3.10+ only (no packages) |
| **Spreadsheets / pandas / SQL** | `exports/csv/*.csv` or `exports/space_mission.sqlite` | nothing |
| **One JSON file** | `space-mission-research/combined/all_space_mission_data.json` | nothing |
| **Browser app to explore** | open the site ( `docs/index.html` ) or `make site` | any browser |

## Try it now
```bash
python3 tools/serve_api.py &           # starts http://127.0.0.1:8000
curl "localhost:8000/collections/rocket_engines?isp_vac_s_gte=440&sort=-isp_vac_s&fields=id,name,isp_vac_s,data_class"
curl "localhost:8000/verified"                                   # only records verified against retrieved sources
curl "localhost:8000/optimize?scenario=lunar_orbiter&objective=balanced&w_science=3&budget_scale=1.2"
curl -X POST localhost:8000/delta-v -d '{"isp_s":310,"delta_v_m_s":4000,"mf_kg":500}'
```
Other examples: [`examples/python_quickstart.py`](examples/python_quickstart.py), [`examples/node_quickstart.mjs`](examples/node_quickstart.mjs), [`examples/pandas_demo.py`](examples/pandas_demo.py).

## Local backend endpoints
| Endpoint | What |
|---|---|
| `GET /collections` | all collections and counts (22) |
| `GET /collections/{c}?q=&field=value&field_gte=&field_lte=&sort=-field&limit=&offset=&fields=a,b` | search / filter / sort / project (dotted paths allowed, e.g. `derived.escape_velocity_m_s_gte=5000`) |
| `GET /collections/{c}/{id}` | one record |
| `GET /verified` | ids of every record whose `data_class` is `verified` |
| `GET /scenarios` | the 3 optimizer scenarios + component catalog + parameters |
| `GET /optimize?scenario=&objective=&budget_scale=&mga=&dv_margin=&power_margin=&w_mass=&w_cost=&w_science=` | exact optimum (objective: `balanced`, `min_mass`, `min_cost`, `min_propellant`, `min_power`, `max_science`, `max_payload`, `max_link_margin`, `max_feasibility_margin`) |
| `GET /pareto?scenario=` | Pareto front (mass, cost, science) |
| `POST /simulate` | Monte Carlo success rate for a design `{scenario, design, samples, seed}` |
| `POST /delta-v` | rocket equation |

## Data map
| Folder | Contents |
|---|---|
| `space-mission-research/celestial` | Sun, 8 planets, 3 dwarf planets, 11 moons, 2 asteroids, elements, atmospheres |
| `…/propulsion`, `…/launch` | 24 engines/thrusters, propellants, 16 launch vehicles, stages, boosters, payload capabilities |
| `…/spacecraft`, `…/instruments`, `…/missions` | component classes, 16 instruments, 14 historical missions, 8 ground stations, scenarios, 80 constraints |
| `…/analysis`, `…/optimization` | Δv/power/comm analysis, 27 optimizer experiments, Pareto fronts, sensitivity, Monte Carlo, benchmarks |
| `…/launch_history` (in combined) | your 57-row SpaceX table (2010–2018) and 485 NASA facilities |
| `…/metadata`, `…/reports` | sources, provenance, quality, validation, verification, written reports |

## ⚠ Trust rules (read before you present)
* Each record has **`data_class`**: `verified` (compared with a retrieved source page — `field_verification` shows what and where), `derived`, `estimated`, `fictional` (credits, budgets, science weights), or `unverified` (recalled values).
* **Verified today:** 25 celestial bodies (core fields), 3 Saturn V stages, NEXT, NSTAR, BPT-4000, BE-4, plus individual fields of SLS, Atlas V, Vulcan, Vega-C, Ariane 62/64, RD-180, RS-25, F-1, J-2 and 11 mission launch dates. **Falcon, Starship, Electron and most engines/instruments/components are still unverified.** Say so on your slide.
* The optimizer's component catalog and **costs are estimated/fictional** — present results as trade-off teaching, not as hardware sizing. "Optimal" means optimal *within the catalog*.
* `null` means *not recorded* (never zero). Don't compare launch payloads across different orbits (`payload_capabilities` lists the conditions).
* Keep `data_class` visible in your UI or demo.

## Project ideas that fit the data
* **Mission planner:** pick Moon/Mars, then show launch vehicle + engine + instruments from *Mission fit* ([`docs/advisor.js`](docs/advisor.js) works in Node) and the optimizer result with sliders.
* **Risk dashboard:** call `/simulate` while a user edits a design and show success rate + failure reasons.
* **Launch-history explorer:** reliability and landing success from the SpaceX table (era-limited, 2010–2018).
* **Verification dashboard:** `GET /verified` + `field_verification` provenance as a trust UI.
* **Education tool:** Hohmann/Δv/link-budget calculators (see `docs/app.js`) with real constants.

## Rebuild / extend
```bash
make setup      # pip install -r requirements.txt  (jsonschema, numpy)
make all        # build data → schemas → validate (82 checks) → API → exports → reports
make test       # parity tests + backend smoke test
make fetch      # re-download source pages (needs network access to JPL/NASA/ULA/ESA hosts)
make verify     # re-run verification against the cached pages, then `make all`
```
New data → add it to `tools/data_*.py` as `unverified`, add a parser in `tools/verify_*.py` if a retrievable source exists, rerun `make all`. `make validate` must stay green.

## FAQ
* **Which file is the source of truth?** `tools/data_*.py` (recalled values) + `space-mission-research/metadata/verification_*.json` (retrieved-source checks); everything else is generated.
* **Can I use the SpaceX / NASA-facility tables commercially?** Their origin/licence is unverified (user-supplied) — see [`LICENSE-DATA.md`](LICENSE-DATA.md).
* **Port 8000 busy?** `python3 tools/serve_api.py --port 8010`.
