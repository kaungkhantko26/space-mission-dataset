# Benchmark report
> **Read first:** 25 celestial records (Sun, planets, dwarf planets, moons, small bodies) have their core physical fields verified against retrieved JPL/NASA pages (198 field checks matched; 16 conflicts were resolved to the sourced value). Six SLS/RS-25 launch figures were also verified against the NASA SLS page; all other launch-vehicle, engine, spacecraft, instrument and mission figures are still unverified (recalled values), as are two user-supplied tables (SpaceX launches 2010-2018, NASA facilities). Derived values inherit the status of their inputs. Optimization catalog values are estimated/fictional. Not retrieved: other launch-vehicle, engine, spacecraft-component, instrument and mission sources (spacex.com and api.spacexdata.com unreachable; others not attempted); those records remain unverified.


All timings are single runs on the build sandbox (Python 3.13.18, numpy 2.5.3); relative speedups are meaningful, absolute seconds are not. Reproduce: `python3 tools/benchmark.py`. Heuristic runs use seeds 0-19.

## 1. Exactness: vectorized solver vs scalar reference
| Scenario | Designs | Result (8 objectives) |
|---|---:|---|
| leo_eo | 22,680 | exact match |
| lunar_orbiter | 15,120 | exact match |
| mars_orbiter | 7,560 | exact match |

## 2. Speed (one full pass over every design)
| Scenario | Designs | Scalar Python (s) | Vectorized (s) | Speedup | JavaScript (s) |
|---|---:|---:|---:|---:|---:|
| leo_eo | 22,680 | 0.23 | 0.024 | 9x | 0.29 |
| lunar_orbiter | 15,120 | 0.33 | 0.017 | 20x | 0.08 |
| mars_orbiter | 7,560 | 0.07 | 0.012 | 6x | 0.08 |

## 3. Scaling with instrument count (lunar scenario, synthetic instrument clones, exact max-science)
| Instruments | Designs | Vectorized (s) | Scalar (s) | Optimum science |
|---|---:|---:|---:|---:|
| 6 | 15,120 | 0.03 | 0.20 | 24 |
| 8 | 61,200 | 0.03 | 0.96 | 33 |
| 10 | 245,520 | 0.03 | — | 40 |
| 12 | 982,800 | 0.08 | — | 46 |
| 14 | 3,931,920 | 0.32 | — | 51 |
| 16 | 15,728,400 | 1.16 | — | 56 |

The design space doubles per added instrument; the vectorized exact solver stays under ~1.2 s up to 15,728,400 designs. Clones are synthetic (perturbed copies) and used only to test scaling.

## 4. Heuristic solvers vs the exact optimum (2000 evaluations per run, 20 seeds)
"Found exact" = reached the exact optimum value; "feasible" = run ended on a feasible design; gap = median relative gap among feasible runs.

| Scenario | Objective | Solver | Found exact | Feasible | Median gap % |
|---|---|---|---:|---:|---:|
| leo_eo | max_science | random_search | 16/20 | 20/20 | 0.0 |
| leo_eo | max_science | hill_climb_restarts | 19/20 | 20/20 | 0.0 |
| leo_eo | max_science | genetic_algorithm | 20/20 | 20/20 | 0.0 |
| leo_eo | min_cost | random_search | 2/20 | 20/20 | 15.1 |
| leo_eo | min_cost | hill_climb_restarts | 4/20 | 20/20 | 18.1 |
| leo_eo | min_cost | genetic_algorithm | 14/20 | 20/20 | 0.0 |
| leo_eo | min_mass | random_search | 1/20 | 20/20 | 5.0 |
| leo_eo | min_mass | hill_climb_restarts | 4/20 | 20/20 | 19.2 |
| leo_eo | min_mass | genetic_algorithm | 15/20 | 20/20 | 0.0 |
| lunar_orbiter | max_science | random_search | 3/20 | 20/20 | 4.2 |
| lunar_orbiter | max_science | hill_climb_restarts | 1/20 | 20/20 | 4.2 |
| lunar_orbiter | max_science | genetic_algorithm | 7/20 | 20/20 | 4.2 |
| lunar_orbiter | min_cost | random_search | 2/20 | 20/20 | 9.9 |
| lunar_orbiter | min_cost | hill_climb_restarts | 17/20 | 20/20 | 0.0 |
| lunar_orbiter | min_cost | genetic_algorithm | 11/20 | 20/20 | 0.0 |
| lunar_orbiter | min_mass | random_search | 4/20 | 20/20 | 2.8 |
| lunar_orbiter | min_mass | hill_climb_restarts | 17/20 | 20/20 | 0.0 |
| lunar_orbiter | min_mass | genetic_algorithm | 10/20 | 20/20 | 2.3 |
| mars_orbiter | max_science | random_search | 19/20 | 20/20 | 0.0 |
| mars_orbiter | max_science | hill_climb_restarts | 5/20 | 13/20 | 6.0 |
| mars_orbiter | max_science | genetic_algorithm | 5/20 | 11/20 | 6.0 |
| mars_orbiter | min_cost | random_search | 4/20 | 20/20 | 1.5 |
| mars_orbiter | min_cost | hill_climb_restarts | 10/20 | 13/20 | 0.0 |
| mars_orbiter | min_cost | genetic_algorithm | 9/20 | 11/20 | 0.0 |
| mars_orbiter | min_mass | random_search | 2/20 | 20/20 | 2.0 |
| mars_orbiter | min_mass | hill_climb_restarts | 10/20 | 13/20 | 0.0 |
| mars_orbiter | min_mass | genetic_algorithm | 10/20 | 11/20 | 0.0 |

## Findings
* The vectorized solver reproduces every scalar optimum exactly (same design, same value) and is ~10-20x faster per pass; it makes exact search practical well beyond the current catalog.
* Heuristics are unreliable here: no solver finds the exact optimum in every run, and in the tightly constrained Mars scenario only ~55-65% of hill-climb/GA runs even end feasible. A genetic algorithm helps on LEO cost/mass but not uniformly.
* Practical rule: use exact enumeration while the space is below ~1e8 designs; consider NSGA-II / MILP only beyond that (not implemented or benchmarked here).

## Ways to get more optimization (ranked)
1. **Replace scalar enumeration by the vectorized exact solver** (done in `tools/vec_model.py`, validated above).
2. **Port the vectorized idea to the browser** (typed arrays/WebWorker) so the website can handle larger catalogs without freezing (not done).
3. **Dominance pruning** of catalog options (e.g. drop a battery/computer that is worse on every metric) before enumeration (not implemented).
4. **Real component data** (retrieval required) will change optima more than any solver improvement.
5. **Add reliability and thermal models** before declaring designs "balanced"; both are currently not modeled.
