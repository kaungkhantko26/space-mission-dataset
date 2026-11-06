#!/usr/bin/env python3
"""Generates reports/*.md from the built JSON so numbers cannot drift from the data."""
import json, os
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","space-mission-research")
L=lambda p: json.load(open(os.path.join(R,p)))
Q=L("metadata/quality_report.json"); J_MAN=json.load(open(os.path.join(R,"..","data_raw","retrieved","MANIFEST.json"))); V=L("metadata/validation_report.json"); comb=L("combined/all_space_mission_data.json")
prop=L("analysis/propulsion_analysis.json"); mass=L("analysis/mass_analysis.json"); pw=L("analysis/power_analysis.json"); cm=L("analysis/communication_analysis.json")
traj={t["id"]:t for t in L("missions/trajectory_reference.json")["records"]}
ex=L("optimization/optimized_configurations.json")["records"]; par=L("optimization/pareto_frontiers.json")["results"]
sens=L("optimization/sensitivity_results.json")["results"]; mc=L("analysis/uncertainty_analysis.json")["results"]; feas=L("analysis/feasibility_analysis.json")["scenarios"]
f=lambda x,d=0: "—" if x is None else f"{x:,.{d}f}"
os.makedirs(R+"/reports",exist_ok=True)
W=lambda n,t: open(f"{R}/reports/{n}","w").write(t)
BANNER="> **Read first:** "+Q["statement"]+" Not retrieved: "+Q["retrieval"]["reason"].split("Not retrieved:")[-1].strip()+"\n\n"
# ---- RESEARCH_SUMMARY
c=Q["record_counts"]; t=Q["targets"]
rows="\n".join(f"| {k.replace('_',' ')} | {c[k]} | {t.get(k,'n/a (external data)')} | {str(Q['target_attainment_pct'].get(k,'n/a'))+'%' if k in t else 'n/a'} |" for k in c)
W("RESEARCH_SUMMARY.md",f"""# Research summary
{BANNER}
## Dataset overview
| Category | Records | Target | Attainment |
|---|---:|---:|---:|
{rows}

Targets are goals from the brief, not quotas; no records were invented to reach them. Where attainment is low the shortfall is real.

* Verified records: **{Q['verified_records']}** · Data classes: {", ".join(f"{k}={v}" for k,v in Q['data_class_counts'].items())}
* Sources listed: {Q['retrieval']['sources_listed']} · retrieved: **{Q['retrieval']['sources_retrieved']}**
* Automated validation: **{V['passed']}/{V['total']}** checks pass (`metadata/validation_report.json`). Checks compare internal consistency and recompute textbook values (e.g. LEO→GEO Hohmann Δv, Earth escape velocity); they do **not** compare against retrieved authoritative data.

## Engineering findings (all derived from unverified inputs)
* **Δv anchors:** 400 km LEO circular speed {f(traj['leo400_circular']['velocity_m_s'])} m/s; LEO→GEO Hohmann {f(traj['leo400_to_geo_hohmann']['total_m_s'])} m/s (+{f(traj['plane_change_28p5_at_geo']['dv_m_s'])} m/s if a 28.5° plane change is done at GEO); LEO→100 km lunar orbit ≈ {f(traj['leo400_to_moon_100km']['total_m_s'])} m/s; Earth→Mars Hohmann v∞ {f(traj['earth_to_mars_hohmann']['v_infinity_departure_m_s'])} m/s, C3 {f(traj['earth_to_mars_hohmann']['c3_km2_s2'],1)} km²/s², transfer {f(traj['earth_to_mars_hohmann']['transfer_time_days'])} d, window every {f(traj['earth_to_mars_hohmann']['synodic_period_days'])} d.
* **Mass:** propellant dominates launch mass; an ideal Δv of 4 km/s needs {f(100*prop['propellant_fraction_examples'][[ (e['delta_v_m_s'],e['system']) for e in prop['propellant_fraction_examples']].index((4000,'biprop 310 s'))]['propellant_fraction_of_initial'],0)}% of initial mass as propellant with a 310 s bipropellant system and {f(100*prop['propellant_fraction_examples'][[ (e['delta_v_m_s'],e['system']) for e in prop['propellant_fraction_examples']].index((4000,'Hall 1600 s'))]['propellant_fraction_of_initial'],0)}% at 1600 s (Hall) — but electric thrust is milli-newtons and needs kW of power.
* **Power:** solar flux falls with distance² ({f(pw['solar_flux'][3]['flux_w_m2'])} W/m² at Mars vs {f(pw['solar_flux'][4]['flux_w_m2'],1)} at Jupiter). Using 80 W/kg array specific power at 1 AU, array specific power drops below MMRTG ({f(pw['crossover']['mmrtg_w_per_kg'],1)} W/kg) near {f(pw['crossover']['distance_au_mmrtg'],1)} AU and below GPHS-RTG ({f(pw['crossover']['gphs_rtg_w_per_kg'],1)} W/kg) near {f(pw['crossover']['distance_au_gphs'],1)} AU (indicative only; see caveat in the file).
* **Communications:** one-way light time to Mars ranges {f(cm['light_time'][1]['one_way_s']/60,1)}–{f(cm['light_time'][2]['one_way_s']/60,1)} min. At Mars max range, X-band, a 3 m dish at 100 W to a 34 m-class station supports ≈ {f([x for x in cm['link_budget_examples'] if x['target']=='Mars max' and x['spacecraft_dish_m']==3.0][0]['max_data_rate_bps_with_3db_margin']/1e3)} kbit/s versus ≈ {f([x for x in cm['link_budget_examples'] if x['target']=='Mars max' and x['spacecraft_dish_m']==1.0][0]['max_data_rate_bps_with_3db_margin']/1e3)} kbit/s for a 1 m dish at 20 W (assumed G/T 53 dB/K).
* **Scenario contrast (not a monotonic complexity scale):** onboard Δv {f(feas[0]['delta_v_m_s'])} (LEO) vs {f(feas[1]['delta_v_m_s'])} (lunar, onboard TLI+LOI) vs {f(feas[2]['delta_v_m_s'])} m/s (Mars; the launcher supplies departure, so onboard Δv is only capture + ops). Feasible fraction of the enumerated catalog: {f(100*feas[0]['feasible_fraction'],1)}% / {f(100*feas[1]['feasible_fraction'],1)}% / {f(100*feas[2]['feasible_fraction'],1)}%; Mars is the tightest because deep-space link rate and radiation tolerance remove most options.

## Where to read more
`ENGINEERING_ANALYSIS.md`, `OPTIMIZATION_REPORT.md`, `DATA_LIMITATIONS.md`; machine-readable results under `analysis/` and `optimization/`; web explorer in `docs/`.

## File locations
Datasets: `celestial/`, `propulsion/`, `launch/`, `spacecraft/`, `instruments/`, `missions/`; analysis: `analysis/`; optimization: `optimization/`; metadata and schemas: `metadata/`, `schemas/`; combined: `combined/all_space_mission_data.json`.
""")
# ---- ENGINEERING_ANALYSIS
sv="\n".join(f"| {s['vehicle_id']} | {f(s['total_ideal_dv_low_m_s'])} | {f(s['total_ideal_dv_high_m_s'])} |" for s in prop["stack_ideal_delta_v"])
ma="\n".join(f"| {s['vehicle_id']} | {f(s['liftoff_mass_kg'])} | {f(s['sum_of_recorded_stage_masses_kg'])} | {f(s['residual_kg'])} |" for s in mass["vehicle_stack_accounting"])
mm="\n".join(f"| {s['mission_id']} | {f(s['launch_mass_kg'])} | {f(s['dry_mass_kg'])} | {f(100*s['propellant_fraction'],1)}% |" for s in mass["mission_mass_fractions"])
tr="\n".join(f"| {k.replace('earth_to_','').replace('_hohmann','')} | {f(v['v_infinity_departure_m_s'])} | {f(v['departure_dv_from_400km_leo_m_s'])} | {f(v['capture_dv_to_400km_circular_m_s'])} | {f(v['transfer_time_days'])} | {f(v['synodic_period_days'])} |" for k,v in traj.items() if k.startswith("earth_to_"))
W("ENGINEERING_ANALYSIS.md",f"""# Engineering analysis
{BANNER}
Methods: two-body/patched-conic orbital mechanics, Tsiolkovsky rocket equation, Friis link budget, inverse-square solar flux (`tools/astro.py`). All approximations are idealizations (impulsive burns, circular coplanar orbits, no losses) and are labelled as such in the JSON.

## Stack ideal Δv (Tsiolkovsky)
Ideal Δv ignores gravity, drag and steering losses, so it must not be read as orbital insertion capability (real ascent to LEO needs roughly 9.3–9.5 km/s including losses — a commonly cited range, not retrieved here).

| Vehicle | Ideal Δv, low (m/s) | Ideal Δv, high (m/s) |
|---|---:|---:|
{sv}

**Do not trust these rows without the accounting check below.** *Electron*'s recorded stage masses sum exactly to its liftoff mass (no payload/fairing room), so its ≈12 km/s figure is an overestimate and flags inconsistent inputs. *SLS* is core-stage-only (boosters not modeled) so its total is not a vehicle capability.

## Mass accounting check (liftoff − Σ recorded stage masses)
| Vehicle | Liftoff (kg) | Σ stages (kg) | Residual (kg) |
|---|---:|---:|---:|
{ma}

Residual should equal payload + fairing + interstages (+ boosters). Falcon 9's 31 t residual exceeds payload+fairing implied by its own payload record, so at least one input is likely wrong — retrieval needed.

## Historical mission mass fractions
| Mission | Launch (kg) | Dry (kg) | Non-dry fraction |
|---|---:|---:|---:|
{mm}

## Interplanetary reference (circular, coplanar Hohmann; 400 km parking/capture orbits)
| Target | v∞ dep. (m/s) | Departure Δv from LEO (m/s) | Capture Δv to 400 km circular (m/s) | Transfer (d) | Synodic (d) |
|---|---:|---:|---:|---:|---:|
{tr}

Outer-planet capture into low circular orbit is unrealistically expensive; real missions capture into highly elliptical orbits or aerobrake. Real transfers use gravity assists, eccentric/inclined orbits.

## Power
Eclipse (circular, β=0, cylindrical shadow): {"; ".join(f"{e['orbit']} {e['max_eclipse_s']/60:.1f} min ({100*e['max_eclipse_fraction']:.0f}% of period)" for e in pw['eclipse'])}.

## Communications
Free-space loss at X-band (8.4 GHz): {"; ".join(f"{x['target']} {x['x_band_8p4ghz_db']:.1f} dB" for x in cm['free_space_loss'])}.
""")
# ---- OPTIMIZATION_REPORT
sc_rows=[]
for e in ex:
    r=e["result"]
    if r: sc_rows.append(f"| {e['scenario_id']} | {e['objective']} | {f(r['wet_kg'],1)} | {f(r['cost'])} | {f(r['science'],1)} | {f(r['avg_power_w'],1)} | {f(r['link_margin_db'],1)} | {e['selected_components']['propulsion']} / {e['selected_components']['comm']} / {e['selected_components']['vehicle']} |")
