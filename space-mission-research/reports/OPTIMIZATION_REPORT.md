# Optimization report
> **Read first:** 25 celestial records (Sun, planets, dwarf planets, moons, small bodies) have their core physical fields verified against retrieved JPL/NASA pages (198 field checks matched; 16 conflicts were resolved to the sourced value). Six SLS/RS-25 launch figures were also verified against the NASA SLS page; all other launch-vehicle, engine, spacecraft, instrument and mission figures are still unverified (recalled values), as are two user-supplied tables (SpaceX launches 2010-2018, NASA facilities). Derived values inherit the status of their inputs. Optimization catalog values are estimated/fictional. Not retrieved: other launch-vehicle, engine, spacecraft-component, instrument and mission sources (spacex.com and api.spacexdata.com unreachable; others not attempted); those records remain unverified.


## Model
Discrete design selection (instrument subset, computer, comm system, array, battery, propulsion, launch vehicle) with analytic sizing of array, battery, propellant, tank and structure; mass growth allowance 20%; Δv margin 5%; power margin 15%; launch-capacity margin 10%. Full equations: `optimization/optimization_models.json`.

**Solver:** exhaustive enumeration (deterministic; ties broken by cost, mass, design string). Because the equations are nonlinear (exponential rocket equation, logarithmic link budget) and the catalog is small, enumeration gives exact optima *within the catalog* and the full Pareto set without solver assumptions; LP/MILP/NSGA-style methods were deliberately not used. "Optimal" here never means globally optimal over all possible spacecraft. The browser optimizer (`docs/model.js`) reproduces all 27 stored results (`tools/parity_check.js`).

**Fictional inputs:** costs are synthetic credits (launch costs derive from published USD only where marked), instrument science weights are educational weights, and most catalog masses/powers are class-level estimates. Reliability is **not optimized**: no evidence-based reliability data were collected.

## Results: 27 experiments (3 scenarios × 9 formulations)
| Scenario | Objective | Mass kg | Cost cr | Science | Avg W | Link dB | Prop / comm / vehicle |
|---|---|---:|---:|---:|---:|---:|---|
| leo_eo | min_mass | 52.9 | 8,150 | 12.0 | 30.0 | 51.6 | mono_n2h4 / hga1_x_20w / electron |
| leo_eo | min_cost | 54.0 | 6,994 | 12.0 | 30.0 | 51.6 | mono_n2h4 / hga1_x_20w / electron |
| leo_eo | min_propellant | 58.4 | 9,978 | 12.0 | 30.0 | 51.6 | bi_mmh_nto / hga1_x_20w / electron |
| leo_eo | min_power | 54.0 | 6,994 | 12.0 | 30.0 | 51.6 | mono_n2h4 / hga1_x_20w / electron |
| leo_eo | max_science | 74.5 | 9,525 | 18.0 | 35.0 | 50.0 | mono_n2h4 / hga1_x_20w / electron |
| leo_eo | max_payload | 74.5 | 9,525 | 18.0 | 35.0 | 50.0 | mono_n2h4 / hga1_x_20w / electron |
| leo_eo | max_link_margin | 79.7 | 11,957 | 12.0 | 37.6 | 68.2 | mono_n2h4 / hga3_x_100w / electron |
| leo_eo | max_feasibility_margin | 71.7 | 8,904 | 15.0 | 32.0 | 50.0 | mono_n2h4 / hga1_x_20w / electron |
| leo_eo | balanced | 72.4 | 9,084 | 16.0 | 33.5 | 50.0 | mono_n2h4 / hga1_x_20w / electron |
| lunar_orbiter | min_mass | 512.5 | 25,113 | 15.0 | 80.1 | 28.4 | bi_mmh_nto / patch_s_5w / f9_class |
| lunar_orbiter | min_cost | 1,170.8 | 20,951 | 15.0 | 80.1 | 28.4 | mono_n2h4 / patch_s_5w / f9_class |
| lunar_orbiter | min_propellant | 512.5 | 25,113 | 15.0 | 80.1 | 28.4 | bi_mmh_nto / patch_s_5w / f9_class |
| lunar_orbiter | min_power | 1,170.8 | 20,951 | 15.0 | 80.1 | 28.4 | mono_n2h4 / patch_s_5w / f9_class |
| lunar_orbiter | max_science | 1,830.3 | 29,714 | 24.0 | 117.6 | 37.7 | mono_n2h4 / hga1_x_20w / f9_class |
| lunar_orbiter | max_payload | 1,747.4 | 27,238 | 22.0 | 114.3 | 28.0 | mono_n2h4 / patch_s_5w / f9_class |
| lunar_orbiter | max_link_margin | 1,695.4 | 29,979 | 15.0 | 170.6 | 76.6 | mono_n2h4 / hga3_x_100w / f9_class |
| lunar_orbiter | max_feasibility_margin | 1,425.6 | 24,673 | 18.0 | 96.2 | 37.7 | mono_n2h4 / hga1_x_20w / f9_class |
| lunar_orbiter | balanced | 673.2 | 27,595 | 23.0 | 98.4 | 37.7 | bi_mmh_nto / hga1_x_20w / f9_class |
| mars_orbiter | min_mass | 346.8 | 55,997 | 20.0 | 245.2 | 4.6 | bi_mmh_nto / hga3_x_100w / falcon_heavy |
| mars_orbiter | min_cost | 415.6 | 48,493 | 20.0 | 245.2 | 4.6 | mono_n2h4 / hga3_x_100w / falcon_heavy |
| mars_orbiter | min_propellant | 346.8 | 55,997 | 20.0 | 245.2 | 4.6 | bi_mmh_nto / hga3_x_100w / falcon_heavy |
| mars_orbiter | min_power | 546.8 | 53,799 | 22.3 | 241.3 | 2.9 | mono_n2h4 / hga3_x_100w / falcon_heavy |
| mars_orbiter | max_science | 546.8 | 53,799 | 22.3 | 241.3 | 2.9 | mono_n2h4 / hga3_x_100w / falcon_heavy |
| mars_orbiter | max_payload | 546.8 | 53,799 | 22.3 | 241.3 | 2.9 | mono_n2h4 / hga3_x_100w / falcon_heavy |
| mars_orbiter | max_link_margin | 415.6 | 48,493 | 20.0 | 245.2 | 4.6 | mono_n2h4 / hga3_x_100w / falcon_heavy |
| mars_orbiter | max_feasibility_margin | 546.8 | 53,799 | 22.3 | 241.3 | 2.9 | mono_n2h4 / hga3_x_100w / falcon_heavy |
| mars_orbiter | balanced | 400.0 | 51,545 | 21.0 | 242.2 | 4.6 | bi_mmh_nto / hga3_x_100w / falcon_heavy |

