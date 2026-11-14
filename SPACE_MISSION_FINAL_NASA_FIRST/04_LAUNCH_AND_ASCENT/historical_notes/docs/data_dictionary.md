# Data Dictionary — Workstream 1 v0.2.2

All CSV files use UTF-8 with a header row. Decimal points are used. Empty cells mean unavailable/not verified; they are not zero.

## `rocket_vehicle_catalog.csv`
- `vehicle_id`: stable key for the selected vehicle configuration.
- `core_or_first_stage_engine_count`: number of first-stage liquid engines (or engine systems where the vehicle source presents that convention).
- `strap_on_solid_booster_count`: attached solid motor count.
- `payload_to_*_kg`: published headline/reference payload point. Interpret with `payload_performance_conditions`.
- `data_status`: concise description of limitations.

## `rocket_stage_engine_specs.csv`
- `component_quantity`: number of engines/motors of this component on the selected vehicle.
- `thrust_sea_level_kN_each`, `thrust_vacuum_kN_each`: only populated when the source explicitly states that condition.
- `thrust_other_or_nominal_kN_each`: published nominal/peak value whose exact ambient condition is not explicit or whose rating is not classed as SL/vacuum in the source.
- `thrust_at_launch_kN_each`, `thrust_max_kN_each`: source-labelled launch and maximum thrust ratings; do not silently relabel as sea-level or vacuum.
- `specific_impulse_other_or_nominal_s`: source-reported specific impulse where the cited table does not explicitly identify sea-level or vacuum conditions; do not assume a condition.
- Historical Atlas V Common Centaur 5X1 values are kept in a separate stage row and must not be merged with the current RL10C-1 engine reference.
- `mission_reference`: mission/configuration/revision to which the row applies; keep distinct variants in separate rows.
- `specific_impulse_*_s`: only populated when the source explicitly supports that condition.
- `stage_dry_mass_kg`, `stage_propellant_mass_kg`: stage-level quantities only where the source actually gives those definitions.
- `reported_component_*_mass_kg`: component/motor mass records that are not necessarily stage-level dry or propellant mass. The mass basis must specify whether this is per engine/motor, loaded, empty, or derived.
- `reported_mass_basis`: text specifying what a reported mass means. Do not silently rename “weight”, “total motor mass”, “empty”, or “burnout estimate”.

## `rocket_payload_performance_reference.csv`
- `payload_kg`: manufacturer/NASA published capability value.
- `orbit_definition`: source-specific reference orbit or mission descriptor.
- `C3_km2_s2`: only used where the source explicitly states a C3 condition.

## `launch_site_specs.csv`
- `precision_flight_dynamics_use` and `recommended_use`: indicate whether source coordinates are suitable for contextual display or require datum/elevation verification before precision calculations.
- `latitude_deg`, `longitude_deg`: decimal geodetic or map coordinates exactly as indicated by the cited source; not all sources identify a common geodetic datum.
- `datum_as_stated_by_source`: datum/ellipsoid text from source. “Not stated” is intentional.
- `site_elevation_m`: blank when no pad-grade elevation tied to a named vertical datum was verified.
- `coordinate_quality`: evidence quality; secondary map coordinates must not be treated as surveyed coordinates.

## `launch_site_vehicle_compatibility.csv`
- `compatibility_status`: evidence strength for matching the selected vehicle to a pad. A family-level match is not automatically a selected-configuration approval.

## `launch_event_reference.csv`
- `time_from_liftoff_s`: mission elapsed seconds from liftoff as published by NASA.
- `time_basis` / `data_status`: distinguishes actual mission timeline values from launch-day milestone estimates.
- Event times are discrete checkpoints, not a continuous ascent telemetry stream.

## `sls_ascent_reference_profile_approx.csv`
- `speed_m_s`, `altitude_m`: conversions from the source's published mph and ft columns.
- `profile_status`: explicit note that the source data is approximate reference mission analysis, not actual flight telemetry.

## `sls_ascent_reference_profile_artemis_ii_prelaunch.csv`
- Seven time/speed/altitude checkpoints published in the NASA Artemis II SLS Reference Guide (October 2025). These are approximate prelaunch estimates, not the executed flight path or raw telemetry.

## `sls_rs25_thrust_schedule_reference.csv`
- `relative_time_s`: seconds relative to liftoff; negative values are pre-liftoff.
- `thrust_command_percent_of_reference`: only included where source provides a percentage. Blank values mean source gives the timing but not a percentage.

## `earth_standard_atmosphere_1976_0_80km_1km.csv`
- 81 one-kilometre samples from sea level through 80 km.
- Density/pressure/temperature are standard-atmosphere model outputs, not measured launch weather.

## `data_completeness_and_known_gaps.csv`
- Records the field-by-field public source coverage and follow-up needed for each selected vehicle.

## `source_registry.csv`
- `source_id` links a value to the publisher/reference that supports it.
- `caveat` records source limitations and intended interpretation.

## Mission-specific SLS rows
- `rocket_stage_engine_specs.csv` keeps earlier SLS/Artemis I reference rows separate from Artemis II prelaunch rows. The Artemis II ICPS uses RL10C-2; Artemis I uses RL10B-2 in NASA's December 2025 RL10 fact sheet.
- Any propellant mass calculated as loaded minus unfueled/empty mass is explicitly marked as derived and approximate.
- `rocket_vehicle_catalog.csv` distinguishes SLS Artemis II reference launch thrust from maximum thrust and labels launch mass as an approximate prelaunch value.
