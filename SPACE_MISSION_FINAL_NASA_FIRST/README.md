# Space Mission Data — Project README

**Project:** NASA-first Space Mission Design Game  
**Planned application:** Browser-based React + TypeScript + Three.js  
**Scientific scope:** Sun–Earth–Moon and Sun–Earth–Mars only  
**Prepared:** November 14, 2026  
**Suggested Windows destination:** `D:\space mission data\SPACE_MISSION_FINAL_NASA_FIRST\`

## 1. Purpose

This folder collects the cleaned **scientific foundations, NASA-supported launch/ascent reference data, developer interface specifications, and quality-assurance records** for the team's space mission design game. It separates information shared by both missions from research that is specific to the Moon or Mars. It is **not** a complete simulator, a verified high-fidelity flight dynamics product, or the complete output of every team member.

## 2. Workstream status

| Workstream / phase | Project status | What is in this folder |
|---|---|---|
| **1 — Rocket Launch & Ascent** | **Completed** as a public-reference research task | A NASA-only, curated **SLS Block 1** subset with rocket/stage data, launch-site references, atmospheric model, event timing, ascent reference profiles, physics helper functions, and limitations. |
| **2A — Earth–Moon Transfer** | **Other team member** | Shared Sun/Earth/Moon scientific foundation and quality-held ephemeris extracts. **The teammate's actual transfer calculations and final transfer dataset are not included.** |
| **2B — Earth–Mars Transfer** | **Other team member** | Shared Sun/Earth/Mars foundation and sparse Earth/Mars JPL Horizons position/velocity reference data. **The teammate's final transfer trajectory, maneuvers, and launch-window results are not included.** |
| **3 — Developer Technical Specification** | **Next — draft prepared** | Developer-facing schema definitions, examples, TypeScript interfaces, telemetry, mission phases, time/frame conventions, visualization adapter, integration guidance, and validation-test plan. Needs interface agreement and implementation sign-off. |
| **Final Phase — Cleaning, Validation & Developer Handover** | **Pending team-wide completion** | An initial cleaned and organized research package, source audit, QA findings, manifests, and starter handover notes. Final integration and release sign-off remain pending. |

**Status distinction:** Workstream 1 research is completed within its declared public-source limitations; this folder does **not** prove a full physics solver or end-to-end launch-to-transfer integration. The cleaned package is a preparation step toward the Final Phase, not proof that the Final Phase is finished.

## 3. Directory guide

```text
SPACE_MISSION_FINAL_NASA_FIRST/
├── 01_COMMON_FOUNDATION/
│   ├── FOUNDATION.md
│   ├── NASA_JPL_source_notes.md
│   ├── horizons_query_template.json
│   ├── planetary_constants_NASA_JPL.csv
│   ├── jpl_planetary_physical_parameters_original.html
│   ├── naif_kernels/
│   │   ├── de440s.official.bsp
│   │   ├── latest_leapseconds.tls
│   │   └── pck00011.tpc
│   └── tools/horizons_fetch.py
├── 02_SUN_EARTH_MOON/
│   ├── README.md
│   ├── foundation_readiness.csv
│   └── QA_HOLD/                       # Three uncertified state-vector CSVs + notes
├── 03_SUN_EARTH_MARS/
│   ├── README.md
│   ├── foundation_readiness.csv
│   ├── earth_mars_horizons_30day_TDB_ECLIPJ2000.csv
│   ├── horizons_original/              # Original JPL Horizons Earth and Mars text
│   └── nasa_planetary_fact_sheet_original.html
├── 04_LAUNCH_AND_ASCENT/
│   ├── README.md
│   ├── data/                          # SLS, atmosphere, events, launch sites, constants
│   ├── src/                           # JavaScript physics helper and validation scripts
│   ├── templates/                     # Blank ascent-profile template
│   ├── nasa_raw_references/           # NASA Glenn atmosphere reference pages
│   └── historical_notes/              # Historical notes, not current subset certification
├── 05_DEVELOPER_SPECIFICATION/
│   ├── README.md
│   ├── data/                          # 15 CSV registries and reference catalogues
│   ├── schemas/                       # Four JSON Schema definitions
│   ├── examples/                      # Four illustrative JSON messages
│   ├── src/                           # TypeScript contracts, Three.js scene adapter
│   ├── docs/                          # Data dictionary, interface and source guidance
│   ├── scripts/                       # Validation and NASA-asset retrieval utilities
│   └── requirements.txt
├── 06_OPTIONAL_NASA_CONTEXT/
│   └── donki_solar_flares_2026_sample.json
├── 07_KAGGLE_CANDIDATES_NOT_AUTHORITATIVE/
│   └── kaggle_NASA_named_rockets_review_only.csv
├── 08_VALIDATION_AND_QA/
│   ├── data_policy.md
│   ├── quality_findings.csv
│   ├── excluded_and_filtered_items.csv
│   ├── duplicate_content_report.csv
│   ├── master_data_manifest.csv
│   ├── original_upload_file_list.csv
│   ├── original_upload_integrity.json
│   ├── validation_results.json
│   └── validate_release.py
├── 09_DEVELOPER_HANDOVER/
│   └── START_HERE.md
└── README.md
```

## 4. Shared foundation — `01_COMMON_FOUNDATION/`

This folder contains information that **both** destination systems require. Avoid keeping a different copy of the Sun/Earth constants or NAIF kernels in each mission folder.

- **NASA/JPL planetary constants:** common physical parameters such as gravitational parameters and body radii, with supporting source documents.
- **NAIF SPICE kernels:** the `de440s.official.bsp` ephemeris kernel; `latest_leapseconds.tls` for leap-second/time handling; and `pck00011.tpc` for planetary constants/orientation definitions.
- **Time conventions:** distinguish human-readable **UTC** from NAIF **TDB/ET seconds past J2000** and mission elapsed time (**MET**).
- **Coordinate conventions:** identify the reference frame (such as **J2000** or **ECLIPJ2000**), the origin (for example the Solar System Barycenter), and units (**km**, **km/s**). A frame name is not an origin.
- **Reproducibility tools:** NASA/JPL notes, Horizons request template, and a fetch helper.

**Foundational concepts:** gravity; Cartesian position/velocity vectors; inertial versus body-fixed frames; time-scale conversion; ephemeris interpolation and coverage; common mission-state handoff formats.

## 5. Sun–Earth–Moon — `02_SUN_EARTH_MOON/`

This folder documents the lunar mission foundation. It references the shared NAIF kernel and includes a readiness checklist.

- Three processed **Earth, Moon, and Sun state-vector CSVs**, **4,018 records each**, are retained under `QA_HOLD/` for auditability.
- Their UTC timestamps show a systematic drift from intended UTC midnight (for example, January 2 labelled `00:00:22` and January 3 labelled `00:00:43`). **Do not use these CSVs as certified mission-time inputs until corrected.**
- The shared DE440S SPICE kernel is the preferred basis for a clean, consistently time-converted re-extraction.
- **Not included:** the teammate's actual Earth–Moon transfer maneuvers, launch windows, trajectory solver, or validated arrival-state outputs.

Relevant foundations: Earth/Moon/Sun gravity; Earth parking orbit; lunar transfer departure and arrival state; consistent epoch, frame and origin.

## 6. Sun–Earth–Mars — `03_SUN_EARTH_MARS/`

This folder documents the Mars mission foundation and contains JPL Horizons reference material.

- `earth_mars_horizons_30day_TDB_ECLIPJ2000.csv` contains **244 Earth/Mars reference records** over **122 matched epochs** (one record per body per epoch).
- The original Earth and Mars Horizons text responses are preserved in `horizons_original/`.
- Source vectors are based on **DE441/mar099**, **TDB**, **ECLIPJ2000**, **Solar System Barycenter origin**, and a **30-day sampling step**. These are **planetary reference states**, not a spacecraft flight path.
- A matching Sun vector for the same Horizons source configuration is not present; obtain compatible Sun states or regenerate every body state under one agreed NAIF kernel/frame/time scheme.
- **Do not directly join** these ECLIPJ2000/DE441 records to J2000/DE440S vectors without deliberate transformation and source-model reconciliation.
- **Not included:** the teammate's final Earth–Mars transfer solution, launch windows, midcourse maneuvers, or arrival conditions.

Relevant foundations: heliocentric/barycentric geometry; Mars/Earth ephemerides; interplanetary transfer boundary states; epoch consistency.

## 7. Workstream 1 — `04_LAUNCH_AND_ASCENT/`

The curated authoritative launch dataset is **NASA-only SLS Block 1**, rather than the older four-launcher research catalogue. This includes:

- `rocket_vehicle_catalog.csv`, `rocket_stage_engine_specs.csv`, and `rocket_payload_performance_reference.csv`.
- `launch_site_specs.csv` and `launch_site_vehicle_compatibility.csv`.
- `earth_standard_atmosphere_1976_0_80km_1km.csv`.
- `launch_event_reference.csv`, two clearly labelled SLS ascent reference profiles, and `sls_rs25_thrust_schedule_reference.csv`.
- `launch_simulation_constants.json` and the NASA source registry.
- `src/ascent_physics.js`, JavaScript smoke tests, and a package-validation script.
- The empty `launch_ascent_profile_template.csv` template, explicitly **not** recorded telemetry.

**Limitations:** Missing stage mass/propellant and full thrust/aerodynamics details prevent a flight-qualified ascent model. Some launch-pad geodetic details require verification. Prelaunch SLS profiles are planning/approximate references, not as-flown continuous data. The historical v0.2.2 report refers to a broader previous package, not certification of this NASA-only subset.

## 8. Workstream 3 — `05_DEVELOPER_SPECIFICATION/`

The integration foundation targets a **React + TypeScript + Three.js** browser game. Scientific propagation remains separate from Three.js rendering.

- **15 CSV files** define units, time systems, reference frames, coordinate transformations, mission phases, telemetry fields, module-handoff fields, source provenance, visualization assets, NASA reference assets, and planned validation tests.
- **Four JSON schemas:** spacecraft state; telemetry record; mission event; module handoff.
- **Four example JSON payloads** illustrate expected message shapes. Their numerical values are examples only and are **not** NASA flight measurements or guaranteed physically consistent timestamps.
- **TypeScript:** `missionContracts.ts` for type definitions, `sceneCoordinates.ts` for rendering-only local-origin/axis/scale mapping.
- **NASA reference files:** Artemis I mission-event timing CSV; Artemis II environmental **dataset catalogue**; Artemis II/SPICE **official asset manifest**. The latter two are *catalogues of links*, not complete raw telemetry or kernel downloads.
- **Utilities:** schema/example validation and a script for downloading selected official Artemis II assets from accessible publisher endpoints.

**Still needed:** agreement with the transfer researcher on frame, origin, TDB epoch, mass, propellant and mission-state semantics; final visualization requirements; and actual cross-module integration tests.

## 9. Optional and review-only material

- **`06_OPTIONAL_NASA_CONTEXT/`** — a sample NASA DONKI solar-flare JSON dataset for an optional space-weather panel. It is **not** gravitational/trajectory force data.
- **`07_KAGGLE_CANDIDATES_NOT_AUTHORITATIVE/`** — a small NASA-labelled rocket record shortlist. Kaggle is approved only as a **secondary research channel**. Candidate labels do not establish NASA authority; the numeric values should not be promoted into game physics without source-level verification.

## 10. Quality assurance — `08_VALIDATION_AND_QA/`

This folder holds the source eligibility rules, duplicate/exclusion logs, master file manifest, upload integrity notes, automated check results, and known limitations.

**Checks recorded as passing in `validation_results.json`:** filtered NASA/SLS and source-ID checks, Horizons/Moon QA structure checks, launch physics JavaScript smoke tests, Workstream 1 filtered validation, and Workstream 3 schema/example validation. **These do not amount to full scientific validation or end-to-end game testing.**

**Known issues to resolve:**

1. Fix Moon-system CSV time labels before production use.
2. Obtain matching, correctly framed Sun/Earth/Mars states for any combined numerical propagation.
3. Resolve missing SLS propulsion and launch-site engineering parameters or keep them explicitly unavailable/approximate.
4. Obtain teammate-owned Moon/Mars transfer results and approve module state contracts.
5. Keep demonstration JSON values separate from real NASA state measurements.
6. Independently re-verify official source provenance and kernel coverage before an external release.

The original large uploaded ZIP is **not included** in the cleaned developer ZIP. Preserve it as a **separate read-only research backup** containing historical and excluded material.

## 11. Developer handover — `09_DEVELOPER_HANDOVER/`

Start with `START_HERE.md`. The intended data flow is:

```text
Mission choices (React/TypeScript)
    -> NASA-backed launch/ascent references and simulation module
    -> documented spacecraft-state handoff
    -> teammate-owned Earth–Moon or Earth–Mars trajectory module
    -> time-tagged spacecraft state/telemetry
    -> Three.js scene rendering and mission dashboard
