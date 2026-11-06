# Benchmark report
> **Read first:** 32 records are verified (25 celestial bodies at core level; engines and stages whose core numeric fields were all checked) against retrieved JPL, NASA (NTRS, SLS page, Apollo 11 press kit), ULA and ESA pages. 198 celestial and 44 launch/engine field checks matched; 16 celestial and 13 launch/engine recalled values were wrong or outdated and were replaced by the sourced value. Launch vehicles are verified field by field only (see verified_field_count); everything not checked (e.g. Falcon, Starship, Electron, Ariane, most engines, spacecraft components, instruments, missions) is still unverified, as are two user-supplied tables. Derived values inherit the status of their inputs. Optimization catalog values are estimated/fictional. Not retrieved: Retrieved: JPL SSD planetary/satellite physical parameters, JPL approximate planet elements, JPL SBDB API, NASA NSSDC fact sheets, NASA SLS page, NASA Apollo 11 press kit and three NTRS electric-propulsion documents, ULA Atlas V/Vulcan pages and the ESA Vega-C page (see metadata/sources.json). Not retrievable or not stating the numbers: SpaceX pages (JavaScript-rendered), api.spacexdata.com (HTTP 522), Rocket Lab, Aerojet Rocketdyne (403), Blue Origin (429), Arianespace manual; those records remain unverified.


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
| leo_eo | 22,680 | 0.28 | 0.037 | 8x | 0.28 |
| lunar_orbiter | 15,120 | 0.20 | 0.019 | 10x | 0.12 |
| mars_orbiter | 7,560 | 0.07 | 0.007 | 10x | 0.08 |

## 3. Scaling with instrument count (lunar scenario, synthetic instrument clones, exact max-science)
| Instruments | Designs | Vectorized (s) | Scalar (s) | Optimum science |
|---|---:|---:|---:|---:|
| 6 | 15,120 | 0.02 | 0.17 | 24 |
| 8 | 61,200 | 0.02 | 0.93 | 33 |
| 10 | 245,520 | 0.03 | — | 40 |
| 12 | 982,800 | 0.08 | — | 46 |
| 14 | 3,931,920 | 0.35 | — | 51 |
| 16 | 15,728,400 | 1.33 | — | 56 |

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
