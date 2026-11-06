# Data limitations
> **Read first:** no source document was retrieved when this package was built (the sandbox proxy returned 403 for nasa.gov, jpl.nasa.gov and esa.int). Every external figure is therefore `unverified` (written from recalled published values with a subjective confidence tag). Derived results inherit that status. Optimization catalog values are `estimated`; credits are `fictional`.


## Provenance
Records carry `source_ids` that point to the *expected* authoritative document or landing page; `retrieved` is `false` for all of them and no page/section, original value or retrieval date is stored. Field-level provenance (original measurement + unit) therefore does not exist yet. Confidence tags (`low|medium|high`) are subjective recall confidence, not measurement uncertainty.

## Known conflicts and issues
* **Deimos GM vs mass** — Recorded GM (9.62e-5 km3/s2) and mass (1.4762e15 kg) disagree by ~2.4% via GM=G*M; both retained, GM preferred for orbital use; resolve against JPL SSD sat_phys_par.
* **Small-body surface gravity** — For irregular bodies (Phobos, Deimos, Bennu, Enceladus) g=mu/R^2 is a spherical approximation; recorded g is a mean/typical value.
* **Saturn V liftoff thrust** — ~33.4 MN (design) vs ~34.5-35.1 MN (flight-reported) — 33.4 MN design value recorded; flight values vary by mission
* **Falcon 9 mass accounting** — Recorded liftoff mass minus recorded stage masses leaves ~31 t, more than payload+fairing implies; at least one input (stage dry mass or liftoff mass) is likely off. See analysis/mass_analysis.json.
* **Electron stage masses** — Recorded stage dry+propellant masses sum exactly to liftoff mass, leaving no room for payload/fairing; ideal dv in propulsion_analysis (~11.6-12 km/s) is therefore an overestimate and not a credible ascent number. Needs retrieval of the payload user's guide.
* **SLS stack ideal delta-v** — Core-stage-only accounting (boosters excluded); stack residual is dominated by booster/upper-stage mass, so the ideal-dv total is not a vehicle capability.
* **Mission launch vehicle variants** — Several missions flew Atlas V 401/411/541 variants not in the launch dataset; launch_vehicle_id is null for them.

## Missing or thin categories
* hybrid rocket motors
* most reaction wheels / star trackers as named products with specs
* magnetometers/seismometers/mass spectrometers beyond SAM
* optical comm hardware specs
* radiation environment per body
* terrain characteristics
* per-field provenance with page numbers and original units/measurements (not available without retrieval)

## Completeness (% of records with non-null field)
* **engines**: thrust_vac_n 83.3%, thrust_sl_n 41.7%, isp_vac_s 95.8%, isp_sl_s 33.3%, dry_mass_kg 45.8%, burn_s 16.7%
* **vehicles**: liftoff_mass_kg 75.0%, thrust_sl_n 50.0%, price_usd 12.5%, fairing_diam_m 81.2%, height_m 100.0%
* **instruments**: mass_kg 75.0%, power_w 56.2%
* **missions**: launch_mass_kg 100.0%, dry_mass_kg 21.4%, cost_musd_nominal 71.4%
* **moons**: rotation_period_h 0.0%
* **components**: mass_kg 13.0%, power_consumption_w 4.3%, power_generation_w 8.7%, energy_capacity_wh 0.0%

## Classification rules applied
`verified` (none), `derived` (calculated from recorded inputs; still depends on unverified inputs), `estimated` (technology-class ranges and optimization catalog), `fictional` (credits, budgets), `unverified` (recalled published values).

## Refresh methodology
1. From a networked environment, fetch each source in `metadata/sources.json`; store original value/unit/page in `provenance.json`.
2. Edit `tools/data_*.py`, set classes to `verified` only when matched to a retrieved document.
3. `python3 tools/build.py && python3 tools/make_schemas.py && python3 tools/validate.py && python3 tools/make_reports.py && node tools/parity_check.js`.
4. Resolve entries in `known_conflicts` first (Electron/Falcon 9 stage masses, Deimos GM).