## Pareto fronts (mass ↓, cost ↓, science ↑)
| Scenario | Front size | Mass range kg | Cost range cr | Science range |
|---|---:|---|---|---|
| leo_eo | 12 | 53–74 | 6,994–10,874 | 12–18 |
| lunar_orbiter | 16 | 513–1,830 | 20,951–29,714 | 15–24 |
| mars_orbiter | 9 | 347–547 | 48,493–61,187 | 20–22 |

## Largest sensitivities (one-at-a-time, re-optimized)
| Scenario | Perturbation | Feasible designs | Δ min mass % | Δ min cost % | Δ max science % |
|---|---|---|---:|---:|---:|
| leo_eo | mga = 0.3 | 258 (base 258) | 8.3 | 0.0 | 0.0 |
| leo_eo | mga = 0.1 | 258 (base 258) | -8.3 | -0.0 | 0.0 |
| leo_eo | power_margin = 0.25 | 244 (base 258) | 0.2 | 1.0 | 0.0 |
| leo_eo | power_margin = 0.05 | 269 (base 258) | -0.2 | -1.0 | 0.0 |
| lunar_orbiter | budget_scale = 0.8 | 17 (base 574) | 2.8 | 0.0 | -29.2 |
| lunar_orbiter | dv_scale = 1.1 | 429 (base 574) | 25.4 | 3.9 | -4.2 |
| lunar_orbiter | budget_scale = 1.2 | 2303 (base 574) | 0.0 | 0.0 | 25.0 |
| lunar_orbiter | dv_scale = 0.9 | 652 (base 574) | -18.9 | -2.1 | 0.0 |
| mars_orbiter | gt_shift_db = -3 | 0 (base 64) | — | — | — |
| mars_orbiter | distance_scale = 1.5 | 0 (base 64) | — | — | — |
| mars_orbiter | distance_scale = 0.5 | 528 (base 64) | -4.3 | -6.9 | 70.1 |
| mars_orbiter | gt_shift_db = 3 | 496 (base 64) | 0.0 | 0.0 | 43.2 |

Budget and Δv dominate; ground G/T and link distance barely move results in the lunar/LEO scenarios because the downlink rate cap (not link margin) binds there — a model-structure finding, not a statement about real missions.

## Monte Carlo (seed 20261106, 2000 samples; assumed distributions)
| Scenario | Design | P(feasible) | Mass p95 kg | Cost p95 cr | Failure counts |
|---|---|---:|---:|---:|---|
| leo_eo | balanced | 97.2% | 81 | 11,797 | {'exceeds_budget': 55} |
| leo_eo | max_science | 91.2% | 83 | 12,327 | {'exceeds_budget': 175} |
| leo_eo | max_feasibility_margin | 97.9% | 80 | 11,634 | {'exceeds_budget': 43} |
| lunar_orbiter | balanced | 48.9% | 857 | 35,969 | {'exceeds_budget': 1021} |
| lunar_orbiter | max_science | 20.7% | 2,853 | 39,118 | {'exceeds_budget': 1586} |
| lunar_orbiter | max_feasibility_margin | 82.5% | 2,210 | 32,334 | {'exceeds_budget': 351} |
| mars_orbiter | balanced | 87.6% | 452 | 66,946 | {'science_below_minimum': 248} |
| mars_orbiter | max_science | 59.8% | 622 | 69,954 | {'science_below_minimum': 804} |
| mars_orbiter | max_feasibility_margin | 62.8% | 623 | 69,589 | {'science_below_minimum': 744} |

Designs that max out science or sit near a budget limit have much lower P(feasible) than designs chosen for worst-case margin; this quantifies why `max_feasibility_margin` exists. Cost-growth distribution is an assumption.

## Bottlenecks and data needs
* Better source data needed for: instrument data rates and duty cycles, real component masses/powers/costs, launch prices, radiation environments, thermal limits (not modeled).
* Model omissions: thermal balance, reliability/redundancy, fairing volume, trajectory timing, peak power coincidence (see `not_modeled`).
