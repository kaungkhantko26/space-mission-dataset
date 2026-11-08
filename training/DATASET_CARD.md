# Training data card — Space Mission Design Game

Built by `python3 tools/make_training.py` (checked by `tools/validate_training.py`) **only from `verified/`**. Nothing is invented; every row traces to a verified record id. Counts and SHA-256 hashes are in `manifest.json`.

| File | Rows | Use | Split |
|---|---:|---|---|
| `qa_pairs.jsonl` | 3,151 | Fine-tune/evaluate a chat model on space-mission facts. `messages` is the standard chat format; `value`, `unit`, `source_collection`, `source_id`, `field` give the machine-checkable answer. | by hash of source record id (train 80% / val 10% / test 10%), so a record never appears in two splits |
| `physics_examples.jsonl` | 110 | Hohmann-transfer delta-v/time around every verified planet and moon, and rocket-equation delta-v for verified engines. `data_class: derived` (exact formulas on verified GM, radius and Isp). `inputs`/`outputs` are numeric for tool-use or regression. | by body/engine |
| `launch_outcome.csv` | 743 | Binary classification: launch `success` (1) vs failure (0) from vehicle, mission type, orbit, pad, year, prior launches. | **chronological** 75/12.5/12.5 (no future leakage) |
| `launcher_specs.csv` | 532 | Regression/lookup: cost, LEO/GTO capacity, thrust, success rate, $/kg from vehicle dimensions and mass. Many cells are empty (not published) — do not zero-fill. | by hash of id |
| `component_numeric.csv` | 2,544 | Long table of vendor-reported component quantities (thruster Isp/thrust, radio data rate, array power…). | by hash of record id |

## Load it
```python
import json
rows = [json.loads(l) for l in open("training/qa_pairs.jsonl")]
train = [r["messages"] for r in rows if r["split"] == "train"]   # feed to your fine-tuning tool
```
```python
import pandas as pd
d = pd.read_csv("training/launch_outcome.csv"); tr, te = d[d.split=="train"], d[d.split=="test"]
```

## Honest limits (read before training)
* **Small:** ~3k Q&A pairs. Good for grounding/fine-tuning a small model or testing retrieval; **not** enough to pre-train. Prefer giving your model the data through retrieval/tool calls (`verified/`, API) and use these files for fine-tuning style and evaluation.
* **Templated questions:** the wording is limited; paraphrase or augment if you need variety (keep the `value` as the ground truth).
* **Launch outcome is highly imbalanced:** 15 failures in 743 launches (SpaceX only). Report precision/recall and use class weights; accuracy alone is meaningless (98% by always guessing success).
* **No mission-success labels:** no source gives real success scores for player-designed missions, and inventing them would break the verified-only rule. If your game needs those, generate them from your own game rules/simulator and label them as game-generated.
* **Sources:** Launch Library 2 (aggregator; check its terms before commercial use), NASA SoA report (vendor-reported), NASA/JPL/NIST. See `LICENSE-DATA.md`.
