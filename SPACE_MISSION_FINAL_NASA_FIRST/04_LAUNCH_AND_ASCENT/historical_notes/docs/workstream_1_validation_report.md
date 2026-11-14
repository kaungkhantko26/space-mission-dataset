# Workstream 1 Validation Report — Package v0.2.2

**Validation date:** 2026-11-14  
**Scope:** public-source rocket launch and ascent research for Falcon Heavy, Vulcan Centaur VC6S, Atlas V 551 and SLS Block 1.

## Summary

This package is a curated public-reference dataset and developer-support foundation. It is not a flight-qualified rocket model, and it does not contain continuous as-flown ascent telemetry or complete proprietary flight-control / aerodynamic data. Unsupported fields remain blank or are explicitly marked as derived, approximate, historical, mission-specific or contextual.

## Dataset row counts

- `data/data_completeness_and_known_gaps.csv`: 32 data rows
- `data/earth_standard_atmosphere_1976_0_80km_1km.csv`: 81 data rows
- `data/launch_ascent_profile_template.csv`: 0 data rows
- `data/launch_event_reference.csv`: 15 data rows
- `data/launch_site_specs.csv`: 4 data rows
- `data/launch_site_vehicle_compatibility.csv`: 6 data rows
- `data/legacy_launch_data_quality_review.csv`: 5 data rows
- `data/rocket_payload_performance_reference.csv`: 10 data rows
- `data/rocket_stage_engine_specs.csv`: 15 data rows
- `data/rocket_vehicle_catalog.csv`: 4 data rows
- `data/sls_ascent_reference_profile_approx.csv`: 7 data rows
- `data/sls_ascent_reference_profile_artemis_ii_prelaunch.csv`: 7 data rows
- `data/sls_rs25_thrust_schedule_reference.csv`: 10 data rows
- `data/source_registry.csv`: 25 data rows

## Work completed in this revision

1. Curated source-backed vehicle and propulsion references for Falcon Heavy, Vulcan Centaur VC6S, Atlas V 551 and SLS Block 1.
2. Added separate Artemis II SLS reference records for the RS-25 core engines, five-segment solid rocket boosters and RL10C-2 ICPS configuration; retained Artemis I RL10B-2 separately.
3. Corrected the Atlas V 500-series Common Core booster inert mass to 21,351 kg from the ULA Atlas V Launch Services User's Guide, Revision 11 (2010); retained its historical revision caveat.
4. Added a separate historical Atlas V 500-series Common Centaur 5X1 single-engine stage reference (2,247 kg inert mass; 20,830 kg propellant; 99.2 kN nominal SEC thrust and source-listed 450.5 s Isp with ambient condition not explicitly labelled). It is not merged with the current RL10C-1 engine record.
5. Distinguished published sea-level, vacuum, launch, maximum, nominal and condition-unspecified thrust ratings rather than conflating them.
6. Kept the Vulcan GEM 63XL value from ULA's vehicle-specific page separate from the slightly different Northrop Grumman catalog rating; both sources and the discrepancy are documented.
7. Included an 81-point U.S. Standard Atmosphere 1976 table from 0 to 80 km at 1 km increments.
8. Included NASA Artemis I actual mission-elapsed-time ascent milestones; these are discrete event times, not continuous telemetry.
9. Included NASA Artemis II launch-day milestone time estimates and a separate seven-point October 2025 prelaunch profile with speed/altitude. These two representations are intentionally not merged: the launch-day update gives event time estimates, while the guide's speed/altitude profile is prelaunch planning data.
10. Documented launch-site vehicle compatibility and the coordinate/elevation limitations. LC-39B historical coordinates carry a Fischer 1960 ellipsoid reference; SLC-3E remains secondary/context-only.
11. Corrected the earlier misuse of the Artemis I 483-second core MECO mission-elapsed time as a generic nominal burn-duration field; it remains only in the event timeline.
12. Added the source registry, data dictionary, model assumptions, physics helper functions, smoke tests and known-gap register.

## Validation checks

- CSV structure and unique column names: PASS
- Source ID cross-references against `source_registry.csv`: PASS
- Atmosphere samples: PASS (81 rows, 0–80 km at 1 km increments)
- Vehicle catalog uniqueness: PASS
- Launch event ID uniqueness: PASS
- SLS reference profile time ordering: PASS
- JSON syntax: PASS
- JavaScript smoke tests: PASS (`npm test` in `src/`)

## What the package supports

- Comparing the four selected launch vehicles and their published configurations.
- Baseline propulsion calculations where all required input values are explicitly available.
- Looking up a standard atmospheric reference from sea level through 80 km.
- Displaying mission events and approximate SLS ascent reference checkpoints with correct provenance labels.
- Showing launch-site context and vehicle compatibility with coordinate-quality caveats.
- Giving developers a starter set of equations and data conventions for a simplified launch model.

## Known public-data limitations

- Complete dry mass, propellant loading and detailed stage mass breakdown are not publicly specified in the cited sources for every selected vehicle/configuration. Atlas historical 5X1 stage values are intentionally labelled as a 2010 reference, not guaranteed for every 551 flight.
- Complete time-dependent thrust, throttle, mass-flow and engine performance curves are not available for every selected vehicle and engine variant.
- Complete aerodynamic coefficient tables (Mach / angle-of-attack / Reynolds dependent), launch-day wind profiles and pad-grade elevations tied to a common vertical datum are not included.
- Artemis I/II material in this package consists of discrete event checkpoints or approximate/preflight profiles, not a continuous public as-flown ascent telemetry series.
- Some pad coordinate datums are unstated or historical. SLC-3E uses secondary approximate coordinates and is contextual only; no pad elevations with confirmed vertical datums are supplied.
- Mission-specific vehicle mass, payload adapter, fairing, launch configuration and current operational pad selection should be checked against the exact mission build documentation before quantitative simulation.
- The 0–80 km standard atmosphere is a reference atmosphere, not actual weather. A launch simulation requiring higher-altitude atmospheric effects needs a separately specified upper-atmosphere model.

## Completion decision

**Workstream 1 public-reference research collection: COMPLETE for the agreed hackathon research scope, with documented limitations.** The package provides source-backed published values where available, distinct mission/configuration records, useful reference event/profile data, and explicit gaps instead of invented engineering specifications.

**A high-fidelity operational launch simulator: NOT completed by this research package.** Workstream 3 must specify a tractable simplified 3-DOF game model, identify non-public engineering values as game-configurable assumptions, and define the handoff of spacecraft position, velocity, mass, propellant and epoch to the separate Earth-Moon / Earth-Mars transfer module.