pt="\n".join(f"| {p['scenario_id']} | {p['front_size']} | {f(min(x['wet_kg'] for x in p['points']),0)}–{f(max(x['wet_kg'] for x in p['points']),0)} | {f(min(x['cost'] for x in p['points']))}–{f(max(x['cost'] for x in p['points']))} | {f(min(x['science'] for x in p['points']),0)}–{f(max(x['science'] for x in p['points']),0)} |" for p in par)
top=[]
for sc in ("leo_eo","lunar_orbiter","mars_orbiter"):
    rs=[r for r in sens if r["scenario_id"]==sc and r["delta_max_science_pct"] is not None or (r["scenario_id"]==sc)]
    rs=[r for r in sens if r["scenario_id"]==sc]
    def mag(r): return max(abs(r[k]) for k in ("delta_min_mass_pct","delta_min_cost_pct","delta_max_science_pct") if r[k] is not None) if any(r[k] is not None for k in ("delta_min_mass_pct","delta_min_cost_pct","delta_max_science_pct")) else (999 if r["result"]["feasible"]==0 else 0)
    for r in sorted(rs,key=mag,reverse=True)[:4]: top.append(f"| {sc} | {r['parameter']} = {r['value']} | {r['result']['feasible']} (base {r['baseline']['feasible']}) | {f(r['delta_min_mass_pct'],1)} | {f(r['delta_min_cost_pct'],1)} | {f(r['delta_max_science_pct'],1)} |")
