# Research summary
> **Read first:** 32 records are verified (25 celestial bodies at core level; engines and stages whose core numeric fields were all checked) against retrieved JPL, NASA (NTRS, SLS page, Apollo 11 press kit), ULA and ESA pages. 198 celestial and 44 launch/engine field checks matched; 16 celestial and 13 launch/engine recalled values were wrong or outdated and were replaced by the sourced value. Launch vehicles are verified field by field only (see verified_field_count); everything not checked (e.g. Falcon, Starship, Electron, Ariane, most engines, spacecraft components, instruments, missions) is still unverified, as are two user-supplied tables. Derived values inherit the status of their inputs. Optimization catalog values are estimated/fictional. Not retrieved: Retrieved: JPL SSD planetary/satellite physical parameters, JPL approximate planet elements, JPL SBDB API, NASA NSSDC fact sheets, NASA SLS page, NASA Apollo 11 press kit and three NTRS electric-propulsion documents, ULA Atlas V/Vulcan pages and the ESA Vega-C page (see metadata/sources.json). Not retrievable or not stating the numbers: SpaceX pages (JavaScript-rendered), api.spacexdata.com (HTTP 522), Rocket Lab, Aerojet Rocketdyne (403), Blue Origin (429), Arianespace manual; those records remain unverified.


## Dataset overview
| Category | Records | Target | Attainment |
|---|---:|---:|---:|
| celestial bodies | 25 | 40 | 62.5% |
| engines and propulsion | 24 | 40 | 60.0% |
| launch vehicles | 16 | 20 | 80.0% |
| stages and boosters | 12 | 40 | 30.0% |
| spacecraft components | 23 | 100 | 23.0% |
| instruments | 16 | 50 | 32.0% |
| historical missions | 14 | 30 | 46.7% |
| spacex launch records | 57 | n/a (external data) | n/a |
| nasa facilities | 485 | n/a (external data) | n/a |
| nasa antenna facilities | 28 | n/a (external data) | n/a |
| launch sites | 3 | n/a (external data) | n/a |
| ground comm systems | 10 | 15 | 66.7% |
| engineering constraints | 80 | 50 | 160.0% |
| optimization examples | 27 | 20 | 135.0% |

Targets are goals from the brief, not quotas; no records were invented to reach them. Where attainment is low the shortfall is real.

* Verified records: **32** · Data classes: verified=32, unverified=631, estimated=20
* Sources listed: 47 · retrieved: **13**
* Automated validation: **82/82** checks pass (`metadata/validation_report.json`). Checks compare internal consistency and recompute textbook values (e.g. LEO→GEO Hohmann Δv, Earth escape velocity); they do **not** compare against retrieved authoritative data.

## Engineering findings (all derived from unverified inputs)
* **Δv anchors:** 400 km LEO circular speed 7,673 m/s; LEO→GEO Hohmann 3,857 m/s (+1,514 m/s if a 28.5° plane change is done at GEO); LEO→100 km lunar orbit ≈ 3,905 m/s; Earth→Mars Hohmann v∞ 2,945 m/s, C3 8.7 km²/s², transfer 259 d, window every 780 d.
* **Mass:** propellant dominates launch mass; an ideal Δv of 4 km/s needs 73% of initial mass as propellant with a 310 s bipropellant system and 23% at 1600 s (Hall) — but electric thrust is milli-newtons and needs kW of power.
* **Power:** solar flux falls with distance² (586 W/m² at Mars vs 50.3 at Jupiter). Using 80 W/kg array specific power at 1 AU, array specific power drops below MMRTG (2.4 W/kg) near 5.7 AU and below GPHS-RTG (5.4 W/kg) near 3.9 AU (indicative only; see caveat in the file).
* **Communications:** one-way light time to Mars ranges 3.1–22.2 min. At Mars max range, X-band, a 3 m dish at 100 W to a 34 m-class station supports ≈ 559 kbit/s versus ≈ 12 kbit/s for a 1 m dish at 20 W (assumed G/T 53 dB/K).
* **Scenario contrast (not a monotonic complexity scale):** onboard Δv 150 (LEO) vs 4,005 (lunar, onboard TLI+LOI) vs 1,064 m/s (Mars; the launcher supplies departure, so onboard Δv is only capture + ops). Feasible fraction of the enumerated catalog: 1.1% / 3.8% / 0.8%; Mars is the tightest because deep-space link rate and radiation tolerance remove most options.

## Where to read more
`ENGINEERING_ANALYSIS.md`, `OPTIMIZATION_REPORT.md`, `DATA_LIMITATIONS.md`; machine-readable results under `analysis/` and `optimization/`; web explorer in `docs/`.

## File locations
Datasets: `celestial/`, `propulsion/`, `launch/`, `spacecraft/`, `instruments/`, `missions/`; analysis: `analysis/`; optimization: `optimization/`; metadata and schemas: `metadata/`, `schemas/`; combined: `combined/all_space_mission_data.json`.
