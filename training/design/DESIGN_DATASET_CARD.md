# Mission-design dataset (what to attach, what not to, and why a mission succeeds or fails)

Built by `python3 tools/make_design_dataset.py`, checked by `tools/validate_design.py` (re-computes every label), rules in `tools/design_rules.py` and `rules.json`.

**Important — what the labels are.** No source publishes success/failure for player-designed missions, so labels come from a **rule engine**: real physics (rocket equation, Hohmann transfer, Friis link budget, solar irradiance, launch mass/cost) applied to **verified component specs**. Thresholds such as the 10% mass margin, 1.15 power margin, 5 W transmitter and 1-year burn limit are **teaching heuristics** (listed in `rules.json`), not real data. Label `data_class = derived`, `label_source = rule_engine`. Align the rules with your game's rules before training on them.

| File | Rows | Content |
|---|---:|---|
| `components_catalog.csv` | 308 | The parts: 64 launchers, 63 thrusters, 72 solar arrays, 37 radios, 54 antennas, 18 instruments, with verified specs + source ids |
| `designs.csv` | 6,000 | One design per row: chosen parts, computed mass / delta-v / power / link margin, `outcome`, `primary_reason`, `all_reasons`, `p_mission_success` |
| `design_chat.jsonl` | 6,000 | Chat format: "review this design" → check-by-check calculations, verdict, reasons, fixes |
| `compatibility_pairs.csv` | 3,018 | Pairwise "attach / do not attach" (radio↔antenna band, thruster↔array power, launcher↔payload mass) with reasons |
| `rules.json` | – | Every rule, threshold and its basis |
| `../image_prompts.csv` | 327 | One AI-image prompt per component and destination (see below) |

Reason codes: `MISSING_*`, `BUDGET_EXCEEDED`, `MASS_OVER_CAPACITY`, `LAUNCHER_NO_CAPACITY`, `DELTA_V_SHORT`, `THRUST_TOO_LOW`, `POWER_SHORT`, `BAND_MISMATCH`, `DATA_RATE_LOW`, `LINK_MARGIN_LOW`.
`p_mission_success` = the launcher's historical launch success rate (Launch Library) when every design check passes, otherwise 0.

`designs.csv` also has `transfer_days`, `total_mission_days` and `one_way_light_time_min` (from `../trajectories/`).

## Limits
* **Class balance is by design** (45% success / 55% failure, designs partly "repaired" toward feasibility). Real random designs almost always fail. Destinations are unbalanced: Mars successes are rare (14) because a small spacecraft rarely satisfies delta-v, thrust and link together — use more Mars data from your own generator if you need it.
* Not modelled: batteries/eclipse, thermal, attitude control, component prices (none are published — the budget covers the launch only), fairing size, radiation, launch windows. Mars/Moon/GTO use the launcher's LEO/GTO capacity as a conservative proxy (no source states Mars-transfer capacity).
* Units that were unknown are left empty, never zero. Components with missing power use a flagged heuristic load.
* Splits are by design id; components repeat across splits. For a strict held-out-component test, split on `launcher` or `thruster` yourself.

## Image generation
`training/image_prompts.csv` columns: `id, category, display_name, reference_item, key_specs, prompt, negative_prompt, aspect_ratio, note`. Paste `prompt` (and `negative_prompt`) into your image generator. Prompts describe the component **type and scale** only; they avoid brand names, so images are illustrative, not accurate pictures of the named product. `id` joins to `components_catalog.csv` (prefix `D_` = planet/moon destinations).
