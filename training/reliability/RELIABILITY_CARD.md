# Real launch success / failure data (all providers)

Source: **Launch Library 2** (The Space Devs; aggregator, labelled) — every past launch, ingested as the verified collection `launch_history_all`. 7,657 launches, 1957-10-04 to 2026-11-07: 7,100 successes, 523 failures, 34 partial failures. Cross-checked against the Kaggle file *All Space Missions from 1957*: of 3,057 launches matched by date and vehicle, 97.6% have the same outcome (`kaggle_crosscheck.json`). Built by `python3 tools/make_reliability.py`, checked by `tools/validate_reliability.py`.

| File | Content |
|---|---|
| `launch_outcomes_all.csv` | One row per launch: `outcome` (success / failure / partial_failure), `success` 0/1, provider, country, vehicle, family, orbit, mission type, pad, and **leak-free history features** (earlier launches and failures of the same vehicle, family and provider, smoothed prior failure rate, family age). Chronological 70/15/15 split |
| `failure_reasons.csv` | Every failed or partially failed launch with the source's failure text and a keyword-derived `cause_category` (engine/propulsion, stage separation/fairing, guidance/control/software, structure, upper stage/insertion, not stated, other) |
| `reliability_by_vehicle/family/provider/country/year/orbit/mission_type.csv` | Launches, successes, failures, partial failures, success rate and Wilson 95% interval; `low_sample_warning` when fewer than 20 launches |
| `maturity_curve.csv` | Success rate by launch number within a rocket family (young rockets fail more) |
| `reliability_qa.jsonl` | Chat Q&A from the tables |
| `baseline_report.json` | Scores of simple predictors on the test split (Brier, AUC) — your model should beat these |
| `kaggle_crosscheck.json` | How well Launch Library agrees with the Kaggle file (statistics only; Kaggle rows are not redistributed) |

## How to use it for the game
* **Launch success probability of a chosen rocket:** `reliability_by_vehicle.csv` (use the interval, not just the rate, and fall back to `reliability_by_family.csv` for small samples).
* **Why launches fail:** `failure_reasons.csv` → pick a failure reason with probability proportional to its category share.
* **New vs mature rockets:** `maturity_curve.csv` or the features `prior_launches_*` / `family_age_days` for a classifier.

## Limits
* Failure is rare (a few % overall), so judge classifiers with AUC/Brier/precision-recall, not accuracy.
* `cause_category` is derived by keyword rules from short source text; about 77% of failures (429 of 557) have no stated cause in Launch Library, so cause statistics describe only the minority with text.
* Launch Library is an aggregator; check its terms before commercial use. Partial failures are kept separate and count as `success = 0`.
* Past reliability does not guarantee future results; rates are historical.
