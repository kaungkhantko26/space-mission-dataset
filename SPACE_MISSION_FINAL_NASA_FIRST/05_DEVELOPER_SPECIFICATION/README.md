# React + TypeScript + Three.js browser integration

Keep scientific simulation and camera/render transform separate. The client receives the scientific state (exact frame, origin and TDB epoch) and applies explicit coordinate transforms and local-origin rendering for Three.js. The JSON schemas/examples and mission-phase/telemetry tables are project-authored interface contracts, not NASA measured flight data.

Ownership: launch/parking orbit research is the current team member; Sun-Earth-Moon and Sun-Earth-Mars transfer research is another team member; landing/material gathering are other researchers. Those transfer/landing deliverables are NOT in this upload and cannot be marked integrated.

`data/artemis_ii_environment_dataset_catalog.csv` and `data/official_reference_asset_manifest.csv` are link catalogues, NOT the referenced original files. Sample JSON values under `examples/` are fabricated schema demonstrations.

Important release blocker: technical interface schema and source registry validation is not proof of end-to-end launch-to-transfer integration.