```

**Do not:** use scene coordinates as physical propagation coordinates; infer numerical zero from missing telemetry; silently mix UTC with TDB, J2000 with ECLIPJ2000, or source models DE440S with DE441; or treat a catalogue link or an approximate profile as measured flight data.

## 12. Approved data-source policy

1. **Primary:** NASA and NASA-managed repositories and archives, including NASA.gov, JPL/NAIF, NASA PDS, NASA Open Data, NASA NTRS, Artemis, DONKI, FIRMS, OSDR and SPHEREx when relevant.
2. **Secondary:** Kaggle datasets, subject to clear original provenance, permitted use, and NASA/source cross-checks. These are not automatically scientific authority.
3. **Excluded from authoritative tables:** China-/Russia-/other non-U.S.-affiliated institutional science and unapproved non-NASA manufacturer-only source values, under the team's chosen scope.
4. Preserve clear labels distinguishing **official raw**, **processed**, **reference/approximate**, **calculated**, **game configurable**, **example**, **QA hold**, and **unverified secondary** content.

These source restrictions are **team research-selection preferences**, not a scientific statement about the quality of entire countries' research.

## 13. Suggested reading order and next steps

1. Read this README and `09_DEVELOPER_HANDOVER/START_HERE.md`.
2. Review `08_VALIDATION_AND_QA/quality_findings.csv` and `data_policy.md` **before importing datasets**.
3. Read `01_COMMON_FOUNDATION/FOUNDATION.md` to establish a single coordinate/time convention.
4. Load the launch reference CSVs under `04_LAUNCH_AND_ASCENT/data/` and examine the documented gaps.
5. Validate Workstream 3 schemas/examples; agree with teammates on the shared spacecraft-state contract.
6. Use the Moon and Mars folders as **reference foundations**, not completed transfer solutions.
7. Integrate the other researcher's transfer data, rerun QA and mark the Final Phase complete **only after** acceptance testing and team sign-off.

---

**Package status:** Cleaned research foundation and draft developer handover, with explicit source/quality restrictions. **Workstream 3 and final cross-team handover remain open.**
