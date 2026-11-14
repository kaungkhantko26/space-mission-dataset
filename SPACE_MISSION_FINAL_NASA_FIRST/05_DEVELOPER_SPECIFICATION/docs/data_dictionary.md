# Workstream 3 Package Data Dictionary

All CSV files are UTF-8 with headers. Empty fields mean unavailable/not applicable, not zero.

- `source_use_matrix.csv`: how the resources from the team's announced source list are used, deferred or excluded.
- `unit_registry.csv`: canonical cross-module unit convention and notes.
- `time_system_registry.csv`: distinction among UTC, SPICE TDB/ET, mission elapsed time (MET) and spacecraft clock (SCLK).
- `reference_frame_registry.csv`: exact frame type, origin expectations and frame-use cautions.
- `coordinate_transform_registry.csv`: required transform steps and correct SPICE functions.
- `mission_phase_registry.csv`: mission phase identifiers, owner and research-scope boundary.
- `telemetry_field_registry.csv`: field definitions, unit, producer and whether mandatory/conditional.
- `module_handoff_field_registry.csv`: required values exchanged between launch, transfer and landing modules.
- `artemis_i_mission_event_reference.csv`: selected NASA-published Artemis I MET event markers; not trajectory samples.
- `artemis_ii_environment_dataset_catalog.csv`: metadata and direct links for two Orion locker HOBO CSVs; raw rows are not copied into this package.
- `official_reference_asset_manifest.csv`: official Artemis II PDS/NAIF files and links.
- `donki_optional_endpoint_registry.csv`: optional DONKI endpoint templates; not a snapshot of event responses.
- `visualization_asset_registry.csv`: source asset recommendations for visual context and integration testing.
- `simulation_validation_test_matrix.csv`: developer acceptance tests.

JSON Schema files are Draft 2020-12. Example messages explicitly contain illustrative values and must not be treated as flight data.