mct="\n".join(f"| {m['scenario_id']} | {m['design_label']} | {f(100*m['p_feasible'],1)}% | {f(m['wet_kg_p95'])} | {f(m['cost_p95'])} | {m['failure_reason_counts']} |" for m in mc)
W("OPTIMIZATION_REPORT.md",f"""# Optimization report
{BANNER}
## Model
Discrete design selection (instrument subset, computer, comm system, array, battery, propulsion, launch vehicle) with analytic sizing of array, battery, propellant, tank and structure; mass growth allowance {comb['optimization']['constraints']['global_parameters']['mga']:.0%}; Δv margin {comb['optimization']['constraints']['global_parameters']['dv_margin']:.0%}; power margin {comb['optimization']['constraints']['global_parameters']['power_margin']:.0%}; launch-capacity margin {comb['optimization']['constraints']['global_parameters']['launch_margin']:.0%}. Full equations: `optimization/optimization_models.json`.

**Solver:** exhaustive enumeration (deterministic; ties broken by cost, mass, design string). Because the equations are nonlinear (exponential rocket equation, logarithmic link budget) and the catalog is small, enumeration gives exact optima *within the catalog* and the full Pareto set without solver assumptions; LP/MILP/NSGA-style methods were deliberately not used. "Optimal" here never means globally optimal over all possible spacecraft. The browser optimizer (`docs/model.js`) reproduces all {len(ex)} stored results (`tools/parity_check.js`).

**Fictional inputs:** costs are synthetic credits (launch costs derive from published USD only where marked), instrument science weights are educational weights, and most catalog masses/powers are class-level estimates. Reliability is **not optimized**: no evidence-based reliability data were collected.

## Results: {len(ex)} experiments (3 scenarios × 9 formulations)
| Scenario | Objective | Mass kg | Cost cr | Science | Avg W | Link dB | Prop / comm / vehicle |
|---|---|---:|---:|---:|---:|---:|---|
{chr(10).join(sc_rows)}

## Pareto fronts (mass ↓, cost ↓, science ↑)
| Scenario | Front size | Mass range kg | Cost range cr | Science range |
|---|---:|---|---|---|
{pt}

## Largest sensitivities (one-at-a-time, re-optimized)
| Scenario | Perturbation | Feasible designs | Δ min mass % | Δ min cost % | Δ max science % |
|---|---|---|---:|---:|---:|
{chr(10).join(top)}

Budget and Δv dominate; ground G/T and link distance barely move results in the lunar/LEO scenarios because the downlink rate cap (not link margin) binds there — a model-structure finding, not a statement about real missions.

## Monte Carlo (seed 20261106, 2000 samples; assumed distributions)
| Scenario | Design | P(feasible) | Mass p95 kg | Cost p95 cr | Failure counts |
|---|---|---:|---:|---:|---|
{mct}

Designs that max out science or sit near a budget limit have much lower P(feasible) than designs chosen for worst-case margin; this quantifies why `max_feasibility_margin` exists. Cost-growth distribution is an assumption.

## Bottlenecks and data needs
* Better source data needed for: instrument data rates and duty cycles, real component masses/powers/costs, launch prices, radiation environments, thermal limits (not modeled).
* Model omissions: thermal balance, reliability/redundancy, fairing volume, trajectory timing, peak power coincidence (see `not_modeled`).
""")
# ---- DATA_LIMITATIONS
conf="\n".join(f"* **{k['topic']}** — {k.get('note') or ' vs '.join(k['values'])+' — '+k['preferred']}" for k in Q["known_conflicts"])
miss="\n".join(f"* {m}" for m in Q["missing_categories"])
W("DATA_LIMITATIONS.md",f"""# Data limitations
{BANNER}
## Provenance
Records carry `source_ids` that point to the *expected* authoritative document or landing page; `retrieved` is `false` for all of them and no page/section, original value or retrieval date is stored. Field-level provenance (original measurement + unit) therefore does not exist yet. Confidence tags (`low|medium|high`) are subjective recall confidence, not measurement uncertainty.

## Known conflicts and issues
{conf}

## Missing or thin categories
{miss}

## Completeness (% of records with non-null field)
{chr(10).join(f"* **{k}**: " + ", ".join(f"{a} {b}%" for a,b in v.items()) for k,v in Q['completeness_pct'].items())}

## Classification rules applied
`verified` (none), `derived` (calculated from recorded inputs; still depends on unverified inputs), `estimated` (technology-class ranges and optimization catalog), `fictional` (credits, budgets), `unverified` (recalled published values).

## Refresh methodology
1. From a networked environment, fetch each source in `metadata/sources.json`; store original value/unit/page in `provenance.json`.
2. Edit `tools/data_*.py`, set classes to `verified` only when matched to a retrieved document.
3. `python3 tools/build.py && python3 tools/make_schemas.py && python3 tools/validate.py && python3 tools/make_reports.py && node tools/parity_check.js`.
4. Resolve entries in `known_conflicts` first (Electron/Falcon 9 stage masses, Deimos GM).
""")
VC=L("metadata/verification_celestial.json")["checks"]; VLn=L("metadata/verification_launch.json")["checks"]
conf=Q["conflicts_resolved"]
cr="\n".join(f"| {c['record_id']} | {c['field']} | {c['recalled_value']} | {c['source_value']} | {c['source_text']} | {c['source_id']} |" for c in conf)
fmtv=lambda x: "—" if x is None else (f"{x:,.4g}" if isinstance(x,float) and abs(x)<1000 else (f"{x:,.0f}" if isinstance(x,(int,float)) else str(x)))
lv="\n".join(f"| {c['collection']}/{c['record_id']} | {c['field']} | {fmtv(c.get('mine_original'))} | {fmtv(c.get('source_value'))} | {c['status']} | {str(c.get('source_original_text',''))[:70].replace('|','/')} | {c['source_id']} |" for c in VLn)
files="\n".join(f"* `{f['file']}` — {f['url']} (retrieved {f['retrieved']}, sha256 `{f['sha256'][:12]}…`)" for f in J_MAN)
W("VERIFICATION_REPORT.md",f"""# Verification report
{BANNER}
## What "verified" means here
A value is `verified` only if it was compared with a value parsed from a **retrieved local copy** of the cited page (kept in `data_raw/retrieved/`, SHA-256 in `MANIFEST.json`) within a stated tolerance. Each check stores the original text, unit, conversion, URL, retrieval date, file hash and tolerance, in `metadata/verification_celestial.json`, `metadata/verification_launch.json` and in each record's `field_verification`.
A **celestial record** is classed `verified` when its GM and mean radius are verified; its other fields are individually listed in `field_verification` or, if not checked, in `unverified_fields` (surface temperature, magnetic field, many moon orbits, ...). A **launch record** stays `unverified` as a whole; only the fields in its `field_verification` are verified (`verified_field_count`).

## Coverage
* Celestial: {sum(1 for c in VC if c['status']=='verified')} field checks matched; {len(conf)} recalled values disagreed and were replaced by the sourced value (table below). 25 of 25 celestial records verified at core level.
* Launch vehicles, stages, boosters, engines and the Apollo 11 launch date: {len(VLn)} checks against NASA (SLS page, Apollo 11 press kit, NTRS electric-propulsion papers), ULA and ESA pages — {sum(1 for c in VLn if c['status']=='verified')} matched, {sum(1 for c in VLn if c['status']=='conflict')} recalled values were wrong/outdated and replaced by the sourced value, {sum(1 for c in VLn if c['status']=='added_from_source')} previously empty fields were filled from the source (table below). A record is classed `verified` only if **all** of its populated core numeric fields were checked: the 3 Saturn V stages, NEXT, NSTAR, BPT-4000 and BE-4. Vehicles are verified field by field. **Not verifiable with the retrieved material (still unverified):** Falcon 9/Heavy, Starship, Merlin, Raptor, Rutherford, Electron, Ariane 5, Delta IV, New Glenn, Soyuz, Long March 5, RL10, Vinci, Vulcain 2, Star 48B, MR-103, AJ10, Draco, T6, SPT-100, RSRM; most spacecraft components, instruments, propellants, atmospheres and mission figures. Reasons: SpaceX pages are JavaScript-rendered, api.spacexdata.com returned HTTP 522, Rocket Lab was unreachable, Aerojet Rocketdyne returned 403, Blue Origin returned 429, and no retrievable document gave the numbers.

## Recalled values that were wrong or outdated (now replaced)
| Record | Field | Recalled | Source | Source text | Source id |
|---|---|---:|---:|---|---|
{cr}

Notes: JPL gives Eris mean radius 1200±50 km (no diameter in SBDB); a more precise occultation-based figure (~1163 km) exists in the literature but was not retrieved, so it is not used. Small-body elements from SBDB are osculating at the stated epoch, so they differ from older mean values.

## Launch / engine / stage checks
| Record | Field | Recalled | Source | Status | Source text | Source id |
|---|---|---:|---:|---|---|---|
{lv}

## Retrieved files
{files}

## Notes on specific findings
* Saturn V: the Apollo 11 press kit shows my recalled S-IC dry mass (137,000 kg), S-IC and S-II/S-IVB propellant, S-IVB dry mass, liftoff mass and liftoff thrust were off by 1–7%; the document's values (nominal Apollo 11 vehicle) are now used. The old 33.4 vs 34.5-35.1 MN thrust conflict is resolved by the source: 7,653,854 lbf = 34.05 MN.
* NSTAR: the retrieved paper is a 1998 pre-flight document (Isp 'about 3300 s'); flight-measured Isp was not retrieved, so the sourced value is used with that caveat.
* BPT-4000: NASA/TM-2006-214453 Table 2 gives 254 mN and 2150 s at 4.5 kW-400 V (my recalled 1850 s was wrong).
* ULA: Atlas V 551 LEO/GTO capacities matched; reference orbits were filled in (200 km, 28.7 deg; GTO at 27 deg). Vulcan VC6 GTO is 14,500 kg (not 14,400) and TLI is 11,500 kg (added). RD-180 weight is 12,081 lb (5,480 kg); BE-4 sea-level thrust is 550,000 lbf (2.45 MN).
* ESA: Ariane 62/64 GTO/LEO capacities, fairing and height match the ESA overview page (LEO figures are quoted to 0.1 t, so they are verified within 1%).
* ESA: Vega-C fairing is 'over 9 m' tall (recalled 8.1 m was wrong).

## How to extend
Run `tools/fetch_sources.sh`, add parsers following `tools/verify_celestial.py`, and re-run the pipeline in `README.md`. Candidate next sources: NTRS documents for Saturn V stages and engines, manufacturer user guides (PDF) for Falcon, Atlas, Ariane and Electron once their hosts are allowed.
""")
BM=L("analysis/benchmark_results.json")
eq="\n".join(f"| {e['scenario_id']} | {e['designs']:,} | {'exact match' if e['exact_match'] else 'MISMATCH '+str(e['mismatches'])} |" for e in BM["equivalence"])
tm="\n".join(f"| {t['scenario_id']} | {t['designs']:,} | {t['scalar_python_enumerate_s']:.2f} | {t['vectorized_one_full_pass_s']:.3f} | {t['speedup']:.0f}x | {t['js_enumerate_s']:.2f} |" for t in BM["timing"])
sc_="\n".join(f"| {s['instruments']} | {s['designs']:,} | {s['vectorized_exact_solve_s']:.2f} | {f(s['scalar_exact_solve_s'],2)} | {s['optimum_science']:.0f} |" for s in BM["scaling"])
hr="\n".join(f"| {h['scenario_id']} | {h['objective']} | {h['solver']} | {h['runs_found_exact_optimum']}/{h['runs']} | {h['runs_feasible']}/{h['runs']} | {f(h['median_gap_pct'],1)} |" for h in BM["heuristics"] if h["evaluations"]==2000)
W("BENCHMARK_REPORT.md",f"""# Benchmark report
{BANNER}
All timings are single runs on the build sandbox (Python {BM['environment']['python']}, numpy {BM['environment']['numpy']}); relative speedups are meaningful, absolute seconds are not. Reproduce: `python3 tools/benchmark.py`. Heuristic runs use seeds 0-19.

## 1. Exactness: vectorized solver vs scalar reference
| Scenario | Designs | Result (8 objectives) |
|---|---:|---|
{eq}

## 2. Speed (one full pass over every design)
| Scenario | Designs | Scalar Python (s) | Vectorized (s) | Speedup | JavaScript (s) |
|---|---:|---:|---:|---:|---:|
{tm}

## 3. Scaling with instrument count (lunar scenario, synthetic instrument clones, exact max-science)
| Instruments | Designs | Vectorized (s) | Scalar (s) | Optimum science |
|---|---:|---:|---:|---:|
{sc_}

The design space doubles per added instrument; the vectorized exact solver stays under ~1.2 s up to {BM['scaling'][-1]['designs']:,} designs. Clones are synthetic (perturbed copies) and used only to test scaling.

## 4. Heuristic solvers vs the exact optimum (2000 evaluations per run, 20 seeds)
"Found exact" = reached the exact optimum value; "feasible" = run ended on a feasible design; gap = median relative gap among feasible runs.

| Scenario | Objective | Solver | Found exact | Feasible | Median gap % |
|---|---|---|---:|---:|---:|
{hr}

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
""")
SX=L("analysis/spacex_launch_analysis.json"); NF=L("analysis/nasa_facilities_analysis.json")
W("EXTERNAL_DATA_REPORT.md",f"""# External (user-supplied) data report
{BANNER}
Two files were supplied by the user and normalized by `tools/ingest_external.py` (raw copies in `data_raw/`, SHA-256 recorded in each output file and re-checked by `tools/validate.py`). Their original publisher, license and accuracy are **not verified**; the SpaceX file is described by the user as Kaggle `scoleman/spacex-launch-data`, which could not be opened from the build sandbox.

## SpaceX launch table → `missions/spacex_launch_history.json`
* {SX['coverage']['launches']} rows, {SX['coverage']['first']} → {SX['coverage']['last']}. **The file ends at flight 56** — later launches and Block 5 maturity are absent.
* Mission success {SX['mission_reliability']['successes']}/{SX['mission_reliability']['launches']} (95% Wilson {100*SX['mission_reliability']['wilson95_low']:.1f}–{100*SX['mission_reliability']['wilson95_high']:.1f}%). Landing attempts (pad/drone ship only) {SX['landing']['successes']}/{SX['landing']['attempts']} = {100*SX['landing']['success_rate']:.0f}% (Wilson {100*SX['landing']['wilson95_low']:.0f}–{100*SX['landing']['wilson95_high']:.0f}%). Rows with a re-flown booster: {SX['reflown_rows']['count']} ({100*SX['reflown_rows']['fraction']:.0f}%).
* Normalization: ISO dates/times, booster family and serials split, payload mass parsed to kg (approximate `~` flagged; "Classified"/blank → null; {SX['mass_unknown_rows']} unknown), orbit classes, landing outcomes parsed per booster (Falcon Heavy has three), `CCAFS LC-40`/`SLC-40` treated as one pad (assumption).
* Use in the project: observed launch reliability feeds the Simulator's optional launch-reliability factor and the Mission-fit evidence line. It does **not** replace vehicle specifications and must not be extrapolated beyond 2010–2018.

## NASA facilities table → `infrastructure/nasa_facilities.json`
* {NF['records']} facilities, all with parsed coordinates. By status: {NF['by_status']}. By derived category: {NF['by_category']}.
* Data-quality issues found: {NF['quality']['missing_status']} rows without status; {NF['quality']['truncated_status_values']} truncated status value "Under" (assumed Under Rehabilitation); {NF['quality']['missing_url']} without URL; {NF['quality']['missing_occupied_date']} without occupied date.
* `category` is a keyword classifier on the facility name (derived, unreviewed; {NF['by_category'].get('other',0)} fall into `other`). {len(NF['antennas'])} entries look like antennas/ground stations (diameter/band parsed from the name where present).
* Use in the project: reference list of ground-test and ground-station infrastructure; it is not wired into the optimizer.
""")
print("reports written")
