# User guide — Space Mission Dataset

Website: https://kaungkhantko26.github.io/space-mission-dataset/ · Code and data: https://github.com/kaungkhantko26/space-mission-dataset

This project is the **data backend for the Space Mission Design Game**: a secondary-school game where players design a space mission and balance spacecraft, instruments, launch vehicle, budget, mass, power, communication and orbit. It is **not the game itself**. Everything is **verified**: each value was compared with, or ingested directly from, a retrieved source (NASA, JPL, NIST, ESA, ULA, or the Launch Library 2 aggregator, which is labelled).

## 1. Who are you? Pick your path

| I want to… | Go to |
|---|---|
| Look things up and compare (students, teachers) | [Use the website](#2-use-the-website) |
| Build the game or an app | [Use the API](#3-use-the-api-for-developers) |
| Use spreadsheets, pandas or SQL | [Download tables](#4-spreadsheets-pandas-and-sql) |
| Train or fine-tune a model | [Training data](#5-train-a-model) |
| Draw component pictures with an AI image tool | [Image prompts](#6-make-pictures-with-ai-image-tools) |
| Know what is trustworthy | [Trust and limits](#7-trust-rules-and-limits) |

## 2. Use the website
Open the site and use the tabs along the top.

| Tab | What it does |
|---|---|
| **Overview** | What is in the dataset and which game need each part serves |
| **Guide** | Short in-site help |
| **Explorer** | Search and filter any collection (planets, moons, engines, components…) and open a record to see its **source and verification** |
| **Compare** | Put two or more items side by side and see which is better for a mission |
| **Mission fit** | Pick a destination (LEO, GTO, Moon, Mars) and see which launchers and thrusters fit, with the reasoning |
| **Calculators** | Rocket equation (delta-v), Hohmann transfer, light time, power and link budget |
| **Launchers** | 532 launch vehicles: capacity, cost, launch record (launch pad coordinates are in the `launch_pads` collection, 202 pads) |
| **Components** | NASA small-spacecraft parts: thrusters, solar arrays, radios, antennas, reaction wheels… |
| **Missions & instruments** | 39 NASA missions and 181 instruments with NASA's descriptions |
| **API** | How to fetch the data from code |
| **Quality** | What was verified, what was corrected, what is missing |

Tips: click a column header to sort; every number can be traced to its source; an empty cell means *not verified* (never zero).

## 3. Use the API (for developers)
Base URL: `https://kaungkhantko26.github.io/space-mission-dataset/api/v1` — plain JSON files, no key, CORS open.

```bash
curl https://kaungkhantko26.github.io/space-mission-dataset/api/v1/index.json
curl https://kaungkhantko26.github.io/space-mission-dataset/api/v1/planets/mars.json
curl https://kaungkhantko26.github.io/space-mission-dataset/api/v1/electric_propulsion.json
```

JavaScript:
```js
const api = new SpaceMissionAPI("https://kaungkhantko26.github.io/space-mission-dataset/api/v1");
const mars = await api.get("planets", "mars");
const launchers = await api.list("launch_vehicle_configs");
```

For filtering, sorting, Hohmann and delta-v endpoints, run the local backend (Python 3.10+, nothing to install):
```bash
git clone https://github.com/kaungkhantko26/space-mission-dataset
cd space-mission-dataset
python3 tools/serve_api.py
```
```bash
curl "localhost:8000/collections/launch_vehicle_configs?active=true&leo_capacity_kg_gte=15000&sort=-leo_capacity_kg&limit=5"
curl -X POST localhost:8000/hohmann -d '{"body":"earth","altitude1_km":400,"altitude2_km":35786}'
curl "localhost:8000/light-time?target=mars"
```
Full reference: [`docs/api.html`](https://kaungkhantko26.github.io/space-mission-dataset/api.html) and `api/v1/openapi.json`. Examples: `examples/python_quickstart.py`, `examples/node_quickstart.mjs`.

## 4. Spreadsheets, pandas and SQL
After `git clone`, the folder `exports/` holds one CSV per collection and `space_mission.sqlite`.
```python
import pandas as pd
lv = pd.read_csv("exports/csv/launch_vehicle_configs.csv")
print(lv[lv.active == True].sort_values("leo_capacity_kg", ascending=False).head())
```
One combined JSON: `verified/combined/verified_space_mission_data.json`. Every record has `data_class`, `source_ids` and verification details.

## 5. Train a model
Ready-made files are in `training/` (each folder has a card explaining it):

| Folder | Use |
|---|---|
| `training/` (`qa_pairs.jsonl`, `physics_examples.jsonl`) | Fact Q&A and physics-calculation examples in chat format |
| `training/design/` | What parts fit together, and why a designed mission **succeeds or fails** (reason codes, delta-v, power, link margin, mass, budget, duration) |
| `training/trajectories/` | Earth → Moon/planet paths, transfer time, delta-v, launch-window spacing |
| `training/reliability/` | Real launch **success/failure** history for all providers (see its RELIABILITY_CARD.md): failure causes, reliability by rocket, provider, year and rocket age, baseline scores |

Chat files use `{"messages":[{"role":"user",...},{"role":"assistant",...}]}` and a `split` field (`train`/`val`/`test`). Read the **limits** in each card before training (the design labels are produced by documented game rules, not observed missions).

## 6. Make pictures with AI image tools
`training/image_prompts.csv` has one row per component (launchers, thrusters, solar arrays, radios, antennas, instruments) and per destination (planets and moons). Copy the `prompt` and `negative_prompt` columns into your image generator; keep `id` to join with `training/design/components_catalog.csv`. Prompts describe the *type* and *size* of each part without brand names, so images are illustrative, not exact pictures of a product.

## 7. Trust rules and limits
1. Look at `data_class`: `verified` (checked against a source) or `derived` (computed from verified inputs).
2. `source_authority` tells you who said it: official NASA/JPL/NIST/ESA/ULA documents, **vendor-reported** (NASA's small-spacecraft report), or **aggregator** (Launch Library 2).
3. A missing value means *unknown*. Never fill it with zero.
4. Not in the data (no retrievable source): real component prices (budgets per component are **estimates** anchored to NASA-stated mission development costs; launch prices are real), structured instrument mass/power/data rate, storable propellants (RP-1, hydrazine…), reference orbits for launcher capacities, calendar launch dates.
5. Mission success/failure labels in `training/design/` come from a rule engine (`rules.json`) using real physics and documented teaching assumptions, not from real missions. Real launch outcomes are in `training/reliability/`.
6. Licences: code MIT; compiled data CC BY 4.0 with third-party credits in `LICENSE-DATA.md`. Check Launch Library 2's terms before commercial use. NASA does not endorse this project.

## 8. Rebuild or extend
```bash
make all      # rebuild verified data, validate, API, exports, training files
make test     # backend checks
```
To add data, keep the raw source in `data_raw/retrieved/`, add a parser in `tools/`, and make sure validation passes. Unverified data must not enter `verified/`.

## 9. Help
* Port busy → `python3 tools/serve_api.py --port 8010`.
* Something looks wrong → open the record in the Explorer and read its source; report issues on GitHub.
